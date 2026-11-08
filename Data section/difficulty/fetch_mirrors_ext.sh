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

# ---- 8 Nov 2026, second round (official sites + author repositories; see official_sources.py) -----------------------
# Author repositories (pinned to the commits that were read; reachable from the cloud workspace and from Toon's machine)
mkdir -p author _authclone
clone() { [ -d "_authclone/$2" ] || git clone -q "https://github.com/$1.git" "_authclone/$2"; git -C "_authclone/$2" checkout -q "$3"; }
clone smallcube/HD-Ensemble HD-Ensemble ae78b37243391f42475ce485bcbc90c124dfdd3d
clone MLneuers/DGOT DGOT bb5ea8b54d8c005ef4651cc17110e034d6bfab77
clone JayoungKim408/SOS SOS f1b450cf199d5e0013b401e380008446ef8757f7
clone b10071007/Model-Based-Synthetic-Sampling MBS 90020a6a12cf88079942ab4988ba046e1941facd
rm -rf author/HD-Ensemble && cp -r _authclone/HD-Ensemble/datasets author/HD-Ensemble
mkdir -p author/DGOT author/SOS && cp _authclone/DGOT/datasets/abalone_15/abalone_15.csv author/DGOT/
cp _authclone/SOS/tabular_datasets/*.npz _authclone/SOS/tabular_datasets/*.json author/SOS/
rm -rf author/MBS && cp -r _authclone/MBS/data author/MBS
# k-means SMOTE release asset (the cloud proxy refuses the release CDN; it was downloaded with curl on Toon's machine,
# sha256 bc0aff0adc079ab01a51d286c070334ca23a393393488a6fee441cf3cd0225cf). Extract only the CSV files, never ._ files:
#   curl -sSL -o author/kmeans_uci_extended.tar.gz https://github.com/felix-last/evaluate-kmeans-smote/releases/download/v0.0.1/uci_extended.tar.gz
#   python3 -I -c "import tarfile; t=tarfile.open('author/kmeans_uci_extended.tar.gz'); t.extractall('author/kmeans', members=[m for m in t.getmembers() if m.isfile() and not m.name.split('/')[-1].startswith('._')], filter='data')"
# UCI (archive.ics.uci.edu/static/public/<id>/<name>.zip) and LibSVM (www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/):
# reachable only from a browser on Toon's machine. The browser saved them as bundles; unpack with
#   python3 unbundle_official.py <bundle> ...      (URL, size and sha256 of every file: official_manifest.csv)
# isolet: the two .Z files are decompressed with  gzip -dc isolet1+2+3+4.data.Z > isolet1+2+3+4.data  (same for isolet5).
