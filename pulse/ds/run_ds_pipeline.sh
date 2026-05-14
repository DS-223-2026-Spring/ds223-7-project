#!/usr/bin/env bash
# =============================================================================
# Pulse — DS Pipeline Runner (Milestone 4)
# Data Scientist: Silva Vardanyan
#
# Runs the full DS pipeline in order. Execute inside the ds container:
#
#   docker-compose exec ds bash run_ds_pipeline.sh
#
# Or from the repo root on the host:
#
#   docker-compose exec ds bash pulse/ds/run_ds_pipeline.sh
#
# Scripts are idempotent — safe to re-run. Each step depends on the previous.
# =============================================================================

set -e
cd "$(dirname "$0")"

echo "============================================================"
echo "  Pulse DS Pipeline"
echo "============================================================"

echo ""
echo "[1/4] Running K-Means segmentation (k=4) ..."
echo "      Fits model, expires old assignments, writes: user_segments"
echo "      Saves: outputs/kmeans_model.pkl"
python segment_kmeans.py

echo ""
echo "[2/4] Running A/B analysis (Thompson Sampling) ..."
echo "      Populates: ab_test_results, ab_assignments, ab_tests"
python run_ab_analysis.py

echo ""
echo "[3/4] Running prediction pipeline ..."
echo "      Trains model if needed, writes: user_conversion_scores, predictions.csv"
python predict.py

echo ""
echo "[4/4] Generating segment summary ..."
echo "      Writes: outputs/segment_summary.csv, outputs/segment_summary.json"
python segment_summary.py

echo ""
echo "============================================================"
echo "  DS Pipeline complete."
echo "  Outputs:"
echo "    outputs/kmeans_model.pkl      — fitted K-Means segmentation model"
echo "    outputs/predictions.csv       — per-user conversion scores"
echo "    outputs/segment_summary.csv   — per-segment summary table"
echo "    outputs/segment_summary.json  — JSON for frontend integration"
echo "  DB tables written:"
echo "    user_segments                 — K-Means cluster assignments"
echo "    ab_test_results               — Thompson Sampling results"
echo "    user_conversion_scores        — per-user ML predictions"
echo "============================================================"
