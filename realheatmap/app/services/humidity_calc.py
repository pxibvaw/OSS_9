from sqlalchemy.orm import Session
from datetime import timedelta, date, datetime
from typing import Optional
from realheatmap.app.database.models import WeatherRaw, WeatherCalculated

def calculate_effective_humidity(db: Session, region: str, target_date: date) -> Optional[float]:
    print(f"✅ 실효습도 계산 시작: {region}, 날짜: {target_date}")

    r = 0.7
    humidity_sum = 0
    latest_weather = None

    for i in range(5):
        day = target_date - timedelta(days=i)
        start_dt = datetime.combine(day, datetime.min.time())  # 00:00:00
        end_dt = datetime.combine(day, datetime.max.time())    # 23:59:59.999999

        weather = (
            db.query(WeatherRaw)
            .filter(
                WeatherRaw.region == region,
                WeatherRaw.timestamp.between(start_dt, end_dt)
            )
            .order_by(WeatherRaw.timestamp.desc())
            .first()
        )

        if not weather:
            print(f"  ⚠️  {day} 습도 데이터 없음")
            return None

        humidity_sum += (r ** i) * weather.humidity
        if i == 0:
            latest_weather = weather

    He = (1 - r) * humidity_sum
    print(f"🔍 저장 직전 He 값: {He}") 

    existing = db.query(WeatherCalculated).filter(
        WeatherCalculated.region == region,
        WeatherCalculated.date == target_date
    ).first()

    if existing:
        existing.effective_humidity = He
        print(f"  🔁 기존 데이터 업데이트됨: He={He:.2f}")
    else:
        new_row = WeatherCalculated(
            region=region,
            district_id=None,
            date=target_date,
            temperature=latest_weather.temperature,
            humidity=latest_weather.humidity,
            wind=latest_weather.wind,
            effective_humidity=round(He, 2),
            timestamp=latest_weather.timestamp
        )
        
        db.add(new_row)
        print(f"  ✅ 새 데이터 추가됨: He={He:.2f}")

    db.commit()
    return He