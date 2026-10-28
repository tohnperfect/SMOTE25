"""characteristics_coverage.py  Analysis E (19 ต.ค. 2026): ข้อมูลมีพอจะบอกลักษณะของ dataset นอกเหนือจาก IR ไหม

อ่าน   out/dataset_records.csv + out/dataset_records_summary.json (ตรวจแล้ว), out/difficulty_evidence.json (Claude คัด, quote ตรวจกับ PDF),
       ai-draft/full/<key>.json (outcome.chosen.condition: ข้อความ protocol ของตารางผลที่สกัด), out/data_handling_matrix.csv (prep_text, ai_draft)
เขียน  out/characteristics_coverage.json
กติกา: ไม่อนุมาน overlap/noise/sparsity จาก IR; ค่าที่ไม่มีคือ "ไม่รายงาน/ไม่ได้สกัด" ไม่ใช่ "ไม่มีคุณสมบัตินั้น"
"""
import csv, glob, json, os, re
from collections import Counter
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
R = [r for r in csv.DictReader(open("out/dataset_records.csv", encoding="utf-8-sig")) if r["is_placeholder"] == "no"]
S = json.load(open("out/dataset_records_summary.json", encoding="utf-8"))["completeness"]
N, P = len(R), sorted({r["paper_key"] for r in R})
miss = lambda v: (not (v or "").strip()) or v.strip().lower().startswith("not stated in paper") or v.strip().lower() in ("none", "null")
def frac(a, b): return dict(n=a, of=b, pct=round(100 * a / b, 1))
def papers_any(f): return len({r["paper_key"] for r in R if f(r)})
out = dict(units="entries = named data entries (1,653); papers = papers with named entries (72)")
# 1 size and class structure (verified fields)
for f in ["n_instances", "n_features", "n_classes", "n_minority", "n_majority", "class_distribution"]:
    out[f] = dict(entries=frac(sum(not miss(r[f]) for r in R), N), papers_with_any=frac(papers_any(lambda r: not miss(r[f])), len(P)))
cls = lambda r: not miss(r["n_minority"]) or not miss(r["class_distribution"])
out["class_proportions_any_form"] = dict(entries=frac(sum(cls(r) for r in R), N), papers_with_any=frac(papers_any(cls), len(P)))
# 2 feature type: no dedicated field; count entries whose extraction text mentions it
FT = re.compile(r"nominal|categorical|numeric(al)?\b|mixed|continuous|\d+\(\d+/[\d-]+\)|\b\d+[NCB]\b", re.I)
ft = lambda r: bool(FT.search(r["preprocessing_note"] + " " + r["group_in_paper"]))
out["feature_type"] = dict(field="none (not extracted systematically)", entries_mentioning=frac(sum(ft(r) for r in R), N),
                           papers_mentioning=frac(papers_any(ft), len(P)), note="mentions found in extraction notes only; absence means not extracted")
# 3 overlap / noise / sparsity (curated evidence)
DF = json.load(open("out/difficulty_evidence.json", encoding="utf-8"))
inh = [i for i in DF["items"] if i["type"] == "inherent"]
recs_measured = {x for i in inh if i["table_values"] for x in i["record_ids"]}
recs_described = {x for i in inh if not i["table_values"] for x in i["record_ids"]}
out["overlap_noise_sparsity"] = dict(
    entries_with_measured_value=frac(len(recs_measured), N), entries_with_described_property=frac(len(recs_described - recs_measured), N),
    papers_reporting_inherent_property=frac(len({i["paper"] for i in inh}), len(P)),
    measures={i["paper"]: i["property"] for i in inh if i["table_values"]},
    papers_with_injected_or_generated_difficulty=frac(len({i["paper"] for i in DF["items"] if i["type"] == "experimentally injected"}), len(P)),
    sparsity="no statement found in the curated evidence",
    caveat=f"curated items cover {DF['summary']['papers_with_items']} papers; {len(DF['papers']) - DF['summary']['papers_with_items']} papers have keyword hits not reviewed")
# 4 evaluation protocol of the extracted results table (paper level)
cond = {}
for f in glob.glob("ai-draft/full/*.json"):
    j = json.load(open(f, encoding="utf-8")); c = (((j.get("outcome") or {}).get("chosen")) or {}).get("condition") or ""
    if j["key"] in P: cond[j["key"]] = c
def proto(c):
    c = c.lower()
    if re.search(r"(\d+|ten|five)\s*[x×]\s*(\d+|ten)|repeated|\d+ (runs|rounds|repetitions)|runs? of|seeds", c) and re.search(r"fold|cv|cross", c): return "repeated k-fold CV"
    if re.search(r"fold|\bcv\b|cross.?valid", c): return "k-fold CV"
    if re.search(r"split|train/test|train-test|\d+:\d+|\d+/\d+ ", c): return "hold-out split (incl. repeated)"
    if not c.strip() or "not applicable" in c: return "no results table / not applicable"
    return "not stated in extracted condition"
pc = Counter(proto(c) for c in cond.values())
out["evaluation_protocol_papers"] = dict(source="ai-draft/full outcome.chosen.condition (extraction text, not separately verified)",
                                         counts={k: frac(v, len(cond)) for k, v in pc.most_common()})
DH0 = {r["key"]: r for r in csv.DictReader(open("out/data_handling_matrix.csv", encoding="utf-8-sig"))}
comb = Counter()
for k, c in cond.items():
    v = proto(c)
    if v == "not stated in extracted condition": v2 = proto(DH0.get(k, {}).get("prep_text", "")); v = v2 + " [from ai_draft prep_text]" if v2 not in ("not stated in extracted condition", "no results table / not applicable") else "not captured in either extraction"
    comb[v] += 1
out["evaluation_protocol_papers"]["with_ai_draft_fallback"] = {k: frac(v, len(cond)) for k, v in comb.most_common()}
# 5 preprocessing placement relative to resampling (ai_draft paper text)
DH = {r["key"]: r for r in csv.DictReader(open("out/data_handling_matrix.csv", encoding="utf-8-sig"))}
PL = re.compile(r"training fold|training folds|only to the training|on the training (set|data|fold)|within (each|the) (fold|training)|before (resampling|oversampling)|after (resampling|oversampling)|test (set|fold)s? (left|kept|remain)", re.I)
pl = [k for k in P if k in DH and PL.search(DH[k]["prep_text"] or "")]
out["preprocessing_or_resampling_placement"] = dict(source="out/data_handling_matrix.csv prep_text (ai_draft, unverified)",
                                                    papers_mentioning=frac(len(pl), len(P)), papers=pl)
json.dump(out, open("out/characteristics_coverage.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(out, ensure_ascii=False, indent=1))
