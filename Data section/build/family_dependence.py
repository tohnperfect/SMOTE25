"""Do results against plain SMOTE cluster by source family inside a paper? (Toon 28 Oct 2026)

Question: within one paper, are outcomes on splits of the same source (e.g. yeast4, yeast5, yeast-2_vs_4)
more alike than outcomes on datasets from different sources? If yes, splits are not independent evidence.

Data: primary set of out/verified_outcomes.csv (plain SMOTE, per dataset, KNNOR's average excluded, MC-MBRC excluded
by rule R8 on 29 Oct 2026: 521 rows, 29 papers; MC-MBRC had no same-family pair, so pairs and p-values are unchanged). Outcome = raw_sign of the interim rule A ('+' proposed higher, '-' SMOTE higher, '=' tie), and,
separately, the rank of diff within the paper (metric scales differ across papers, ranks do not).
Family of a dataset (two versions):
  confirmed : yeast / ecoli / glass by name prefix (the families confirmed in R3); every other name is its own family
  (the earlier heuristic prefix grouping was dropped once Toon decided rule T1)
  t1        : Toon's rule T1 (28 Oct 2026), out/dataset_families.csv from build/family_rule.py; names not in that
              file fall back to their own punctuation-free key
Statistics, pooled over papers, with family labels permuted WITHIN each paper (10,000 permutations, seed 0):
  S_sign = share of same-family pairs that have the same raw_sign   (vs. same share under permutation)
  S_rank = mean absolute difference of within-paper diff ranks for same-family pairs (smaller = more alike)
Only papers that have at least one family with two rows contribute pairs; papers whose rows all have the
same sign carry no information for S_sign and are counted separately.
Writes out/family_dependence.json and out/family_dependence_papers.csv. Descriptive; no win/loss claims.
"""
import json, re, sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "build"))
from analyse_dataset_usage import norm  # same normalisation as the 771 names
import reconcile_counts as RC  # R8: EXCLUDED_COMPARATOR

NPERM, SEED = 10000, 0


def fam_h(n):
    m = re.match(r"[a-z]+(?:[-_ ][a-z]+)*", n)
    return m.group(0).rstrip("-_ ") if m else n


def fam_c(n):
    for f in ("yeast", "ecoli", "glass"):
        if n.startswith(f):
            return f
    return "own:" + n


def _stats(groups):
    """groups: list of (sign_codes, ranks) arrays for each same-family group with >= 2 rows.
    Returns (same-sign pairs, pairs, sum of |rank gap| over pairs)."""
    same = tot = gapsum = 0.0
    for sg, rk in groups:
        n = len(sg)
        tot += n * (n - 1) / 2
        _, c = np.unique(sg, return_counts=True); same += float((c * (c - 1) / 2).sum())
        x = np.sort(rk); k = np.arange(1, n + 1); gapsum += float((x * (2 * k - n - 1)).sum())
    return same, tot, gapsum


def collect(paper_arrays, labels_by_paper):
    groups = []
    for (sg, rk), lab in zip(paper_arrays, labels_by_paper):
        for f in np.unique(lab):
            m = lab == f
            if m.sum() >= 2:
                groups.append((sg[m], rk[m]))
    return _stats(groups)


def run(df, famcol, rng):
    paper_arrays, labels = [], []
    for _, g in df.groupby("paper"):
        paper_arrays.append((g.raw_sign.map({"+": 0, "-": 1, "=": 2}).values, g.rk.values))
        labels.append(g[famcol].values)
    same, tot, gs = collect(paper_arrays, labels)
    obs = dict(pairs=int(tot), same_sign=round(same / tot, 4) if tot else None, rank_gap=round(gs / tot, 4) if tot else None)
    ps, pg = [], []
    for _ in range(NPERM):
        a, t, g_ = collect(paper_arrays, [rng.permutation(l) for l in labels])
        ps.append(a / t if t else np.nan); pg.append(g_ / t if t else np.nan)
    ps, pg = np.array(ps), np.array(pg)
    obs["perm_same_sign_mean"] = round(float(np.nanmean(ps)), 4)
    obs["p_same_sign"] = round(float((np.sum(ps >= same / tot - 1e-12) + 1) / (NPERM + 1)), 4)
    obs["perm_rank_gap_mean"] = round(float(np.nanmean(pg)), 4)
    obs["p_rank_gap"] = round(float((np.sum(pg <= gs / tot + 1e-12) + 1) / (NPERM + 1)), 4)
    return obs


