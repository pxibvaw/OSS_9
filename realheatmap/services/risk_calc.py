import pandas as pd

# Min-Max 정규화
def minmax(value, min_val, max_val):
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

def compute_risk_score(data: dict, stats: dict) -> dict:

    # 개별 자치구 위험 점수 계산 함수
    # Parameters:
    # - data: 해당 자치구의 원본 지표 값들 (dict)
    # - stats: 전체 지표에 대한 min/max 값들 (dict)
    # Returns:
    # - dict: danger_score, weak_score, prevent_score, total_score

    def w(d, key, weight):
        return minmax(d[key], stats[key]['min'], stats[key]['max']) * weight

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
        'danger_score': round(danger * 1000, 2),
        'weak_score': round(weak * 1000, 2),
        'prevent_score': round(prevent * 1000, 2),
        'total_score': round(total * 1000, 2),
    }
