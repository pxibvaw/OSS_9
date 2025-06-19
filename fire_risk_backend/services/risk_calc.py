# riskCalc.py

import pandas as pd

# min-max 정규화가 이상치에 민감할 수 있기 때문에 zscore형식으로 변환
def zscore(value, mean, std):
    if std == 0:
        return 0.0
    return (value - mean) / std

def compute_risk_score(data: dict, stats: dict) -> dict:

    # 개별 자치구 위험 점수 계산 함수
    # Parameters:
    # - data: 해당 자치구의 원본 지표 값들 (dict)
    # - stats: 전체 지표에 대한 평균/표준편차 (dict)

    # Returns:
    # - dict: danger_score, weak_score, prevent_score, total_score

    def w(d, key, weight):
        return zscore(d[key], stats[key]['mean'], stats[key]['std']) * weight

    # 1. 위해지표 (45%)
    danger = (
        w(data, 'fire_deaths',  0.446) +
        w(data, 'fire_cases',   0.0036)
    )

    # 2. 취약지표 (30%)
    weak = (
        w(data, 'vulnerable_people',   0.06 ) +
        w(data, 'pub_workers',         0.02 ) +
        w(data, 'warehouse_workers',   0.015) +
        w(data, 'old_buildings_ratio', 0.035) +
        w(data, 'flammable_cases',     0.17 )
    )

    # 3. 경감지표 (25%)
    prevent = (
        w(data, 'hospital_beds',   0.028) +
        w(data, 'financial_index', 0.022) +
        w(data, 'urban_area',      0.20 )
    )

    total = danger + weak + prevent

    return {
        'danger_score': round(danger * 100, 2),
        'weak_score': round(weak * 100, 2),
        'prevent_score': round(prevent * 100, 2),
        'total_score': round(total * 100, 2),
    }
