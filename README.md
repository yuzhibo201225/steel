# steel: NEU-DET RT-DETR vs YOLO Benchmark

This repository provides a reproducible experiment scaffold for **fair RT-DETR vs YOLO comparison** on NEU-DET with a shared **4-fold stratified CV protocol**.

## What is implemented

- Fold generation script with stratified 4-fold splitting.
- Fold-aware training entry points for RT-DETR and YOLO.
- Unified metric schema (`model_name`, `fold_id`, `seed`, `AP50`, `mAP50_95`, `per_class_AP`).
- Statistical aggregation script exporting ANOVA and Tukey HSD tables.
- Smoke-test mode for quick pipeline verification without full GPU training.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
# Optional for real training:
pip install -e '.[train]'
```

## Expected annotation input for split

`create_stratified_folds.py` expects a CSV with columns:

- `image_id`
- `class_id`

Example:

```csv
image_id,class_id
img_0001,0
img_0001,4
img_0002,1
```

## Reproducible runbook

### 1) Create stratified folds

```bash
python scripts/create_stratified_folds.py \
  --annotations data/neu_det/annotations.csv \
  --out data/neu_det/folds_4_seed42.json \
  --n-folds 4 --seed 42
```

### 2) RT-DETR training (single fold smoke test)

```bash
PYTHONPATH=src python scripts/train_rtdetr.py \
  --data configs/neudet_base.yaml \
  --fold-id 1 --seed 42 --smoke-test \
  --output runs/neu_det/rtdetr/fold_1/metrics.json
```

### 3) YOLO training (single fold smoke test)

```bash
PYTHONPATH=src python scripts/train_yolo.py \
  --data configs/neudet_base.yaml \
  --fold-id 1 --seed 42 --smoke-test \
  --output runs/neu_det/yolo/fold_1/metrics.json
```

### 4) Unified evaluation record (optional normalization step)

```bash
PYTHONPATH=src python scripts/evaluate.py \
  --input runs/neu_det/rtdetr/fold_1/metrics.json \
  --model-name RT-DETR --fold-id 1 --seed 42 \
  --output runs/neu_det/rtdetr/fold_1/eval_metrics.json
```

### 5) Statistical analysis input + ANOVA + Tukey HSD

```bash
python scripts/aggregate_stats.py \
  --inputs runs/neu_det/rtdetr/fold_1/metrics.json runs/neu_det/yolo/fold_1/metrics.json \
  --out-dir runs/neu_det/statistics \
  --metric mAP50_95
```

Outputs:

- `runs/neu_det/statistics/metrics_tidy.csv`
- `runs/neu_det/statistics/anova_summary.csv`
- `runs/neu_det/statistics/tukey_input.csv`

## Notes on fair comparison

1. Use exactly the same folds file for both RT-DETR and YOLO.
2. Keep seed, image size, and epoch budget aligned unless explicitly ablated.
3. Do not change metric definitions across models.
4. Run all 4 folds before reporting final claims.

## What remains before full experiments

- Prepare NEU-DET in YOLO detection format and validate paths in `configs/neudet_base.yaml`.
- Disable `--smoke-test` and run all folds with GPU.
- Archive all per-fold JSON metrics for statistics.
