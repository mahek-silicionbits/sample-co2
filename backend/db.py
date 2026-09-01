"""
MongoDB connection for the FastAPI backend.

This is a READ-ONLY connection from the API's perspective — the
pipeline is the only thing that writes to MongoDB. FastAPI just
queries it.
"""

import certifi
from pymongo import MongoClient
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_uri: str
    mongo_db_name: str = "sensor_pipeline"

    class Config:
        env_file = ".env"


settings = Settings()

_client = None


def get_mongo_client() -> MongoClient:
    """
    Returns a shared MongoDB client, created once and reused across
    requests (avoids opening a new connection on every API call).
    """
    global _client
    if _client is None:
        _client = MongoClient(settings.mongo_uri, tlsCAFile=certifi.where())
    return _client


def get_db():
    """
    Returns the actual database object, ready to query collections from.
    """
    client = get_mongo_client()
    return client[settings.mongo_db_name]