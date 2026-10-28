"""hypotheses.py  tests of H1-H3 (handoff section 1) on the extracted comparisons (29 Oct 2026, Claude; Toon delegated)

Win/loss definition (Toon, 28 Oct 2026): every metric a paper reports with the SMOTE column, classifier and condition
fixed by rule A; compare the printed numbers in the metric's direction; equal printed values = tie; non-numeric = not
comparable. Unit = dataset x metric row. Main set = plain SMOTE comparator (29 papers); other comparators reported apart.

Reads   out/allmetric_links.csv (build/allmetric_links.py), out/winloss_allmetric_rows.csv, out/verified_outcomes.csv,
        out/reconcile_counts.json, out/dataset_records.csv, out/outcome_dataset_links.csv, out/full_summary.json
Writes  out/hypotheses.json, out/hypotheses_paper_split.csv, out/h3_entries.csv

H1  win rate on modified + synthetic data > on original data (the hypothesis as stated in handoff section 1).
    Ties are left out of the win/loss models and reported. Data types: original, repository-defined (KEEL-made
    two-class files; decisions-pending 2, option 3), modified, synthetic, not stated.
    Models (paper is the cluster because rows of one paper are not independent):
      M1 GEE logistic, exchangeable working correlation within paper, robust (sandwich) SE   - population average
      M2 conditional logistic regression stratified by paper                                 - within paper only
      M3 Bayesian binomial mixed GLM, random intercepts for paper and for dataset in paper   - variational fit
      Fisher exact on pooled counts                                                          - crude reference only
    Robustness: R1 one row per dataset (majority of metrics; equal counts = tie); R2 rule-A set (one metric per paper).
H2  papers that include only one standard (original or repository-defined) dataset next to other data:
    descriptive per paper (too few papers for a test).
H3  (a) granularity of reported results, 73 empirical papers; (b) dataset entries listed by a paper that has
    per-dataset SMOTE comparisons but that do not appear in its extracted comparison table(s).
Significance: two-sided 0.05 (conventional); no other threshold is set.
"""
import csv, json, os, re, warnings
from collections import Counter, defaultdict
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.discrete.conditional_models import ConditionalLogit
from statsmodels.genmod.bayes_mixed_glm import BinomialBayesMixedGLM
from statsmodels.stats.proportion import proportion_confint
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
STD = {"original", "repository-defined"}
TYPES = ["original", "repository-defined", "modified", "synthetic", "not stated"]

def wil(k, n):
    lo, hi = proportion_confint(k, n, method="wilson") if n else (np.nan, np.nan)
    return dict(k=int(k), n=int(n), pct=round(100 * k / n, 1) if n else None, ci95=[round(100 * lo, 1), round(100 * hi, 1)])

def counts(df):
    c = Counter(df.result)
    return dict(rows=int(len(df)), papers=int(df.paper.nunique()), win=c["win"], tie=c["tie"], loss=c["loss"],
                win_share_of_decided=wil(c["win"], c["win"] + c["loss"]))

