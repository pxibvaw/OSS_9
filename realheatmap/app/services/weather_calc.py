from sqlalchemy.orm import Session
from realheatmap.app.database.models import WeatherCalculated
from datetime import date
from math import exp

def calculate_fire_risk_score(db: Session, region: str, target_date: date):
    """
    주어진 자치구(region)와 날짜(target_date)에 대해
    실효습도 및 기상 데이터를 기반으로 산불 위험지수를 계산합니다.
    
    - 봄철/여름 (3~8월): [1 + exp(-(2.706 + 0.088T - 0.055Rh - 0.023Eh - 0.014W))]^-1 - 1
    - 가을/겨울 (9~2월): [1 + exp(-(1.099 + 0.117T - 0.069Rh - 0.182W))]^-1 - 1

    반환: 0~100 사이의 백분율 위험지수 (소수점 2자리) 또는 None
    """

    # 날짜 필터는 timestamp가 아닌 date 컬럼 사용
    row = (
        db.query(WeatherCalculated)
        .filter(
            WeatherCalculated.region == region,
            WeatherCalculated.date == target_date
        )
        .first()
    )

    if not row:
        print(f"[오류] 기상 계산 데이터 없음: region={region}, date={target_date}")
        return None

    Tmean = row.temperature
    Rh = row.humidity
    Eh = row.effective_humidity
    Wmean = row.wind

    month = target_date.month
    score = None

    if month in [3, 4, 5, 6, 7, 8]:  # 봄~여름: 봄 모델
        score = (1 / (1 + exp(-(2.706 + 0.088 * Tmean - 0.055 * Rh - 0.023 * Eh - 0.014 * Wmean)))) - 1
    elif month in [9, 10, 11, 12, 1, 2]:  # 가을~겨울: 가을 모델
        score = (1 / (1 + exp(-(1.099 + 0.117 * Tmean - 0.069 * Rh - 0.182 * Wmean)))) - 1

    if score is None:
        return None

    score_percentage = round(score * 100, 2)
    print(f"[계산 완료] 위험지수: {score_percentage}% (region={region}, date={target_date})")
    return score_percentage