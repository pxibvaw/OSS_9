import os
import cv2
import random
from glob import glob
from tqdm import tqdm

# 설정
IMG_DIR = "realheatmap_split/images/train"
LBL_DIR = "realheatmap_split/labels/train"
SAVE_IMG_DIR = IMG_DIR
SAVE_LBL_DIR = LBL_DIR
TARGET_CLASS = 3
MULTIPLIER = 1.5  # 증강 비율

# wire만 찾기
wire_labels = []
for label_path in glob(os.path.join(LBL_DIR, "*.txt")):
    with open(label_path, "r") as f:
        lines = f.readlines()
        if any(line.startswith(f"{TARGET_CLASS} ") for line in lines):
            wire_labels.append(label_path)

# 몇 개 증강할지 결정
aug_total = int(len(wire_labels) * MULTIPLIER)

def apply_clahe(img):
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    cl = clahe.apply(l)
    merged = cv2.merge((cl, a, b))
    return cv2.cvtColor(merged, cv2.COLOR_LAB2BGR)

def apply_rotation(img, angle):
    h, w = img.shape[:2]
    M = cv2.getRotationMatrix2D((w/2, h/2), angle, 1)
    return cv2.warpAffine(img, M, (w, h), borderMode=cv2.BORDER_REFLECT)

# 증강 실행
count = 0
for label_path in tqdm(random.sample(wire_labels, len(wire_labels))):
    if count >= aug_total:
        break

    img_path = label_path.replace("labels", "images").replace(".txt", ".jpg")
    if not os.path.exists(img_path):
        img_path = img_path.replace(".jpg", ".png")

    img = cv2.imread(img_path)
    if img is None:
        continue

    # 증강 조합
    aug_img = apply_rotation(img, random.uniform(-30, 30))
    aug_img = apply_clahe(aug_img)
    aug_img = cv2.GaussianBlur(aug_img, (3, 3), 0)

    # 저장
    base = os.path.basename(img_path).split(".")[0]
    new_img_name = f"{base}_aug{count}.jpg"
    new_lbl_name = f"{base}_aug{count}.txt"
    cv2.imwrite(os.path.join(SAVE_IMG_DIR, new_img_name), aug_img)
    with open(label_path, "r") as f:
        lines = f.read()
    with open(os.path.join(SAVE_LBL_DIR, new_lbl_name), "w") as f:
        f.write(lines)

    count += 1

print(f"\n증강 완료: wire 이미지 {count}개 추가됨 (총 {len(wire_labels)} → {len(wire_labels) + count})")
