import os
os.environ["WANDB_MODE"] = "disabled"
os.environ["WANDB_SILENT"] = "true"

import sys
sys.modules["wandb"] = None  # wandb 비활성화

from ultralytics import YOLO

def main():
    # yolov10s.yaml은 현재 작업 디렉토리에 있어야 함    
    model = YOLO("C:/Users/admin/realheatmap/yolov10/ultralytics/cfg/models/v10/yolov10m.yaml")


    model.train(
        data="c:/Users/admin/realheatmap/data.yaml",
        epochs=200,
        imgsz=640, #이미지 해상도 올리기
        batch=16, #이미지가 커지면 batch를 줄이기
        device=0,
        name="betrain_v10m",
        optimizer="AdamW",
        lr0=0.001,
        cos_lr=True,
        hsv_h=0.015, hsv_s=0.3, hsv_v=0.3,
        degrees=10.0, translate=0.05, scale=0.2, shear=0.0,
        mosaic=0.2,
        mixup=0.1,
        save_period=10,
        patience=30,
        verbose = True,
        project = "training_logs",
    )

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()
