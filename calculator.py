# calculator.py

def normalize(value, min_val, max_val):
    """0~1 정규화"""
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

def compute_risk_score(data, stats):
    """
    data: dict - 해당 자치구의 원본 지표값
    stats: dict - 전체 자치구의 지표들에 대한 min/max 정보
    """
    # 정규화 후 가중치 곱
    def w(v, key, weight):
        return normalize(data[key], stats[key]['min'], stats[key]['max']) * weight

    # 위해지표
    danger = (
        w(data, 'fire_deaths',     0.446) +
        w(data, 'fire_cases',      0.0036 )
    )

    # 취약지표
    weak = (
        w(data, 'vulnerable_people',    0.06 ) +
        w(data, 'pub_workers',          0.02 ) +
        w(data, 'warehouse_workers',    0.015  ) +
        w(data, 'old_buildings_ratio',  0.035 ) +
        w(data, 'flammable_cases',      0.17 )
    )

    # 경감지표
    prevent = (
        w(data, 'hospital_beds',    0.028 ) +
        w(data, 'financial_index',  0.022 ) +
        w(data, 'urban_area',       0.20)
    )

    total = danger + weak + prevent

    return {
        'danger_score': round(danger * 100, 2),
        'weak_score': round(weak * 100, 2),
        'prevent_score': round(prevent * 100, 2),
        'total_score': round(total * 100, 2),
    }
