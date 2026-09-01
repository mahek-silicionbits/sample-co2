"""
Shared S3 helper functions, used by both extract.py and load.py.
"""

import boto3
from config import settings

_s3_client = None


def get_s3_client():
    """
    Returns a shared boto3 S3 client, created once and reused.
    """
    global _s3_client
    if _s3_client is None:
        _s3_client = boto3.client(
            "s3",
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region,
        )
    return _s3_client