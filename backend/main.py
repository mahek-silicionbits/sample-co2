"""
FastAPI application entry point.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import sensors, readings

app = FastAPI(title="Sensor Pipeline API")

# Allow the React frontend (running on a different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # fine for learning; restrict this in a real deployment
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sensors.router)
app.include_router(readings.router)


@app.get("/")
def root():
    return {"status": "ok", "message": "Sensor Pipeline API is running"}