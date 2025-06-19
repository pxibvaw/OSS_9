from realheatmap.app.models import WeatherRaw
from realheatmap.app.database import Session
from realheatmap.app.services.weather_calc import WeatherCalculated
from datetime import timedelta

def calculate_effective_humidity(db: Session, district_id: int, target_date):
 
    # 실효습도(He)를 계산하여 weather_calculated 테이블에 저장
    # He = (1 - r) × [H0d + r*H1d + r^2*H2d + r^3*H3d + r^4*H4d]
    # - r: 가중치 감쇄 계수 (0.7)
    # - Hnd: n일 전의 상대습도

    r = 0.7
    humidity_sum = 0

    for i in range(5):
        day = target_date - timedelta(days=i)
        weather = db.query(WeatherRaw).filter_by(district_id=district_id, date=day).first()
        if not weather:
            print(f"[오류] {i}일 전({day}) 상대습도 정보 없음")
            return None
        humidity_sum += (r ** i) * weather.humidity

    He = (1 - r) * humidity_sum

    # DB 저장 (업데이트 또는 생성)
    existing = db.query(WeatherCalculated).filter_by(district_id=district_id, date=target_date).first()
    if existing:
        existing.real_feel_humidity = He
    else:
        new_row = WeatherCalculated(
            district_id=district_id,
            date=target_date,
            real_feel_humidity=He
        )
        db.add(new_row)

    db.commit()
    print(f"[성공] district_id={district_id}, date={target_date} → 실효습도 {He:.2f} 저장됨")
    return He
