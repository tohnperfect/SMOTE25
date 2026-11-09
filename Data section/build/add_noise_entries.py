"""Add the noisy versions of real data sets as 'modified' dataset entries  (9 Nov 2026, Claude; Toon 9 Nov: the noisy sets of
the seven papers are not counted as entries anywhere -> "เอาเข้า modify เลย").

Seven papers add noise (label, attribute/feature) or missing values to real data sets as an experimental condition. Until now
only the base sets were entries (in their own category) and the noisy versions were not entries at all, unlike SMOTE-IPF, whose
noisy versions were recorded on 18 Oct as two grouped entries ("Class noise versions of the 9 real-world datasets", "Attribute
noise versions ..."). The same granularity is used here: ONE entry per paper and kind of noise, category 'modified', values
only where the paper prints them (none of these groups has a printed size). in_results_table = "no" so that the row-order
fallback of build/full_extraction.py (which counts entries marked "yes") cannot change how outcome rows are matched; the
noise results are in separate tables or figures that were not extracted. The apply step asserts that out/full_outcome_rows.csv
is unchanged.

Entries are APPENDED after each paper's existing entries, so every existing record_id is unchanged.
Modes (run from Data section/):
  python3 build/add_noise_entries.py --check-pdf   on the machine with paper/: every evidence quote is on the cited PDF page
  python3 build/add_noise_entries.py --apply       edit ai-draft/full/<KEY>.json (the originals are in git history; the backup folder was removed 9 Nov),
                                                   rerun build/full_extraction.py, insert the new rows into out/verify_datasets.csv
                                                   and out/verified_datasets.csv at the same positions
Idempotent: an entry whose name already exists in the paper's JSON is not added again.
"""
import csv, json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
WHO = "Claude, 9 Nov 2026 (evidence quote asserted on the cited PDF page; Toon asked to count the noisy versions as modified entries)"

def E(name, group, src, c=None, detail="", ref="", page=None, quote=""):
    return dict(entry=dict(name=name, group=group, source_repo=src, n_instances=None, n_features=None, n_classes=c, n_minority=None,
                           n_majority=None, class_distribution=None, ir_printed=None, how_obtained="modified", how_obtained_detail=detail,
                           in_results_table="no", ref=ref), page=page, quote=quote)

NEW = {
 "RAMOBoost": [
  E("Class label noise versions of Abalone", "Noisy modified data - class label noise (Sec. IV, Table XVIII)", "UCI", 2,
    "the two-class Abalone set of the paper with class label noise added by the authors at several levels (procedure of [58]: an "
    "instance of class X is mislabelled as Y with probability x); levels as in Table XVIII; sizes not printed",
    "Sec. IV, p.16-17; Table XVIII", (0, 16), "we manually introduce class label noise and attribute noise of different levels into the"),
  E("Attribute noise versions of Abalone", "Noisy modified data - attribute noise (Sec. IV, Table XXI)", "UCI", 2,
    "the two-class Abalone set of the paper with attribute noise added by the authors at several levels (procedure of [59]: each "
    "attribute replaced by a random value with probability x); levels as in Table XXI; sizes not printed",
    "Sec. IV, p.16-17; Table XXI", (0, 16), "we manually introduce class label noise and attribute noise of different levels into the")],
 "RSMOTE": [
  E("Label noise versions of the binary data sets (10%, 20%, 30%)", "Noisy modified data - label noise (Sec. 4)", "UCI", 2,
    "every binary data set of the paper with label noise added to the training data at 10%, 20% and 30%: minority labels flipped to "
    "the majority class first, then the same number of majority labels flipped, so the IR is kept (p.12); sizes not printed",
    "p.12", (0, 12), "experiments are designed and conducted on all the data sets with three different levels of label noise, 10%, 20%, and 30%")],
 "RBO": [
  E("Label noise versions of the benchmark data sets", "Noisy modified data - label noise (Experiment 3)", "KEEL", 2,
    "the paper's benchmark sets with pairwise label noise (an object of the majority class X labelled as the minority class Y with "
    "probability x), x in {0.0, 0.05, 0.1, 0.15, 0.20} (p.8); sizes not printed",
    "Sec. 4.4, p.8", (0, 8), "Experiment 3: imbalanced data with label noise"),
  E("Feature noise versions of the benchmark data sets", "Noisy modified data - feature noise (Experiment 4)", "KEEL", 2,
    "the paper's benchmark sets with feature noise added by the authors (Experiment 4, p.8); levels as in the paper's figures; "
    "sizes not printed", "Sec. 4.5, p.8", (0, 8), "Experiment 4: imbalanced data with feature noise")],
 "MC-CCR": [
  E("Label noise versions of the multiclass benchmark data sets", "Noisy modified data - label noise (Sec. 4.4)", "KEEL", None,
    "the paper's multiclass benchmark sets with random label noise in the training data (a subset of training examples chosen "
    "uniformly at random gets a randomly chosen other label), levels {0.0, 0.05, 0.1, 0.15, 0.20, 0.25} (p.9); sizes not printed",
    "Sec. 4.4, p.9", (0, 9), "we decided to use random label noise imputation")],
 "MC-MBRC": [
  E("Label noise versions of the real data sets", "Noisy modified data - label noise (Experiment 3, Fig. 6)", "KEEL", None,
    "the paper's real data sets with label noise (labels randomly replaced), noise content {0, 5, 10, 15, 20, 25, 30}% "
    "(Sec. 5.3, Fig. 6); sizes not printed", "Sec. 5.3, p.10-11; Fig. 6", (0, 10),
    "We add noise to the dataset by randomly replacing the label categories")],
 "MC-NCLWO": [
  E("Feature noise versions of four data sets", "Noisy modified data - Gaussian feature noise (Fig. 13)", "KEEL", None,
    "four of the paper's data sets (incl. winequality-red and page-blocks) with Gaussian feature noise of 5% to 30% in steps of 5% "
    "(p.15, Fig. 13); sizes not printed", "p.15; Fig. 13", (0, 15),
    "by sequentially adding 5%, 10%, 15%, 20%, 25%, and 30% Gaussian feature noise to the datasets")],
 "SPE": [
  E("Missing-value versions of the benchmark data sets", "Modified data - missing values added (Sec. 5)", "UCI", 2,
    "the paper's data sets with values removed at random from all features in training and test data and replaced by 0 to "
    "simulate missing values (p.10); levels as in the paper; sizes not printed", "p.10", (0, 10),
    "To simulate the situation of missing values")],
}

