# realheatmap/app/database/view_base_indicators.py

from sqlalchemy.orm import Session
from realheatmap.app.database.database import SessionLocal
from realheatmap.app.database.models import BaseIndicator

def view_base_indicators():
    db: Session = SessionLocal()
    try:
        rows = db.query(BaseIndicator).all()
        print(f"총 {len(rows)}개의 행이 조회되었습니다.")
        for row in rows:
            print(f"[{row.region}] {row.indicator_name}: {row.indicator_value}")
    finally:
        db.close()

if __name__ == "__main__":
    view_base_indicators()