#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from steel_exp.io import dump_json, load_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Normalize fold metrics into unified schema")
    p.add_argument("--input", type=Path, required=True, help="Raw or existing metrics JSON")
    p.add_argument("--model-name", required=True)
    p.add_argument("--fold-id", type=int, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--output", type=Path, required=True)
    return p.parse_args()


def main() -> None:
    args = parse_args()
    raw = load_json(args.input)

    payload = {
        "model_name": args.model_name,
        "fold_id": args.fold_id,
        "seed": args.seed,
        "AP50": float(raw["AP50"]),
        "mAP50_95": float(raw["mAP50_95"]),
        "per_class_AP": raw.get("per_class_AP", {}),
    }
    dump_json(args.output, payload)
    print(f"Saved normalized eval -> {args.output}")


if __name__ == "__main__":
    main()
