"""Modified data: what was done, why, signals in the experimental design, reuse, and use over time  (9 Nov 2026, Claude;
Toon 9 Nov: which data sets had noise added; split 'other' into named operations; what the authors modified the data for and
in what share; how to tell whether a change suits the method; what is common among modified sets; which modified sets several
papers use; which original, modified and shared synthetic sets are still used in recent years, shown for every period).

Reads (no file is changed):
  out/modified_operations_audit.csv / _summary.json  operations per modified entry (build/modified_operations.py, run on Toon's machine)
  out/modification_purpose_quotes.csv                 reasons quoted from the PDFs (build/modification_purpose.py, checked in the PDFs)
  out/noise_injection_papers.csv                      noise added to real data as an experimental condition (same script)
  out/dataset_records.csv, out/dataset_families.csv   entries, categories, years, families (T1 rule)
  out/allmetric_links.csv                             win/tie/loss rows linked to entries (all-metric set, Toon 28 Oct)
  out/synthetic_availability.csv                      where each paper's synthetic sets can be obtained
  out/pdf_map.json                                    folder of each PDF in the project Drive (reported only, not used in a rule)
Writes out/modification_analysis.json, out/modification_purpose_by_paper.csv, out/modified_families.csv, out/usage_by_period.csv

Rules (written before counting; no thresholds of our own):
  papers covered        the papers with a 'modified' entry (since 9 Nov the noisy versions of real data are modified entries,
                        build/add_noise_entries.py), plus any paper in out/noise_injection_papers.csv without one (none now)
  theme of a paper      every theme with at least one quote; a paper with none is "not stated"
  theme of an entry     a modified entry carries a paper's theme only when its operations are the ones the quote is about:
                        two-class scope -> CS; create/raise imbalance -> IM or US; robustness test -> NI; practical -> SF or US
  "harder"              Toon's wording: create/raise imbalance or robustness test
  same data unmodified  the paper also uses an entry of the same family (T1) that is original, repository-defined or not stated
  several levels        within the paper, a family has two or more IM/NI variants, or the noise is applied at several levels
  converted to two-class, evaluated on two-class only   the paper converts classes (CS) and every entry of the paper with a
                        printed class count has two classes (the experiments are two-class only, so the conversion fits
                        the scope of the method as tested)
  win share             all-metric rows with the plain SMOTE comparator; modified rows vs the paper's other real-data rows
  periods               publication year in 5-year bins (Toon 9 Nov: show every period)
"""
import csv, json, os, re
from collections import Counter, defaultdict
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
def rd(f): return list(csv.DictReader(open(f, encoding="utf-8-sig")))

AUD = rd("out/modified_operations_audit.csv"); SUMM = json.load(open("out/modified_operations_summary.json", encoding="utf-8"))
QU = rd("out/modification_purpose_quotes.csv"); NOI = rd("out/noise_injection_papers.csv")
REC = rd("out/dataset_records.csv"); FAM = {r["normalized_name"]: r["family"] for r in rd("out/dataset_families.csv")}
LNK = rd("out/allmetric_links.csv"); SYN = rd("out/synthetic_availability.csv")
PM = json.load(open("out/pdf_map.json", encoding="utf-8"))
P2PDF = {"CTGAN / TVAE": "CTGAN", "DSRBF / Static-SMOTE": "DSRBF", "EasyEnsemble / BalanceCascade": "EasyEnsemble", "RACOG / wRACOG": "RACOG",
         "ROS (Buda)": "ROS-Buda", "SMOTE-ENN / SMOTE-Tomek": "SMOTE-ENN", "k-means SMOTE": "k-means-SMOTE"}
NCL = defaultdict(list)
for r in REC:
    if re.fullmatch(r"\d+", r["n_classes"].strip()): NCL[r["paper_key"]].append(int(r["n_classes"]))
def only_two(p): return bool(NCL[p]) and all(c <= 2 for c in NCL[p])
def setting(k):
    m = PM.get(P2PDF.get(k, k), {}).get("main", "")
    return next((s for s in ("Binary", "Multiclass", "Both", "Survey") if f"/{s}/" in m), "unknown")

