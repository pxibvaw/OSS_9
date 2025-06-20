# Fire Risk Object Detection (YOLOv10s)

본 프로젝트는 도시 내 화재 위험 요소(담배꽁초, 쓰레기, 연기, 전선)를 객체 탐지를 통해 자동으로 식별하고, 이를 기반으로 **Heatmap 시각화**에 활용하는 것을 목표로 합니다.

## 🔧 Model Information

- **Architecture**: YOLOv10s (`ultralytics/cfg/models/v10/yolov10s.yaml`)
- **Framework**: Ultralytics YOLO (v8.3.152)
- **Device**: NVIDIA RTX 3060 (12GB)
- **Total Parameters**: ~7.2M

## 🏋️ Training Configuration (`train.py` 기반)

| 항목 | 값 |
|------|----|
| Epochs | 200 |
| Batch size | 16 |
| Image size | 640 |
| Optimizer | AdamW |
| Learning rate | 0.001 |
| Scheduler | Cosine LR (`cos_lr=True`) |
| Augmentation | HSV(h=0.015, s=0.3, v=0.3), degrees=10.0, translate=0.05, scale=0.2, shear=0.0, mosaic=0.2, mixup=0.1 |
| Early Stopping | patience=30 |
| Logging | W&B 비활성화 |
| Save Interval | 10 epochs |
| Project Name | training_logs/betrain_v10m |

## 🗂️ Dataset

- **Classes (4)**: `cigarette`, `garbage`, `smoke`, `wires`
- **Total Instances**: 약 6,700개
- **Split**: Train: 80%, Validation: 20%
- **Config File**: `data.yaml`
- **Source**: 직접 수집 + Roboflow 기반 보강

## 📊 Evaluation Results (best.pt 기준)

| Class      | Precision | Recall | mAP@0.5 |
|------------|-----------|--------|---------|
| cigarette  | 0.831     | 0.631  | 0.711   |
| garbage    | 0.766     | 0.488  | 0.565   |
| smoke      | 0.877     | 0.724  | 0.790   |
| wires      | 0.782     | 0.347  | 0.457   |
| **All**    | 0.814     | 0.547  | 0.631   |

> ⚠️ `wires` 클래스는 성능이 낮아 실시간 대응용으로 활용하기에 부적절할 수 있음.

## 🖼️ Sample Visualizations

- `results/confusion_matrix.png`
- `results/PR_curve.png`
- `results/heatmap_example.png` (예시 Heatmap 포함 가능)

## 🚀 Inference Example

```bash
yolo task=detect mode=predict model=weights/best.pt source=images/test1.jpg imgsz=640
