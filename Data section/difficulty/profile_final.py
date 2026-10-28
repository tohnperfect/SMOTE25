"""Final difficulty profile per verified task (Toon 28 Oct 2026: noise reported as a
continuous value plus the cited outlier flag; borderline and outlier kept as columns).

Reads  difficulty_groups_cited.csv (group_cited.py)
Writes difficulty_profile_final.csv   one row per task, the columns the manuscript would use
       profile_final_summary.json     counts by task and by corpus entry
       profile_summary_proposal.tex   proposed table, NOT inserted into the manuscript

Rules (all cited, see group_cited.py):
  small_disjuncts  rare >= 0.20            Napierala & Stefanowski 2016, sec. 6.2
  outlier_flag     outlier > 0.20          Napierala & Stefanowski 2016, sec. 6.2
  small_sample     n_min / d_raw < 10      Jain, Duin & Mao 2000, sec. 3
  ir_band          <=1.5 / 1.5-3 / 3-9 / >9  Fernandez et al. 2008, sec. 5 (descriptor only)
  noise_index      borderline + outlier, continuous, no cut-off
Entry weighting: 'entries' = corpus entries that use the task; used only for binary and
binarised tasks (an OvR task is our construction, not a task a paper evaluated).
Measures: HVDM neighbourhoods, Napierala rare rule incl. same-class-neighbour condition (28 Oct).
"""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
FLAGS = ["small_disjuncts", "small_sample", "outlier_flag"]
IR_ORDER = ["<=1.5", "1.5-3 low", "3-9 medium", ">9 high"]


def tf(s):
    return s.astype(str).str.lower() == "true"


def q(s):
    return {k: round(float(s.quantile(v)), 3) for k, v in
            [("P10", .1), ("P25", .25), ("median", .5), ("P75", .75), ("P90", .9)]}


def block(sub, weight=None):
    w = sub[weight] if weight else pd.Series(1, index=sub.index)
    n = int(w.sum())
    res = {"n": n, "flags": {f: {"n": int(w[sub[f]].sum()), "pct": round(100 * w[sub[f]].sum() / n, 1)}
                             for f in FLAGS}}
    none = ~sub[FLAGS].any(axis=1)
    res["no_flag"] = {"n": int(w[none].sum()), "pct": round(100 * w[none].sum() / n, 1)}
    res["ir_band"] = {b: int(w[sub.ir_band == b].sum()) for b in IR_ORDER}
    res["profiles"] = {k: int(v) for k, v in w.groupby(sub.profile).sum().sort_values(ascending=False).items()}
    if weight is None:
        res["noise_index"] = q(sub.noise_index)
        res["borderline"] = q(sub.borderline)
        res["outlier"] = q(sub.outlier)
        res["noise_index_by_ir_band"] = {b: q(s.noise_index) | {"n": int(len(s))}
                                         for b, s in sub.groupby("ir_band") if len(s)}
    return res


def main():
    g = pd.read_csv(HERE / "difficulty_groups_cited.csv")
    g = g[~tf(g.min_share_ge_half)].copy()
    g["small_disjuncts"], g["small_sample"] = tf(g.small_disjuncts), tf(g.small_sample)
    g["outlier_flag"] = tf(g.outlier_heavy)
    g["profile"] = g[FLAGS].apply(lambda r: " + ".join(f for f in FLAGS if r[f]) or "none", axis=1)
    g["origin"] = g.task_type.map({"binary": "binary file", "binarized": "binarised (rule reproduced)",
                                   "ovr": "one-vs-rest (ours)"})
    cols = ["file", "source", "origin", "minority_label", "N", "n_min", "n_features_raw", "IR", "ir_band",
            "noise_index", "borderline", "outlier", "rare", "safe", "n_min_per_feature",
            "small_disjuncts", "small_sample", "outlier_flag", "profile", "entries", "papers", "version_note"]
    g = g.sort_values(["origin", "noise_index"], ascending=[True, False])
    g[cols].to_csv(HERE / "difficulty_profile_final.csv", index=False)

    b = g[g.task_type != "ovr"]
    o = g[g.task_type == "ovr"]
    out = {"tasks_binary_binarised": block(b), "tasks_ovr": block(o), "tasks_all": block(g),
           "entries_binary_binarised": block(b, "entries"),
           "entries_binary_binarised_papers": int(len(set("; ".join(b.papers).split("; "))))}
    (HERE / "profile_final_summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

    T, E = out["tasks_binary_binarised"], out["entries_binary_binarised"]
    TO = out["tasks_ovr"]
    nq = T["noise_index"]
    row = lambda lab, f: (f"{lab} & {T['flags'][f]['n']} ({T['flags'][f]['pct']:.0f}\\%) & "
                          f"{E['flags'][f]['n']} ({E['flags'][f]['pct']:.0f}\\%) & "
                          f"{TO['flags'][f]['n']} ({TO['flags'][f]['pct']:.0f}\\%)\\\\")
    r_sd = row("Small disjuncts (rare $\\geq$ 20\\%)~\\citep{napierala2016types}", "small_disjuncts")
    r_ol = row("Outliers $>$ 20\\%~\\citep{napierala2016types}", "outlier_flag")
    r_ss = row("Small sample ($n_{\\min}/d < 10$)~\\citep{jain2000statistical}", "small_sample")
    tex = rf"""% PROPOSAL (Claude, 28 Oct 2026) - not inserted into data-section-draft.tex. Source: difficulty/profile_final.py
\begin{{table}}[t]
\centering\small
\caption{{Difficulty profile of the verifiable datasets. A task can carry several flags.
Entries count how often the corpus uses a task. One-vs-rest tasks are built by us from
multiclass files and are shown separately.}}
\label{{tab:data-difficulty}}
\begin{{tabular}}{{lrrr}}
\toprule
 & \multicolumn{{2}}{{c}}{{Binary and binarised}} & One-vs-rest\\
\cmidrule(lr){{2-3}}
 & Tasks & Entries & Tasks\\
\midrule
All & {T['n']} & {E['n']} & {TO['n']}\\
{r_sd}
{r_ol}
{r_ss}
None of the three & {T['no_flag']['n']} ({T['no_flag']['pct']:.0f}\%) & {E['no_flag']['n']} ({E['no_flag']['pct']:.0f}\%) & {TO['no_flag']['n']} ({TO['no_flag']['pct']:.0f}\%)\\
\addlinespace
IR $>$ 9~\citep{{fernandez2008study}} & {T['ir_band']['>9 high']} & {E['ir_band']['>9 high']} & {TO['ir_band']['>9 high']}\\
\addlinespace
noise index, median [P25, P75] & \multicolumn{{2}}{{c}}{{{nq['median']:.2f} [{nq['P25']:.2f}, {nq['P75']:.2f}]}} & {TO['noise_index']['median']:.2f} [{TO['noise_index']['P25']:.2f}, {TO['noise_index']['P75']:.2f}]\\
\bottomrule
\end{{tabular}}
\end{{table}}
"""
    (HERE / "profile_summary_proposal.tex").write_text(tex)
    print(json.dumps({k: {kk: out[k][kk] for kk in ("n", "flags", "no_flag", "ir_band")} for k in
                      ["tasks_binary_binarised", "entries_binary_binarised", "tasks_ovr"]}, indent=1))
    print("papers behind binary tasks:", out["entries_binary_binarised_papers"])
    print("noise by IR band (binary):", json.dumps(T["noise_index_by_ir_band"]))
    print("profiles binary tasks:", T["profiles"])


if __name__ == "__main__":
    main()
