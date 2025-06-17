from pathlib import Path

val_label_dir = Path("realheatmap_split/labels/valid")
class_counts = [0, 0, 0, 0]

for file in val_label_dir.glob("*.txt"):
    with open(file, "r") as f:
        for line in f:
            class_id = int(line.strip().split()[0])
            if 0 <= class_id <= 3:
                class_counts[class_id] += 1

print(f"cigarette: {class_counts[0]}")
print(f"garbage:   {class_counts[1]}")
print(f"smoke:     {class_counts[2]}")
print(f"wires:     {class_counts[3]}")
