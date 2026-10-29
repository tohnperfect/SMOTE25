"""name_level_types.py  ชนิดและแหล่งของ dataset ระดับชื่อหลัง normalise (771 ชื่อ) + ความยากที่วัดได้ของแต่ละชื่อ
(29 ต.ค. 2026, Claude; Toon สั่งให้แท็บภาพรวมของ Atlas ใช้จำนวนที่ normalise แล้วแทนจำนวน entry)

อ่าน  out/dataset_records.csv                    (1 แถว = 1 entry; ตัด placeholder ตามกติกา R1 -> 1,653 entry, 771 ชื่อ)
      difficulty/verifiability_entries.csv       (สถานะตรวจได้ของแต่ละ entry + ไฟล์ที่จับคู่)
      difficulty/difficulty_profile_final.csv    (โปรไฟล์ความยากของ task สองคลาส: ธงตามเกณฑ์ที่มีอ้างอิง)
เขียน out/name_level_types.csv  (771 แถว) และ out/name_level_types.json (สรุป + ตารางไขว้ ชนิด x ความยาก)

กติกาชนิดระดับชื่อ (Claude ตัดสิน 29 ต.ค., Toon ยืนยันในแชตว่า "original + modified ก็คือ modified"):
  ชื่อหนึ่งได้ชนิดเดียวตามลำดับ modified > synthetic > repository-defined > original > not stated
  คือถ้ามี entry ใดของชื่อนั้นเคยถูกดัดแปลง ชื่อนั้นนับเป็น modified (ไม่ได้ตั้ง threshold)
กติกาความยากระดับชื่อ (ไม่ได้ตั้ง threshold ใหม่ ใช้ธงที่ profile_final.py คำนวณไว้):
  1. entry ที่จับคู่กับ task สองคลาสที่วัดแล้วได้ (ไฟล์สองคลาส: verif V-binary_file / V-keel_name_only / V-name_only_other
     จับด้วย file+source; binarise: V-binarized_rule_unique จับด้วย file+source+n_min = n_minority ที่พิมพ์)
     -> ชื่อได้โปรไฟล์ของ task นั้น ถ้าจับได้หลาย task และโปรไฟล์ต่างกัน = "varies"
  2. ไม่มี task สองคลาส แต่ entry ตรวจได้กับไฟล์หลายคลาส (V-multiclass_asis, V?-binarized_rule_ambiguous หรือชื่อตรงกับ
     ไฟล์หลายคลาสโดยไม่รู้คลาส minority) -> "multiclass" (วัดได้แค่ราย class แบบ one-vs-rest ไม่มีโปรไฟล์เดียว)
  3. ที่เหลือ -> "not measured" พร้อมเหตุผล (สถานะ U-* ของ entry)
"""
import json, os, re
from collections import Counter
import pandas as pd

# ---- แหล่งข้อมูล (29 ต.ค. บ่าย, Toon สั่ง "normalize แหล่งข้อมูลด้วย") ----
# จัด source_as_reported (51 ค่าตามที่ paper เขียน) เป็น 8 กลุ่ม ด้วยการจับข้อความตรงตัว ไม่มี threshold
SRC = ["KEEL", "UCI", "group-level", "other repository", "other paper/author", "private", "synthetic", "not stated"]
_GROUP = ("UCI/KEEL", "UCI or KEEL", "UCI or ELENA")                 # paper บอกแค่ระดับกลุ่ม ไม่ระบุรายชุด
_UCI = ("UCI KDD Archive", "kdd.ics.uci.edu")                        # คลัง KDD ของ UCI
_REF = ("reported in", "refs [", "from ref", "biological datasets", "hyperspectral image source", "cited as ref", "provided by",
        "originally considered in", "from refs", "generated from Can", "USF Intelligent", "ref [1]", "ref [23]")
_REPO = ("Kaggle", "LibSVM", "imbalanced-learn", "UCR")
def src_group(s):
    if s in ("KEEL", "UCI", "private", "synthetic"): return s
    if s == "not stated in paper": return "not stated"
    if s in _REPO: return "other repository"
    assert s.startswith("other: "), f"STOP: unknown source string {s!r}"
    if any(k in s for k in _GROUP): return "group-level"
    if any(k in s for k in _UCI): return "UCI"
    if any(k in s for k in _REF): return "other paper/author"
    return "other repository"   # คลังหรือ benchmark ที่มีชื่อ เช่น HDDT, PROMISE, ELENA, MNIST, ImageNet, NASA MDP
