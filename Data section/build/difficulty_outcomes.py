"""difficulty_outcomes.py  do reported wins over plain SMOTE depend on measured data difficulty? (29 Oct 2026, Claude)

Exploratory (not one of H1-H3). Joins all-metric plain-SMOTE rows (out/allmetric_links.csv) through their dataset record
to the verified two-class file (difficulty/verifiability_entries.csv: verif V-binary_file / V-keel_name_only /
V-name_only_other) and its measured profile (difficulty/difficulty_profile_final.csv, origin 'binary file').
Binarised and one-vs-rest tasks are not joined (entry -> task needs the class rule; left out).
Models: GEE logistic clustered by paper (exchangeable) and conditional logit within paper; ties left out.
Predictors one at a time: noise_index (per 0.1), log2 IR, cited flags (small sample, outliers > 20%, small disjuncts).
Writes out/difficulty_outcomes.json, out/difficulty_outcomes_rows.csv
"""
import json, os, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm
from statsmodels.discrete.conditional_models import ConditionalLogit
warnings.filterwarnings("ignore")
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)

L = pd.read_csv("out/allmetric_links.csv", dtype=str).fillna("")
L = L[(L.comparator_group == "plain SMOTE") & L.result.isin(["win", "loss", "tie"]) & (L.record_id != "")]
V = pd.read_csv("difficulty/verifiability_entries.csv", dtype=str).fillna("")
V = V[V.verif.isin(["V-binary_file", "V-keel_name_only", "V-name_only_other", "V-name_only_ext"])][["record_id", "file", "file_src"]]   # 8 Nov: + V-name_only_ext
P = pd.read_csv("difficulty/difficulty_profile_final.csv")
P = P[P.origin == "binary file"].rename(columns={"source": "file_src"})
J = L.merge(V, on="record_id").merge(P, on=["file", "file_src"])
J["y"] = (J.result == "win").astype(int)
J[["paper", "dataset_as_printed", "metric_group", "result", "record_id", "file", "file_src", "profile", "noise_index", "IR",
   "small_sample", "outlier_flag", "small_disjuncts"]].to_csv("out/difficulty_outcomes_rows.csv", index=False)
D = J[J.result != "tie"].copy()
D["noise_per_0.1"] = D.noise_index * 10
D["log2_IR"] = np.log2(D.IR)
for f in ("small_sample", "outlier_flag", "small_disjuncts"): D[f] = D[f].astype(str).str.lower().eq("true").astype(float)
out = dict(rows_joined=int(len(J)), decided_rows=int(len(D)), papers=int(J.paper.nunique()), tasks=int(J.file.nunique()),
           ties=int((J.result == "tie").sum()),
           win_share_by_profile={k: dict(rows=int(len(s)), win=int(s.y.sum()), share=round(float(s.y.mean()), 3))
                                 for k, s in D.groupby("profile")}, models={})
for x in ("noise_per_0.1", "log2_IR", "small_sample", "outlier_flag", "small_disjuncts"):
    r = {}
    try:
        g = sm.GEE(D.y, sm.add_constant(D[[x]]), groups=D.paper, family=sm.families.Binomial(),
                   cov_struct=sm.cov_struct.Exchangeable()).fit()
        ci = g.conf_int().loc[x]
        r["gee"] = dict(odds_ratio=round(float(np.exp(g.params[x])), 3), ci95=[round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)],
                        p=round(float(g.pvalues[x]), 4))
    except Exception as e: r["gee"] = dict(error=str(e)[:150])
    var = D.groupby("paper")[x].nunique(); yv = D.groupby("paper").y.nunique()
    keep = [p for p in var.index if var[p] > 1 and yv[p] > 1]
    s = D[D.paper.isin(keep)]
    if len(keep) >= 2:
        try:
            m = ConditionalLogit(s.y.values, s[[x]].values, groups=s.paper.values).fit(disp=0)
            ci = m.conf_int()[0]
            r["within_paper"] = dict(papers=len(keep), rows=int(len(s)), odds_ratio=round(float(np.exp(m.params[0])), 3),
                                     ci95=[round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)], p=round(float(m.pvalues[0]), 4))
        except Exception as e: r["within_paper"] = dict(error=str(e)[:150])
    else: r["within_paper"] = dict(papers=len(keep), note="too few papers vary")
    out["models"][x] = r
# robustness: one row per paper x task (majority over metrics; equal counts = tie, left out)
M = J.groupby(["paper", "file", "file_src"]).agg(w=("result", lambda r: (r == "win").sum()), l=("result", lambda r: (r == "loss").sum()),
                                                 noise=("noise_index", "first")).reset_index()
M = M[M.w != M.l].assign(y=lambda d: (d.w > d.l).astype(int), x=lambda d: d.noise * 10)
g = sm.GEE(M.y, sm.add_constant(M[["x"]]), groups=M.paper, family=sm.families.Binomial(), cov_struct=sm.cov_struct.Exchangeable()).fit()
ci = g.conf_int().loc["x"]
out["robust_task_majority_noise_per_0.1"] = dict(rows=int(len(M)), papers=int(M.paper.nunique()), odds_ratio=round(float(np.exp(g.params["x"])), 3),
    ci95=[round(float(np.exp(ci[0])), 3), round(float(np.exp(ci[1])), 3)], p=round(float(g.pvalues["x"]), 4))
json.dump(out, open("out/difficulty_outcomes.json", "w", encoding="utf-8"), indent=1)
print(json.dumps(out, indent=1)[:2500])
