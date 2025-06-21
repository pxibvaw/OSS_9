from fastapi import APIRouter, Query
from sqlalchemy.orm import Session
from datetime import datetime
from fastapi.responses import JSONResponse

from realheatmap.app.database.database import SessionLocal
from realheatmap.app.database.models import FireRiskScore
from realheatmap.app.services.weather_calc import calculate_fire_risk_score
from realheatmap.app.services.risk_calc import get_risk_scores_by_region

router = APIRouter()

@router.get("/calculate-risk")
def calc_fire_risk(
    region: str = Query(..., description="자치구 이름"),
    date: str = Query(None, description="YYYY-MM-DD 형식 날짜 (선택)")
):
    """
    기상정보별화재위험지수를 계산하고 DB에 저장합니다.
    날짜를 지정하지 않으면 오늘 날짜 기준으로 계산합니다.
    """
    db: Session = SessionLocal()
    try:
        target_date = datetime.now().date() if date is None else datetime.strptime(date, "%Y-%m-%d").date()

        result = calculate_fire_risk_score(db, region, target_date)
        if result is None:
            return JSONResponse(status_code=404, content={"message": "위험지수 계산 실패 (데이터 없음)"})
        
        dwi_grade = result["dwi_score"] 
        daily_weight = result["daily_weight"] 

        risk = FireRiskScore(
            region=region,
            score_type="dwi",
            score_value=dwi_grade,
            timestamp=datetime.now()
        )
        db.add(risk)
        db.commit()

        return {
            "region": region,
            "date": str(target_date),
            "dwi_score": dwi_grade,
            "daily_weight": daily_weight
        }
    finally:
        db.close()


@router.get("/base-risk")
def base_risk(region: str = Query(..., description="자치구 이름")):
    """
    자치구의 기초 인프라 기반 위험 점수를 반환합니다.
    """
    db: Session = SessionLocal()
    try:
        scores = get_risk_scores_by_region(db, region)
        if not scores:
            return JSONResponse(status_code=404, content={"message": "기초 지표 데이터 부족"})
        return {
            "region": region,
            "danger_score": scores['danger_score'],
            "weak_score": scores['weak_score'],
            "prevent_score": scores['prevent_score'],
            "total_score": scores['total_score']
        }
    finally:
        db.close()