THEMES = ["two-class scope", "create/raise imbalance", "robustness test", "practical"]
BASIS = ["basis: earlier work", "basis: stated rule"]
TOPS = {"two-class scope": {"CS"}, "create/raise imbalance": {"IM", "US"}, "robustness test": {"NI"}, "practical": {"SF", "US"}}
YEAR = {}
for r in REC: YEAR.setdefault(r["paper_key"], int(r["year"]))
MODP = sorted({a["paper_key"] for a in AUD}); NOISEP = sorted({n["paper_key"] for n in NOI})
PAPERS = sorted(set(MODP) | set(NOISEP))
qt = defaultdict(lambda: defaultdict(list))
for q in QU: qt[q["paper_key"]][q["theme"]].append(f'"{q["quote"]}" ({q["pdf_page"]})')
assert set(qt) <= set(PAPERS), f"STOP: quotes for papers outside the set: {set(qt) - set(PAPERS)}"

# --- entries ---------------------------------------------------------------------------------------------------------------
ent_theme = Counter(); ent_rows = []
for a in AUD:
    ops = set(x for x in a["ops"].split(";") if x)
    th = [t for t in THEMES if t in qt[a["paper_key"]] and ops & TOPS[t]]
    ent_rows.append((a["record_id"], a["paper_key"], th))
    for t in th: ent_theme[t] += 1
    if not th: ent_theme["not stated"] += 1
harder_e = sum(1 for _, _, th in ent_rows if {"create/raise imbalance", "robustness test"} & set(th))
scope_e = sum(1 for _, _, th in ent_rows if "two-class scope" in th)

# --- papers ----------------------------------------------------------------------------------------------------------------
byfam_paper = defaultdict(lambda: defaultdict(set))   # paper -> family -> categories
for r in REC:
    if r["normalized_name"]: byfam_paper[r["paper_key"]][FAM.get(r["normalized_name"], r["normalized_name"])].add(r["category"])
audp = defaultdict(list)
for a in AUD: audp[a["paper_key"]].append(a)
win = defaultdict(lambda: {"mod": Counter(), "other": Counter()})
for l in LNK:
    if l["comparator_group"] != "plain SMOTE" or l["result"] not in ("win", "tie", "loss"): continue
    if l["how_obtained"] == "modified": win[l["paper"]]["mod"][l["result"]] += 1
    elif l["how_obtained"] in ("original", "repository-defined", "not stated"): win[l["paper"]]["other"][l["result"]] += 1
def share(c): n = c["win"] + c["loss"]; return round(c["win"] / n, 3) if n else None
prow = []
for p in PAPERS:
    A = audp.get(p, [])
    ops = Counter(o for a in A for o in a["ops"].split(";") if o)
    fams_mod = {FAM.get(a["normalized_name"], a["normalized_name"]) for a in A}
    unmod = sorted(f for f in fams_mod if byfam_paper[p][f] & {"original", "repository-defined", "not stated"})
    lv = Counter(FAM.get(a["normalized_name"], a["normalized_name"]) for a in A if {"IM", "NI"} & set(a["ops"].split(";")))
    noise_here = [n for n in NOI if n["paper_key"] == p]
    several = any(v >= 2 for v in lv.values()) or any(re.search(r"\d+%.*\d+%|levels|steps", n["levels"]) for n in noise_here)
    th = [t for t in THEMES if t in qt[p]]
    w = win.get(p)
    prow.append(dict(
        paper_key=p, year=YEAR.get(p, ""), drive_folder=setting(p), modified_entries=len(A),
        operations=";".join(f"{o}:{n}" for o, n in sorted(ops.items())), noise_added=";".join(n["what_was_added"] for n in noise_here),
        stated_purpose=";".join(th) or "not stated",
        harder="yes" if {"create/raise imbalance", "robustness test"} & set(th) else "no",
        basis=";".join(t.replace("basis: ", "") for t in BASIS if t in qt[p]) or "not stated",
        publishes_modified_data="yes" if "publishes modified data" in qt[p] else "not stated",
        converted_and_two_class_only="yes" if ops.get("CS") and only_two(p) else "no",
        same_data_also_unmodified=f"{len(unmod)} of {len(fams_mod)} families" if A else "n/a (noise only)",
        several_levels="yes" if several else "no",
        win_share_modified=share(w["mod"]) if w else None, win_share_other=share(w["other"]) if w else None,
        rows_modified=sum(w["mod"].values()) if w else 0, rows_other=sum(w["other"].values()) if w else 0,
        quotes=" | ".join(f"{t}: " + "; ".join(qt[p][t]) for t in THEMES + BASIS + ["publishes modified data"] if t in qt[p])))
