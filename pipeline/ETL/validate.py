"""
Validation stage of the ETL pipeline.

Checks the raw DataFrame for structural and value-level problems.
Does NOT fix anything — that's clean.py's job. This stage only
detects and reports issues, splitting data into valid/invalid rows.
"""

import pandas as pd

# Expected columns in every incoming CSV
REQUIRED_COLUMNS = [
    "datetime", "sensor_id", "co2_ppm",
    "co2_enhancement", "temp_c", "humidity_pct", "pressure_hpa"
]

# Sane real-world ranges for each sensor reading
VALID_RANGES = {
    "co2_ppm": (300, 5000),
    "temp_c": (-20, 50),
    "humidity_pct": (0, 100),
    "pressure_hpa": (950, 1050),
}


def check_schema(df: pd.DataFrame) -> None:
    """
    Confirm all required columns exist. Raises an error immediately
    if the file structure itself is wrong — no point checking values
    on a malformed file.
    """
    missing = set(REQUIRED_COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    print("[validate] Schema check passed")


def flag_out_of_range(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a boolean '_valid' column marking whether each row falls
    within sane sensor value ranges.
    """
    df = df.copy()
    df["_valid"] = True

    for column, (low, high) in VALID_RANGES.items():
        out_of_range = ~df[column].between(low, high)
        df.loc[out_of_range, "_valid"] = False

    return df


def flag_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Marks rows invalid if any required field is null/NaN.
    """
    df = df.copy()
    has_nulls = df[REQUIRED_COLUMNS].isnull().any(axis=1)
    df.loc[has_nulls, "_valid"] = False
    return df


def flag_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Marks rows invalid if (datetime, sensor_id) pair appears more than once —
    keeps the FIRST occurrence as valid, flags the rest as duplicates.
    """
    df = df.copy()
    is_duplicate = df.duplicated(subset=["datetime", "sensor_id"], keep="first")
    df.loc[is_duplicate, "_valid"] = False
    return df


def validate(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Runs the full validation suite and splits the data into
    valid and invalid rows.

    Returns:
        (valid_df, invalid_df)
    """
    check_schema(df)

    df = flag_out_of_range(df)
    df = flag_missing_values(df)
    df = flag_duplicates(df)

    valid_df = df[df["_valid"]].drop(columns=["_valid"])
    invalid_df = df[~df["_valid"]]

    print(f"[validate] {len(valid_df)} valid rows, {len(invalid_df)} invalid rows")
    return valid_df, invalid_df