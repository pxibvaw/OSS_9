#insert_dummy_weather_all.py
from datetime import datetime
from sqlalchemy.orm import Session

from realheatmap.app.database import SessionLocal
from realheatmap.app.database.models import WeatherRaw

# 자치구별 임의 습도값 (5일치)
dummy_humidity_data = {
    "강남구": [65, 60, 62, 61, 59],
    "강동구": [66, 63, 61, 60, 58],
    "강북구": [60, 55, 58, 62, 57],
    "강서구": [64, 61, 63, 60, 56],
    "관악구": [67, 66, 64, 62, 61],
    "광진구": [62, 60, 59, 58, 57],
    "구로구": [59, 58, 56, 55, 54],
    "금천구": [63, 62, 61, 60, 59],
    "노원구": [68, 66, 65, 63, 62],
    "도봉구": [65, 63, 61, 60, 59],
    "동대문구": [66, 64, 62, 60, 58],
    "동작구": [61, 60, 59, 58, 57],
    "마포구": [64, 62, 61, 60, 59],
    "서대문구": [63, 61, 60, 58, 57],
    "서초구": [65, 64, 63, 61, 60],
    "성동구": [60, 59, 58, 57, 56],
    "성북구": [67, 66, 65, 63, 62],
    "송파구": [62, 60, 59, 58, 57],
    "양천구": [61, 60, 59, 58, 57],
    "영등포구": [65, 64, 63, 62, 61],
    "용산구": [66, 65, 64, 62, 60],
    "은평구": [64, 63, 62, 60, 59],
    "종로구": [63, 62, 60, 59, 58],
    "중구": [62, 61, 60, 59, 58],
    "중랑구": [61, 60, 59, 58, 57],
}

dates = ["2025-06-20", "2025-06-16", "2025-06-17", "2025-06-18", "2025-06-19"]

db: Session = SessionLocal()
try:
    for region, humidity_list in dummy_humidity_data.items():
        for i, date_str in enumerate(dates):
            timestamp = datetime.strptime(date_str, "%Y-%m-%d")

            exists = db.query(WeatherRaw).filter(
                WeatherRaw.region == region,
                WeatherRaw.timestamp == timestamp
            ).first()

            if not exists:
                new_row = WeatherRaw(
                    region=region,
                    temperature=23.0,
                    humidity=humidity_list[i],
                    wind=1.5,
                    timestamp=timestamp
                )
                db.add(new_row)
                print(f"✅ {region} - {date_str}: 습도 {humidity_list[i]} 삽입됨")
            else:
                print(f"⚠️ {region} - {date_str}: 이미 존재함")

    db.commit()
    print("🎉 모든 자치구 데이터 삽입 완료")
finally:
    db.close()