# ---- แหล่งที่ต่างกัน (29 ต.ค. บ่าย 3, Toon: "KEEL นับเป็น 1"): 1 แหล่ง = 1 คลัง/benchmark/งานที่อ้าง/ข้อมูลเฉพาะของ 1 paper ----
# ชื่อที่เขียนต่างกันแต่เป็นแหล่งเดียวกันรวมเป็นหนึ่ง (MNIST 3 แบบ, ImageNet 2 รุ่น, ref [6] ของ LS 2 แบบ) · ไม่นับ synthetic, group-level, not stated
_ID = [("UCI KDD Archive", "UCI"), ("kdd.ics.uci.edu", "UCI"), ("MNIST", "MNIST"), ("ImageNet", "ImageNet"), ("CIFAR-10", "CIFAR-10"),
       ("HDDT collection", "HDDT collection (Cieslak et al.)"), ("ELENA project", "ELENA"), ("PROMISE", "PROMISE"),
       ("NASA Metrics", "NASA Metrics Data Program"), ("TREC", "TREC"), ("WebACE", "WebACE"), ("Crowd Analytix", "Crowd Analytix"),
       ("IBM Analytics", "IBM Analytics"), ("mafalda", "GitHub sisinflab-swot/mafalda"), ("Compustat", "Compustat"),
       ("KDD Cup 2008", "KDD Cup 2008"), ("KDD'99 Challenge", "KDD Cup 1999"), ("multi-imbalance library", "multi-imbalance library"),
       ("Maldonado", "microarray (Maldonado et al.)"), ("ordinal regression benchmark", "ordinal regression benchmark (SMOM refs [13,25])"),
       ("Akritidis", "software defect (Akritidis & Bozanis)"), ("Radivojac", "biological (Radivojac et al.)"),
       ("hyperspectral image source [53]", "hyperspectral source [53] (DLexiBoost)"), ("hyperspectral image source [54]", "hyperspectral source [54] (DLexiBoost)"),
       ("hyperspectral image source [55]", "hyperspectral source [55] (DLexiBoost)"), ("KRNN", "Zhang et al. (KRNN)"),
       ("provided by Dr. N. Chawla", "ให้โดย N. Chawla"), ("Kubat", "Kubat et al."), ("provided by authors of [45]", "ผู้เขียน ref [45] (SMOTE-IPF)"),
       ("S. aureus", "predictive microbiology refs [57,58]"), ("originally considered in [6]", "ref [6] (LS)"),
       ("Can ExodusII", "Can ExodusII (AVATAR)"), ("USF Intelligent", "USF Intelligent Systems Lab (Woods et al.)"),
       ("ref [1] (Chawla", "SMOTE paper (Chawla et al. 2002)"), ("ref [23] (Provost", "Provost et al. 1998")]
def src_id(raw, paper):
    g = src_group(raw)
    if g in ("synthetic", "group-level", "not stated"): return None
    if g == "private": return f"private: {paper}"
    if raw in ("KEEL", "UCI") + _REPO: return raw
    hit = [v for k, v in _ID if k in raw]
    assert len(hit) == 1, f"STOP: source string has no unique identity: {raw!r}"
    return hit[0]
SPEC = ["KEEL", "UCI", "other repository", "other paper/author", "private", "synthetic"]   # ระบุแหล่งรายชุด

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
ORDER = ["modified", "synthetic", "repository-defined", "original", "not stated"]
DIFF = ["none", "small_sample", "outlier_flag", "small_sample + outlier_flag", "small_disjuncts + outlier_flag",
        "small_disjuncts + small_sample", "small_disjuncts + small_sample + outlier_flag", "varies", "multiclass", "not measured"]
BIN_FILE = {"V-binary_file", "V-keel_name_only", "V-name_only_other"}
MULTI = {"V-multiclass_asis", "V?-binarized_rule_ambiguous"}

D = pd.read_csv("out/dataset_records.csv", dtype=str).fillna("")
D = D[D.is_placeholder != "yes"]
V = pd.read_csv("difficulty/verifiability_entries.csv", dtype=str).fillna("")
P = pd.read_csv("difficulty/difficulty_profile_final.csv", dtype=str).fillna("")
assert len(D) == 1653 and D.normalized_name.nunique() == 771, "STOP: dataset_records.csv changed (expected 1,653 entries, 771 names)"
M = D.merge(V[["record_id", "verif", "file", "file_src"]], on="record_id", how="left")
assert M.verif.notna().all(), "STOP: a record has no verifiability row"
M["src"] = M.source_as_reported.map(src_group)
M["sid"] = [src_id(r, p) for r, p in zip(M.source_as_reported, M.paper_key)]

PB = {(r.file, r.source): r for r in P[P.origin == "binary file"].itertuples()}
OVR = {(r.file, r.source) for r in P[P.origin.str.startswith("one-vs")].itertuples()}
PZ = {}
for r in P[P.origin.str.startswith("binarised")].itertuples(): PZ.setdefault((r.file, r.source), []).append(r)