def models(df, label):
    """df: columns paper, dskey, y (1 win / 0 loss), grp in {'base','test'}; returns OR test vs base"""
    out = {"label": label, "n_rows": int(len(df)), "n_papers": int(df.paper.nunique())}
    tab = pd.crosstab(df.grp, df.y)
    a, b = int(tab.loc["test", 1]), int(tab.loc["test", 0]); c, d = int(tab.loc["base", 1]), int(tab.loc["base", 0])
    orr, p = stats.fisher_exact([[a, b], [c, d]])
    out["crude"] = dict(test_win=a, test_loss=b, base_win=c, base_loss=d, odds_ratio=round(orr, 3), fisher_p=round(p, 4))
    X = (df.grp == "test").astype(float)
    try:
        g = sm.GEE(df.y, sm.add_constant(X), groups=df.paper, family=sm.families.Binomial(),
                   cov_struct=sm.cov_struct.Exchangeable()).fit()
        ci = g.conf_int().iloc[1]
        out["M1_gee"] = dict(odds_ratio=round(float(np.exp(g.params.iloc[1])), 3),
                             ci95=[round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)], p=round(float(g.pvalues.iloc[1]), 4))
    except Exception as e: out["M1_gee"] = dict(error=str(e)[:200])
    both = df.groupby("paper").grp.nunique(); keep = both[both == 2].index
    vary = df[df.paper.isin(keep)].groupby("paper").y.nunique(); keep2 = vary[vary == 2].index
    sub = df[df.paper.isin(keep2)]
    out["M2_conditional"] = dict(papers_with_both_groups=int(len(keep)), papers_informative=int(len(keep2)), rows=int(len(sub)))
    if len(keep2) >= 2:
        try:
            m = ConditionalLogit(sub.y.values, (sub.grp == "test").astype(float).values.reshape(-1, 1), groups=sub.paper.values).fit(disp=0)
            ci = m.conf_int()[0]
            if not np.isfinite(m.bse[0]) or m.bse[0] > 10:  # separation: within-paper outcomes perfectly split
                out["M2_conditional"].update(not_estimable="quasi-complete separation within papers (log-OR SE %.1f)" % m.bse[0])
            else:
                out["M2_conditional"].update(odds_ratio=round(float(np.exp(m.params[0])), 3),
                                             ci95=[round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)], p=round(float(m.pvalues[0]), 4))
        except Exception as e: out["M2_conditional"]["error"] = str(e)[:200]
    try:
        d2 = df.assign(test=(df.grp == "test").astype(float), pds=df.paper + "|" + df.dskey)
        vc = {"paper": "0 + C(paper)", "dataset": "0 + C(pds)"}
        b = BinomialBayesMixedGLM.from_formula("y ~ test", vc, d2).fit_vb()
        i = list(b.model.exog_names).index("test")
        mu, sd = float(b.fe_mean[i]), float(b.fe_sd[i])
        out["M3_bayes_mixed"] = dict(odds_ratio=round(float(np.exp(mu)), 3),
                                     ci95_approx=[round(float(np.exp(mu - 1.96 * sd)), 4), round(float(np.exp(mu + 1.96 * sd)), 4)],
                                     posterior_mean_log_or=round(mu, 3), posterior_sd=round(sd, 3))
    except Exception as e: out["M3_bayes_mixed"] = dict(error=str(e)[:200])
    return out

def h1_frames(rows, unit):
    """rows: DataFrame with paper, dskey, how_obtained, result. unit 'row' or 'dataset' (majority over metrics)"""
    d = rows[rows.result.isin(["win", "loss", "tie"])].copy()
    if unit == "dataset":
        g = d.groupby(["paper", "dskey", "how_obtained"]).result.value_counts().unstack(fill_value=0).reset_index()
        for c in ("win", "loss", "tie"):
            if c not in g: g[c] = 0
        g["result"] = np.where(g.win > g.loss, "win", np.where(g.loss > g.win, "loss", "tie"))
        d = g[["paper", "dskey", "how_obtained", "result"]]
    return d

def run_h1(d, tag):
    res = {"overall": counts(d), "datasets": int(d[["paper", "dskey"]].drop_duplicates().shape[0]),
           "by_type": {t: counts(d[d.how_obtained == t]) for t in TYPES + ["unmatched"] if (d.how_obtained == t).any()}}
    dd = d[d.result.isin(["win", "loss"])].assign(y=lambda x: (x.result == "win").astype(int))
    def contrast(test, base, label):
        s = dd[dd.how_obtained.isin(test | base)].assign(grp=lambda x: np.where(x.how_obtained.isin(test), "test", "base"))
        return models(s, label)
    res["H1_primary_modsyn_vs_original"] = contrast({"modified", "synthetic"}, {"original"}, f"{tag}: modified+synthetic vs original")
    res["H1_modsyn_vs_standard"] = contrast({"modified", "synthetic"}, STD, f"{tag}: modified+synthetic vs original+repository-defined")
    res["repository_defined_vs_original"] = contrast({"repository-defined"}, {"original"}, f"{tag}: repository-defined vs original")
    res["not_stated_vs_standard"] = contrast({"not stated"}, STD, f"{tag}: not stated vs original+repository-defined")
    return res

