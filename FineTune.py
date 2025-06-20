import os
os.environ["WANDB_MODE"] = "disabled"
os.environ["WANDB_SILENT"] = "true"

import sys
sys.modules["wandb"] = None  # wandb 비활성화

from ultralytics import YOLO

def main():
    # 이미 학습된 best.pt에서 이어서 학습
    model = YOLO("fire_risk_detection/weights/best.pt")  # 기존 best 모델 불러오기

    model.train(
        data="c:/Users/admin/realheatmap/data.yaml",
        epochs=80,
        imgsz=640,
        batch=16,
        device=0,
        name="fine_betrain_v10m",  # 새로운 실험 이름
        optimizer="AdamW",
        lr0=0.0005,  # 기존보다 살짝 줄임 (fine-tune 안정성)
        cos_lr=True,
        hsv_h=0.015, hsv_s=0.3, hsv_v=0.3,
        degrees=10.0, translate=0.05, scale=0.2, shear=0.0,
        mosaic=0.2,
        mixup=0.1,
        save_period=10,
        patience=30,
        verbose=True,
        project="training_logs",
    )

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()
