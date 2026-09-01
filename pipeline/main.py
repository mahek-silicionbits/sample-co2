"""
Main entry point for the ETL pipeline.

Scans raw-validated/ in S3 for files not yet processed, and runs
the full ETL sequence on each one. Designed to be called repeatedly
by cron with no arguments needed.
"""

from pathlib import Path

from ETL.extract import extract_from_s3
from ETL.validate import validate
from ETL.clean import clean
from ETL.transform import transform
from ETL.load import load
from ETL.s3_utils import get_s3_client
from config import settings


def list_unprocessed_files() -> list[str]:
    """
    Lists files in raw-validated/ that don't yet have a corresponding
    output in raw-processed/ — our simple 'already processed' check.
    """
    s3 = get_s3_client()

    validated = s3.list_objects_v2(
        Bucket=settings.s3_bucket_name,
        Prefix="raw-validated/"
    ).get("Contents", [])

    processed = s3.list_objects_v2(
        Bucket=settings.s3_bucket_name,
        Prefix="raw-processed/"
    ).get("Contents", [])

    processed_filenames = {Path(obj["Key"]).stem for obj in processed}

    unprocessed_keys = []
    for obj in validated:
        key = obj["Key"]
        if key.endswith("/"):  # skip folder placeholder itself
            continue
        filename_stem = Path(key).stem
        if filename_stem not in processed_filenames:
            unprocessed_keys.append(key)

    return unprocessed_keys


def run_pipeline(s3_key: str) -> None:
    """
    Runs the complete ETL pipeline for a single file already sitting
    in S3 (in raw-validated/).
    """
    print(f"\n{'='*50}")
    print(f"Starting pipeline for: {s3_key}")
    print(f"{'='*50}\n")

    source_filename = Path(s3_key).name

    raw_df = extract_from_s3(s3_key)
    valid_df, invalid_df = validate(raw_df)

    if len(invalid_df) > 0:
        print(f"[main] WARNING: {len(invalid_df)} rows failed validation and were dropped")

    if len(valid_df) == 0:
        print("[main] No valid rows to process. Stopping pipeline.")
        return

    cleaned_df = clean(valid_df)
    hourly_df = transform(cleaned_df)
    load(cleaned_df, hourly_df, source_filename=source_filename)

    print(f"\n{'='*50}")
    print(f"Pipeline completed successfully for: {s3_key}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    unprocessed = list_unprocessed_files()

    if not unprocessed:
        print("[main] No new files to process.")
    else:
        print(f"[main] Found {len(unprocessed)} unprocessed file(s)")
        for key in unprocessed:
            run_pipeline(key)