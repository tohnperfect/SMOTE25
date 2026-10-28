"""Figure for the manuscript subsection on measured difficulty (Toon 28 Oct 2026).

Reads  difficulty_profile_final.csv, dimension_profile.json
Writes ../manuscript/figures/data-difficulty.pdf (for LaTeX) and .png (for the Atlas manuscript tab)

(a) noise index of every binary / binarised verifiable task, one row per flag profile; marker area
    ~ number of corpus entries that use the task; vertical bar = median. No threshold is drawn.
(b) number of features printed for each dataset entry (display bins, not thresholds), with the
    entries that could be verified and measured overlaid.
Greyscale-safe: profile rows differ by position, verified bars by fill.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "manuscript" / "figures"
NAMES = {"none": "No flag", "small_sample": "Small sample",
         "small_sample + outlier_flag": "Small sample + outliers",
         "small_disjuncts + small_sample + outlier_flag": "Small disjuncts + small sample\n+ outliers"}


def main():
    g = pd.read_csv(HERE / "difficulty_profile_final.csv")
    b = g[g.origin != "one-vs-rest (ours)"]
    dim = json.load(open(HERE / "dimension_profile.json"))
    plt.rcParams.update({"font.size": 8, "axes.spines.top": False, "axes.spines.right": False,
                         "pdf.fonttype": 42})
    fig, ax = plt.subplots(1, 2, figsize=(6.8, 2.8), gridspec_kw={"width_ratios": [1.45, 1]})

    a = ax[0]
    order = [p for p in ["small_disjuncts + small_sample + outlier_flag", "small_sample + outlier_flag",
                         "small_sample", "none"] if p in set(b.profile)]
    rng = np.random.default_rng(0)
    for i, p in enumerate(order):
        s = b[b.profile == p]
        y = i + rng.uniform(-0.22, 0.22, len(s))
        a.scatter(s.noise_index, y, s=6 + 3 * s.entries, facecolor="#9a9a9a" if p != "none" else "white",
                  edgecolor="#333333", linewidth=0.5, alpha=0.85, zorder=3)
        med = s.noise_index.median()
        a.plot([med, med], [i - 0.33, i + 0.33], color="black", lw=1.6, zorder=4)
        a.text(1.02, i, f"n={len(s)}\nmed {med:.2f}", va="center", fontsize=6.5, transform=a.get_yaxis_transform())
    a.set_yticks(range(len(order)), [NAMES[p] for p in order])
    a.set_xlim(-0.02, 1.0); a.set_ylim(-0.6, len(order) - 0.4)
    a.set_xlabel("Noise index (share of minority examples\nthat are borderline or outliers)")
    a.set_title("(a) Verified binary tasks by flag profile", fontsize=8, loc="left")
    a.grid(axis="x", color="#dddddd", lw=0.5, zorder=0)

    a = ax[1]
    bins = list(dim["entry_level"]["bins"].keys())
    tot = [dim["entry_level"]["bins"][k]["n"] for k in bins]
    ver = [dim["verifiability_by_bin"][k]["verified"] for k in bins]
    x = np.arange(len(bins))
    a.bar(x, tot, color="white", edgecolor="#333333", lw=0.6, label="all entries")
    a.bar(x, ver, color="#9a9a9a", edgecolor="#333333", lw=0.6, label="verified, measured")
    a.set_xticks(x, bins, rotation=45, ha="right")
    a.set_ylabel("Dataset entries")
    a.set_xlabel("Number of features printed")
    a.set_title("(b) Features per entry", fontsize=8, loc="left")
    a.set_ylim(0, max(tot) * 1.32)
    a.legend(frameon=False, fontsize=6.5, loc="upper right", bbox_to_anchor=(1.0, 1.0))
    fig.tight_layout(w_pad=3.0)
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "data-difficulty.pdf")
    fig.savefig(OUT / "data-difficulty.png", dpi=200)
    print("ok", OUT / "data-difficulty.pdf")


if __name__ == "__main__":
    main()
