# weather_calc.py
from sqlalchemy.orm import Session
from realheatmap.app.database.models import WeatherCalculated
from datetime import date
from typing import Optional, Dict
import math
import logging

logging.basicConfig(level=logging.INFO)

# 1. 날짜별 가중치 테이블
DAILY_WEIGHT_MAP = {
    1: 0.85, 2: 0.85,
    3: {(1, 10): 0.90, (11, 20): 0.95, (21, 31): 1.00},
    4: {(1, 10): 1.00, (11, 20): 0.95, (21, 30): 0.90},
    5: 0.85, 6: 0.80,
    7: 0.33, 8: 0.33,
    9: 0.50, 10: 0.61, 11: 0.78, 12: 0.83
}

def get_daily_weight(target_date: date) -> float:
    # 월·일 기준 가중치 반환
    rule = DAILY_WEIGHT_MAP.get(target_date.month)
    if isinstance(rule, dict):
        for (start, end), w in rule.items():
            if start <= target_date.day <= end:
                return w
        return 1.0
    return rule or 1.0

# 2. 계절별(봄/가을) DWI 구간
SPRING_THRESHOLDS = [
    (0.0000, 0.1183), (0.1184, 0.1878), (0.1879, 0.2571),
    (0.2572, 0.3320), (0.3321, 0.4089), (0.4090, 0.4932),
    (0.4933, 0.5861), (0.5862, 0.6862), (0.6863, 0.7820),
    (0.7820, 1.0000)
]

FALL_THRESHOLDS = [
    (0.0000, 0.0265), (0.0266, 0.0409), (0.0410, 0.0575),
    (0.0576, 0.0750), (0.0751, 0.0968), (0.0969, 0.1258),
    (0.1259, 0.1601), (0.1602, 0.2072), (0.2073, 0.2659),
    (0.2860, 1.0000)
]

# 점수 -> 등급 매핑
def get_dwi_score(score: float, season: str) -> int:
    thresholds = SPRING_THRESHOLDS if season == "spring" else FALL_THRESHOLDS
    for idx, (low, high) in enumerate(thresholds, start=1):
        if low <= score <= high:
            return idx
    return 10  # fallback 안전장치

# 3. 메인 계산 함수
def calculate_fire_risk_score(
    db: Session,
    region: str,
    target_date: date
) -> Optional[Dict[str, float | int]]:

    # db에서 데이터 읽어와서 계산
    row: WeatherCalculated | None = (
        db.query(WeatherCalculated)
          .filter_by(region=region, date=target_date)
          .first()
    )
    if row is None:
        logging.error("기상 계산 데이터 없음 | region=%s date=%s", region, target_date)
        return None

    # 1) 날짜 가중치
    daily_weight = get_daily_weight(target_date)

    # 2) 기초 위험 점수(로지스틱): 봄(1~6월) vs 가을(7~12월)
    month = target_date.month
    Wmean = max(row.wind, 0.1)  # 풍속 0 보정
    try:
        if 1 <= month <= 6:      # 봄 모델
            z = (
                2.706
                + 0.088 * row.temperature
                - 0.055 * row.humidity
                - 0.023 * row.effective_humidity
                - 0.014 * Wmean
            )
        else:                    # 가을 모델
            z = (
                1.099
                + 0.117 * row.temperature
                - 0.069 * row.humidity
                - 0.182 * Wmean
            )
        risk_score = 1 / (1 + math.exp(-z)) # 공통으로 들어가는 부분 빼둠

    except OverflowError:
        logging.warning("OverflowError 발생 → score=0 | region=%s date=%s", region, target_date)
        risk_score = 0.0

    # 3) 가중치 및 등급 적용
    adjusted_score = risk_score * daily_weight
    season = "spring" if 1 <= month <= 6 else "fall"
    dwi_score = get_dwi_score(adjusted_score, season)

    # 4) DB 반영
    row.daily_weight = daily_weight
    row.dwi_score = dwi_score
    db.commit()

    logging.info(
        "DWI 계산 완료 | region=%s date=%s season=%s weight=%.2f adjusted=%.4f grade=%d",
        region, target_date, season, daily_weight, adjusted_score, dwi_score
    ) # 지역, 날짜, 게절, 가중치, 조정된 점수, 등급

    # 5) 프론트에 전달할 값
    return {
        "dwi_score": dwi_score,         # 1~10 등급
        "daily_weight": round(daily_weight, 2),
        "adjusted_score": round(adjusted_score, 4)
    }