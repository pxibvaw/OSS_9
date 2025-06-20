import pandas as pd
from sqlalchemy.orm import Session
from realheatmap.app.database.database import SessionLocal
from realheatmap.app.database.models import BaseIndicator
from tqdm import tqdm

def reload_base_indicators(csv_path: str):
    """
    지정된 CSV 파일로부터 base_indicators 테이블을 갱신합니다.
    기존 데이터는 삭제되고, 새 데이터가 삽입됩니다.
    """
    try:
        # CSV 로드
        df = pd.read_csv(csv_path)

        # NaN 제거
        df = df.dropna(subset=["indicator_value"])

        # 컬럼명 정리
        if "district_id" in df.columns:
            df = df.rename(columns={"district_id": "region"})

        db: Session = SessionLocal()

        # 기존 데이터 삭제
        deleted = db.query(BaseIndicator).delete()
        db.commit()
        print(f"🗑️ 기존 데이터 {deleted}건 삭제 완료")

        # 새 데이터 삽입
        for _, row in tqdm(df.iterrows(), total=len(df)):
            indicator = BaseIndicator(
                region=row["region"].strip(),
                indicator_name=row["indicator_name"].strip(),
                indicator_value=float(row["indicator_value"])
            )
            db.add(indicator)

        db.commit()
        print(f"📥 새 데이터 {len(df)}건 삽입 완료 from {csv_path}")

    except Exception as e:
        db.rollback()
        print(f"❌ 오류 발생: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    # 여기 경로만 바꾸면 다른 CSV로도 사용 가능
    reload_base_indicators("realheatmap/app/data/rawindicator2.csv")