from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from realheatmap.app.database.connection import SessionLocal
from realheatmap.app.database.models import ObjectDetection, BaseIndicator

# 인구수 정보
REGION_POPULATION = {
    "강남구": 531739, "강동구": 453409, "강북구": 280273, "강서구": 548230, "관악구": 492798,
    "광진구": 345068, "구로구": 421170, "금천구": 244446, "노원구": 489087, "도봉구": 298678,
    "동대문구": 357112, "동작구": 384310, "마포구": 363402, "서대문구": 319148, "서초구": 389511,
    "성동구": 278757, "성북구": 431377, "송파구": 630780, "양천구": 421425, "영등포구": 402439,
    "용산구": 207409, "은평구": 453735, "종로구": 146227, "중구": 127022, "중랑구": 376147
}

def get_detection_totals(db: Session):
    """ObjectDetection 테이블에서 자치구별 누적 탐지 합계 조회"""
    return db.query(
        ObjectDetection.region,
        func.sum(ObjectDetection.cigarettes).label("cigarettes"),
        func.sum(ObjectDetection.garbage).label("garbage"),
        func.sum(ObjectDetection.smoke).label("smoke"),
        func.sum(ObjectDetection.wires).label("wires")
    ).group_by(ObjectDetection.region).all()

def migrate_to_base_indicator(db: Session, rows):
    """탐지 누적합을 위험지표(BaseIndicator)로 이관"""
    for row in rows:
        pop = REGION_POPULATION.get(row.region)
        if not pop:
            print(f"⚠️ 인구 정보 없음: {row.region}")
            continue

        scale = 10000 / pop
        indicators = {
            '담배꽁초탐지수': row.cigarettes * scale,
            '쓰레기탐지수':   row.garbage * scale,
            '연기탐지수':     row.smoke * scale,
            '전선탐지수':     row.wires * scale,
        }

        for name, value in indicators.items():
            db.add(BaseIndicator(
                region=row.region,
                indicator_name=name,
                indicator_value=value
            ))

    db.commit()
    print(f" [{datetime.now().strftime('%H:%M')}] 위험지표 이관 완료")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        print(f"[{datetime.now()}] 위험지표 계산 시작")
        rows = get_detection_totals(db)
        migrate_to_base_indicator(db, rows)
    finally:
        db.close()
        print("실행 완료")