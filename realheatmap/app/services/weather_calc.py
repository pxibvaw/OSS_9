from sqlalchemy.orm import Session
from realheatmap.app.database.models import WeatherCalculated
from datetime import date
from typing import Optional
import math

# 일자 가중치 딕셔너리
DAILY_WEIGHT_MAP = {
    1: 0.85,
    2: 0.85,
    3: {
        (1, 10): 0.9,
        (11, 20): 0.95,
        (21, 31): 1.0
    },
    4: {
        (1, 10): 1.0,
        (11, 20): 0.95,
        (21, 30): 0.9
    },
    5: 0.85,
    6: 0.8,
    7: 0.33,
    8: 0.33,
    9: 0.5,
    10: 0.61,
    11: 0.78,
    12: 0.83
}

def get_daily_weight(target_date: date) -> float:
    month = target_date.month
    day = target_date.day
    rule = DAILY_WEIGHT_MAP.get(month)
    if isinstance(rule, dict):
        for (start, end), weight in rule.items():
            if start <= day <= end:
                return weight
        return 1.0
    return rule or 1.0

def calculate_fire_risk_score(db: Session, region: str, target_date: date) -> Optional[float]:
    row = db.query(WeatherCalculated).filter_by(region=region, date=target_date).first()
    if not row:
        print(f"[오류] 기상 계산 데이터 없음: region={region}, date={target_date}")
        return None

    weather = {
        "Tmean": row.temperature,
        "Rh": row.humidity,
        "Eh": row.effective_humidity,
        "Wmean": row.wind
    }

    try:
        month = target_date.month
        if 1 <= month <= 6:
            # 봄철 모델 (1~6월)
            risk_score = 1 / (1 + math.exp((2.706
                                + 0.088 * weather["Tmean"]
                                - 0.055 * weather["Rh"]
                                - 0.023 * weather["Eh"]
                                - 0.014 * weather["Wmean"]) ** -1))
        else:
            # 가을/겨울 모델 (7~12월)
            risk_score = 1 / (1 + math.exp((1.099
                                + 0.117 * weather["Tmean"]
                                - 0.069 * weather["Rh"]
                                - 0.182 * weather["Wmean"]) ** -1))
    except OverflowError:
        print(f"[경고] 지수 계산 중 Overflow 발생. 기본 score=0 반환")
        risk_score = 0

    daily_weight = get_daily_weight(target_date)
    adjusted_score = risk_score * daily_weight

    print(f"[계산 완료] 위험지수: {adjusted_score}% (region={region}, date={target_date}, 가중치={daily_weight})")
    return adjusted_score