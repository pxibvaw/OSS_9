from pathlib import Path
from collections import defaultdict, Counter
import random
import shutil
import albumentations as A
import cv2

# 설정
random.seed(42)
TARGET_INSTANCES = {
    0: 2500,  # cigarette
    1: 1500,  # garbage
    2: 1500,  # smoke (includes ~1.2x augmentation)
    3: 1599   # wires (all used)
}

IMG_DIR = Path("train/images")
LABEL_DIR = Path("converted_labels")
OUTPUT_IMG_DIR = Path("balanced_dataset/images")
OUTPUT_LABEL_DIR = Path("balanced_dataset/labels")

OUTPUT_IMG_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_LABEL_DIR.mkdir(parents=True, exist_ok=True)

class_to_labels = defaultdict(list)

# 라벨 파일 분석
for label_file in LABEL_DIR.glob("*.txt"):
    with open(label_file, 'r') as f:
        class_ids = [int(line.strip().split()[0]) for line in f if line.strip()]
        for cid in set(class_ids):
            class_to_labels[cid].append(label_file)

# 증강 정의 (smoke)
augment = A.Compose([
    A.HorizontalFlip(p=0.5),
    A.RandomBrightnessContrast(p=0.5),
    A.Rotate(limit=10, p=0.5),
])

augmented_count = 0

# 클래스별 처리
for class_id, target_total in TARGET_INSTANCES.items():
    used = 0
    used_files = []
    label_pool = list(set(class_to_labels[class_id]))
    random.shuffle(label_pool)

    for label_file in label_pool:
        with open(label_file, 'r') as f:
            count = sum(1 for line in f if line.strip().split()[0] == str(class_id))

        if used + count > target_total:
            continue

        img_file = IMG_DIR / f"{label_file.stem}.jpg"
        if img_file.exists():
            shutil.copy(img_file, OUTPUT_IMG_DIR / img_file.name)
            shutil.copy(label_file, OUTPUT_LABEL_DIR / label_file.name)
            used += count
            used_files.append(label_file)

        if used >= target_total:
            break

    # smoke만 증강
    if class_id == 2 and used < target_total:
        needed = target_total - used
        reuse_files = used_files[:needed]
        for i, label_file in enumerate(reuse_files):
            img_file = IMG_DIR / f"{label_file.stem}.jpg"
            image = cv2.imread(str(img_file))
            if image is None:
                continue
            aug = augment(image=image)['image']
            aug_name = f"aug_{label_file.stem}_{i}"
            cv2.imwrite(str(OUTPUT_IMG_DIR / f"{aug_name}.jpg"), aug)
            shutil.copy(label_file, OUTPUT_LABEL_DIR / f"{aug_name}.txt")
            augmented_count += 1

print(f"클래스별 인스턴스 수 설정 완료")
print(f"smoke 증강 횟수: {augmented_count}")
print(f"결과: balanced_dataset/images/, labels/")
