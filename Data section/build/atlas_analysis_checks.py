"""Checks that the Atlas "Analyses A-F" tab data (out/explorer_data.json -> an) equals the analysis outputs.

Run from `Data section/`:  python3 build/atlas_analysis_checks.py
Reads only; writes nothing. Exit code 1 if any check fails.
Added 19 Oct 2026 with the Analyses tab.
"""
import csv, json, sys, collections, os

OUT = "out"
an = json.load(open(os.path.join(OUT, "explorer_data.json"), encoding="utf-8"))["an"]
dash = json.load(open(os.path.join(OUT, "explorer_data.json"), encoding="utf-8"))["dash"]
res = []


def chk(name, cond, detail=""):
    res.append((name, bool(cond), detail))


def rcsv(p):
    with open(os.path.join(OUT, p), encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


# A
ma = rcsv("modified_operations_audit.csv")
ms = json.load(open(os.path.join(OUT, "modified_operations_summary.json"), encoding="utf-8"))
A = an["A"]
rows = [dict(zip(A["fields"], r)) for r in A["rows"]]
chk("A rows = audit csv", len(rows) == len(ma), f"{len(rows)} vs {len(ma)}")
chk("A rows identical to csv (fields shown)", all(all(r[k] == m.get(k, "") for k in A["fields"]) for r, m in zip(rows, ma)))
chk("A summary = summary json", A["summary"] == ms)
tag = {o: sum(o in r["ops"].split(";") for r in rows) for o in ["CS", "US", "IM", "SF", "FM", "OT", "IS"]}
chk("A per-op entries recomputed = summary", all(ms["tag_entries"].get(o, 0) == n for o, n in tag.items()), str(tag))
chk("A entries = dashboard modified", len(rows) == dash["entries"]["by_cat"]["modified"])
purp = len({r["paper_key"] for r in rows if not r["purpose_stated_by_authors"].startswith("none")})
chk("A purpose papers recomputed", purp == ms["purpose"]["papers_with_stated_purpose"], f"{purp}")

# B
bp = rcsv("baseline_provenance_papers.csv")
bs = json.load(open(os.path.join(OUT, "baseline_provenance_summary.json"), encoding="utf-8"))
bi = rcsv("baseline_identical_values.csv")
chk("B papers = csv", an["B"]["papers"] == [{k: r[k] for k in an["B"]["papers"][0]} for r in bp], f"{len(an['B']['papers'])} vs {len(bp)}")
chk("B summary = json", an["B"]["summary"] == bs)
chk("B identical rows = csv", len(an["B"]["identical"]) == len(bi))
lab = collections.Counter(r["provenance"][:2] for r in bp)
pc = bs["rows_by_partition_and_provenance"]["primary_cat"]
t1 = sum(n for k, n in pc.items() if k.startswith("B1|") and k.split("|")[1] not in ("not stated", "unlinked"))
prim = sum(bs["rows_by_partition_and_provenance"]["primary"].values())
chk("B tier1 recomputed", t1 == 216 and prim == 521,  # 541 before rule R8 (MC-MBRC, 29 Oct 2026)
    f"tier1 {t1}, primary {prim}, labels {dict(lab)}")

# C
cj = json.load(open(os.path.join(OUT, "benchmark_concentration.json"), encoding="utf-8"))
chk("C summary = json", an["C"]["summary"] == cj)
chk("C names sum = uses", sum(n for _, n in an["C"]["names"]) == cj["by_name"]["uses"])
cum, half = 0, None
for i, (_, n) in enumerate(an["C"]["names"], 1):
    cum += n
    if half is None and cum >= cj["by_name"]["uses"] / 2:
        half = i
chk("C half-of-uses recomputed (chart)", half == cj["by_name"]["names_for_half_of_uses"], f"{half}")
chk("C top table = csv top20", len(an["C"]["top"]) == min(20, len(rcsv("benchmark_top_names.csv"))))

# D / E
chk("D data = json", an["D"]["data"] == json.load(open(os.path.join(OUT, "temporal_comparison.json"), encoding="utf-8")))
dd = an["D"]["data"]["by_period"]
chk("D papers per period", [dd[p]["papers_with_named_entries"] for p in an["D"]["data"]["periods"]] == [14, 26, 32])
ej = json.load(open(os.path.join(OUT, "characteristics_coverage.json"), encoding="utf-8"))
chk("E data = json", an["E"]["data"] == ej)
chk("E protocol sums to 72", sum(v["n"] for v in ej["evaluation_protocol_papers"]["with_ai_draft_fallback"].values()) == 72)
chk("E follow-up items complete", len(an["E"]["followup"]) == 3 and all(x.rstrip().endswith(".") for x in an["E"]["followup"]))

# F
fm = rcsv("claim_evidence_matrix.csv")
fs = json.load(open(os.path.join(OUT, "claim_evidence_summary.json"), encoding="utf-8"))
chk("F rows = csv", len(an["F"]["rows"]) == len(fm) == fs["claims"] == 25,  # 27 before rule R8 (MC-MBRC claims need its comparison rows)
    f"{len(fm)}")
chk("F papers = 21 (22 before rule R8)", len({r["paper"] for r in an["F"]["rows"]}) == fs["papers"] == 21)
chk("F labels recomputed = summary", dict(collections.Counter(r["label"] for r in an["F"]["rows"])) == fs["by_label"])

# G
chk("G decision table 7 rows, 5 columns", len(an["G"]["rows"]) == 7 and all(len(r) == 5 for r in an["G"]["rows"]))
chk("every analysis has interpretation text", all(an[k].get("interpretation") for k in "ABCDEF"))

# Landscape tab (19 Oct 2026): D.land equals build/landscape_candidates.py outputs
LD = json.load(open(os.path.join(OUT, "explorer_data.json"), encoding="utf-8"))["land"]
lf = rcsv("landscape_families.csv"); lc = rcsv("benchmark_candidates.csv")
lj = json.load(open(os.path.join(OUT, "benchmark_candidates.json"), encoding="utf-8"))
recs = [r for r in rcsv("dataset_records.csv") if r["is_placeholder"] == "no"]
chk("L family map = csv, covers every record name", LD["fam"] == {r["normalized_name"]: r["family"] for r in lf} and {r["normalized_name"] for r in recs} == set(LD["fam"]))
chk("L family count = Analysis C (T1)", len(set(LD["fam"].values())) == cj["by_family"]["names"], str(len(set(LD["fam"].values()))))
fp = collections.defaultdict(set)
for r in recs: fp[LD["fam"][r["normalized_name"]]].add(r["paper_key"])
chk("L family paper uses = Analysis C", sum(map(len, fp.values())) == cj["by_family"]["uses"])
r3 = json.load(open(os.path.join(OUT, "reconcile_counts.json"), encoding="utf-8"))["name_frequencies"]
chk("L R3 figures = reconcile_counts", all(LD["r3"][k]["prefix"] == r3[k]["family_papers"] for k in LD["r3"]), str(LD["r3"]))
chk("L candidates = csv (without record_ids)", LD["cand"] == [{k: v for k, v in r.items() if k != "record_ids"} for r in lc], f"{len(lc)}")
chk("L candidate group counts = json", dict(collections.Counter(r["group"] for r in lc)) == lj["counts"] == LD["counts"], str(lj["counts"]))
chk("L frequent group = datasets used by 10+ papers (C, T1)", lj["counts"].get("frequently used benchmark") == cj["datasets_used_by_10plus_papers"])
pk = collections.defaultdict(set)
dsk = {r["normalized_name"]: r["dataset_key"] for r in lf}
for r in recs: pk[dsk[r["normalized_name"]]].add(r["paper_key"])
chk("L candidate paper counts recomputed (dataset, T1)", all(int(r["papers"]) == len(pk[r["dataset_key"]]) for r in lc))
chk("L all 11 listed names present", not lj["listed_not_found"] and sum(r["listed_in_task"] == "yes" for r in lc) == 11)

# Manuscript integration (19 Oct 2026): landscape paragraphs in data-section-draft.tex agree with out/ files
import subprocess, re as _re
tex = open("manuscript/data-section-draft.tex", encoding="utf-8").read()
ms = json.load(open(os.path.join(OUT, "explorer_data.json"), encoding="utf-8"))["manuscript"]
chk("M Atlas manuscript tex = source tex", ms["tex"] == tex)
chk("M candidate table rows = benchmark_candidates.csv", subprocess.run([sys.executable, "build/landscape_manuscript.py", "--check"], capture_output=True).returncode == 0)
lc_sel = [r for r in lc if r["listed_in_task"] == "yes" or r["group"] != "frequently used benchmark"]
cnt = collections.Counter(r["group"] for r in lc)
chk("M prose counts 18 / 11 / 33 / 7 (datasets, T1)", f"lists {len(lc_sel)} datasets" in tex and f"the {sum(r['listed_in_task']=='yes' for r in lc)} datasets we set out" in tex
    and f"ten papers ({cnt['frequently used benchmark']} datasets)" in tex and f"({cnt['potential diversity candidate']} datasets)" in tex)
cov = ej
chk("M coverage percentages = characteristics_coverage.json", all(f"{cov[k]['entries']['pct']}" in tex for k in ("n_instances", "n_features", "n_classes", "class_proportions_any_form"))
    and f"overlap exists for {cov['overlap_noise_sparsity']['entries_with_measured_value']['n']} entries" in tex)
sp = cj["size_profile_all_entries"]
chk("M medians 800 / nine = Analysis C", sp["instances"]["median"] == 800 and sp["features"]["median"] == 9 and "800 or fewer instances" in tex and "nine or fewer" in tex)
sv = json.load(open(os.path.join(OUT, "shuttle_versions.json"), encoding="utf-8"))
sizes = [g["n_instances"] for g in sv["groups"] if g["n_instances"]]
chk("M shuttle sizes = shuttle_versions.json", len(sizes) == 4 and all(f"{int(x):,}" in tex for x in sizes) and sum(1 for g in sv["groups"] if g["status"].startswith("consistent")) == 2)
chk("M F/D/V approved (Toon 28 Oct): slot removed, no provisional wording", "Approve, revise or drop the provisional groups" not in tex and "Provisional Groups" not in tex and "approved by Toon 28 Oct 2026" in tex)
chk("M high-dim statement wording", "this is a property of the rule, not evidence that the corpus contains no high-dimensional data sets" in " ".join(tex.split()))

for n, ok, d in res:
    print(("PASS " if ok else "FAIL ") + n + (f"  [{d}]" if d else ""))
nf = sum(not ok for _, ok, _ in res)
print(f"{len(res) - nf}/{len(res)} passed")
sys.exit(1 if nf else 0)
