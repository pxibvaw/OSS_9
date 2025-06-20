# realheatmap/app/database/createdb.py

import sys
import os

# 📌 현재 경로 기준으로 최상단 경로(OSS_9-main)를 PYTHONPATH에 추가
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

# ✅ Base와 engine 불러오기
from realheatmap.app.database.database import Base, engine

# ✅ 모든 모델을 import해야 Base.metadata에 테이블 등록됨
from realheatmap.app.database import models  # ⚠️ 반드시 필요

# ✅ 테이블 생성
print("🛠️ SQLite DB에 테이블 생성 중...")
Base.metadata.create_all(bind=engine)
print("✅ DB 테이블이 성공적으로 생성되었습니다.")