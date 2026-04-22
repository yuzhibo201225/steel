#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Aggregate fold metrics and export ANOVA/Tukey-ready tables")
    p.add_argument("--inputs", nargs="+", type=Path, required=True, help="metrics.json files")
    p.add_argument("--out-dir", type=Path, required=True)
    p.add_argument("--metric", default="mAP50_95", choices=["AP50", "mAP50_95"])
    return p.parse_args()


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs)


def anova_f(groups: dict[str, list[float]]) -> tuple[float, int, int]:
    all_values = [v for values in groups.values() for v in values]
    grand_mean = mean(all_values)

    ss_between = sum(len(values) * (mean(values) - grand_mean) ** 2 for values in groups.values())
    ss_within = sum(sum((v - mean(values)) ** 2 for v in values) for values in groups.values())

    df_between = len(groups) - 1
    df_within = len(all_values) - len(groups)
    ms_between = ss_between / df_between if df_between else 0.0
    ms_within = ss_within / df_within if df_within else 0.0
    f_stat = ms_between / ms_within if ms_within else math.inf
    return f_stat, df_between, df_within


def main() -> None:
    args = parse_args()
    rows: list[dict[str, object]] = []
    for path in args.inputs:
        rows.append(json.loads(path.read_text(encoding="utf-8")))

    args.out_dir.mkdir(parents=True, exist_ok=True)

    tidy_path = args.out_dir / "metrics_tidy.csv"
    fieldnames = ["model_name", "fold_id", "seed", "AP50", "mAP50_95", "per_class_AP"]
    with tidy_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            row = dict(row)
            row["per_class_AP"] = json.dumps(row.get("per_class_AP", {}), ensure_ascii=False)
            writer.writerow({k: row.get(k) for k in fieldnames})

    by_model: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        by_model[str(row["model_name"])].append(float(row[args.metric]))

    f_stat, df_between, df_within = anova_f(by_model)
    anova_path = args.out_dir / "anova_summary.csv"
    with anova_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "f_statistic", "df_between", "df_within"])
        writer.writeheader()
        writer.writerow(
            {
                "metric": args.metric,
                "f_statistic": f"{f_stat:.6f}",
                "df_between": df_between,
                "df_within": df_within,
            }
        )

    tukey_input = args.out_dir / "tukey_input.csv"
    with tukey_input.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["model_name", "value"])
        writer.writeheader()
        for model, values in sorted(by_model.items()):
            for value in values:
                writer.writerow({"model_name": model, "value": f"{value:.6f}"})

    print(f"Wrote {tidy_path}\nWrote {anova_path}\nWrote {tukey_input}")


if __name__ == "__main__":
    main()
