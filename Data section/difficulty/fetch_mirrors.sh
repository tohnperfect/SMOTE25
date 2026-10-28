#!/usr/bin/env bash
# Rebuild the mirror files that catalog.py / measure.py read from difficulty/src/ (not stored in git).
# Used 28 Oct 2026; re-running measure.py on these reproduced the earlier difficulty_measures.csv exactly
# (all numeric columns identical before the rare-rule change).
set -euo pipefail
cd "$(dirname "$0")"; mkdir -p src/dl src/kd src/idb src/pmlb
pip download --no-deps -d src/dl keel-ds==0.2.5 imbalanced-databases==0.1.1
python3 -m zipfile -e src/dl/keel_ds-0.2.5-py3-none-any.whl src/kd
python3 -m zipfile -e src/dl/imbalanced_databases-0.1.1-py3-none-any.whl src/idb
curl -sSfL -o src/pmlb_summary.tsv https://raw.githubusercontent.com/EpistasisLab/pmlb/master/pmlb/all_summary_stats.tsv
for f in adult balance_scale car_evaluation coil2000 connect_4 dermatology ecoli hepatitis lymphography \
         new_thyroid nursery page_blocks pendigits shuttle spambase spect wine_quality_red wine_quality_white yeast; do
  curl -sSfL -o "src/pmlb/$f.tsv.gz" "https://media.githubusercontent.com/media/EpistasisLab/pmlb/master/datasets/$f/$f.tsv.gz"
done