def pdf_text(key, i, p):
    pm = json.load(open("out/pdf_map.json"))
    f = ([pm[key]["main"]] + list(pm[key].get("supp") or []))[i]
    t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), f, "-"], capture_output=True, text=True).stdout
    return re.sub(r"\s+", " ", re.sub(r"-\n", "", t))

def check_pdf():
    n = 0
    for k, lst in NEW.items():
        for e in lst:
            i, p = e["page"]
            assert e["quote"] in pdf_text(k, i, p), f"STOP: quote not on {k} file {i} p.{p}: {e['quote']}"
            n += 1
    print("ok: all", n, "evidence quotes found on the cited page")

def rcsv(f): return list(csv.DictReader(open(f, encoding="utf-8-sig")))
def wcsv(f, rows):
    with open(f, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

def apply():
    old_full = rcsv("out/full_datasets.csv"); old_ver = rcsv("out/verify_datasets.csv"); old_vd = rcsv("out/verified_datasets.csv")
    old_out = open("out/full_outcome_rows.csv", encoding="utf-8-sig").read()
    assert len(old_full) == len(old_ver) == len(old_vd)
    added = 0
    for k, lst in NEW.items():
        f = f"ai-draft/full/{k}.json"
        d = json.load(open(f, encoding="utf-8"))
        have = {x["name"] for x in d["datasets"]}
        for e in lst:
            if e["entry"]["name"] not in have: d["datasets"].append(e["entry"]); added += 1
        json.dump(d, open(f, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    r = subprocess.run([sys.executable, "build/full_extraction.py"], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr[-2000:]
    assert open("out/full_outcome_rows.csv", encoding="utf-8-sig").read() == old_out, "STOP: outcome rows changed"
    new_full = rcsv("out/full_datasets.csv")
    newkeys = {(k, e["entry"]["name"]) for k, lst in NEW.items() for e in lst}
    vrows, vdrows, j = [], [], 0
    for x in new_full:
        pk = x["paper"]
        if (pk, x["name"]) in newkeys and not (j < len(old_full) and old_full[j]["paper"] == pk and old_full[j]["name"] == x["name"]):
            vrows.append(dict(paper=pk, name=x["name"], ref=x["ref"], status="ok (evidence quote, add_noise_entries.py)",
                              detail="quote asserted on the cited page; no size printed for the noisy versions"))
            vdrows.append({**x, "value_status": "verified against paper",
                           "verification": "PDF text layer: evidence quote found on the cited page (build/add_noise_entries.py --check-pdf)",
                           "verified_page": "", "verified_by": WHO})
            continue
        o = old_full[j]; assert (o["paper"], o["name"]) == (pk, x["name"]), (j, o["paper"], o["name"], pk, x["name"])
        assert o == x, f"STOP: unexpected change in row {j}: {pk} {x['name']}"
        vrows.append(old_ver[j]); vdrows.append(old_vd[j]); j += 1
    assert j == len(old_full)
    wcsv("out/verify_datasets.csv", vrows); wcsv("out/verified_datasets.csv", vdrows)
    print("added", added, "entries; full_datasets", len(old_full), "->", len(new_full))

if __name__ == "__main__":
    if "--check-pdf" in sys.argv: check_pdf()
    elif "--apply" in sys.argv: apply()
    else: print(__doc__)
