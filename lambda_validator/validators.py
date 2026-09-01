"""
Validation logic for the Lambda function.

Checks that an incoming CSV has the right structure before it's
allowed to move to raw-validated/. This is a LIGHTWEIGHT structural
check only — deep value validation (ranges, duplicates) still
happens later in the main pipeline on EC2.
"""

import pandas as pd
import io

REQUIRED_COLUMNS = [
    "datetime", "sensor_id", "co2_ppm",
    "co2_enhancement", "temp_c", "humidity_pct", "pressure_hpa"
]


def is_valid_csv(csv_bytes: bytes) -> tuple[bool, str]:
    """
    Checks if the given bytes represent a well-formed CSV with the
    expected columns.

    Returns:
        (is_valid, reason) — reason is empty string if valid,
        otherwise a short explanation of why it failed.
    """
    try:
        df = pd.read_csv(io.BytesIO(csv_bytes))
    except Exception as e:
        return False, f"Could not parse as CSV: {e}"

    if df.empty:
        return False, "CSV has no rows"

    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        return False, f"Missing required columns: {missing}"

    return True, ""