def main():
    L = pd.read_csv("out/allmetric_links.csv", dtype=str).fillna("")
    L["dskey"] = np.where(L.record_id != "", L.record_id, L.dataset_as_printed.str.lower())
    plain = L[L.comparator_group == "plain SMOTE"]
    R = {"definition": __doc__.split("Win/loss definition")[1].split("Reads")[0].strip()}
    R["all_metric_plain"] = run_h1(h1_frames(plain, "row"), "all-metric rows")
    mp = plain.groupby("paper").metric_group.nunique()
    R["all_metric_plain"]["metric_groups_per_paper"] = dict(median=float(mp.median()), min=int(mp.min()), max=int(mp.max()),
                                                            distribution={int(k): int(v) for k, v in mp.value_counts().sort_index().items()})
    pl = plain[plain.result.isin(["win", "loss", "tie"])].groupby("paper").result.apply(lambda r: (r == "loss").sum())
    R["all_metric_plain"]["papers_with_at_least_one_loss"] = int((pl > 0).sum())
    R["all_metric_plain"]["papers_without_loss"] = sorted(pl[pl == 0].index)
    R["all_metric_plain"]["rows_incl_not_comparable"] = int(len(plain))
    R["all_metric_plain"]["datasets_incl_not_comparable"] = int(plain[["paper", "dskey"]].drop_duplicates().shape[0])
    R["all_metric_plain"]["by_metric_group"] = {g: counts(x[x.result.isin(["win", "loss", "tie"])]) for g, x in plain.groupby("metric_group")}
    R["all_metric_plain"]["rate_definitions"] = "win_share_of_decided = wins / (wins + losses); ties and not comparable left out"
    R["robust_R1_dataset_majority"] = run_h1(h1_frames(plain, "dataset"), "dataset majority")
    # R2 rule-A set (521 rows), types from verified_outcomes, dataset key from links
    import sys; sys.path.insert(0, "build"); import reconcile_counts as RC
    O = pd.read_csv("out/verified_outcomes.csv", dtype=str, encoding="utf-8-sig").fillna("")
    LK = pd.read_csv("out/outcome_dataset_links.csv", dtype=str).fillna("")
    O["dskey"] = np.where(LK.record_id != "", LK.record_id, O.dataset.str.lower())
    cross = {k for k, v in RC.CROSS_TABLE_REVIEW.items() if v.startswith("cross-table")}
    A = O[(O.smote_kind == RC.PLAIN) & ~O.dataset.str.match(RC.AGG_RE) & ~O.paper.isin(cross) & ~O.paper.isin(list(RC.EXCLUDED_COMPARATOR))].copy()
    A["result"] = A.raw_sign.map({"+": "win", "-": "loss", "=": "tie"})
    assert len(A) == 521, len(A)
    R["robust_R2_ruleA"] = run_h1(A[["paper", "dskey", "how_obtained", "result"]], "rule A (one metric)")
    # non-plain comparators: descriptive by type
    np_ = L[~L.comparator_group.isin(["plain SMOTE", "excluded"]) & L.result.isin(["win", "loss", "tie"])]
    R["non_plain_by_type"] = {g: {t: counts(s[s.how_obtained == t]) for t in TYPES if (s.how_obtained == t).any()}
                              for g, s in np_.groupby("comparator_group")}
    # per-paper split standard vs modified+synthetic (all-metric plain)
    d = h1_frames(plain, "row"); rows = []
    for p, s in d.groupby("paper"):
        st, ms = s[s.how_obtained.isin(STD)], s[s.how_obtained.isin({"modified", "synthetic"})]
        f = lambda x: (int((x.result == "win").sum()), int((x.result == "loss").sum()), int((x.result == "tie").sum()))
        rows.append(dict(paper=p, std_datasets=s[s.how_obtained.isin(STD)].dskey.nunique(),
                         modsyn_datasets=ms.dskey.nunique(), other_datasets=s[~s.how_obtained.isin(STD | {"modified", "synthetic"})].dskey.nunique(),
                         std_win_loss_tie="/".join(map(str, f(st))), modsyn_win_loss_tie="/".join(map(str, f(ms))),
                         std_win_share=round(f(st)[0] / max(1, f(st)[0] + f(st)[1]), 3) if len(st) else "",
                         modsyn_win_share=round(f(ms)[0] / max(1, f(ms)[0] + f(ms)[1]), 3) if len(ms) else ""))
    pd.DataFrame(rows).to_csv("out/hypotheses_paper_split.csv", index=False)
    both = [r for r in rows if r["std_datasets"] and r["modsyn_datasets"]]
    R["H1_within_paper_descriptive"] = dict(papers_with_both=len(both),
        modsyn_higher=sum(r["modsyn_win_share"] > r["std_win_share"] for r in both),
        std_higher=sum(r["modsyn_win_share"] < r["std_win_share"] for r in both),
        equal=sum(r["modsyn_win_share"] == r["std_win_share"] for r in both))
    sgn = [1 if r["modsyn_win_share"] > r["std_win_share"] else 0 for r in both if r["modsyn_win_share"] != r["std_win_share"]]
    R["H1_within_paper_descriptive"]["sign_test_p"] = round(float(stats.binomtest(sum(sgn), len(sgn)).pvalue), 4) if sgn else None
    # H2
    token = [r for r in rows if r["std_datasets"] == 1 and (r["modsyn_datasets"] + r["other_datasets"]) >= 1]
    R["H2"] = dict(rule="exactly one standard dataset and at least one other dataset in the paper's plain-SMOTE comparisons",
                   papers=[{k: r[k] for k in ("paper", "std_datasets", "modsyn_datasets", "other_datasets", "std_win_loss_tie", "modsyn_win_loss_tie")} for r in token],
                   zero_standard=[r["paper"] for r in rows if r["std_datasets"] == 0],
                   only_standard=[r["paper"] for r in rows if r["std_datasets"] and not (r["modsyn_datasets"] + r["other_datasets"])],
                   note="two papers meet the rule; reported per paper, no test")
    oth = d[d.paper.isin([r["paper"] for r in rows if r["std_datasets"] >= 2]) & d.how_obtained.isin({"modified", "synthetic", "not stated"})]
    tok = d[d.paper.isin([r["paper"] for r in token]) & d.how_obtained.isin({"modified", "synthetic", "not stated"})]
    R["H2"]["non_standard_rows_token_papers"] = counts(tok); R["H2"]["non_standard_rows_other_papers"] = counts(oth)
    # H3 (a) granularity
    FS = json.load(open("out/full_summary.json", encoding="utf-8"))["papers"]
    gran = Counter(p["results_granularity"] for p in FS)
    R["H3a_granularity"] = dict(papers=len(FS), counts=dict(gran),
        checkable_per_dataset=wil(gran["per-dataset"], len(FS)),
        not_checkable=wil(sum(gran[k] for k in ("plots only", "aggregate only", "ranking only")), len(FS)))
    # H3 (b) listed entries without a comparison row
    DR = pd.read_csv("out/dataset_records.csv", dtype=str, encoding="utf-8-sig").fillna("")
    DR = DR[DR.is_placeholder != "yes"]
    linked = set(LK.record_id[LK.record_id != ""]) | set(L.record_id[L.record_id != ""])
    pk = lambda p: p.split(" /")[0]
    have = {pk(p) for p in O[~O.dataset.str.match(RC.AGG_RE)].paper} | set(L.paper)
    have -= {"KNNOR"}
    sub = DR[DR.paper_key.map(pk).isin(have)].copy()
    sub["in_comparison"] = sub.record_id.isin(linked)
    gr = {p: FS_g for p, FS_g in ((x["key"], x["results_granularity"]) for x in FS)}
    sub["granularity"] = sub.paper_key.map(lambda p: gr.get(p, gr.get(pk(p), "")))
    sub[["record_id", "paper_key", "name_as_reported", "category", "granularity", "in_comparison"]].to_csv("out/h3_entries.csv", index=False)
    per = sub.groupby("paper_key").in_comparison.agg(["size", "sum"])
    per["missing"] = per["size"] - per["sum"]
    R["H3b_listed_not_compared"] = dict(papers=int(len(per)), entries=int(len(sub)),
        not_in_comparison=wil(int((~sub.in_comparison).sum()), len(sub)),
        papers_with_any_missing=int((per.missing > 0).sum()),
        by_paper={p: dict(listed=int(r["size"]), missing=int(r["missing"])) for p, r in per.sort_values("missing", ascending=False).iterrows() if r["missing"] > 0},
        by_category={c: wil(int((~s.in_comparison).sum()), len(s)) for c, s in sub.groupby("category")},
        caveat="absence from the extracted table that compares with SMOTE; a dataset may still appear in another results table of the paper")
    json.dump(R, open("out/hypotheses.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
    def show(k):
        x = R["all_metric_plain"][k]; print(k, x["crude"], x.get("M1_gee"), x.get("M2_conditional"), x.get("M3_bayes_mixed"))
    for k in ("H1_primary_modsyn_vs_original", "H1_modsyn_vs_standard", "repository_defined_vs_original", "not_stated_vs_standard"): show(k)
    for t in ("robust_R1_dataset_majority", "robust_R2_ruleA"):
        x = R[t]["H1_primary_modsyn_vs_original"]; print(t, x["crude"], x.get("M1_gee"), x.get("M2_conditional"), x.get("M3_bayes_mixed"))
    print("by type", json.dumps({t: (v["rows"], v["win"], v["tie"], v["loss"], v["win_share_of_decided"]["pct"]) for t, v in R["all_metric_plain"]["by_type"].items()}))
    print("within", R["H1_within_paper_descriptive"]); print("H2", json.dumps(R["H2"])[:900])
    print("H3a", R["H3a_granularity"]); print("H3b", {k: v for k, v in R["H3b_listed_not_compared"].items() if k != "by_paper"})

if __name__ == "__main__":
    main()