def task_of(e):
    """measured two-class task for one entry, or None"""
    if e.verif in BIN_FILE: return PB.get((e.file, e.file_src))
    if e.verif == "V-binarized_rule_unique":
        m = re.search(r"\d+", e.n_minority)
        hit = [r for r in PZ.get((e.file, e.file_src), []) if m and r.n_min == m.group()]
        return hit[0] if len(hit) == 1 else None
    return None

rows, unmapped_binarised = [], []
for name, g in M.groupby("normalized_name", sort=True):
    cats = Counter(g.category)
    ntype = next(c for c in ORDER if cats.get(c))
    tasks = {}
    multi = False
    for e in g.itertuples():
        t = task_of(e)
        if t is not None: tasks[(t.file, t.source, t.minority_label)] = t
        elif e.verif in MULTI: multi = True
        elif e.verif in BIN_FILE:   # name matched a multiclass file without a known minority class -> measured only one-vs-rest
            assert (e.file, e.file_src) in OVR, f"STOP: {e.record_id} matched {e.file} but no measured task"
            multi = True
        if e.verif == "V-binarized_rule_unique" and t is None: unmapped_binarised.append(e.record_id)
    profs = sorted({t.profile for t in tasks.values()})
    if profs: diff = profs[0] if len(profs) == 1 else "varies"
    elif multi: diff = "multiclass"
    else: diff = "not measured"
    reason = "; ".join(f"{k} {v}" for k, v in Counter(x for x in g.verif if x.startswith("U-")).most_common()) if diff == "not measured" else ""
    sc = Counter(g.src); spec = [x for x in SPEC if sc.get(x)]
    # แหล่งระดับชื่อ: แหล่งที่ระบุรายชุดถ้ามีแค่แหล่งเดียว · หลายแหล่ง = "multiple" · ไม่มีแหล่งรายชุด -> ระดับกลุ่ม หรือ not stated
    nsrc = spec[0] if len(spec) == 1 else "multiple" if spec else "group-level" if sc.get("group-level") else "not stated"
    rows.append(dict(
        normalized_name=name, name_type=ntype, entries=len(g),
        entries_by_category="; ".join(f"{c} {cats[c]}" for c in ORDER if cats.get(c)),
        n_papers=g.paper_key.nunique(), papers="; ".join(sorted(set(g.paper_key))),
        names_as_reported="; ".join(sorted(set(g.name_as_reported)))[:300],
        source=nsrc, source_combo=" + ".join(spec) if len(spec) > 1 else "",
        entries_by_source="; ".join(f"{x} {sc[x]}" for x in SRC if sc.get(x)),
        source_ids="; ".join(sorted({x for x in g.sid if x})),
        difficulty=diff,
        measured_tasks="; ".join(f"{t.file} [{t.source}] minority={t.minority_label.strip()} N={t.N} n_min={t.n_min} IR={t.IR} noise={t.noise_index} profile={t.profile}"
                                 for t in tasks.values()),
        verif_statuses="; ".join(f"{k} {v}" for k, v in Counter(g.verif).most_common()),
        not_measured_reason=reason, record_ids="; ".join(g.record_id)))
R = pd.DataFrame(rows)
assert len(R) == 771 and set(R.difficulty) <= set(DIFF)
assert not unmapped_binarised, f"STOP: binarised entries without a measured task: {unmapped_binarised}"
R.to_csv("out/name_level_types.csv", index=False)

