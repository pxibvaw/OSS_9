import random
from pathlib import Path
import shutil
from collections import defaultdict, Counter

# 각 라벨 파일은 1개 이상 클래스 포함 가능
# 파일 안의 클래스들을 보고 통계 기반 분할 해야함
# 각 txt 파일이 포함하는 클래스 ID 리스트 분석
# 클래스별 인스턴스 수가 train:valid:test 7:2:1로 분할되도록 조정

# 설정
random.seed(42)
label_dir = Path("balanced_dataset/labels")
image_dir = Path("balanced_dataset/images")
output_dir = Path("realheatmap_split")

splits = ["train", "valid", "test"]
split_ratios = {"train": 0.7, "valid": 0.2, "test": 0.1}

# 출력 폴더 구조 생성
for split in splits:
    (output_dir / f"images/{split}").mkdir(parents=True, exist_ok=True)
    (output_dir / f"labels/{split}").mkdir(parents=True, exist_ok=True)

# 각 라벨 파일의 인스턴스를 리스트로 수집
all_instances = []  # [(filename, class_id)]
for label_file in label_dir.glob("*.txt"):
    with open(label_file, 'r') as f:
        for line in f:
            parts = line.strip().split()
            if parts and parts[0].replace('.', '', 1).isdigit():
                class_id = int(float(parts[0]))
                all_instances.append((label_file.name, class_id))

# 클래스별 인스턴스 목록 분리
grouped_by_class = defaultdict(list)
for file, cls in all_instances:
    grouped_by_class[cls].append(file)

# 중복 제거된 인스턴스 리스트를 기반으로 split 분배
file_to_split = {}  # 파일: split
used_files = set()

for cls, files in grouped_by_class.items():
    unique_files = list(set(files))
    random.shuffle(unique_files)
    n = len(unique_files)
    n_train = int(n * split_ratios["train"])
    n_valid = int(n * split_ratios["valid"])
    n_test = n - n_train - n_valid
    
    for i, f in enumerate(unique_files):
        if f in used_files:
            continue  # 이미 다른 클래스에서 배정됨
        if i < n_train:
            file_to_split[f] = "train"
        elif i < n_train + n_valid:
            file_to_split[f] = "valid"
        else:
            file_to_split[f] = "test"
        used_files.add(f)

# 파일 복사 수행
for file, split in file_to_split.items():
    label_src = label_dir / file
    image_src = image_dir / (file.replace(".txt", ".jpg"))
    label_dst = output_dir / f"labels/{split}" / file
    image_dst = output_dir / f"images/{split}" / image_src.name

    shutil.copy(label_src, label_dst)
    if image_src.exists():
        shutil.copy(image_src, image_dst)

print(" 클래스 인스턴스 기준 7:2:1 smart split 완료.")
