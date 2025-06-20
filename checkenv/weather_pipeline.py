# ✅ weather_pipeline.py
from sqlalchemy.orm import Session
from realheatmap.app.database import SessionLocal
from realheatmap.app.models import WeatherRaw, WeatherCalculated
from datetime import datetime

# 실효습도 계산 함수 (간단 버전)
def calculate_effective_humidity(region, records):
    r = 0.7
    humidity_sum = 0
    for i, record in enumerate(records):
        if record.humidity is None:
            return None
        humidity_sum += (r ** i) * record.humidity
    return (1 - r) * humidity_sum

# weather_raw → weather_calculated 자동 변환

def generate_weather_calculated():
    db: Session = SessionLocal()
    try:
        today = datetime.now().date()

        regions = db.query(WeatherRaw.region).distinct().all()
        for (region,) in regions:
            records = (
                db.query(WeatherRaw)
                .filter(WeatherRaw.region == region)
                .order_by(WeatherRaw.date.desc())
                .limit(5)
                .all()
            )
            if len(records) < 5:
                print(f"[SKIP] {region}: 5일치 데이터 부족")
                continue

            He = calculate_effective_humidity(region, records)
            if He is None:
                print(f"[오류] {region}: 유효한 습도 데이터 부족")
                continue

            latest = records[0]
            existing = (
                db.query(WeatherCalculated)
                .filter(WeatherCalculated.region == region, WeatherCalculated.date == today)
                .first()
            )

            if existing:
                existing.temperature = latest.temperature
                existing.humidity = latest.humidity
                existing.wind = latest.wind
                existing.effective_humidity = He
            else:
                new_row = WeatherCalculated(
                    region=region,
                    district_id=latest.district_id,
                    date=today,
                    temperature=latest.temperature,
                    humidity=latest.humidity,
                    wind=latest.wind,
                    effective_humidity=He
                )
                db.add(new_row)

            db.commit()
            print(f"[✅] {region} 실효습도 계산 및 저장 완료: {He:.2f}")

    finally:
        db.close()