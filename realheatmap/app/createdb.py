from realheatmap.app.database import engine
from realheatmap.app.models import Base

print("🛠️ SQLite DB에 테이블 생성 중...")
Base.metadata.create_all(bind=engine)
print("✅ DB 테이블이 성공적으로 생성되었습니다.")