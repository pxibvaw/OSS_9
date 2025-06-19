print("✅ main.py에서 import 시작")

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from realheatmap.app.database import SessionLocal
from realheatmap.app.models import WeatherRaw
from realheatmap.app.api.weather_api import get_weather_and_save

print("✅ import 성공")

app = FastAPI()

# ✅ 자치구별 최신 날씨 정보 조회 API
@app.get("/weather-info")
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
                content={"message": f"'{region}'에 대한 기상 데이터가 존재하지 않습니다."}
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

# ✅ 서울시 25개 자치구 날씨 정보 저장 API
@app.get("/save-weather")
def save_all_weather():
    success = []
    failed = []

    for gu in [
        '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
        '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
        '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
    ]:
        result = get_weather_and_save(gu)
        if "error" in result:
            failed.append({"region": gu, "error": result["error"]})
        else:
            success.append({"region": gu, "data": result})

    return {
        "message": f"총 {len(success)}개 자치구의 기상 정보 저장 완료",
        "success": success,
        "failed": failed
    }