"""modified_operations.py  Analysis A (19 ต.ค. 2026): จำแนกการดัดแปลงข้อมูลของ 331 entry ที่ category = modified

อ่าน   out/dataset_records.csv (ไม่แก้; category เดิมคงไว้เป็นระดับบน)
       PDF ของ paper (ผ่าน out/pdf_map.json) เพื่อตรวจข้อความ "เหตุผลที่ดัดแปลง" ที่อ้างใน PURPOSE ว่ามีอยู่จริง
เขียน  out/modified_operations_audit.csv     1 แถวต่อ entry (331)
       out/modified_operations_summary.json  ตัวนับ (หน่วย entry และ paper แยกกัน)

ที่มาของป้าย: บันทึกการได้มา/การดัดแปลง (preprocessing_note) ที่ตรวจกับ PDF แล้ว 18 ต.ค. + กติกาต่อ paper ข้างล่าง (Claude อ่าน, 19 ต.ค.)
ป้ายการดำเนินการ (operation) ซ้อนกันได้ต่อ entry:
  CS  class selection / task conversion   แปลง multiclass เป็น binary, เลือก/รวม/ตัดคลาส, ตั้ง threshold บน target
  US  sample reduction / undersampling    ลดจำนวนตัวอย่างของคลาสใดคลาสหนึ่ง
  FM  feature modification                ตัด/เลือก/แปลง feature, ทำ feature extraction, ใส่ noise ใน attribute
  SF  sample filtering / subset selection ตัดแถวที่ค่าหาย, ใช้ subset ของข้อมูล (ไม่เจาะจงคลาส)
  IM  imbalance manipulation              ตั้งใจเปลี่ยน IR (ต้องมีข้อความบอกว่าทำเพื่อเปลี่ยน/สร้างความไม่สมดุล)
  OT  other documented modification        เช่น ใส่ label noise, สร้างป้ายจากข้อมูลดิบเอง
  IS  insufficiently specified             รู้ว่าดัดแปลงแต่ระบุการดำเนินการไม่ได้
ops_conditional = ข้อความระดับ paper ที่อาจใช้กับ entry นี้ แต่ระบุรายชุดไม่ได้ (ไม่นับในตัวนับหลัก)
"""
import csv, json, os, re, subprocess, sys, unicodedata
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
OPS = ["CS", "US", "FM", "SF", "IM", "OT", "IS"]
OPNAME = {"CS": "class selection / task conversion", "US": "sample reduction / undersampling", "FM": "feature modification",
          "SF": "sample filtering / subset selection", "IM": "imbalance manipulation", "OT": "other documented modification",
          "IS": "insufficiently specified modification"}
