#!/usr/bin/env bash
# Confirmatory runs as specified in PREREGISTRATION.md: seeds 0-29, default Config.
# Do not edit src/ while this runs.
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src
OUT=${OUT:-results/confirmatory}
mkdir -p "$OUT"
{
  echo "commit: $(git rev-parse HEAD)"
  echo "started: $(date -u +%FT%TZ)"
  echo "python: $(python3 --version)"
  echo "numpy: $(python3 -c 'import numpy; print(numpy.__version__)')"
} > "$OUT/RUN_INFO.txt"
for exp in s1_selection s2_ablation s3_succession s4_agency; do
  echo "=== $exp $(date -u +%T)"
  python3 -m agency_gradients.experiments.$exp --seeds 30 --seed0 0 --workers 2 --out "$OUT"
done
echo "=== control $(date -u +%T)"
python3 -m agency_gradients.experiments.s_control --seeds 30 --seed0 0 --out "$OUT"
echo "finished: $(date -u +%FT%TZ)" >> "$OUT/RUN_INFO.txt"
echo "ALL DONE"
