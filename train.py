import os
os.environ["WANDB_MODE"] = "disabled"
os.environ["WANDB_SILENT"] = "true"

import sys
sys.modules["wandb"] = None  # wandb 비활성화

from ultralytics import YOLO

def main():
    # yolov10s.yaml은 현재 작업 디렉토리에 있어야 함    
    model = YOLO("C:/Users/admin/realheatmap/yolov10/ultralytics/cfg/models/v10/yolov10s.yaml")


    model.train(
        data="c:/Users/admin/realheatmap/data.yaml",  # 로컬 경로로 변경
        epochs=50,
        imgsz=640,
        batch=16,
        device=0,  # GPU 사용
        name="train_v10",
    )

if __name__ == "__main__":
    from multiprocessing import freeze_support
    freeze_support()
    main()