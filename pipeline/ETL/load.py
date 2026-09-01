"""
Load stage of the ETL pipeline.

Writes cleaned raw data and hourly aggregates to MongoDB and S3.
This is the ONLY stage that writes to external storage — everything
before this just transforms data in memory.
"""

import json
import certifi
import pandas as pd
from datetime import datetime, timezone
from pymongo import MongoClient
from config import settings
from .s3_utils import get_s3_client

_client = None


def get_mongo_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_uri, tlsCAFile=certifi.where())
    return _client


def df_to_mongo_records(df: pd.DataFrame) -> list[dict]:
    """
    Converts a DataFrame to a list of dicts suitable for MongoDB insertion,
    preserving actual datetime objects (not strings) so date range
    queries work correctly later.
    """
    records = df.to_dict(orient="records")
    for record in records:
        for key, value in record.items():
            if isinstance(value, pd.Timestamp):
                record[key] = value.to_pydatetime()
    return records


def load_raw_to_mongo(df: pd.DataFrame) -> int:
    """
    Inserts cleaned raw sensor readings into the 'raw_readings' collection.
    """
    client = get_mongo_client()
    db = client[settings.mongo_db_name]
    collection = db["raw_readings"]

    records = df_to_mongo_records(df)

    if not records:
        print("[load] No raw records to insert")
        return 0

    result = collection.insert_many(records)
    print(f"[load] Inserted {len(result.inserted_ids)} raw readings into MongoDB")
    return len(result.inserted_ids)


def load_hourly_to_mongo(df: pd.DataFrame) -> int:
    """
    Inserts hourly aggregated data into the 'hourly_aggregates' collection.
    """
    client = get_mongo_client()
    db = client[settings.mongo_db_name]
    collection = db["hourly_aggregates"]

    records = df_to_mongo_records(df)

    if not records:
        print("[load] No hourly records to insert")
        return 0

    result = collection.insert_many(records)
    print(f"[load] Inserted {len(result.inserted_ids)} hourly aggregates into MongoDB")
    return len(result.inserted_ids)


def upload_json_to_s3(records: list, key: str) -> None:
    """
    Uploads a list of dict records as a JSON file to S3 at the given key.

    Args:
        records: list of dicts (already JSON-serializable)
        key: full S3 object key, e.g. "raw-processed/2026-08-31.json"
    """
    s3 = get_s3_client()
    body = json.dumps(records, indent=2)

    s3.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=body,
        ContentType="application/json",
    )
    print(f"[load] Uploaded {key} to S3 ({len(records)} records)")


def load_to_s3(raw_df: pd.DataFrame, hourly_df: pd.DataFrame, source_filename: str) -> None:
    """
    Writes both raw and hourly data to S3 as JSON, using the source
    filename (minus extension) as the basis for the output keys.

    e.g. source_filename="2026-08-31.csv" produces:
        raw-processed/2026-08-31.json
        processed/2026-08-31_hourly.json
    """
    base_name = source_filename.rsplit(".", 1)[0]  # strip ".csv"

    raw_records = json.loads(raw_df.to_json(orient="records", date_format="iso"))
    hourly_records = json.loads(hourly_df.to_json(orient="records", date_format="iso"))

    upload_json_to_s3(raw_records, f"{settings.raw_processed_prefix}{base_name}.json")
    upload_json_to_s3(hourly_records, f"{settings.processed_prefix}{base_name}_hourly.json")


def load(raw_df: pd.DataFrame, hourly_df: pd.DataFrame, source_filename: str) -> None:
    """
    Runs the full load sequence: raw data + hourly aggregates ->
    MongoDB AND S3.
    """
    load_raw_to_mongo(raw_df)
    load_hourly_to_mongo(hourly_df)
    load_to_s3(raw_df, hourly_df, source_filename)