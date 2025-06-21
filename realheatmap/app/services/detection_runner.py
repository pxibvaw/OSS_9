import os
import time
import random
from datetime import datetime
from sqlalchemy.orm import Session
from realheatmap.app.database.connection import SessionLocal
from realheatmap.app.database.models import ObjectDetection
from ultralytics import YOLO

# 자치구 리스트
DISTRICTS = [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구",
    "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구",
    "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"
]

# 경로 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, "../../.."))

model_path = os.path.join(PROJECT_ROOT, "realheatmap", "fire_risk_detection", "weights", "best.pt")
if not os.path.isfile(model_path):
    raise FileNotFoundError(f"❌ YOLO 모델 파일을 찾을 수 없습니다: {model_path}")

image_folder = os.path.join(PROJECT_ROOT, "realheatmap", "images")
if not os.path.isdir(image_folder):
    raise FileNotFoundError(f"❌ 이미지 폴더가 존재하지 않습니다: {image_folder}")

model = YOLO(model_path)


def save_detection_result(db: Session, region: str, counts: list[int]):
    """탐지 결과를 DB에 저장하거나 누적 업데이트합니다."""
    obj = db.query(ObjectDetection).filter_by(region=region).first()

    if obj:
        old = (obj.cigarettes, obj.garbage, obj.smoke, obj.wires)
        obj.cigarettes += counts[0]
        obj.garbage += counts[1]
        obj.smoke += counts[2]
        obj.wires += counts[3]
        obj.timestamp = datetime.utcnow()
        print(f"[🔄 업데이트] {region}: {old} → {counts}")
    else:
        obj = ObjectDetection(
            region=region,
            cigarettes=counts[0],
            garbage=counts[1],
            smoke=counts[2],
            wires=counts[3],
            timestamp=datetime.utcnow()
        )
        db.add(obj)
        print(f"[✅ 신규 등록] {region} → {counts}")

    db.commit()


def detect_and_store(image_path: str, db: Session):
    """이미지 한 장에 대해 객체 탐지 후 DB에 저장"""
    results = model(image_path)[0]
    counts = [0, 0, 0, 0]  # [cigarettes, garbage, smoke, wires]

    for box in results.boxes:
        cls = int(box.cls.item())
        if 0 <= cls < len(counts):
            counts[cls] += 1

    random_region = random.choice(DISTRICTS)
    save_detection_result(db, random_region, counts)


def run_detection_loop():
    """이미지 폴더 내 모든 이미지에 대해 탐지 수행"""
    db = SessionLocal()
    try:
        image_files = sorted([
            f for f in os.listdir(image_folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

        if not image_files:
            print("⚠️ 탐지할 이미지가 없습니다.")
            return

        for image_file in image_files:
            image_path = os.path.join(image_folder, image_file)
            print(f"[📷 처리 시작] {image_file}")
            detect_and_store(image_path, db)
            time.sleep(10)

    finally:
        db.close()
        print("[✅ 종료] DB 세션 닫힘")

# 파일 테스트
# if __name__ == "__main__":
#     run_detection_loop()

# 인공지능 백그라운드 스레드
def start_detection_loop(interval: int = 10):
    while True:
        run_detection_loop()          
        time.sleep(interval)    