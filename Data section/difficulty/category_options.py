"""Numbers behind the discussion of candidate data-type categories (28 Oct 2026).

Reads difficulty/difficulty_groups_cited.csv only (rare revised 28 Oct) (tasks with min_share_ge_half dropped).
Writes difficulty/category_options.json. No win/loss. Thresholds printed here are
candidate cut-offs for discussion, not decisions (Toon: no self-set thresholds).
"""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
COLS = ["n_features_raw", "n_features_encoded", "T2_points_per_dim", "T4_pca95_share",
        "min_sparsity_ratio", "N", "n_min", "IR", "n_min_per_feature", "safe",
        "noise_index", "rare", "outlier", "borderline", "n_subconcepts",
        "largest_subconcept_share"]


def flag(s):
    return s.astype(str).str.lower() == "true"


def main():
    g = pd.read_csv(HERE / "difficulty_groups_cited.csv")
    g = g[~flag(g.min_share_ge_half)].copy()
    for c in ["outlier_heavy", "small_disjuncts", "small_sample"]:
        g[c] = flag(g[c])
    # O = outlier > 0.20, D = rare >= 0.20, S = n_min/d < 10 (cited cut-offs, group_cited.py)
    g["combo"] = (g.outlier_heavy.map({True: "O", False: "-"})
                  + g.small_disjuncts.map({True: "D", False: "-"})
                  + g.small_sample.map({True: "S", False: "-"}))
    out = {
        "n_tasks": int(len(g)),
        "task_types": {k: int(v) for k, v in g.task_type.value_counts().items()},
        "sources": {k: int(v) for k, v in g.source.value_counts().items()},
        "quantiles": {c: {q: round(float(g[c].quantile(float(q))), 3)
                          for q in ["0.1", "0.25", "0.5", "0.75", "0.9"]} for c in COLS},
        "max": {c: round(float(g[c].max()), 3) for c in COLS},
        "candidate_counts": {
            "features_encoded_ge_100": int((g.n_features_encoded >= 100).sum()),
            "features_encoded_ge_50": int((g.n_features_encoded >= 50).sum()),
            "IR_gt_9": int((g.IR > 9).sum()),
            "IR_ge_50": int((g.IR >= 50).sum()),
            "rare_ge_0.2": int((g.rare >= .2).sum()),
            "outlier_gt_0.2": int((g.outlier > .2).sum()),
            "safe_ge_0.5": int((g.safe >= .5).sum()),
            "n_min_per_feature_lt_10": int((g.n_min_per_feature < 10).sum()),
            "n_min_lt_20": int((g.n_min < 20).sum()),
            "min_sparsity_ratio_gt_1": int((g.min_sparsity_ratio > 1).sum()),
            "has_nominal_features": int((g.n_features_encoded > g.n_features_raw).sum()),
        },
        "axis_combinations_all": {k: int(v) for k, v in g.combo.value_counts().items()},
        "axis_combinations_binary_binarized": {
            k: int(v) for k, v in g[g.task_type != "ovr"].combo.value_counts().items()},
        "spearman": g[COLS].rank().corr().round(3).loc[
            ["IR", "noise_index", "rare", "n_features_encoded", "T2_points_per_dim",
             "min_sparsity_ratio", "n_min_per_feature"]].to_dict(orient="index"),
    }
    (HERE / "category_options.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out["candidate_counts"], indent=2))


if __name__ == "__main__":
    main()
