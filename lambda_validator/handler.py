"""
Lambda entry point.

Triggered automatically by S3 whenever a new object is created in
the raw/ prefix. Validates the file's structure and moves it to
either raw-validated/ or raw-rejected/.
"""

import boto3
import urllib.parse
from validators import is_valid_csv

s3 = boto3.client("s3")


def lambda_handler(event, context):
    """
    AWS Lambda invokes this function automatically on the S3 trigger.
    `event` contains details about which file was uploaded.
    """
    # S3 events can contain multiple records, though usually just one
    for record in event["Records"]:
        bucket = record["s3"]["bucket"]["name"]
        # S3 keys in events are URL-encoded (e.g. spaces become '+')
        key = urllib.parse.unquote_plus(record["s3"]["object"]["key"])

        print(f"[lambda] New file detected: s3://{bucket}/{key}")

        process_file(bucket, key)

    return {"statusCode": 200, "body": "Processed"}


def process_file(bucket: str, key: str) -> None:
    """
    Downloads the file, validates it, and moves it to the
    appropriate destination folder based on the result.
    """
    filename = key.split("/")[-1]

    response = s3.get_object(Bucket=bucket, Key=key)
    csv_bytes = response["Body"].read()

    valid, reason = is_valid_csv(csv_bytes)

    if valid:
        destination_key = f"raw-validated/{filename}"
        print(f"[lambda] VALID — moving to {destination_key}")
    else:
        destination_key = f"raw-rejected/{filename}"
        print(f"[lambda] INVALID ({reason}) — moving to {destination_key}")

    # Copy to destination, then delete original (this is how you "move" in S3 —
    # there's no native move operation, only copy + delete)
    s3.copy_object(
        Bucket=bucket,
        CopySource={"Bucket": bucket, "Key": key},
        Key=destination_key,
    )
    s3.delete_object(Bucket=bucket, Key=key)