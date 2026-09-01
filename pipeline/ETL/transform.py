"""
Transformation stage of the ETL pipeline.

Takes CLEANED data and aggregates it into hourly summaries per sensor.
This is the step that makes frontend graphs fast later — instead of
sending every raw reading, we send pre-computed hourly stats.
"""

import pandas as pd


def aggregate_hourly(df: pd.DataFrame) -> pd.DataFrame:
    """
    Groups readings by sensor and by hour, computing avg/min/max
    for each numeric sensor field.

    Returns a DataFrame with one row per (sensor_id, hour) combination.
    """
    df = df.copy()

    # Truncate each timestamp down to the start of its hour
    # e.g. 2026-08-31 02:30:02 -> 2026-08-31 02:00:00
    df["hour"] = df["datetime"].dt.floor("h")

    metrics = ["co2_ppm", "co2_enhancement", "temp_c", "humidity_pct", "pressure_hpa"]

    grouped = df.groupby(["sensor_id", "hour"])[metrics].agg(["mean", "min", "max"])

    # Flatten the multi-level column names (e.g. ('co2_ppm', 'mean') -> 'co2_ppm_mean')
    grouped.columns = ["_".join(col) for col in grouped.columns]
    grouped = grouped.reset_index()

    # Round the aggregated values too
    numeric_cols = [c for c in grouped.columns if c not in ("sensor_id", "hour")]
    grouped[numeric_cols] = grouped[numeric_cols].round(2)

    print(f"[transform] Aggregated into {len(grouped)} hourly rows")
    return grouped


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """
    Runs the full transformation sequence.
    """
    hourly_df = aggregate_hourly(df)
    return hourly_df