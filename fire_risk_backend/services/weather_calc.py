from sqlalchemy.orm import Session
from models.weather_calculated import WeatherCalculated
from datetime import date

def calculate_fire_risk_score(db: Session, district_id: int, target_date: date):

    # 산불 위험지수 계산
    # - 봄철(3~6월): [1 + exp{-(2.706 + 0.088T - 0.055Rh - 0.023Eh - 0.014W)}]^-1 - 1
    # - 가을·겨울(9~2월): [1 + exp{-(1.099 + 0.117T - 0.069Rh - 0.182W)}]^-1 - 1
    # - 여름(7~8): 봄철 모델 사용
    # - 겨울(1~2): 가을 모델 사용

    row = db.query(WeatherCalculated).filter_by(district_id=district_id, date=target_date).first()
    if not row:
        print(f"[오류] 기상 계산 데이터 없음: district_id={district_id}, date={target_date}")
        return None

    Tmean = row.temperature
    Rh = row.humidity
    Eh = row.real_feel_humidity
    Wmean = row.wind_speed

    month = target_date.month
    score = None

    # 봄/여름 → 봄철 모델
    if month in [3, 4, 5, 6, 7, 8]:
        score = (1 / (1 + (2.71828 ** -(2.706 + 0.088 * Tmean - 0.055 * Rh - 0.023 * Eh - 0.014 * Wmean)))) - 1
    # 가을/겨울 → 가을철 모델
    elif month in [9, 10, 11, 12, 1, 2]:
        score = (1 / (1 + (2.71828 ** -(1.099 + 0.117 * Tmean - 0.069 * Rh - 0.182 * Wmean)))) - 1

    if score is None:
        return None

    score_percentage = round(score * 100, 2)
    print(f"[계산 완료] 위험지수: {score_percentage}% (district_id={district_id}, date={target_date})")
    return score_percentage
