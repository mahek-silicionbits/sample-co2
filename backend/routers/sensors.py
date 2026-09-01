"""
Routes for listing available sensors.
"""

from fastapi import APIRouter
from db import get_db
from models import SensorListResponse

router = APIRouter()


@router.get("/sensors", response_model=SensorListResponse)
def list_sensors():
    """
    Returns the list of distinct sensor IDs that have data available.
    """
    db = get_db()
    collection = db["hourly_aggregates"]

    sensor_ids = collection.distinct("sensor_id")

    return SensorListResponse(sensors=sorted(sensor_ids))