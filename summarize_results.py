import pandas as pd
from pathlib import Path

# 경로 설정 (너가 지정한 project와 name 기준)
project_dir = Path("training_logs/train_v10")  # 너가 name/project에 맞게 바꿔
results_csv = project_dir / "results.csv"
best_weights = project_dir / "weights/best.pt"

if not results_csv.exists():
    print(f" 결과 파일이 없습니다: {results_csv}")
    exit()

# CSV 읽기
df = pd.read_csv(results_csv)

# 마지막 epoch 기준 요약
last = df.iloc[-1]

print("\n YOLO 학습 결과 요약:")
print(f" Epochs Trained: {len(df)}")
print(f" mAP50:  {last['metrics/mAP50']:.4f}")
print(f" mAP50-95: {last['metrics/mAP50-95']:.4f}")
print(f" Precision: {last['metrics/precision']:.4f}")
print(f" Recall:    {last['metrics/recall']:.4f}")
print(f" Best Weights File: {best_weights if best_weights.exists() else 'Not Found'}")