EX, IN, AM = "explicitly reported", "supported by indirect evidence", "ambiguous"
# กติกาต่อ paper: (เงื่อนไขบน name หรือ note เป็น regex, '*' = ทุก entry, ops, ops_conditional, class_op_kind, confidence, เหตุผล)
R = {
 "A-SUWO": [("*", "CS", "", "one-vs-rest", EX, "minority class named in Table 3.1, rest merged; conversion stated p.35")],
 "ADASYN": [("abalone|Abalone", "CS FM", "", "class subset (two classes kept)", EX, "class 18 vs class 9; discrete feature 'sex' removed (p.4)"),
            ("*", "CS", "", "one-vs-rest", EX, "one class chosen as minority, rest collapsed (p.3-4)")],
 "AMDO": [("missing", "SF", "", "", EX, "samples with missing values removed (p.6)"),
          ("*", "CS", "", "class subset (small classes dropped)", EX, "classes with fewer than 10 samples eliminated (p.6)")],
 "Borderline-SMOTE": [("*", "CS", "", "one-vs-rest", EX, "class 4 as minority, rest merged (p.6, Table 2)")],
 "CISO": [("*", "CS", "", "one-vs-rest", EX, "smallest class vs rest (rule p.15, Table 1 p.16)")],
 "COG-OS": [("breast-w", "SF US IM", "", "", EX, "16 instances with missing data deleted; class 1 randomly sampled for imbalance experiments (Tables 2-3)"),
            ("randomly sampled with ratio", "US IM", "", "", EX, "class 1 randomly sampled at a stated ratio for the imbalance experiments (Table 3)"),
            ("probe|r2l", "CS SF", "", "one-vs-rest", EX, "rare class vs the other four merged, from the KDD'99 10% sample (p.8, Table 8)"),
            ("*", "SF", "", "", EX, "10% sample; test instances with labels absent from training deleted (Table 8)")],
 "CTGAN / TVAE": [("*", "FM", "", "", EX, "MNIST images resized/binarised and flattened into tabular columns (main p.7)")],
 "Cluster-SMOTE": [("*", "OT CS", "", "label construction", EX, "data set built and labelled by the authors from network traffic; attack types collapsed into 2 classes (p.2)")],
 "ClusterCentroids": [("*", "SF", "", "", EX, "incomplete records removed (30,162 after cleaning) (p.8)")],
 "DGOT": [("*", "CS", "", "threshold on target", EX, "#T gives a threshold on the target as the minority definition (Table I)")],
 "DLexiBoost": [("*", "SF FM", "", "", EX, "random ~2% of synsets per subtree sampled from ImageNet; Inception-v3 features (main Sec 4.5)")],
 "DSRBF / Static-SMOTE": [("CYT", "CS", "", "class subset (two classes kept)", EX, "only CYT and POX patterns used (p.7)"),
                          ("*", "CS", "", "one-vs-rest", EX, "ME2 vs remaining patterns (p.7)")],
 "EasyEnsemble / BalanceCascade": [("*", "CS", "", "one-vs-rest", EX, "target class as minority, others as majority (Table II caption)")],
 "G-SMOTE": [("*", "US IM", "", "", EX, "minority randomly undersampled so the IR is multiplied by 2 or 3 (p.18); purpose stated p.3")],
 "GAMO": [("MNIST|Fashion", "US IM", "", "", EX, "imbalanced variant made by random selection of a disparate number per class (Sec 4.1)"),
          ("CIFAR|SVHN", "US", "IM", "", IN, "classes subsampled in label order (Sec 4.2); imbalance creation implied by the order, not quoted in the note"),
          ("*", "CS FM", "", "class subset (classes selected)", EX, "authors selected a subset of classes; images rescaled/cropped (Sec 4.3-4.4)")],
 "GMMSampling": [("*", "CS", "", "class grouping (minority/majority sets)", EX, "minority/majority grouping taken from SOUP (p.11, Table 1)")],
 "GOIO": [("*", "CS", "", "threshold on target or class choice", EX, "#T gives the authors' target class/threshold (Table I)")],
 "HDE": [("*", "US IM", "", "", EX, "minority instances randomly removed to create highly imbalanced sets (Sec 4.1, p.9)")],
 "INOS": [("originally", "CS US", "IM", "one-vs-rest", EX, "one class positive vs rest (p.8); number of positive training samples set by the authors"),
          ("*", "US", "CS IM", "", AM, "positive training counts set by the authors; class count and positive class not stated")],
 "LS": [("Intrusion", "CS SF", "", "class subset (two classes kept)", EX, "subset of KDD'99, u2r vs normal (p.7-8)"),
        ("*", "CS", "", "class grouping (vowels vs consonants)", EX, "each vowel vs consonants (p.8)")],
 "MWMOTE": [("majority = All other", "CS", "", "one-vs-rest", EX, "Table 5 minority vs all other classes (p.13)"),
            ("*", "CS", "", "class subset (named classes kept)", EX, "Table 5 names both minority and majority classes (p.13)")],
 "NBU": [("*", "CS US IM", "", "one-vs-rest", EX, "class chosen as minority one-vs-all, then undersampled to a higher imbalance (p.18)")],
 "OSS": [("discarded", "CS US", "", "one-vs-rest", EX, "class vs others; examples discarded to equalise fold proportions (p.5)"),
         ("*", "CS", "", "one-vs-rest", EX, "class vs others (p.5)")],
 "OVO-SMOTE": [("*", "SF", "", "", EX, "instances with missing values removed (Sec 4.1, p.5)")],
 "RACOG / wRACOG": [("Modified yeast", "CS", "", "one-vs-rest", EX, "minority class named in Table 2"),
                    ("binned", "CS FM", "", "one-vs-rest (class not stated)", EX, "one class vs rest (p.4), class not stated; real-valued attributes equal-width binned"),
                    ("size printed as 5000", "CS SF", "", "one-vs-rest (class not stated)", IN, "one class vs rest (p.4); size 5000 implies a subset, selection not described"),
                    ("*", "CS", "", "one-vs-rest (class not stated)", EX, "one class vs rest (p.4), class not stated")],
 "RAMOBoost": [("*", "CS", "", "one-vs-rest or class subset", EX, "class mapping listed in Table II")],
 "ROS (Buda)": [("MNIST", "SF US IM", "", "", EX, "classes subsampled to <=5000, then artificially imbalanced (Sec 3.3.1)"),
                ("ILSVRC", "SF US IM", "", "", EX, "majority classes reduced 1200->1000; step-imbalanced subsets (Sec 3.3.3)"),
                ("*", "US IM", "", "", EX, "training set artificially imbalanced (Sec 3.3.2)")],
 "RSMOTE": [("*", "US IM", "", "", EX, "positive class randomly undersampled to obtain higher IR (p.12)")],
 "RUSBoost": [("SOLARFLARE", "CS", "", "class or threshold (not stated)", AM, "general statement: one class positive or threshold on a continuous target (p.5); which one not stated"),
              ("*", "CS", "", "one-vs-rest (class inferred from suffix)", IN, "general statement p.5; positive class inferred from the name suffix, not stated")],
 "SMOM": [("dropped classes|chose a subset", "CS", "", "class subset (classes dropped)", IN, "class labels absent from Table 1 imply dropped classes"),
          ("*", "CS", "", "class merging", EX, "Table 1 'Description of classes' shows merged original classes")],
 "SMOTE": [("continuous features", "FM", "", "", EX, "only continuous features used for SMOTE (p.13)"),
           ("generated by authors", "OT", "", "label construction", EX, "built by the authors from simulation output, labels assigned by the authors (p.14)"),
           ("two classes", "CS", "", "class subset (two classes kept)", EX, "two of seven classes extracted (p.13-14)"),
           ("*", "CS", "", "one-vs-rest", EX, "smallest class vs rest (p.13)")],
 "SMOTE-ENN / SMOTE-Tomek": [("*", "CS", "", "one-vs-rest", EX, "class vs remainder (Table 3, p.5)")],
 "SMOTE-IPF": [("Class noise", "OT", "CS", "label noise injection", EX, "pairwise class noise at 20%/40% (Sec 4.2); base sets binarised"),
               ("*", "FM", "CS", "", EX, "attribute noise at 20%/40% (Sec 4.2); base sets binarised")],
 "SMOTEBoost": [("KDDCup", "SF US", "CS", "", EX, "train+test merged, 69,980 connections sampled from the majority classes only (p.6)"),
                ("*", "CS", "", "one-vs-rest", EX, "smallest class vs rest (p.6)")],
 "SOUP": [("*", "CS", "", "class grouping (minority/majority sets)", IN, "paper says some data were modified by aggregating classes without naming them (p.7); Table 2 groups classes")],
 "SPE": [("*", "CS", "", "class subset (two classes kept)", EX, "two-class problem formed from KDDCUP-99 categories")],
 "SVDD-WSMOTE": [("^(Pageblock|Yeast)", "CS IM", "", "one-vs-rest or class pair", EX, "one-versus-others; Pageblock and Yeast class combinations used to obtain higher-IR sets (p.22)"),
                 ("*", "CS", "", "one-vs-rest", EX, "one-versus-others, smaller class as minority (p.22)")],
 "Safe-Level-SMOTE": [("*", "CS", "", "one-vs-rest", EX, "class 4 as minority, rest merged (p.6)")],
 "k-means SMOTE": [("*", "US IM", "CS", "", EX, "randomly undersampled to raise the IR by stated factors (p.14); multiclass bases binarised one-vs-rest, per-entry not identified")],
}
# เหตุผลที่ผู้เขียนให้ (ข้อความในไฟล์ PDF; ตรวจอัตโนมัติด้านล่าง) ระดับ paper
PURPOSE = {
 "ADASYN": ("since our interest here is to test the learning capabilities from two-class imbalanced problems", "two-class problems"),
 "G-SMOTE": ("In order to test the performance of the algorithm on more extreme cases of imbalance", "more extreme imbalance"),
 "HDE": ("To evaluate the proposed HD-Ensemble for extreme case, we manually created 14 highly imbalanced datasets", "extreme imbalance"),
 "k-means SMOTE": ("In order to generate additional datasets with even higher imbalance ratios", "higher imbalance"),
 "MWMOTE": ("We transform them to two-class problems because of our interest", "two-class problems"),
 "NBU": ("were undersampled to obtained higher class imbalance degrees", "higher imbalance"),
 "RAMOBoost": ("we modified those datasets following suggestions in literature to make them into two-class datasets", "two-class problems"),
 "ROS (Buda)": ("to make them artificially imbalanced", "imbalance study"),
 "RSMOTE": ("artificially imbalanced to obtain higher imbalanced ratios", "higher imbalance"),
 "RUSBoost": ("Since this paper considers only the binary classification problem, it was necessary to transform some of the data sets to have a binary class", "two-class problems"),
 "SMOTE": ("Since our system currently works for binary classes we extracted data for two classes from this dataset and ignored the rest", "two-class problems"),
 "SMOTE-IPF": ("Multi-class datasets are modiﬁed to obtain two-class imbalanced problems", "two-class problems"),
 "SMOTEBoost": ("in order to reduce the size of the data set", "data-set size"),
 "Safe-Level-SMOTE": ("because we only study the two-class imbalanced problem", "two-class problems"),
 "SVDD-WSMOTE": ("to simulate the scenarios with higher imbalance ratios", "higher imbalance"),
}
P2PDF = {"CTGAN / TVAE": "CTGAN", "DSRBF / Static-SMOTE": "DSRBF", "EasyEnsemble / BalanceCascade": "EasyEnsemble", "RACOG / wRACOG": "RACOG",
         "ROS (Buda)": "ROS-Buda", "SMOTE-ENN / SMOTE-Tomek": "SMOTE-ENN", "k-means SMOTE": "k-means-SMOTE"}
