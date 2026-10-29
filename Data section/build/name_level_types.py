"""name_level_types.py  ชนิดของ dataset ระดับชื่อหลัง normalise (771 ชื่อ) + ความยากที่วัดได้ของแต่ละชื่อ
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
    rows.append(dict(
        normalized_name=name, name_type=ntype, entries=len(g),
        entries_by_category="; ".join(f"{c} {cats[c]}" for c in ORDER if cats.get(c)),
        n_papers=g.paper_key.nunique(), papers="; ".join(sorted(set(g.paper_key))),
        names_as_reported="; ".join(sorted(set(g.name_as_reported)))[:300],
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
out = dict(
    source="build/name_level_types.py; inputs out/dataset_records.csv, difficulty/verifiability_entries.csv, difficulty/difficulty_profile_final.csv",
    unit="normalized dataset name (R1 placeholders removed)", names=int(len(R)), entries=int(len(D)),
    precedence=ORDER, by_type=by_type, entry_level_by_category={c: int(ent[c]) for c in ORDER},
    names_single_type=int(len(R) - len(mixed)), names_mixed_type=int(len(mixed)),
    difficulty_order=DIFF, by_difficulty={k: int((R.difficulty == k).sum()) for k in DIFF}, type_by_difficulty=cross,
    measured_names=int(R.difficulty.isin(DIFF[:8]).sum()),
    rules=dict(type="ชื่อหนึ่งได้ชนิดเดียว: ถ้ามี entry ใดเป็นชนิดที่มาก่อนตามลำดับ precedence ใช้ชนิดนั้น (เคยดัดแปลง = modified)",
               difficulty="โปรไฟล์ของ task สองคลาสที่วัดแล้ว (ธงจาก difficulty/profile_final.py) · หลาย task ต่างโปรไฟล์ = varies · มีแต่ไฟล์หลายคลาส = multiclass · ไม่มีไฟล์ที่ตรวจได้ = not measured"))
assert sum(by_type.values()) == 771 and all(sum(v.values()) == by_type[c] for c, v in cross.items())
json.dump(out, open("out/name_level_types.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({k: out[k] for k in ("by_type", "by_difficulty", "measured_names", "names_mixed_type")}, indent=1))
for c in ORDER: print(c, {k: v for k, v in cross[c].items() if v})
