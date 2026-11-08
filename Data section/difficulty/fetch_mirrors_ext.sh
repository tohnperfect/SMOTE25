#!/usr/bin/env bash
# Extra mirror files read by mirrors_ext.py (8 Nov 2026, Claude). Run after fetch_mirrors.sh, from Data section/difficulty.
# KEEL / UCI / OpenML sites are refused by the proxy, so the files come from public GitHub copies (not stored in git).
set -eu
cd "$(dirname "$0")"; mkdir -p src && cd src
for r in Fuminides/keel_datasets 15399240803/keel_csv lpfgarcia/ucipp renatopp/arff-datasets klainfo/DefectData; do
  d=$(echo "$r" | tr '/' '_'); [ -d "$d" ] || git clone -q --depth 1 "https://github.com/$r" "$d"
done
mkdir -p keelcsv_lfs   # keel_csv stores its CSVs in Git LFS
for f in $(ls 15399240803_keel_csv/standard_classification/unprocessed/); do
  [ -s "keelcsv_lfs/$f" ] || curl -sSfL -o "keelcsv_lfs/$f" "https://media.githubusercontent.com/media/15399240803/keel_csv/master/standard_classification/unprocessed/$f"
done
python3 - <<'PY'
import pandas as pd
s = pd.read_csv('pmlb_summary.tsv', sep='\t'); s = s[s.task == 'classification']
open('pmlb_list.txt', 'w').write('\n'.join(s.dataset))
PY
mkdir -p pmlb
for f in $(cat pmlb_list.txt); do
  [ -s "pmlb/$f.tsv.gz" ] || curl -sSfL -o "pmlb/$f.tsv.gz" "https://media.githubusercontent.com/media/EpistasisLab/pmlb/master/datasets/$f/$f.tsv.gz"
done
mkdir -p jbrownlee
for f in mammography oil-spill new-thyroid banknote_authentication wheat-seeds pima-indians-diabetes sonar ionosphere wine glass ecoli haberman abalone breast-cancer-wisconsin breast-cancer german phoneme adult-all horse-colic; do
  [ -s "jbrownlee/$f.csv" ] || curl -sSfL -o "jbrownlee/$f.csv" "https://raw.githubusercontent.com/jbrownlee/Datasets/master/$f.csv" || echo "missing $f"
done
