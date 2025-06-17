from pathlib import Path
from collections import Counter

# split 경로들
split_dirs = {
    "train": Path("realheatmap_split/labels/train"),
    "valid": Path("realheatmap_split/labels/valid"),
    "test": Path("realheatmap_split/labels/test")
}

# 결과 저장용
split_class_counts = {split: Counter() for split in split_dirs}

# 각 split별 클래스 인스턴스 수 세기
for split, path in split_dirs.items():
    for label_file in path.glob("*.txt"):
        with open(label_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if parts and parts[0].replace('.', '', 1).isdigit():
                    class_id = int(float(parts[0]))
                    split_class_counts[split][class_id] += 1

# 전체 클래스별 총합 계산
total_counts = Counter()
for counts in split_class_counts.values():
    total_counts.update(counts)

# 비율 계산
def format_ratio(c):
    return f"{round(c*100, 1)}%"

print("\n클래스별 인스턴스 수 및 비율")
print("Class\tTotal\tTrain\t(%)\tValid\t(%)\tTest\t(%)")
for cls in sorted(total_counts):
    total = total_counts[cls]
    train = split_class_counts['train'][cls]
    valid = split_class_counts['valid'][cls]
    test = split_class_counts['test'][cls]
    print(f"{cls}\t{total}\t{train}\t({format_ratio(train/total)})\t{valid}\t({format_ratio(valid/total)})\t{test}\t({format_ratio(test/total)})")