ent = Counter(D.category)
by_type = {c: int((R.name_type == c).sum()) for c in ORDER}
cross = {c: {k: int(((R.name_type == c) & (R.difficulty == k)).sum()) for k in DIFF} for c in ORDER}
mixed = R[R.entries_by_category.str.contains(";")]
SRCN = SRC[:-1] + ["multiple", "not stated"]
assert set(R.source) <= set(SRCN)
src_cnt = {x: int((R.source == x).sum()) for x in SRCN}
src_x_type = {x: {c: int(((R.source == x) & (R.name_type == c)).sum()) for c in ORDER} for x in SRCN}
src_x_diff = {x: {k: int(((R.source == x) & (R.difficulty == k)).sum()) for k in DIFF} for x in SRCN}
out = dict(
    source="build/name_level_types.py; inputs out/dataset_records.csv, difficulty/verifiability_entries.csv, difficulty/difficulty_profile_final.csv",
    unit="normalized dataset name (R1 placeholders removed)", names=int(len(R)), entries=int(len(D)),
    precedence=ORDER, by_type=by_type, entry_level_by_category={c: int(ent[c]) for c in ORDER},
    names_single_type=int(len(R) - len(mixed)), names_mixed_type=int(len(mixed)),
    difficulty_order=DIFF, by_difficulty={k: int((R.difficulty == k).sum()) for k in DIFF}, type_by_difficulty=cross,
    source_order=SRCN, by_source=src_cnt, source_by_type=src_x_type, source_by_difficulty=src_x_diff,
    multiple_source_combos=dict(Counter(R.source_combo[R.source == "multiple"]).most_common()),
    entry_level_by_source={x: int((M.src == x).sum()) for x in SRC},
    source_map={raw: src_group(raw) for raw in sorted(set(M.source_as_reported))},
    measured_names=int(R.difficulty.isin(DIFF[:8]).sum()),
    rules=dict(source="แหล่งตามที่ paper เขียน จัดเป็น 8 กลุ่มด้วยการจับข้อความ (source_map) · ระดับชื่อ: ถ้า paper ที่ระบุแหล่งรายชุดระบุตรงกันแหล่งเดียว ใช้แหล่งนั้น · ระบุต่างกัน = multiple · ไม่มี paper ระบุรายชุด แต่มีระดับกลุ่ม (เช่น UCI หรือ KEEL) = group-level · ไม่มีเลย = not stated",
               type="ชื่อหนึ่งได้ชนิดเดียว: ถ้ามี entry ใดเป็นชนิดที่มาก่อนตามลำดับ precedence ใช้ชนิดนั้น (เคยดัดแปลง = modified)",
               difficulty="โปรไฟล์ของ task สองคลาสที่วัดแล้ว (ธงจาก difficulty/profile_final.py) · หลาย task ต่างโปรไฟล์ = varies · มีแต่ไฟล์หลายคลาส = multiclass · ไม่มีไฟล์ที่ตรวจได้ = not measured"))
assert sum(src_cnt.values()) == 771 and sum(out["entry_level_by_source"].values()) == 1653
assert sum(by_type.values()) == 771 and all(sum(v.values()) == by_type[c] for c, v in cross.items())
# แหล่งที่ต่างกัน: 1 แถวต่อแหล่ง
S = M[M.sid.notna()]
SI = pd.DataFrame([dict(source=k, group=src_group(g.source_as_reported.iloc[0]), names=g.normalized_name.nunique(), entries=len(g),
                        papers=g.paper_key.nunique(), paper_list="; ".join(sorted(set(g.paper_key))),
                        as_reported=" | ".join(sorted(set(g.source_as_reported)))) for k, g in S.groupby("sid")])
SI = SI.sort_values(["names", "entries", "source"], ascending=[False, False, True])
SI.to_csv("out/name_level_sources.csv", index=False)
pp = M.groupby("paper_key").sid.apply(lambda x: len({v for v in x if v}))
dist = Counter(min(int(v), 4) for v in pp)
out["distinct_sources"] = dict(
    n=int(len(SI)), by_group={k: int((SI.group == k).sum()) for k in SPEC if k != "synthetic"},
    named_public=int(SI.group.isin(["KEEL", "UCI", "other repository"]).sum()),
    rows=SI[["source", "group", "names", "entries", "papers", "paper_list", "as_reported"]].to_dict("records"),
    papers=int(len(pp)), sources_per_paper={("4+" if k == 4 else str(k)): int(v) for k, v in sorted(dist.items())},
    names_with_a_source=int(R.source_ids.ne("").sum()),
    rule="1 แหล่ง = 1 คลังหรือ benchmark, 1 งานหรือผู้ให้ข้อมูลที่อ้าง, หรือข้อมูลเฉพาะของ 1 paper · ชื่อที่เขียนต่างกันแต่เป็นแหล่งเดียวกันรวมกัน (ตาราง _ID ใน build/name_level_types.py) · ไม่นับ synthetic, ระบุแค่ระดับกลุ่ม และไม่ระบุ",
    source="out/name_level_sources.csv")
assert SI.entries.sum() == len(S) and pp.index.nunique() == M.paper_key.nunique()
json.dump(out, open("out/name_level_types.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ("by_type", "by_difficulty", "measured_names", "names_mixed_type")}, indent=1))
for c in ORDER: print(c, {k: v for k, v in cross[c].items() if v})
print("distinct", out["distinct_sources"]["n"], out["distinct_sources"]["by_group"], out["distinct_sources"]["sources_per_paper"], out["distinct_sources"]["names_with_a_source"])
print(SI.head(12)[["source","names","entries","papers"]].to_string())
print("source", src_cnt, "\nentry", out["entry_level_by_source"], "\ncombos", out["multiple_source_combos"])
for x in SRCN: print(x, {k: v for k, v in src_x_type[x].items() if v})
for k, v in out["source_map"].items():
    if v in ("other repository", "other paper/author", "group-level") or k.startswith("other: UCI"): print("  ", v, "<-", k[:90])