def main():
    o = pd.read_csv(HERE / "out" / "verified_outcomes.csv", encoding="utf-8-sig", dtype=str).fillna("")
    o["line"] = [str(i + 2) for i in range(len(o))]  # csv line number (header = line 1)
    p = o[(o.smote_kind == "plain SMOTE") & (o.paper != "KNNOR")
          & ~o.paper.isin(list(RC.EXCLUDED_COMPARATOR))].copy().reset_index(drop=True)
    if len(p) != 521:
        sys.exit(f"STOP: {len(p)} rows, expected 521 (541 before rule R8)")
    # dataset name: the linked dataset record (out/outcome_dataset_links.csv) where one exists, so that table
    # abbreviations such as 'Haber' or 'ldd3 (ecoli-0-1 vs 5)' resolve to the record's normalised name
    L = pd.read_csv(HERE / "out" / "outcome_dataset_links.csv", dtype=str).fillna("")
    D = pd.read_csv(HERE / "out" / "dataset_records.csv", dtype=str).set_index("record_id").normalized_name.to_dict()
    link = {r.outcome_csv_line: D.get(r.record_id, "") for r in L.itertuples()}
    p["name"] = [link.get(l) or norm(d) for l, d in zip(p.line, p.dataset)]
    out_linked = int(sum(bool(link.get(l)) for l in p.line))
    p["fam_c"], p["fam_h"] = p.name.map(fam_c), p.name.map(fam_h)
    T1 = pd.read_csv(HERE / "out" / "dataset_families.csv", dtype=str).set_index("normalized_name").family.to_dict()
    p["fam_t1"] = [T1.get(n, re.sub(r"[-_ .]", "", n)) for n in p.name]
    out_unmapped = int(sum(n not in T1 for n in p.name))
    p["d"] = pd.to_numeric(p["diff"], errors="coerce")
    p["rk"] = p.groupby("paper").d.rank(pct=True)
    rng = np.random.default_rng(SEED)
    out = {"rows": len(p), "papers": int(p.paper.nunique()), "sign_counts": dict(Counter(p.raw_sign))}
    per = []
    out["t1_unmapped_rows"] = out_unmapped
    out["rows_linked_to_records"] = out_linked
    for famcol, label in (("fam_c", "confirmed"), ("fam_t1", "t1")):  # heuristic fam() dropped 28 Oct 2026 (T1 decided)
        inf = []
        for k, g in p.groupby("paper"):
            fc = g[famcol].value_counts()
            multi = fc[fc >= 2]
            per.append(dict(version=label, paper=k, rows=len(g), families_with_2plus=int(len(multi)),
                            rows_in_those=int(multi.sum()), signs=dict(Counter(g.raw_sign)),
                            all_same_sign=g.raw_sign.nunique() == 1,
                            by_family={f: dict(Counter(g[g[famcol] == f].raw_sign)) for f in multi.index}))
            if len(multi) and g.raw_sign.nunique() > 1:
                inf.append(k)
        sub = p[p.paper.isin(inf)]
        res = run(sub, famcol, rng)
        res.update(informative_papers=len(inf), informative_rows=int(len(sub)))
        # robustness: drop the paper that contributes most same-family pairs and rerun
        pairs_by = {k: int(sum(n * (n - 1) // 2 for n in g[famcol].value_counts() if n >= 2)) for k, g in sub.groupby("paper")}
        top = max(pairs_by, key=pairs_by.get)
        res["pairs_by_paper"] = pairs_by
        res["without_" + top] = run(sub[sub.paper != top], famcol, rng)
        if label == "t1":  # leave each contributing paper out (2,000 permutations each)
            global NPERM
            keep, NPERM = NPERM, 2000
            res["leave_one_paper_out"] = {k: {x: run(sub[sub.paper != k], famcol, rng)[x] for x in ("pairs", "rank_gap", "perm_rank_gap_mean", "p_rank_gap")}
                                          for k, v in pairs_by.items() if v >= 5}
            NPERM = keep
        out[label] = res
    # Toon's follow-up (28 Oct): split same-family pairs (t1) into pairs that share the minority examples and other
    # pairs. Proxy for "same minority": both linked records print the same minority size (n_minority) in the same
    # family (e.g. yeast4 and yeast-0-5-6-7-9_vs_4, 51 each); 'unknown' when either size is not printed.
    # Null: permute the within-paper ranks inside each paper (10,000 times) and recompute each category's mean gap.
    Dm = pd.read_csv(HERE / "out" / "dataset_records.csv", dtype=str).set_index("record_id").n_minority.to_dict()
    lrec = {r.outcome_csv_line: r.record_id for r in L.itertuples()}
    def nmin(line):
        v = re.sub(r"[^0-9]", "", str(Dm.get(lrec.get(line, ""), "")))
        return int(v) if v else None
    p["nmin"] = [nmin(l) for l in p.line]
    inf = [k for k, g in p.groupby("paper") if (g.fam_t1.value_counts() >= 2).any() and g.raw_sign.nunique() > 1]
    sub = p[p.paper.isin(inf)].reset_index(drop=True)
    pr = []  # (paper index array position a, b, category)
    for k, g in sub.groupby("paper"):
        for f, h in g.groupby("fam_t1"):
            idx = list(h.index)
            for i in range(len(idx)):
                for j in range(i + 1, len(idx)):
                    a, b = idx[i], idx[j]
                    na, nb = sub.at[a, "nmin"], sub.at[b, "nmin"]
                    cat = "unknown" if (na is None or nb is None) else ("shared_minority" if na == nb else "different_minority")
                    pr.append((a, b, cat))
    A = np.array([x[0] for x in pr]); Bb = np.array([x[1] for x in pr]); C = np.array([x[2] for x in pr])
    rk = sub.rk.values.copy(); grp = [g.index.values for _, g in sub.groupby("paper")]
    def gaps(r):
        g_ = np.abs(r[A] - r[Bb]); return {c: float(g_[C == c].mean()) for c in np.unique(C)}
    obs = gaps(rk); null = {c: [] for c in obs}
    for _ in range(NPERM):
        r2 = rk.copy()
        for ix in grp:
            r2[ix] = rng.permutation(r2[ix])
        for c, v in gaps(r2).items():
            null[c].append(v)
    out["t1_by_minority_sharing"] = {c: dict(pairs=int((C == c).sum()), rank_gap=round(obs[c], 4),
                                             null_mean=round(float(np.mean(null[c])), 4),
                                             p=round(float((np.sum(np.array(null[c]) <= obs[c] + 1e-12) + 1) / (NPERM + 1)), 4),
                                             papers=sorted({sub.at[a, "paper"] for a, _, cc in pr if cc == c}))
                                     for c in obs}
    pd.DataFrame(per).to_csv(HERE / "out" / "family_dependence_papers.csv", index=False)
    json.dump(out, open(HERE / "out" / "family_dependence.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
