from collections import Counter
from pathlib import Path

label_dir = Path("balanced_dataset/labels")
class_counts = Counter()


# 모든 .txt 파일 순회하면서 수정
for label_file in label_dir.glob("*.txt"):
    lines_out = []
    with open(label_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if not parts or not parts[0].replace('.', '', 1).isdigit():
                continue
            try:
                class_id = int(float(parts[0]))
                rest = parts[1:]
                lines_out.append(f"{class_id} {' '.join(rest)}\n")
            except ValueError:
                continue

    with open(label_file, "w") as f:
        f.writelines(lines_out)

"✅ 모든 라벨 파일에서 클래스 ID를 정수로 변환 완료되었습니다."


for label_file in label_dir.glob("*.txt"):
    with open(label_file, 'r') as f:
        for line in f:
            if line.strip():
                class_id = int(line.strip().split()[0])
                class_counts[class_id] += 1

# 출력
print(" 클래스별 인스턴스 수:")
for class_id, count in sorted(class_counts.items()):
    print(f"Class {class_id}: {count}개")
