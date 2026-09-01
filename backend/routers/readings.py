"""
Routes for fetching hourly readings for a specific sensor.
"""

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime, timedelta, timezone
from db import get_db
from models import ReadingsResponse, HourlyReading

router = APIRouter()


@router.get("/readings/{sensor_id}", response_model=ReadingsResponse)
def get_readings(
    sensor_id: str,
    hours: int = Query(default=24, ge=1, le=720, description="How many hours of history to return")
):
    """
    Returns hourly aggregated readings for one sensor, going back
    the requested number of hours (default 24, max 720 = 30 days).
    """
    db = get_db()
    collection = db["hourly_aggregates"]

    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)

    cursor = collection.find(
        {"sensor_id": sensor_id, "hour": {"$gte": cutoff}}
    ).sort("hour", 1)

    readings = [HourlyReading(**doc) for doc in cursor]

    if not readings:
        raise HTTPException(status_code=404, detail=f"No data found for sensor '{sensor_id}'")

    return ReadingsResponse(sensor_id=sensor_id, readings=readings)