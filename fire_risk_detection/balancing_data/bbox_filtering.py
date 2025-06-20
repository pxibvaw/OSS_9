import os
from pathlib import Path

# === 설정값 ===
IMAGE_WIDTH = 896
IMAGE_HEIGHT = 896
MIN_SIZE = 10  # 픽셀 기준
MAX_AREA = 0.9 * IMAGE_WIDTH * IMAGE_HEIGHT
ASPECT_RATIO_THRESHOLD = 10  # 너무 납작하거나 긴 비율 제거

def is_valid_bbox(w, h):
    bbox_width = w * IMAGE_WIDTH
    bbox_height = h * IMAGE_HEIGHT
    bbox_area = bbox_width * bbox_height
    if bbox_width < MIN_SIZE or bbox_height < MIN_SIZE:
        return False
    if bbox_area > MAX_AREA:
        return False
    if (bbox_width / bbox_height > ASPECT_RATIO_THRESHOLD) or (bbox_height / bbox_width > ASPECT_RATIO_THRESHOLD):
        return False
    return True

def filter_labels(label_dir):
    label_dir = Path(label_dir)
    output_dir = label_dir.parent / (label_dir.name + "_filtered")
    output_dir.mkdir(exist_ok=True)
    
    for file in label_dir.glob("*.txt"):
        new_lines = []
        with open(file, "r") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) != 5:
                    continue
                cls, xc, yc, w, h = map(float, parts)
                if is_valid_bbox(w, h):
                    new_lines.append(line.strip())
        with open(output_dir / file.name, "w") as f:
            for line in new_lines:
                f.write(line + "\n")
    print(f"완료: 필터링된 라벨은 '{output_dir}'에 저장됨")

if __name__ == "__main__":
    #여기 경로를 실제 YOLO 라벨 디렉토리로 바꿔
    filter_labels("balanced_dataset/labels")
