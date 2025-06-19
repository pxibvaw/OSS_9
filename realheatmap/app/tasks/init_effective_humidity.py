from sqlalchemy.orm import Session
from realheatmap.app.database.models import WeatherRaw, WeatherCalculated
from datetime import timedelta, date
from sqlalchemy import func
from typing import Optional

def calculate_effective_humidity(db: Session, region: str, target_date: date) -> Optional[float]:
    print(f"✅ 실효습도 계산 시작: {region}, 날짜: {target_date}")
    
    r = 0.7
    humidity_sum = 0

    for i in range(5):
        day = target_date - timedelta(days=i)
        weather = (
            db.query(WeatherRaw)
            .filter(
                WeatherRaw.region == region,
                func.date(WeatherRaw.timestamp) == day
            )
            .first()
        )
        if not weather:
            print(f"  ⚠️  {day} 습도 데이터 없음")
            return None
        humidity_sum += (r ** i) * weather.humidity

    He = (1 - r) * humidity_sum

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
            district_id=None,  # 필요시 추후 할당
            date=target_date,
            temperature=weather.temperature,
            humidity=weather.humidity,
            wind=weather.wind,
            effective_humidity=He,
            timestamp=weather.timestamp
        )
        db.add(new_row)
        print(f"  ✅ 새 데이터 추가됨: He={He:.2f}")

    db.commit()
    return He