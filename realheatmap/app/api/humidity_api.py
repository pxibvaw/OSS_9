from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
from realheatmap.app.database.database import get_db
from realheatmap.app.database.models import WeatherCalculated
from realheatmap.app.services.humidity_calc import calculate_effective_humidity

router = APIRouter()

@router.get("/humidity/{region}")
def get_effective_humidity(
    region: str,
    date: str = Query(..., description="YYYY-MM-DD 형식의 날짜"),
    db: Session = Depends(get_db)
):
    try:
        target_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="날짜 형식은 YYYY-MM-DD여야 합니다.")

    existing = db.query(WeatherCalculated).filter(
        WeatherCalculated.region == region,
        WeatherCalculated.date == target_date
    ).first()

    if existing:
        print(f"✅ [DB 응답] {region} {target_date} 실효습도: {existing.effective_humidity:.2f}")
        return {
            "region": region,
            "date": str(target_date),
            "effective_humidity": existing.effective_humidity,
            "source": "DB"
        }

    He = calculate_effective_humidity(db, region, target_date)
    print(f"🔍 저장 직전 He 값: {He}") 
    if He is None:
        print(f"❌ [계산 실패] {region} {target_date} - 습도 데이터 부족")
        raise HTTPException(status_code=404, detail="습도 데이터가 부족해 실효습도 계산이 불가능합니다.")

    print(f"✅ [계산 완료] {region} {target_date} 실효습도 계산됨: {He:.2f}")
    return {
        "region": region,
        "date": str(target_date),
        "effective_humidity": He,
        "source": "calculated"
    }