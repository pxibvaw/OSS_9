from pathlib import Path
import random, shutil

# 기준 경로
base_path = Path(__file__).resolve().parent / "train"
img_dir = base_path / "images"
label_dir = base_path / "labels"

# 결과 저장 경로
output_root = Path(__file__).resolve().parent / "realheatmap_split"
for split in ['train', 'valid', 'test']:
    (output_root / f"images/{split}").mkdir(parents=True, exist_ok=True)
    (output_root / f"labels/{split}").mkdir(parents=True, exist_ok=True)

# 이미지 파일 가져오기
image_files = sorted(img_dir.glob("*.jpg"))
random.seed(42)
random.shuffle(image_files)

n_total = len(image_files)
n_train = int(n_total * 0.7)
n_valid = int(n_total * 0.15)
n_test = n_total - n_train - n_valid

splits = {
    "train": image_files[:n_train],
    "valid": image_files[n_train:n_train + n_valid],
    "test":  image_files[n_train + n_valid:]
}

# 복사
for split, files in splits.items():
    for img_path in files:
        label_path = label_dir / (img_path.stem + ".txt")
        shutil.copy(img_path, output_root / f"images/{split}" / img_path.name)
        if label_path.exists():
            shutil.copy(label_path, output_root / f"labels/{split}" / label_path.name)
        else:
            open(output_root / f"labels/{split}" / label_path.name, 'w').close()

print("분할 완료: realheatmap_split 폴더 생성")
