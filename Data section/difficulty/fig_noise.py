"""Figures for deciding how to report noise (Toon 28 Oct 2026: see the real picture first).

Reads  difficulty_groups_cited.csv (output of group_cited.py)
Writes fig_noise.png, fig_noise_summary.json

noise_index = borderline + outlier share of minority examples (Napierala & Stefanowski
types, k = 5, HVDM, rare rule of sec. 5.2.1).
No threshold is drawn for noise_index. The only cited line is outlier > 0.20 (Napierala
& Stefanowski 2016, sec. 6.2), shown as a marker colour, not as a cut on noise_index.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
BLUE, ORANGE, GREY, RED = "#4C72B0", "#DD8452", "#8C8C8C", "#C44E52"


def main():
    g = pd.read_csv(HERE / "difficulty_groups_cited.csv")
    g = g[g.min_share_ge_half.astype(str).str.lower() != "true"].copy()
    g["outlier_heavy"] = g.outlier_heavy.astype(str).str.lower() == "true"
    b = g[g.task_type != "ovr"]
    o = g[g.task_type == "ovr"]

    fig, ax = plt.subplots(2, 2, figsize=(13, 9.5))

    # (a) histogram
    a = ax[0, 0]
    edges = np.linspace(0, 1, 21)
    a.hist([b.noise_index, o.noise_index], bins=edges, stacked=True, color=[BLUE, GREY],
           edgecolor="white", label=[f"binary + binarised (n={len(b)})", f"one-vs-rest, ours (n={len(o)})"])
    a.set_xlabel("noise_index (borderline + outlier share of minority)")
    a.set_ylabel("Tasks")
    a.set_title("(a) Distribution of noise_index", loc="left", fontsize=10)
    a.legend(fontsize=8, frameon=False)

    # (b) ECDF with quantiles
    a = ax[0, 1]
    qs = {}
    for sub, col, lab in [(g, GREY, f"all tasks (n={len(g)})"), (b, BLUE, f"binary + binarised (n={len(b)})")]:
        x = np.sort(sub.noise_index.values)
        a.step(x, np.arange(1, len(x) + 1) / len(x), where="post", color=col, lw=1.8, label=lab)
        qs[lab] = {str(q): round(float(sub.noise_index.quantile(q)), 3) for q in [.25, .5, .75]}
    for q in [.25, .5, .75]:
        v = b.noise_index.quantile(q)
        a.plot([v, v], [0, q], color=BLUE, ls=":", lw=1)
        a.text(v, 0.02, f"{v:.2f}", color=BLUE, fontsize=8, ha="center")
        a.axhline(q, color="#DDDDDD", lw=.8, zorder=0)
    a.set_xlim(0, 1); a.set_ylim(0, 1.02)
    a.set_xlabel("noise_index")
    a.set_ylabel("Share of tasks with value ≤ x")
    a.set_title("(b) Cumulative distribution (dotted: binary P25 / median / P75)", loc="left", fontsize=10)
    a.legend(fontsize=8, frameon=False, loc="lower right")

    # (c) noise vs IR
    a = ax[1, 0]
    for sub, mk, lab in [(o, "o", "one-vs-rest"), (b, "s", "binary + binarised")]:
        for heavy, col in [(False, BLUE), (True, RED)]:
            s = sub[sub.outlier_heavy == heavy]
            a.scatter(s.IR, s.noise_index, marker=mk, s=22, alpha=.7, color=col,
                      facecolors=col if mk == "s" else "none", linewidths=1,
                      label=f"{lab}, outlier {'> 0.20' if heavy else '≤ 0.20'} (n={len(s)})")
    a.set_xscale("log")
    for v in [1.5, 3, 9]:
        a.axvline(v, color="#BBBBBB", ls="--", lw=.8)
        a.text(v, 1.01, f"IR {v:g}", fontsize=7, color=GREY, ha="center", va="bottom")
    rho_all = g[["IR", "noise_index"]].rank().corr().iloc[0, 1]
    rho_b = b[["IR", "noise_index"]].rank().corr().iloc[0, 1]
    a.text(0.02, 0.97, f"Spearman ρ: all {rho_all:.2f} · binary {rho_b:.2f}", transform=a.transAxes,
           fontsize=8, va="top")
    a.set_ylim(-0.02, 1.06)
    a.set_xlabel("IR = n_maj / n_min from file (log; dashed = Fernández et al. 2008 bands)")
    a.set_ylabel("noise_index")
    a.set_title("(c) noise_index against IR", loc="left", fontsize=10)
    a.legend(fontsize=7, frameon=False, loc="lower right")

    # (d) composition per binary task
    a = ax[1, 1]
    s = b.sort_values("noise_index").reset_index(drop=True)
    xi = np.arange(len(s))
    a.bar(xi, s.borderline, color=ORANGE, width=1, label="borderline")
    a.bar(xi, s.outlier, bottom=s.borderline, color=RED, width=1, label="outlier")
    a.bar(xi, s.rare, bottom=s.borderline + s.outlier, color="#BBBBBB", width=1, label="rare (not in noise_index)")
    a.set_xlim(-.5, len(s) - .5); a.set_ylim(0, 1)
    a.set_xlabel(f"Binary + binarised tasks, sorted by noise_index (n={len(s)})")
    a.set_ylabel("Share of minority examples")
    a.set_title("(d) What noise_index is made of", loc="left", fontsize=10)
    a.legend(fontsize=8, frameon=False, loc="upper left")

    fig.suptitle("noise_index as a continuous measure — 284 verified tasks (no threshold applied)", fontsize=12)
    fig.tight_layout()
    fig.savefig(HERE / "fig_noise.png", dpi=150)

    out = {"n_all": int(len(g)), "n_binary_binarised": int(len(b)), "n_ovr": int(len(o)),
           "quantiles": qs, "spearman_IR_noise": {"all": round(float(rho_all), 3), "binary": round(float(rho_b), 3)},
           "outlier_heavy": {"all": int(g.outlier_heavy.sum()), "binary": int(b.outlier_heavy.sum())},
           "noise_eq_0": {"all": int((g.noise_index == 0).sum()), "binary": int((b.noise_index == 0).sum())},
           "binary_borderline_vs_outlier_median": {"borderline": round(float(b.borderline.median()), 3),
                                                   "outlier": round(float(b.outlier.median()), 3)}}
    (HERE / "fig_noise_summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
