# realheatmap/app/database/insert_base_indicators.py

import pandas as pd
from sqlalchemy.orm import Session
from realheatmap.app.database.database import SessionLocal
from realheatmap.app.database.models import BaseIndicator
from tqdm import tqdm

# CSV 경로
csv_path = "realheatmap/app/data/rawindicator.csv"

# CSV 불러오기
df = pd.read_csv(csv_path)

# NaN 제거
df = df.dropna(subset=["indicator_value"])

# DB 세션 시작
db: Session = SessionLocal()

try:
    for _, row in tqdm(df.iterrows(), total=len(df)):
        indicator = BaseIndicator(
            region=row["district_id"],
            indicator_name=row["indicator_name"],
            indicator_value=row["indicator_value"]
        )
        db.add(indicator)
    db.commit()
    print("✅ base_indicators 테이블에 성공적으로 저장되었습니다.")
except Exception as e:
    db.rollback()
    print(f"❌ 오류 발생: {e}")
finally:
    db.close()