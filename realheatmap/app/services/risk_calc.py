import pandas as pd
from sqlalchemy.orm import Session
from realheatmap.app.database.models import BaseIndicator

# 한글 지표명을 영어 키로 변환하는 매핑
INDICATOR_KEY_MAPPING = {
    '사망자수': 'fire_deaths',
    '만명당화재발생건수': 'fire_cases',
    '재난약자수': 'vulnerable_people',
    '식품위생업등종사자수': 'pub_workers',
    '창고및운송관련서비스업체수': 'warehouse_workers',
    '인구 1만 명 당 노후 건축물 수': 'old_buildings_ratio',
    '병상수': 'hospital_beds',
    '재정자주도': 'financial_index',
    '도시지역면적': 'urban_area'
}

# Min-Max 정규화 함수
def minmax(value, min_val, max_val):
    if max_val == min_val:
        return 0.0
    return (value - min_val) / (max_val - min_val)

# 위험도 점수 계산 함수
def compute_risk_score(data: dict, stats: dict) -> dict:
    def w(d, key, weight):
        if key not in d or key not in stats:
            print(f"[⚠️ 누락된 지표] '{key}'가 data 또는 stats에 없습니다.")
            return 0.0
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

    result = {
        'danger_score': round(danger * 1000, 2),
        'weak_score': round(weak * 1000, 2),
        'prevent_score': round(prevent * 1000, 2),
        'total_score': round(total * 1000, 2),
    }

    print(f"🎯 [RESULT] 위험도 계산 결과: {result}")

    return result

# DB에서 전체 지표 min/max 계산
def get_indicator_stats(db: Session) -> dict:
    rows = db.query(BaseIndicator).all()
    df = pd.DataFrame([{
        "region": row.region,
        "name": INDICATOR_KEY_MAPPING.get(row.indicator_name.strip(), row.indicator_name.strip()),
        "value": row.indicator_value
    } for row in rows])

    pivot = df.pivot(index="region", columns="name", values="value")
    stats = {}
    for col in pivot.columns:
        stats[col] = {
            "min": pivot[col].min(),
            "max": pivot[col].max()
        }

    return stats

# 자치구별 지표값 반환 (영문 키 기준)
def get_region_data(db: Session, region: str) -> dict:
    rows = db.query(BaseIndicator).filter(BaseIndicator.region == region).all()
    return {
        INDICATOR_KEY_MAPPING.get(row.indicator_name.strip(), row.indicator_name.strip()): row.indicator_value
        for row in rows
    }

# API에서 사용하는 최종 함수
def get_risk_scores_by_region(db: Session, region: str) -> dict:
    stats = get_indicator_stats(db)
    data = get_region_data(db, region)

    print("📊 [DEBUG] 전체 stats keys:", list(stats.keys()))
    print("📊 [DEBUG] 지역 데이터 keys:", list(data.keys()))

    filtered_data = {k: v for k, v in data.items() if k in stats}

    print("📌 [DEBUG] 필터링 후 사용된 keys:", list(filtered_data.keys()))

    return compute_risk_score(filtered_data, stats)