with open("out/modification_purpose_by_paper.csv", "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(prow[0])); wr.writeheader(); wr.writerows(prow)

nP = len(PAPERS)
def cnt(pred): return sum(1 for r in prow if pred(r))
both = [r for r in prow if r["win_share_modified"] is not None and r["win_share_other"] is not None]
purpose = dict(
    papers=nP, papers_with_modified_entries=len(MODP), papers_noise_only=sorted(set(NOISEP) - set(MODP)),
    by_theme_papers={t: cnt(lambda r, t=t: t in r["stated_purpose"].split(";")) for t in THEMES} | {"not stated": cnt(lambda r: r["stated_purpose"] == "not stated")},
    harder_papers=cnt(lambda r: r["harder"] == "yes"), scope_papers=cnt(lambda r: "two-class scope" in r["stated_purpose"]),
    by_theme_entries=dict(ent_theme), entries=len(AUD), harder_entries=harder_e, scope_entries=scope_e,
    basis_papers={b: cnt(lambda r, b=b: b.replace("basis: ", "") in r["basis"]) for b in BASIS} | {"not stated": cnt(lambda r: r["basis"] == "not stated")},
    note="a paper can have several themes; shares are of the papers covered; 'not stated' = no sentence found")
signals = dict(
    papers_with_class_conversion=cnt(lambda r: "CS:" in r["operations"]),
    converted_and_two_class_only=cnt(lambda r: r["converted_and_two_class_only"] == "yes"),
    of_which_state_two_class_scope=cnt(lambda r: r["converted_and_two_class_only"] == "yes" and "two-class scope" in r["stated_purpose"]),
    same_data_also_unmodified_papers=cnt(lambda r: r["same_data_also_unmodified"].split(" ")[0] not in ("0", "n/a")),
    papers_with_modified_entries=len(MODP),
    several_levels=cnt(lambda r: r["several_levels"] == "yes"),
    harder_papers_with_several_levels=cnt(lambda r: r["harder"] == "yes" and r["several_levels"] == "yes"),
    publishes_modified_data=cnt(lambda r: r["publishes_modified_data"] == "yes"),
    win_share_both=dict(papers=len(both), modified_higher=sum(r["win_share_modified"] > r["win_share_other"] for r in both),
                        other_higher=sum(r["win_share_modified"] < r["win_share_other"] for r in both),
                        equal=sum(r["win_share_modified"] == r["win_share_other"] for r in both),
                        rows_modified=sum(r["rows_modified"] for r in both), rows_other=sum(r["rows_other"] for r in both)))

# --- noise ------------------------------------------------------------------------------------------------------------------
syn_noise = [dict(paper=r["paper_key"], record_id=r["record_id"], name=r["name_as_reported"], note=r["preprocessing_note"][:200])
             for r in REC if r["category"] == "synthetic" and re.search(r"nois|outlier", r["name_as_reported"] + " " + r["preprocessing_note"], re.I)]
noise = dict(real_data=NOI, real_data_papers=len(NOISEP), synthetic_generated_with_noise=syn_noise,
             synthetic_with_noise_papers=len({s["paper"] for s in syn_noise}))

# --- common modifications and modified sets used by several papers ----------------------------------------------------------
fam = defaultdict(lambda: dict(papers=set(), entries=0, ops=Counter(), names=Counter(), kinds=Counter()))
for a in AUD:
    f = fam[FAM.get(a["normalized_name"], a["normalized_name"])]
    f["papers"].add(a["paper_key"]); f["entries"] += 1; f["names"][a["normalized_name"]] += 1
    for o in a["ops"].split(";"):
        if o: f["ops"][o] += 1
    if a["class_op_kind"]: f["kinds"][a["class_op_kind"]] += 1
name_papers = defaultdict(set)
for a in AUD: name_papers[a["normalized_name"]].add(a["paper_key"])
famrows = sorted(([k, len(v["papers"]), v["entries"], ";".join(f"{o}:{n}" for o, n in v["ops"].most_common()),
                   ";".join(f"{o}:{n}" for o, n in v["kinds"].most_common()),
                   ";".join(f"{n}({len(name_papers[n])}p)" for n, _ in v["names"].most_common(8)), ";".join(sorted(v["papers"]))]
                  for k, v in fam.items()), key=lambda x: (-x[1], -x[2], x[0]))
with open("out/modified_families.csv", "w", newline="", encoding="utf-8") as fh:
    wr = csv.writer(fh); wr.writerow(["family", "papers", "modified_entries", "operations", "class_operation_kinds", "modified_names (papers using that exact name)", "paper_keys"]); wr.writerows(famrows)
RECID = {r["record_id"]: r for r in REC}
def versions(n):   # printed (N, minority) pairs of the modified entries with this name; same pair = same version as printed
    v = defaultdict(set)
    for a in AUD:
        if a["normalized_name"] != n: continue
        r = RECID[a["record_id"]]
        key = (r["n_instances"].strip() or "?") + "/" + (r["n_minority"].strip() or "?")
        v[key].add(a["paper_key"])
    return ";".join(f"{k} ({len(ps)}p)" for k, ps in sorted(v.items(), key=lambda kv: -len(kv[1])))
shared_names = sorted(([n, len(ps), ";".join(sorted(ps)), versions(n)] for n, ps in name_papers.items() if len(ps) >= 2), key=lambda x: (-x[1], x[0]))
common = dict(families_modified=len(fam), families_modified_by_2plus_papers=sum(1 for r in famrows if r[1] >= 2),
              top_families=[dict(family=r[0], papers=r[1], entries=r[2], operations=r[3], kinds=r[4]) for r in famrows[:15]],
              same_modified_name_in_2plus_papers=[dict(name=n, papers=k, paper_keys=p, printed_N_over_minority=v) for n, k, p, v in shared_names],
              combinations=SUMM["combinations"], tag_entries=SUMM["tag_entries"], tag_papers=SUMM["tag_papers"], class_op_kind=SUMM["class_op_kind"])

# --- use over time ----------------------------------------------------------------------------------------------------------
def period(y): return "<=2004" if y <= 2004 else "2025-2026" if y >= 2025 else f"{(y // 5) * 5}-{(y // 5) * 5 + 4}"
PER = ["<=2004", "2005-2009", "2010-2014", "2015-2019", "2020-2024", "2025-2026"]
pub_syn_papers = {s["paper"] for s in SYN if s["group"] == "published"}
use = defaultdict(lambda: defaultdict(lambda: defaultdict(set)))   # family -> category -> period -> papers
pp = defaultdict(set); cat_entries = defaultdict(Counter)
for r in REC:
    if not r["normalized_name"]: continue
    y = int(r["year"]); per = period(y); c = r["category"]
    if c == "synthetic": c = "synthetic (published)" if r["paper_key"] in pub_syn_papers else "synthetic (not published)"
    pp[per].add(r["paper_key"]); cat_entries[per][c] += 1
    use[FAM.get(r["normalized_name"], r["normalized_name"])][c][per].add(r["paper_key"])
urows = []
for f, cs in use.items():
    for c, per in cs.items():
        row = dict(family=f, category=c, papers_total=len(set().union(*per.values())))
        for p_ in PER: row[p_] = len(per.get(p_, set()))
        row["first_year"] = min(YEAR[x] for s in per.values() for x in s); row["last_year"] = max(YEAR[x] for s in per.values() for x in s)
        urows.append(row)
urows.sort(key=lambda r: (r["category"], -r["papers_total"], r["family"]))
with open("out/usage_by_period.csv", "w", newline="", encoding="utf-8") as fh:
    wr = csv.DictWriter(fh, fieldnames=list(urows[0])); wr.writeheader(); wr.writerows(urows)
CATS = ["original", "repository-defined", "modified", "not stated", "synthetic (published)", "synthetic (not published)"]
def top(c, pers, n=12):
    rs = [r for r in urows if r["category"] == c and sum(r[p_] for p_ in pers) > 0]
    rs.sort(key=lambda r: (-sum(r[p_] for p_ in pers), -r["papers_total"], r["family"]))
    return [dict(family=r["family"], papers_in_period=sum(r[p_] for p_ in pers), papers_total=r["papers_total"], first_year=r["first_year"], last_year=r["last_year"]) for r in rs[:n]]
periods = {p_: dict(papers=len(pp[p_]), entries=dict(cat_entries[p_])) for p_ in PER}
recent = ["2020-2024", "2025-2026"]
time = dict(periods=periods, top_by_period={p_: {c: top(c, [p_], 8) for c in CATS} for p_ in PER},
            recent_2020_2026={c: top(c, recent, 15) for c in CATS}, recent_papers=len(pp["2020-2024"] | pp["2025-2026"]),
            published_synthetic_sets=[dict(paper=s["paper"], year=YEAR.get(s["paper"]), entries=s["entries"], where=s["evidence"][:160]) for s in SYN if s["group"] == "published"])

OUTJ = dict(source=__doc__.split("\n")[0], purpose=purpose, signals=signals, noise=noise, common=common, time=time)
json.dump(OUTJ, open("out/modification_analysis.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=list)
print(json.dumps(dict(purpose=purpose, signals=signals, noise_papers=noise["real_data_papers"], syn_noise=noise["synthetic_with_noise_papers"],
                      fam=common["families_modified"], fam2=common["families_modified_by_2plus_papers"], shared=len(shared_names)), indent=1, ensure_ascii=False))
