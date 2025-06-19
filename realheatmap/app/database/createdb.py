# realheatmap/app/database/createdb.py

from realheatmap.app.database.database import engine, Base
from realheatmap.app.database import models  # 테이블 클래스들 import

print("🛠️ SQLite DB에 테이블 생성 중...")
Base.metadata.create_all(bind=engine)
print("✅ DB 테이블이 성공적으로 생성되었습니다.")