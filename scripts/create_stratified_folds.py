#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create 4-fold stratified CV splits for NEU-DET")
    p.add_argument("--annotations", type=Path, required=True, help="CSV with image_id,class_id")
    p.add_argument("--out", type=Path, required=True, help="Output JSON path")
    p.add_argument("--n-folds", type=int, default=4)
    p.add_argument("--seed", type=int, default=42)
    return p.parse_args()


def dominant_class(classes: list[int]) -> int:
    counts = Counter(classes)
    max_count = max(counts.values())
    winners = [cls for cls, cnt in counts.items() if cnt == max_count]
    return min(winners)


def main() -> None:
    args = parse_args()

    by_image: dict[str, list[int]] = defaultdict(list)
    with args.annotations.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        required = {"image_id", "class_id"}
        if not required.issubset(reader.fieldnames or []):
            raise ValueError(f"Missing required columns: {required - set(reader.fieldnames or [])}")
        for row in reader:
            by_image[row["image_id"]].append(int(row["class_id"]))

    image_labels = [(img, dominant_class(clses)) for img, clses in by_image.items()]

    label_buckets: dict[int, list[str]] = defaultdict(list)
    for image_id, label in image_labels:
        label_buckets[label].append(image_id)

    rng = random.Random(args.seed)
    fold_vals: list[list[str]] = [[] for _ in range(args.n_folds)]
    for _, images in sorted(label_buckets.items()):
        rng.shuffle(images)
        for i, image_id in enumerate(images):
            fold_vals[i % args.n_folds].append(image_id)

    folds = []
    all_images = {img for img, _ in image_labels}
    for fold_idx in range(args.n_folds):
        val = sorted(fold_vals[fold_idx])
        train = sorted(all_images - set(val))
        folds.append({"fold_id": fold_idx + 1, "train": train, "val": val})

    payload = {
        "dataset": "NEU-DET",
        "protocol": "4-fold stratified by dominant class per image",
        "seed": args.seed,
        "n_folds": args.n_folds,
        "folds": folds,
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote folds to {args.out}")


if __name__ == "__main__":
    main()
