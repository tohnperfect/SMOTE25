"""benchmark_concentration.py  Analysis C (19 ต.ค. 2026): การกระจุกตัวของ benchmark

อ่าน   out/dataset_records.csv (1,654 entry; ตัด placeholder ของ Tomek ตามกติกา R1 เหลือ 1,653)
เขียน  out/benchmark_concentration.json, out/benchmark_top_names.csv
หน่วย
  entry      = 1 dataset ใน 1 paper ตามที่ extraction บันทึก (ชุดที่ถูกดัดแปลงหลายแบบนับหลาย entry)
  use        = คู่ (paper, ชื่อหลัง normalise) ไม่ซ้ำ  -> ใช้วัดว่า "กี่ paper ใช้ชื่อนี้"
  name       = ชื่อหลัง norm() ของ build/analyse_dataset_usage.py (771 ชื่อ)
  dataset    = กฎ T1 ข้อ 1 (Toon 28 ต.ค. 2026): ชื่อที่ต่างกันแค่ - _ เว้นวรรค จุด เป็นชุดเดียวกัน (682)
  family     = กฎ T1 ข้อ 2-3: ชุดที่มีเลข/การแบ่งเป็น subset ของชุดหลัก, ชื่อไม่มาตรฐานไม่รวม (build/family_rule.py; แทน heuristic เดิม)
ตัวชี้วัด
  top-k share         = สัดส่วนของ use ทั้งหมดที่มาจาก k ชื่อที่ถูกใช้มากที่สุด
  effective number    = 1 / sum(p_i^2) โดย p_i = use ของชื่อ i / use ทั้งหมด (inverse Simpson; = จำนวนชื่อถ้าทุกชื่อถูกใช้เท่ากัน)
  Gini                = ความไม่เท่ากันของจำนวน use ต่อชื่อ (0 = เท่ากันหมด)
"""
import csv, json, os, re, statistics as st
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
R = [r for r in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig")) if r["is_placeholder"] == "no"]
P = sorted({r["paper_key"] for r in R})
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__))))
import families as T1
def fam(n): return T1.family_of(n)
def dkey(n): return T1.dataset_key(n)
def measures(groups):  # groups: name -> set(papers)
    uses = {k: len(v) for k, v in groups.items()}; tot = sum(uses.values()); srt = sorted(uses.values(), reverse=True)
    n = len(srt); cum = 0; gini_num = sum((2 * (i + 1) - n - 1) * x for i, x in enumerate(sorted(srt)))
    return dict(names=n, uses=tot, singletons=sum(x == 1 for x in srt), singleton_share_of_names=round(sum(x == 1 for x in srt) / n, 4),
                singleton_share_of_uses=round(sum(x == 1 for x in srt) / tot, 4),
                top_share={str(k): round(sum(srt[:k]) / tot, 4) for k in (5, 10, 20, 50, 100)},
                names_for_half_of_uses=next(i + 1 for i in range(n) if sum(srt[:i + 1]) >= tot / 2),
                effective_number=round(1 / sum((x / tot) ** 2 for x in srt), 1), gini=round(gini_num / (n * sum(srt)), 4),
                papers_per_name_distribution={b: sum(lo <= x <= hi for x in srt) for b, lo, hi in
                                              [("1", 1, 1), ("2", 2, 2), ("3-4", 3, 4), ("5-9", 5, 9), ("10-19", 10, 19), ("20+", 20, 999)]})
byname = defaultdict(set); entries = Counter(); byfam = defaultdict(set); byds = defaultdict(set)
for r in R:
    n = r["normalized_name"]
    byname[n].add(r["paper_key"]); entries[n] += 1; byfam[fam(n)].add(r["paper_key"]); byds[dkey(n)].add(r["paper_key"])
M_name, M_fam, M_ds = measures(byname), measures(byfam), measures(byds)
ent_sorted = sorted(entries.values(), reverse=True); te = sum(ent_sorted)
M_entries = dict(entries=te, top_share={str(k): round(sum(ent_sorted[:k]) / te, 4) for k in (5, 10, 20, 50, 100)},
                 effective_number=round(1 / sum((x / te) ** 2 for x in ent_sorted), 1))
# paper-level: how much of each paper's list is "shared" (names used by >=5 papers)
common = {k for k, v in byname.items() if len(v) >= 5}
pp = defaultdict(set)
for r in R: pp[r["paper_key"]].add(r["normalized_name"])
share_common = {k: len(v & common) / len(v) for k, v in pp.items()}
papers_any_common = sum(1 for v in pp.values() if v & common)
papers_only_unique = [k for k, v in pp.items() if all(len(byname[n]) == 1 for n in v)]
# characteristics of the 20 most used names (values as printed; spread across papers)
def num(x):
    m = re.fullmatch(r"\d[\d,]*(\.\d+)?", (x or "").strip()); return float(m.group(0).replace(",", "")) if m else None
