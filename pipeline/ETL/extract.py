"""
Extract stage of the ETL pipeline.

Responsible ONLY for getting raw CSV data into a pandas DataFrame.
No validation, cleaning, or transformation happens here.
"""

import io
import pandas as pd
from pathlib import Path
from .s3_utils import get_s3_client
from config import settings


def extract_from_local(file_path: str) -> pd.DataFrame:
    """
    Read a CSV file from the local filesystem into a DataFrame.
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"No such file: {file_path}")

    df = pd.read_csv(path)
    print(f"[extract] Loaded {len(df)} rows from {file_path}")
    return df


def extract_from_s3(key: str) -> pd.DataFrame:
    """
    Read a CSV file from S3 into a DataFrame.

    Args:
        key: S3 object key, e.g. "raw-validated/2026-08-31.csv"

    Returns:
        A pandas DataFrame with the raw (unvalidated) contents.
    """
    s3 = get_s3_client()

    response = s3.get_object(Bucket=settings.s3_bucket_name, Key=key)
    csv_bytes = response["Body"].read()

    df = pd.read_csv(io.BytesIO(csv_bytes))
    print(f"[extract] Loaded {len(df)} rows from s3://{settings.s3_bucket_name}/{key}")
    return df