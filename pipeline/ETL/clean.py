"""
Cleaning stage of the ETL pipeline.

Takes VALIDATED data (already passed validate.py) and standardizes it
for downstream transformation. This is about consistency, not
correctness checks — validate.py already handled correctness.
"""

import pandas as pd


def parse_datetime(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts the 'datetime' column from string to actual pandas
    datetime objects, so we can later group/aggregate by hour easily.
    """
    df = df.copy()
    df["datetime"] = pd.to_datetime(df["datetime"], utc=True)
    return df


def sort_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Sorts rows chronologically, grouped by sensor. Makes the data
    easier to inspect and ensures consistent ordering for aggregation.
    """
    df = df.copy()
    df = df.sort_values(by=["sensor_id", "datetime"]).reset_index(drop=True)
    return df


def round_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rounds sensor readings to a sane precision. Raw sensor data often
    has excessive decimal places (e.g. 95.97588) that don't add real
    value and just bloat storage.
    """
    df = df.copy()
    numeric_columns = ["co2_ppm", "co2_enhancement", "temp_c", "humidity_pct", "pressure_hpa"]
    df[numeric_columns] = df[numeric_columns].round(2)
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs the full cleaning sequence on validated data.
    """
    df = parse_datetime(df)
    df = sort_data(df)
    df = round_numeric_columns(df)

    print(f"[clean] Cleaned {len(df)} rows")
    return df