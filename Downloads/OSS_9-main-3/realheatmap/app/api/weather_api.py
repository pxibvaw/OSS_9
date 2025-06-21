# api/weather_api.py

from fastapi import APIRouter, Query
from realheatmap.app.services.weather_fetcher import get_weather_and_save
from sqlalchemy.orm import Session
from realheatmap.app.database.database import SessionLocal
from realheatmap.app.database.models import WeatherRaw
from fastapi.responses import JSONResponse
from datetime import datetime

router = APIRouter()

@router.get("/weather/{region}")
def fetch_weather(region: str):
    return get_weather_and_save(region)

@router.get("/weather-info")
def get_latest_weather(region: str = Query(..., description="자치구 이름")):
    db: Session = SessionLocal()
    try:
        weather = (
            db.query(WeatherRaw)
            .filter(WeatherRaw.region == region)
            .order_by(WeatherRaw.timestamp.desc())
            .first()
        )
        if not weather:
            return JSONResponse(
                status_code=404,
                content={"message": f"{region}에 대한 기상 데이터가 존재하지 않습니다."}
            )
        return {
            "region": weather.region,
            "temperature": weather.temperature,
            "humidity": weather.humidity,
            "wind": weather.wind,
            "timestamp": weather.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
    finally:
        db.close()
