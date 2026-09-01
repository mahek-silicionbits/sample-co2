"""
Simulates new sensor data arriving, mimicking real IoT devices.

Generates a realistic-looking CSV (same shape as real sensor exports)
and uploads it directly to S3 raw/, standing in for actual hardware
sending data.
"""

import io
import boto3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, timezone
from config import settings

SENSOR_IDS = ["T01", "T04"]
READINGS_PER_SENSOR = 10          # how many rows to generate per sensor
INTERVAL_MINUTES = 30              # roughly how far apart readings are


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_region,
    )


def generate_sensor_readings(sensor_id: str, start_time: datetime) -> pd.DataFrame:
    """
    Generates a realistic sequence of readings for one sensor,
    with small random jitter in both timing and values.
    """
    rows = []
    current_time = start_time

    # Base values that drift slightly over time, like real conditions
    base_co2 = np.random.uniform(480, 540)
    base_temp = np.random.uniform(16, 18)
    base_humidity = np.random.uniform(88, 96)
    base_pressure = np.random.uniform(1008, 1011)

    for _ in range(READINGS_PER_SENSOR):
        jitter_minutes = np.random.randint(-2, 3)  # +/- a couple minutes, like real sensors
        timestamp = current_time + timedelta(minutes=jitter_minutes)

        rows.append({
            "datetime": timestamp.isoformat(),
            "sensor_id": sensor_id,
            "co2_ppm": round(base_co2 + np.random.normal(0, 8), 2),
            "co2_enhancement": 0.0,
            "temp_c": round(base_temp + np.random.normal(0, 0.5), 5),
            "humidity_pct": round(base_humidity + np.random.normal(0, 2), 5),
            "pressure_hpa": round(base_pressure + np.random.normal(0, 0.3), 3),
        })

        current_time += timedelta(minutes=INTERVAL_MINUTES)

    return pd.DataFrame(rows)


def generate_batch() -> pd.DataFrame:
    """
    Generates readings for all sensors, combined into one DataFrame.
    """
    start_time = datetime.now(timezone.utc) - timedelta(hours=5)

    all_dfs = [generate_sensor_readings(sensor_id, start_time) for sensor_id in SENSOR_IDS]
    combined = pd.concat(all_dfs, ignore_index=True)
    combined = combined.sort_values(by="datetime").reset_index(drop=True)

    return combined


def upload_to_s3(df: pd.DataFrame) -> str:
    """
    Uploads the generated DataFrame as a CSV to S3 raw/, with a
    unique timestamped filename so each run produces a genuinely new file.
    """
    filename = f"{datetime.now(timezone.utc).strftime('%Y-%m-%d_%H%M%S')}.csv"
    key = f"{settings.raw_prefix}{filename}"

    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)

    s3 = get_s3_client()
    s3.put_object(
        Bucket=settings.s3_bucket_name,
        Key=key,
        Body=csv_buffer.getvalue(),
        ContentType="text/csv",
    )

    print(f"[simulator] Uploaded {len(df)} rows to s3://{settings.s3_bucket_name}/{key}")
    return key


if __name__ == "__main__":
    df = generate_batch()
    upload_to_s3(df)