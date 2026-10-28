"""landscape_candidates.py  (19 ต.ค. 2026) ข้อมูลเสริมของแท็บ Landscape ใน Atlas

ไม่ได้วิเคราะห์ใหม่: ใช้ค่า verified ใน out/dataset_records.csv และผล A (modified_operations_audit.csv),
not_stated_audit.csv, difficulty_evidence.json, benchmark_concentration.json, reconcile_counts.json
คำนวณใหม่เฉพาะสิ่งที่ยังไม่มีในไฟล์ใด:
  1. dataset และ family ต่อชื่อ: กฎ T1 ของ Toon (28 ต.ค. 2026) ผ่าน build/families.py (ต้นทาง out/dataset_families.csv)
     dataset = ชื่อที่ต่างกันแค่เครื่องหมาย, family = ชุดหลักของ split; ธงมาจาก build/family_rule.py (ข้อมูลเท่านั้น ไม่แก้)
  2. ตารางผู้สมัคร benchmark ตามเกณฑ์ที่เขียนไว้ใน CRITERIA (เกณฑ์ตัวเลขทุกตัวมาจาก Analysis C)
เขียน  out/landscape_families.csv, out/benchmark_candidates.csv, out/benchmark_candidates.json
"""
import csv, json, os, re, statistics as st
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
R = [r for r in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig")) if r["is_placeholder"] == "no"]
C = json.load(open("out/benchmark_concentration.json", encoding="utf-8"))
R3 = json.load(open("out/reconcile_counts.json", encoding="utf-8"))["name_frequencies"]

import sys; sys.path.insert(0, os.path.join(HERE, "build"))
import families as T1
def fam(n): return T1.family_of(n)
def dkey(n): return T1.dataset_key(n)
def num(x):  # กติกาเดียวกับ C และ Atlas: เฉพาะตัวเลขเดี่ยว
    m = re.fullmatch(r"\d[\d,]*(\.\d+)?", (x or "").strip()); return float(m.group(0).replace(",", "")) if m else None
def g(x): return f"{x:g}"

# byname is keyed by DATASET (rule 1); the row label is the most used spelling (T1.display)
byname, byfam, famnames, ent, rawnames = defaultdict(set), defaultdict(set), defaultdict(set), defaultdict(list), defaultdict(set)
for r in R:
    n = r["normalized_name"]; k = dkey(n)
    byname[k].add(r["paper_key"]); byfam[fam(n)].add(r["paper_key"]); famnames[fam(n)].add(k); ent[k].append(r); rawnames[n].add(r["paper_key"])
# guard: ต้องได้ตัวเลขเดียวกับ C
assert len(byfam) == C["by_family"]["names"] and sum(map(len, byfam.values())) == C["by_family"]["uses"], "T1 family counts differ from Analysis C"
assert len(byname) == C["by_dataset"]["names"]

# ---- 1. families (T1) ----
FR = list(csv.DictReader(open("out/dataset_families.csv", encoding="utf-8")))
ff = defaultdict(list)
for x in FR:
    if x["flag"] in ("feature_mismatch", "stem_family"):
        ff[x["family"]].append(f"{x['normalized_name']}: {x['flag']}")
ff = {f: sorted(set(v)) for f, v in ff.items()}
with open("out/landscape_families.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.writer(fh, lineterminator="\n"); w.writerow(["normalized_name", "dataset_key", "family", "name_papers", "dataset_papers", "name_entries", "family_papers", "family_datasets", "family_flags"])
    for n in sorted(rawnames):
        k, f = dkey(n), fam(n)
        w.writerow([n, k, f, len(rawnames[n]), len(byname[k]), sum(r["normalized_name"] == n for r in ent[k]), len(byfam[f]), len(famnames[f]), "; ".join(ff.get(f, []))])

# ---- 2. candidates ----
GIVEN = [dkey(n) for n in ["ecoli", "yeast", "glass", "pima", "vehicle", "haberman", "balance", "wine", "satimage", "page-blocks", "shuttle"]]
FREQ_MIN = 10; POOL_MIN = 3; BIG_N = 10000; BIG_F = 100   # 10 / 10,000 / 100 = เกณฑ์ใน Analysis C; 3 = ขอบล่างของ bucket "3-4" ใน C
CRITERIA = dict(
    frequent=f"dataset papers >= {FREQ_MIN} (datasets by rule T1-1: spellings that differ only by punctuation are one dataset; the 'datasets used by 10+ papers' set of Analysis C)",
    diversity=(f"dataset papers >= {POOL_MIN} and < {FREQ_MIN}, and every single-number value printed for it is >= {BIG_N:,} instances "
               f"or every one is >= {BIG_F} features, printed in >= 2 papers; Analysis C found no entry of the 10+ set at or above these values"),
    verification="a listed candidate or pool name that meets neither rule, or whose printed values are too sparse or inconsistent to place it",
    not_used="IR is not used to select candidates: definitions differ across papers (Analysis E); difficulty is not inferred from IR",
    pool=f"the {len(GIVEN)} names listed in the task + every name meeting the frequent or diversity rule",
    label_status="approved by Toon (28 Oct 2026): group labels follow mechanically from the rules above (proposed by Claude 19 Oct 2026)",
    high_dim_note=(f"No dataset used by at least {POOL_MIN} papers is printed with {BIG_F} or more features every time it is reported. "
                   "This is a statement about this rule, not a finding that the corpus lacks high-dimensional data sets."),
    family_note="family = rule T1 (Toon, 28 Oct 2026): numbered or split versions belong to their main set; non-standard names are not merged; see build/family_rule.py",
    scope_note="the rule covers use frequency and printed size/dimensionality only; it does not establish diversity in overlap, noise, sparsity, feature type or any other characteristic")
AUD = {r["record_id"]: r for r in csv.DictReader(open("out/modified_operations_audit.csv", encoding="utf-8-sig"))}
NSA = {r["record_id"]: r["assessment"] for r in csv.DictReader(open("out/not_stated_audit.csv", encoding="utf-8-sig"))}
DE = json.load(open("out/difficulty_evidence.json", encoding="utf-8"))["items"]
DREC = defaultdict(list)
for it in DE:
    for rid in it.get("record_ids") or []: DREC[rid].append(f"{it['paper']} {it['type']}: {it['property']}")

def profile(n):
    E = ent[n]; P = byname[n]
    def vals(k): return [(r["paper_key"], num(r[k])) for r in E if num(r[k]) is not None]
    ni, nf, nc, nm = vals("n_instances"), vals("n_features"), vals("n_classes"), vals("n_minority")
    irp = [r for r in E if r["ir_as_printed"].strip() and not r["ir_as_printed"].lower().startswith("not stated")]
    irdef = sorted({r["ir_definition_paper"] for r in E if not r["ir_definition_paper"].lower().startswith("not stated")})
    ops = Counter(o for r in E if r["record_id"] in AUD for o in AUD[r["record_id"]]["ops"].split(";") if o)
    f_ = fam(E[0]["normalized_name"])
    d = dict(name=T1.display(n), dataset_key=n, family=f_, family_label=T1.display(f_), papers=len(P), entries=len(E), family_papers=len(byfam[f_]), family_names=len(famnames[f_]),
             family_flags="; ".join(ff.get(f_, [])),
             spellings="; ".join(sorted({r["normalized_name"] for r in E})),
             n_instances_printed=len(ni), n_instances_papers=len({p for p, _ in ni}), n_instances_values=";".join(g(x) for x in sorted({v for _, v in ni})),
             n_instances_median=g(st.median([v for _, v in ni])) if ni else "",
             n_features_printed=len(nf), n_features_values=";".join(g(x) for x in sorted({v for _, v in nf})),
             n_classes_printed=len(nc), n_classes_values=";".join(g(x) for x in sorted({v for _, v in nc})),
             n_minority_printed=len(nm), n_minority_values=";".join(g(x) for x in sorted({v for _, v in nm})),
             ir_printed=len(irp), ir_definitions_stated=len(irdef), ir_papers_without_definition=len({r["paper_key"] for r in irp if r["ir_definition_paper"].lower().startswith("not stated")}),
             categories="; ".join(f"{a} {b}" for a, b in Counter(r["category"] for r in E).most_common()),
             basis_rule_entries=sum(not r["category_basis"].startswith("reader") for r in E),
             modified_entries=sum(r["category"] == "modified" for r in E), modified_ops="; ".join(f"{a} {b}" for a, b in ops.most_common()),
             not_stated_audit="; ".join(f"{a} {b}" for a, b in Counter(NSA[r["record_id"]] for r in E if r["record_id"] in NSA).most_common()),
             difficulty_evidence=" | ".join(sorted({x for r in E for x in DREC.get(r["record_id"], [])})),
             record_ids=";".join(r["record_id"] for r in E))
    big_n = len({p for p, _ in ni}) >= 2 and all(v >= BIG_N for _, v in ni)
    big_f = len({p for p, _ in nf}) >= 2 and all(v >= BIG_F for _, v in nf)
    adds = []
    if big_n: adds.append(f"instances >= {BIG_N:,} in every printed value ({d['n_instances_values']})")
    if big_f: adds.append(f"features >= {BIG_F} in every printed value ({d['n_features_values']})")
    if not big_n and ni and any(v >= BIG_N for _, v in ni): adds.append(f"some printed sizes >= {BIG_N:,} but not all ({d['n_instances_values']})")
    if not big_f and nf and any(v >= BIG_F for _, v in nf): adds.append(f"some printed feature counts >= {BIG_F} but not all ({d['n_features_values']})")
    if d["papers"] >= FREQ_MIN: grp = "frequently used benchmark"
    elif d["papers"] >= POOL_MIN and (big_n or big_f): grp = "potential diversity candidate"
    else: grp = "requires verification"
    why = []
    if d["papers"] >= FREQ_MIN: why.append(f"used by {d['papers']} papers (dataset, rule T1-1)")
    elif grp == "requires verification":
        if d["papers"] < POOL_MIN: why.append(f"only {d['papers']} papers")
        elif any(x.startswith("some printed") for x in adds): why.append("printed sizes or feature counts disagree across papers: some reach the threshold, some do not; which version each paper used needs checking")
        else: why.append("no printed size or dimensionality outside the range of the frequent set")
    flags = []
    if len(set(d["n_instances_values"].split(";")) - {""}) > 1: flags.append("papers print different instance counts")
    if len(set(d["n_classes_values"].split(";")) - {""}) > 1: flags.append("papers print different class counts (binarised or other variants)")
    if d["family_names"] > 1: flags.append(f"family has {d['family_names']} datasets (splits by rule T1)")
    if d["modified_entries"]: flags.append(f"{d['modified_entries']} of {d['entries']} entries modified by authors")
    if "not stated" in d["categories"]: flags.append("some entries: origin not stated")
    if d["ir_papers_without_definition"]: flags.append(f"IR printed without a stated definition in {d['ir_papers_without_definition']} papers")
    if d["n_instances_printed"] < d["entries"]: flags.append(f"size not printed for {d['entries'] - d['n_instances_printed']} of {d['entries']} entries")
    if d["family_flags"]: flags.append("family grouping flagged")
    if n == dkey("shuttle") and os.path.exists("out/shuttle_versions.json"):
        SV = json.load(open("out/shuttle_versions.json", encoding="utf-8"))
        flags.append("shuttle versions (out/shuttle_versions.csv): " + "; ".join(f"{g['group']} {g['n_instances'] or 'size not printed'} = {', '.join(g['papers'])} [{g['status']}]" for g in SV["groups"]) + "; not pooled")
    d.update(label_status="approved (Toon, 28 Oct 2026)", group=grp, group_reason="; ".join(why), diversity_evidence="; ".join(adds), caveats="; ".join(flags), listed_in_task="yes" if n in GIVEN else "no")
    return d

pool = sorted(set(GIVEN) | {n for n, v in byname.items() if len(v) >= FREQ_MIN} | {n for n, v in byname.items() if len(v) >= POOL_MIN})
rows = [profile(n) for n in pool]
rows = [r for r in rows if r["listed_in_task"] == "yes" or r["group"] != "requires verification"]
ORDER = {"frequently used benchmark": 0, "potential diversity candidate": 1, "requires verification": 2}
rows.sort(key=lambda r: (ORDER[r["group"]], -r["papers"], r["name"]))
missing = [n for n in GIVEN if n not in byname]
with open("out/benchmark_candidates.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
S = dict(criteria=CRITERIA, listed_not_found=missing, counts=dict(Counter(r["group"] for r in rows)),
         frequent_set_size=sum(len(v) >= FREQ_MIN for v in byname.values()), frequent_set_check_vs_C=C["datasets_used_by_10plus_papers"],
         families=dict(total=len(byfam), rule=T1.RULE, flagged=len(ff), flagged_list={k: v for k, v in ff.items() if v}),
         sources=["out/dataset_records.csv", "out/benchmark_concentration.json", "out/reconcile_counts.json", "out/modified_operations_audit.csv",
                  "out/not_stated_audit.csv", "out/difficulty_evidence.json", "out/dataset_families.csv"])
assert S["frequent_set_size"] == S["frequent_set_check_vs_C"]
json.dump(S, open("out/benchmark_candidates.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in S.items() if k != "families"}, ensure_ascii=False, indent=1)); print("families", S["families"]["total"], "flagged", S["families"]["flagged"])
for r in rows: print(r["group"][:12], r["name"], r["papers"], r["family_papers"], "|", r["diversity_evidence"][:90], "|", r["group_reason"])
