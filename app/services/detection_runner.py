import os
import time
import random
from datetime import datetime
from sqlalchemy.orm import Session
from realheatmap.app.database.connection import SessionLocal
from realheatmap.app.database.models import ObjectDetection

from ultralytics import YOLO
from PIL import Image

# 자치구 리스트
DISTRICTS = [
    "강남구", "강동구", "강북구", "강서구", "관악구", "광진구", "구로구", "금천구", "노원구",
    "도봉구", "동대문구", "동작구", "마포구", "서대문구", "서초구", "성동구", "성북구",
    "송파구", "양천구", "영등포구", "용산구", "은평구", "종로구", "중구", "중랑구"
]

# YOLO 모델 로드
model = YOLO("realheatmap/fire_risk_detection/weights/best.pt")

# 이미지 폴더 경로
image_folder = "realheatmap/images"

def save_detection_result(db: Session, region: str, counts: list[int]):
    obj = db.query(ObjectDetection).filter_by(region=region).first()

    if obj:
        obj.cigarettes += counts[0]
        obj.garbage += counts[1]
        obj.smoke += counts[2]
        obj.wires += counts[3]
        obj.timestamp = datetime.utcnow()
        print(f"[🔄 업데이트] {region} 누적: {counts}")
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
        print(f"[✅ 신규 추가] {region} 등록: {counts}")

    db.commit()

def detect_and_store(image_path: str, db: Session):
    results = model(image_path)[0]
    counts = [0, 0, 0, 0]  # [cigarettes, garbage, smoke, wires]

    for box in results.boxes:
        cls = int(box.cls.item())
        if 0 <= cls <= 3:
            counts[cls] += 1

    random_region = random.choice(DISTRICTS)
    save_detection_result(db, random_region, counts)

def run_detection_loop():
    db = SessionLocal()
    try:
        image_files = sorted([
            f for f in os.listdir(image_folder)
            if f.lower().endswith((".jpg", ".jpeg", ".png"))
        ])

        for image_file in image_files:
            image_path = os.path.join(image_folder, image_file)
            print(f"[INFO] 처리 중: {image_path}")
            detect_and_store(image_path, db)
            time.sleep(10)  # 10초 대기

    finally:
        db.close()

if __name__ == "__main__":
    run_detection_loop()