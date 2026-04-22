#!/usr/bin/env python3
from __future__ import annotations

import argparse
import random
from pathlib import Path

from steel_exp.io import dump_json


DEFAULT_CLASSES = ["crazing", "inclusion", "patches", "pitted_surface", "rolled-in_scale", "scratches"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train RT-DETR on NEU-DET fold")
    p.add_argument("--data", type=Path, required=True, help="Dataset YAML")
    p.add_argument("--fold-id", type=int, required=True)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--epochs", type=int, default=100)
    p.add_argument("--imgsz", type=int, default=640)
    p.add_argument("--device", default="cpu")
    p.add_argument("--output", type=Path, required=True, help="metrics.json")
    p.add_argument("--smoke-test", action="store_true", help="Skip heavy training; write deterministic mock metrics")
    return p.parse_args()


def smoke_metrics(seed: int, fold_id: int) -> tuple[float, float, dict[str, float]]:
    rng = random.Random(seed * 100 + fold_id)
    ap50 = round(0.70 + rng.random() * 0.2, 4)
    map_50_95 = round(ap50 - (0.15 + rng.random() * 0.05), 4)
    per_class = {name: round(max(0.1, ap50 - rng.random() * 0.2), 4) for name in DEFAULT_CLASSES}
    return ap50, map_50_95, per_class


def main() -> None:
    args = parse_args()

    if not args.smoke_test:
        try:
            from ultralytics import RTDETR  # type: ignore
        except ImportError as exc:
            raise SystemExit("ultralytics is required for non-smoke training. Install with: pip install '.[train]'") from exc

        model = RTDETR("rtdetr-l.pt")
        results = model.train(
            data=str(args.data),
            epochs=args.epochs,
            imgsz=args.imgsz,
            device=args.device,
            seed=args.seed,
            project="runs/neu_det",
            name=f"rtdetr/fold_{args.fold_id}",
        )
        metrics = results.results_dict
        ap50 = float(metrics.get("metrics/mAP50(B)", 0.0))
        map_50_95 = float(metrics.get("metrics/mAP50-95(B)", 0.0))
        per_class = {k: float(v) for k, v in metrics.items() if k.startswith("metrics/AP-")}
    else:
        ap50, map_50_95, per_class = smoke_metrics(args.seed, args.fold_id)

    payload = {
        "model_name": "RT-DETR",
        "fold_id": args.fold_id,
        "seed": args.seed,
        "AP50": ap50,
        "mAP50_95": map_50_95,
        "per_class_AP": per_class,
    }
    dump_json(args.output, payload)
    print(f"Saved metrics -> {args.output}")


if __name__ == "__main__":
    main()
