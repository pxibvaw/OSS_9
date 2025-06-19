from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime

from realheatmap.app.database.database import get_db
from realheatmap.app.database.models import WeatherCalculated
from realheatmap.app.tasks.init_effective_humidity import calculate_effective_humidity

router = APIRouter()

@router.get("/humidity/{region}")
def get_effective_humidity(
    region: str,
    date: str = Query(..., description="YYYY-MM-DD 형식의 날짜"),
    db: Session = Depends(get_db)
):
    """
    특정 자치구(region)와 날짜(date)를 받아 해당 날짜의 실효습도를 반환합니다.
    DB에 없으면 새로 계산 후 저장합니다.
    """
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식은 YYYY-MM-DD여야 합니다.")

    # DB에 이미 있는 경우
    existing = db.query(WeatherCalculated).filter(
        WeatherCalculated.region == region,
        WeatherCalculated.date == target_date
    ).first()

    if existing:
        return {
            "region": region,
            "date": str(target_date),
            "effective_humidity": existing.effective_humidity,
            "source": "DB"
        }

    # 없으면 계산 후 저장
    He = calculate_effective_humidity(db, region, target_date)
    if He is None:
        raise HTTPException(status_code=404, detail="습도 데이터가 부족해 실효습도 계산이 불가능합니다.")

    return {
        "region": region,
        "date": str(target_date),
        "effective_humidity": He,
        "source": "calculated"
    }