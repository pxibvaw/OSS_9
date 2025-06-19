print("✅ main.py에서 import 시작")

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import asyncio
import os
from datetime import datetime

from realheatmap.app.database.database import SessionLocal
from realheatmap.app.database.database import engine
from realheatmap.app.database import database
from realheatmap.app.database import models
from realheatmap.app.database.models import WeatherRaw, WeatherCalculated, FireRiskScore
from realheatmap.app.api.weather_api import get_weather_and_save
from realheatmap.app.services.humidity_calc import calculate_effective_humidity
from realheatmap.app.services.weather_calc import calculate_fire_risk_score
from realheatmap.app.services.risk_calc import get_risk_scores_by_region  # ✅ 추가

print("✅ import 성공")

print(f"📦 사용 중인 DB 파일 위치: {os.path.abspath(database.DATABASE_URL.replace('sqlite:///', ''))}")

app = FastAPI()

# ✅ 최신 날씨 정보 조회 API
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


# ✅ 자동 저장: 1시간마다 날씨 저장
@app.on_event("startup")
async def start_weather_loop():
    async def weather_task():
        while True:
            print("⏱️ 1시간 주기 기상 정보 저장 시작...")
            for gu in [
                '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구',
                '노원구', '도봉구', '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구',
                '성북구', '송파구', '양천구', '영등포구', '용산구', '은평구', '종로구', '중구', '중랑구'
            ]:
                get_weather_and_save(gu)
            print("✅ 모든 자치구 날씨 저장 완료. 다음 저장까지 1시간 대기.\n")
            await asyncio.sleep(3600)

    asyncio.create_task(weather_task())


# ✅ 실효습도 계산 요청 API
@app.get("/calculate-humidity")
def calc_humidity(
    region: str = Query(..., description="자치구 이름"),
    date: str = Query(None, description="YYYY-MM-DD 형식 날짜 (선택)")
):
    db: Session = SessionLocal()
    try:
        target_date = datetime.now().date() if date is None else datetime.strptime(date, "%Y-%m-%d").date()

        existing = db.query(WeatherCalculated).filter(
            WeatherCalculated.region == region,
            WeatherCalculated.date == target_date
        ).first()

        if existing:
            return {
                "region": region,
                "date": str(target_date),
                "effective_humidity": existing.effective_humidity,
                "source": "DB"
            }

        result = calculate_effective_humidity(db, region, target_date)
        if result is None:
            return {"message": "실효습도 계산 실패 (5일치 데이터 부족)"}

        return {
            "region": region,
            "date": str(target_date),
            "effective_humidity": result,
            "source": "calculated"
        }
    finally:
        db.close()


# ✅ 오늘 날짜 기준 위험도 계산 API
@app.get("/calculate-risk")
def calc_fire_risk(region: str = Query(..., description="자치구 이름")):
    db: Session = SessionLocal()
    try:
        today = datetime.now().date()
        score = calculate_fire_risk_score(db, region, today)
        if score is None:
            return {"message": "위험지수 계산 실패 (데이터 없음)"}

        risk = FireRiskScore(
            region=region,
            score_type="tmp_score",
            score_value=score,
            timestamp=datetime.now()
        )
        db.add(risk)
        db.commit()

        return {
            "region": region,
            "date": str(today),
            "risk_score": score
        }
    finally:
        db.close()


# ✅ 자치구와 날짜 기반 위험도 계산 API
@app.get("/fire-risk")
def get_fire_risk_score(
    region: str = Query(..., description="자치구 이름"),
    date: str = Query(..., description="YYYY-MM-DD 형식의 날짜")
):
    db: Session = SessionLocal()
    try:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return JSONResponse(
                status_code=400,
                content={"message": "날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식이어야 합니다."}
            )

        score = calculate_fire_risk_score(db, region, target_date)
        if score is None:
            return JSONResponse(
                status_code=404,
                content={"message": f"{region}의 {date}에 대한 계산된 기상 데이터가 존재하지 않습니다."}
            )

        return {
            "region": region,
            "date": date,
            "fire_risk_score": score
        }
    finally:
        db.close()


# ✅ 기초 지표 기반 위험 점수 API
@app.get("/base-risk")
def base_risk(region: str = Query(..., description="자치구 이름")):
    db: Session = SessionLocal()
    try:
        scores = get_risk_scores_by_region(db, region)
        if not scores:
            return JSONResponse(
                status_code=404,
                content={"message": f"{region}에 대한 기초 위험 지표 데이터가 부족합니다."}
            )
        return {
            "region": region,
            "danger_score": scores['danger_score'],
            "weak_score": scores['weak_score'],
            "prevent_score": scores['prevent_score'],
            "total_score": scores['total_score']
        }
    finally:
        db.close()


# ✅ DB 테이블 생성
models.Base.metadata.create_all(bind=engine)