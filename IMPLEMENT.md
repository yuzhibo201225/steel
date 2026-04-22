# IMPLEMENT

## Rules
- Keep modifications focused and minimal.
- Preserve metric schema consistency across models.
- Use same fold protocol for fair comparison.

## Execution order
1. Generate `folds_4_seed42.json` once.
2. Train/evaluate RT-DETR and YOLO with the same `fold_id` + `seed`.
3. Save per-fold JSON metrics using shared fields.
4. Aggregate all fold outputs to statistics tables.

## Verification
- Smoke test at least one fold for each model.
- Validate generated files exist and can be loaded by `aggregate_stats.py`.