top = sorted(byname, key=lambda k: (-len(byname[k]), k))[:20]
rows = []
for k in top:
    E = [r for r in R if r["normalized_name"] == k]
    def vals(f): v = [num(r[f]) for r in E]; return [x for x in v if x is not None]
    n, f, c = vals("n_instances"), vals("n_features"), vals("n_classes")
    rows.append(dict(name=k, papers=len(byname[k]), entries=len(E),
                     n_instances_reported=len(n), n_instances_distinct=len(set(n)), n_instances_median=st.median(n) if n else "",
                     n_instances_range=f"{min(n):g}-{max(n):g}" if n else "",
                     n_features_reported=len(f), n_features_values=";".join(f"{x:g}" for x in sorted(set(f))),
                     n_classes_reported=len(c), n_classes_values=";".join(f"{x:g}" for x in sorted(set(c))),
                     ir_printed_reported=sum(1 for r in E if (r["ir_as_printed"] or "").strip() and not r["ir_as_printed"].lower().startswith("not stated")),
                     categories="; ".join(f"{a} {b}" for a, b in Counter(r["category"] for r in E).most_common())))
with open("out/benchmark_top_names.csv", "w", encoding="utf-8", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n"); w.writeheader(); w.writerows(rows)
# size profile: all entries vs entries of names used by >=10 papers
def prof(E):
    n = [num(r["n_instances"]) for r in E]; n = [x for x in n if x is not None]
    f = [num(r["n_features"]) for r in E]; f = [x for x in f if x is not None]
    c = [num(r["n_classes"]) for r in E]; c = [x for x in c if x is not None]
    q = lambda v, p: round(st.quantiles(v, n=100)[p - 1], 1) if len(v) > 2 else None
    return dict(entries=len(E), instances=dict(reported=len(n), median=st.median(n) if n else None, p90=q(n, 90), share_ge_10000=round(sum(x >= 10000 for x in n) / len(n), 3) if n else None),
                features=dict(reported=len(f), median=st.median(f) if f else None, p90=q(f, 90), share_ge_100=round(sum(x >= 100 for x in f) / len(f), 3) if f else None),
                classes=dict(reported=len(c), share_2=round(sum(x == 2 for x in c) / len(c), 3) if c else None, share_ge_5=round(sum(x >= 5 for x in c) / len(c), 3) if c else None))
heavy = {k for k, v in byname.items() if len(v) >= 10}
heavy_ds = {k for k, v in byds.items() if len(v) >= 10}
S = dict(units="entry = data set in one paper; use = distinct (paper, normalised name); name = norm() of analyse_dataset_usage.py",
         papers=len(P), named_entries=len(R), by_name=M_name, by_entry=M_entries, by_dataset=M_ds, by_family=M_fam, t1_rule=T1.RULE,
         names_used_by_10plus_papers=len(heavy), uses_on_those_names=sum(len(byname[k]) for k in heavy),
         papers_using_any_name_shared_by_5plus=papers_any_common, papers_whose_names_are_all_single_paper=sorted(papers_only_unique),
         median_share_of_a_papers_names_that_are_common_5plus=round(st.median(share_common.values()), 3),
         datasets_used_by_10plus_papers=len(heavy_ds), uses_on_those_datasets=sum(len(byds[k]) for k in heavy_ds),
         datasets_used_by_10plus=sorted((T1.display(k), len(byds[k])) for k in heavy_ds),
         size_profile_all_entries=prof(R), size_profile_names_used_by_10plus_papers=prof([r for r in R if r["normalized_name"] in heavy]),
         size_profile_datasets_used_by_10plus_papers=prof([r for r in R if dkey(r["normalized_name"]) in heavy_ds]),
         top20=[(r["name"], r["papers"], r["entries"]) for r in rows],
         top20_datasets=[(T1.display(k), len(byds[k])) for k in sorted(byds, key=lambda k: (-len(byds[k]), k))[:20]],
         top20_families=[(T1.display(k), len(byfam[k])) for k in sorted(byfam, key=lambda k: (-len(byfam[k]), k))[:20]])
json.dump(S, open("out/benchmark_concentration.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(S, ensure_ascii=False, indent=1)[:5000])
