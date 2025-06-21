import pandas as pd
from sqlalchemy.orm import Session
from realheatmap.app.database.models import BaseIndicator, ObjectDetection

# 한글 지표명을 영어 키로 변환하는 매핑
INDICATOR_KEY_MAPPING = {
    '만명당사망자수': 'fire_deaths',
    '만명당화재발생건수': 'fire_cases',
    '재난약자수': 'vulnerable_people',
    '식품위생업등종사자수': 'pub_workers',
    '창고및운송관련서비스업체수': 'warehouse_workers',
    '인구 1만 명당 노후 건축물 수': 'old_buildings_ratio',
    '병상수': 'hospital_beds',
    '재정자주도': 'financial_index',
    '도시지역면적': 'urban_area',
    '담배꽁초탐지수': 'cigarette_detect',
    '쓰레기탐지수': 'garbage_detect',
    '연기탐지수': 'smoke_detect',
    '전선탐지수': 'wires_detect'
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
        val = minmax(d[key], stats[key]['min'], stats[key]['max']) * weight
        print(f"🔸 {key}: val={d[key]}, min={stats[key]['min']}, max={stats[key]['max']}, "
              f"정규화 후={val:.4f}")
        return val

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
        w(data, 'cigarette_detect',     0.09 ) +
        w(data, 'garbage_detect',    0.05 ) +
        w(data, 'smoke_detect',  0.015 ) +
        w(data, 'wires_detect',    0.015 )
    )

    # 3. 경감지표 (25%)
    prevent = (
        w(data, 'hospital_beds',   0.028) +
        w(data, 'financial_index', 0.022) +
        w(data, 'urban_area',      0.20 )
    )
    print(f"🛡️ Prevent Score: {round(prevent * 1000, 2)}")
    

    total = danger + weak + prevent

    result = {
        'danger_score': round(danger * 100, 2),
        'weak_score': round(weak * 100, 2),
        'prevent_score': round(prevent * 100, 2),
        'total_score': round(total * 100, 2),
    }
    
    print(f"🔥 Danger Score: {result['danger_score']}")
    print(f"🧓 Weak Score: {result['weak_score']}")
    print(f"🛡️ Prevent Score: {result['prevent_score']}")
    print(f"🎯 [RESULT] 총합 위험도 점수: {result}")

    return result

# DB에서 전체 지표 min/max 계산
def get_indicator_stats(db: Session) -> dict:
    rows = db.query(BaseIndicator).all()
    df = pd.DataFrame([
        [row.region, INDICATOR_KEY_MAPPING.get(row.indicator_name.strip(), row.indicator_name.strip()), row.indicator_value]
        for row in rows
    ], columns=["region", "indicator_name", "indicator_value"])

    pivot = df.pivot(index="region", columns="indicator_name", values="indicator_value")

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

    print("📊 [DEBUG] 전체 통계 지표 keys:", list(stats.keys()))
    print("📊 [DEBUG] 지역 원본 데이터 keys:", list(data.keys()))

    filtered_data = {k: v for k, v in data.items() if k in stats}
    excluded = [k for k in data if k not in stats]

    if excluded:
        print(f"⚠️ [경고] 통계에 포함되지 않은 지역 지표 키: {excluded}")

    print("📌 [DEBUG] 최종 사용될 데이터 keys:", list(filtered_data.keys()))

    result = compute_risk_score(filtered_data, stats)

    result = compute_risk_score(filtered_data, stats)

    # 👉 최신 ObjectDetection 데이터 추가
    detection = (
        db.query(ObjectDetection)
        .filter(ObjectDetection.region == region)
        .order_by(ObjectDetection.timestamp.desc())
        .first()
    )

    result["danger_elements"] = {
        "cigarette": detection.cigarettes if detection else 0,
        "wires": detection.wires if detection else 0,
        "smoke": detection.smoke if detection else 0,
        "garbage": detection.garbage if detection else 0,
    }

    print("🧾 [DEBUG] 탐지 객체 수:", result["danger_elements"])

    return {
        "region": region,
        "danger_score": result['danger_score'],
        "weak_score": result['weak_score'],
        "prevent_score": result['prevent_score'],
        "total_score": result['total_score'],
        "danger_elements": result["danger_elements"]  # ✅ 꼭 포함되어야 함
    }

if __name__ == "__main__":
    from realheatmap.app.database.connection import SessionLocal

    db = SessionLocal()
    try:
        # 🔍 여기에서 계산하고 싶은 자치구 이름을 넣으세요 (예: "강남구", "성북구" 등)
        get_risk_scores_by_region(db, "마포구")
    finally:
        db.close()