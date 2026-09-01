"""
Main entry point for the ETL pipeline.

Runs the full sequence: extract -> validate -> clean -> transform -> load.

Usage:
    python main.py <s3_key>
    e.g. python main.py raw-validated/2026-09-01_143022.csv
"""

import sys
from pathlib import Path

from ETL.extract import extract_from_s3
from ETL.validate import validate
from ETL.clean import clean
from ETL.transform import transform
from ETL.load import load


def run_pipeline(s3_key: str) -> None:
    """
    Runs the complete ETL pipeline for a single file already sitting
    in S3 (in raw-validated/).
    """
    print(f"\n{'='*50}")
    print(f"Starting pipeline for: {s3_key}")
    print(f"{'='*50}\n")

    source_filename = Path(s3_key).name

    # Extract
    raw_df = extract_from_s3(s3_key)

    # Validate
    valid_df, invalid_df = validate(raw_df)

    if len(invalid_df) > 0:
        print(f"[main] WARNING: {len(invalid_df)} rows failed validation and were dropped")

    if len(valid_df) == 0:
        print("[main] No valid rows to process. Stopping pipeline.")
        return

    # Clean
    cleaned_df = clean(valid_df)

    # Transform
    hourly_df = transform(cleaned_df)

    # Load
    load(cleaned_df, hourly_df, source_filename=source_filename)

    print(f"\n{'='*50}")
    print(f"Pipeline completed successfully for: {s3_key}")
    print(f"{'='*50}\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <s3_key>")
        sys.exit(1)

    run_pipeline(sys.argv[1])