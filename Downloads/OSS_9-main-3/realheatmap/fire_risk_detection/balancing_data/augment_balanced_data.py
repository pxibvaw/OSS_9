import cv2
import albumentations as A
from pathlib import Path
import random

# 클래스별 증강 비율 설정 (1.2x -> 0.2 추가, 1.5x -> 0.5 추가)
augmentation_ratios = {
    0: 0.5,
    1: 0.5,
    2: 0.2,
    3: 0.5
}

# 경로 설정
base_img_dir = Path("train/images")
base_lbl_dir = Path("train/labels")
output_img_dir = base_img_dir
output_lbl_dir = base_lbl_dir

# Albumentations 증강 파이프라인
augment = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.5),
    A.HueSaturationValue(p=0.5),
], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))

# 클래스별 해당 bbox가 포함된 라벨 파일 수집
class_to_files = {i: [] for i in augmentation_ratios.keys()}
all_label_files = list(base_lbl_dir.glob("*.txt"))

for label_file in all_label_files:
    with open(label_file, "r") as f:
        labels = f.readlines()
    label_classes = [int(line.strip().split()[0]) for line in labels if line.strip()]
    for cls in set(label_classes):
        if cls in class_to_files:
            class_to_files[cls].append(label_file)

# 증강 수행
aug_count = 0
for cls_id, files in class_to_files.items():
    num_to_augment = int(len(files) * augmentation_ratios[cls_id])
    selected_files = random.sample(files, min(num_to_augment, len(files)))

    for label_path in selected_files:
        image_path = base_img_dir / (label_path.stem + ".jpg")
        if not image_path.exists():
            continue

        image = cv2.imread(str(image_path))
        height, width = image.shape[:2]

        with open(label_path, "r") as f:
            raw_labels = f.readlines()

        bboxes = []
        class_labels = []
        for line in raw_labels:
            parts = line.strip().split()
            if len(parts) >= 5 and int(parts[0]) == cls_id:
                class_labels.append(int(parts[0]))
                bboxes.append([float(x) for x in parts[1:5]])

        if not bboxes:
            continue

        try:
            augmented = augment(image=image, bboxes=bboxes, class_labels=class_labels)
        except Exception:
            continue

        aug_img_name = f"aug_{aug_count:05d}.jpg"
        aug_lbl_name = f"aug_{aug_count:05d}.txt"

        cv2.imwrite(str(output_img_dir / aug_img_name), augmented["image"])
        with open(output_lbl_dir / aug_lbl_name, "w") as f:
            for cls, bbox in zip(augmented["class_labels"], augmented["bboxes"]):
                f.write(f"{cls} {' '.join(f'{x:.6f}' for x in bbox)}\n")

        aug_count += 1

print(f"총 {aug_count}개의 증강 샘플이 생성되었습니다.")
