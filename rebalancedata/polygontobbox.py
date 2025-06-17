from pathlib import Path

def convert_polygon_to_bbox(label_path):
    lines = []
    with open(label_path, 'r') as f:
        for line in f:
            parts = list(map(float, line.strip().split()))
            class_id = int(parts[0])
            coords = parts[1:]

            if len(coords) % 2 != 0 or len(coords) < 4:
                continue  # 이상한 라벨은 무시

            xs = coords[0::2]
            ys = coords[1::2]

            xmin = min(xs)
            xmax = max(xs)
            ymin = min(ys)
            ymax = max(ys)

            x_center = (xmin + xmax) / 2
            y_center = (ymin + ymax) / 2
            width = xmax - xmin
            height = ymax - ymin

            lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\n")

    return lines

# 변환 경로 설정
base_dir = Path("train")
label_dir = base_dir / "labels"
output_dir = Path("converted_labels")  # 새로 저장할 폴더
output_dir.mkdir(parents=True, exist_ok=True)

for label_file in label_dir.glob("*.txt"):
    new_lines = convert_polygon_to_bbox(label_file)
    with open(output_dir / label_file.name, 'w') as f:
        f.writelines(new_lines)

print("polygon → bbox 라벨 변환 완료")