PM = json.load(open("out/pdf_map.json", encoding="utf-8"))
def nz(s): return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", s).replace("ﬁ", "fi")).lower()
def pdf_pages(k):
    pk = P2PDF.get(k, k); fl = ([PM[pk]["main"]] if PM.get(pk, {}).get("main") else []) + list(PM.get(pk, {}).get("supp", []))
    out = []
    for f in fl: out += subprocess.run(["pdftotext", f, "-"], capture_output=True, text=True).stdout.split("\f")
    return out
purpose_found = {}
for k, (q, theme) in PURPOSE.items():
    pages = [i for i, t in enumerate(pdf_pages(k), 1) if nz(q) in nz(t)]
    if not pages: sys.exit(f"STOP: purpose quote for {k} not found in PDF: {q}")
    purpose_found[k] = (q, theme, pages)
D = [r for r in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig")) if r["category"] == "modified"]
MISS = [("minority class not stated", r"which class not stated|minority class not stated|positive-class choice not stated|not explicitly stated|presumably the positive"),
        ("target IR not stated", r"target IR not stated"), ("affected data sets not named", r"without saying which datasets"),
        ("subset selection not described", r"subset selection not described"), ("original class count not stated", r"original class count (and positive-class choice )?not stated"),
        ("characteristics not printed", r"omitted from Table|not printed|counts not printed")]
rows = []
for d in D:
    rules = R.get(d["paper_key"])
    if not rules: sys.exit(f"STOP: no rule for paper {d['paper_key']}")
    text = d["name_as_reported"] + " || " + d["preprocessing_note"]
    rule = next(r for r in rules if r[0] == "*" or re.search(r[0], text))
    ops = rule[1].split(); cond = [o for o in rule[2].split() if o not in ops]
    pf = purpose_found.get(d["paper_key"])
    if pf and d["paper_key"] == "SVDD-WSMOTE" and "IM" not in ops: pf = None   # SVDD purpose applies to Pageblock/Yeast class combinations only
    ch = dict(class_structure="yes" if ("CS" in ops or rule[3] in ("label noise injection", "label construction")) else "no",
              sample_composition="yes" if (set(ops) & {"US", "SF", "IM"} or "subset" in rule[3] or "dropped" in rule[3]) else "no",
              feature_space="yes" if "FM" in ops else "no",
              imbalance_level="deliberately changed" if "IM" in ops else ("changed as a consequence" if set(ops) & {"CS", "US", "SF"} else "not changed by the reported operation"))
    rows.append(dict(record_id=d["record_id"], paper_key=d["paper_key"], paper_id=d["paper_id"], bibkey=d["bibkey"], year=d["year"],
                     name_as_reported=d["name_as_reported"], normalized_name=d["normalized_name"], category=d["category"], category_basis=d["category_basis"],
                     ops=";".join(o for o in OPS if o in ops), ops_conditional=";".join(cond), n_ops=len(ops), class_op_kind=rule[3],
                     changes_class_structure=ch["class_structure"], changes_sample_composition=ch["sample_composition"],
                     changes_feature_space=ch["feature_space"], changes_imbalance_level=ch["imbalance_level"],
                     changes_task="yes" if ch["class_structure"] == "yes" else "no",
                     what_changed=d["preprocessing_note"], evidence_ref=d["evidence_ref"],
                     purpose_stated_by_authors=(f'"{pf[0]}" (PDF p.{",".join(map(str, pf[2]))}; theme: {pf[1]})' if pf else "none found (extracted note + targeted PDF search)"),
                     missing_information="; ".join(n for n, p in MISS if re.search(p, d["preprocessing_note"], re.I)),
                     confidence=rule[4], classification_note=rule[5]))
with open("out/modified_operations_audit.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
# ---- สรุป ----
N, P = len(rows), sorted({r["paper_key"] for r in rows})
assert N == 331 and len({r["record_id"] for r in rows}) == N, "duplicate or missing rows"
tag_entries = {o: sum(o in r["ops"].split(";") for r in rows) for o in OPS}
tag_papers = {o: len({r["paper_key"] for r in rows if o in r["ops"].split(";")}) for o in OPS}
combo = Counter(r["ops"] for r in rows)
paper_purpose = {k: (k in purpose_found) for k in P}
S = dict(unit="dataset entry with category = modified (out/dataset_records.csv)", entries=N, papers=len(P),
         tag_entries=tag_entries, tag_entries_note="an entry can carry several tags; these counts sum to more than the number of entries",
         tag_papers=tag_papers, combinations=dict(combo.most_common()), combinations_note="mutually exclusive; sums to the number of entries",
         entries_by_number_of_ops=dict(Counter(r["n_ops"] for r in rows)),
         entries_multiple_ops=sum(r["n_ops"] > 1 for r in rows), papers_with_multiple_ops_entries=len({r["paper_key"] for r in rows if r["n_ops"] > 1}),
         entries_with_conditional_ops=sum(bool(r["ops_conditional"]) for r in rows),
         confidence=dict(Counter(r["confidence"] for r in rows)),
         changes_task_entries=sum(r["changes_task"] == "yes" for r in rows), changes_task_papers=len({r["paper_key"] for r in rows if r["changes_task"] == "yes"}),
         changes=dict(class_structure=sum(r["changes_class_structure"] == "yes" for r in rows), sample_composition=sum(r["changes_sample_composition"] == "yes" for r in rows),
                      feature_space=sum(r["changes_feature_space"] == "yes" for r in rows), imbalance=dict(Counter(r["changes_imbalance_level"] for r in rows))),
         class_op_kind=dict(Counter(r["class_op_kind"] for r in rows if "CS" in r["ops"].split(";"))),
         purpose=dict(papers_with_stated_purpose=sum(paper_purpose.values()), papers=len(P),
                      entries_with_stated_purpose=sum(not r["purpose_stated_by_authors"].startswith("none") for r in rows),
                      themes_by_paper=dict(Counter(v[1] for k, v in purpose_found.items() if k in P)),
                      papers_without=[k for k, v in paper_purpose.items() if not v]),
         missing_information=dict(Counter(m for r in rows for m in r["missing_information"].split("; ") if m)),
         entries_with_missing_information=sum(bool(r["missing_information"]) for r in rows),
         by_paper={k: dict(entries=sum(r["paper_key"] == k for r in rows), ops=dict(Counter(o for r in rows if r["paper_key"] == k for o in r["ops"].split(";"))),
                           purpose=k in purpose_found) for k in P},
         im_entries_by_paper=dict(Counter(r["paper_key"] for r in rows if "IM" in r["ops"].split(";"))))
json.dump(S, open("out/modified_operations_summary.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: S[k] for k in ("entries", "papers", "tag_entries", "tag_papers", "entries_multiple_ops", "papers_with_multiple_ops_entries", "confidence",
                                     "changes_task_entries", "changes_task_papers", "changes", "purpose", "entries_with_missing_information", "missing_information")}, ensure_ascii=False, indent=1))
print("combinations", S["combinations"]); print("class_op_kind", S["class_op_kind"]); print("IM by paper", S["im_entries_by_paper"])
