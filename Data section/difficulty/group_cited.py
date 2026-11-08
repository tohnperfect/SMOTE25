"""Difficulty profile with cited thresholds only (Toon 28 Oct 2026: no self-set cut-offs).

Reads  difficulty_measures.csv (measure.py; 291 tasks on 28 Oct, more after the 8 Nov mirrors) + version_notes.csv (Toon 28 Oct: keep flagged files, note
       that the paper gives only the name; copied from the earlier difficulty_groups.csv, which is now superseded)
Writes difficulty_groups_cited.csv, group_cited_summary.json

Axes (a task may carry several):
  small_disjuncts : rare >= 0.20
      Napierala & Stefanowski (2016) JIIS 46:563-597, sec. 6.2: rare-group datasets have
      "about 20% or more of rare examples" (read from the PDF, handoff 28 Oct).
  outlier_heavy   : outlier > 0.20
      same paper, sec. 6.2: outlier group "more than 20%". Reported separately because
      Toon merged overlap into noise and no cited cut-off exists for borderline+outlier.
  noise_index     : borderline + outlier, kept CONTINUOUS (no cited cut-off found).
  small_sample    : n_min / d < 10, d = raw number of features
      Jain, Duin & Mao (2000) IEEE TPAMI 22(1):4-37, sec. 3, p. 11: at least ten training
      samples per class per feature (n/d > 10) is good practice; they cite their ref. [80]
      (identity of [80] not yet checked). Variant with one-hot d is also reported.
Descriptor (not a difficulty axis):
  ir_band : <1.5 balanced-ish, 1.5-3 low, 3-9 medium, >9 high
      Fernandez, Garcia, del Jesus & Herrera (2008) Fuzzy Sets Syst., doi 10.1016/j.fss.2007.12.023,
      sec. 5 (p. 14 of the in-press version). Volume/pages still to be copied from the final issue.
No dimensionality class: Toon asked to profile dimensions first (dimension_profile.py).

rare follows Napierala & Stefanowski sec. 5.2.1 including the condition on the same-class
neighbour; neighbourhoods use HVDM (Wilson & Martinez 1997), as in Napierala & Stefanowski (measure.py revised 28 Oct).
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
RARE_T, OUTLIER_T, PER_FEATURE_T = 0.20, 0.20, 10
IR_BINS, IR_LABELS = [0, 1.5, 3, 9, np.inf], ["<=1.5", "1.5-3 low", "3-9 medium", ">9 high"]


def main():
    g = pd.read_csv(HERE / "difficulty_measures.csv")
    vn = pd.read_csv(HERE / "version_notes.csv")
    key = ["file", "source", "task_type", "minority_label", "N"]
    n0 = len(g)
    g = g.merge(vn, on=key, how="left", validate="one_to_one", indicator="_vn")
    assert len(g) == n0, (len(g), n0)
    # 8 Nov: tasks added by verify_ext.py have no row in version_notes.csv (28 Oct). Same rule as Toon's 28 Oct
    # decision: when every verifiable entry of the file gives only the name, note that the structure is the file's.
    ve = pd.read_csv(HERE / "verifiability_entries.csv")
    ve = ve[ve.verif.str.startswith("V-")]
    nameonly = ve.groupby(["file", "file_src"]).note_structure.apply(lambda s: s.notna().all() and (s.astype(str) != "").all())
    new = g._vn == "left_only"
    for i in g[new].index:
        k = (g.at[i, "file"], g.at[i, "source"])
        g.at[i, "version_note"] = ("paper reports only the name; structure taken from the named file (8 Nov)"
                                   if nameonly.get(k, False) else "")
    g = g.drop(columns="_vn")
    excluded = g.min_share_ge_half.astype(str).str.lower() == "true"
    g["small_disjuncts"] = g.rare >= RARE_T
    g["outlier_heavy"] = g.outlier > OUTLIER_T
    g["small_sample"] = g.n_min_per_feature < PER_FEATURE_T
    g["small_sample_onehot"] = g.n_min / g.n_features_encoded < PER_FEATURE_T
    g["ir_band"] = pd.cut(g.IR, IR_BINS, labels=IR_LABELS, right=True)  # ">9" = higher than 9, as in the paper.astype(str)
    axes = ["small_disjuncts", "outlier_heavy", "small_sample"]
    g["profile"] = g[axes].apply(lambda r: " + ".join(a for a in axes if r[a]) or "none of the cited axes", axis=1)
    g.loc[excluded, "profile"] = "excluded (minority share >= 50%)"
    g.to_csv(HERE / "difficulty_groups_cited.csv", index=False)

    G = g[~excluded]
    out = {"thresholds": {"rare_ge": RARE_T, "outlier_gt": OUTLIER_T, "n_min_per_feature_lt": PER_FEATURE_T,
                          "ir_bands": IR_LABELS}, "excluded": int(excluded.sum())}
    for name, sub in [("all_tasks", G), ("binary_and_binarized", G[G.task_type != "ovr"])]:
        out[name] = {
            "n_tasks": int(len(sub)),
            "axis_counts": {a: int(sub[a].sum()) for a in axes + ["small_sample_onehot"]},
            "profiles": {k: int(v) for k, v in sub.profile.value_counts().items()},
            "ir_band": {k: int(v) for k, v in sub.ir_band.value_counts().reindex(IR_LABELS).fillna(0).items()},
            "noise_index_quantiles": {q: round(float(sub.noise_index.quantile(q)), 3) for q in [.1, .25, .5, .75, .9]},
            "ir_band_by_profile": {p: {k: int(v) for k, v in s.ir_band.value_counts().items()}
                                   for p, s in sub.groupby("profile")},
        }
    (HERE / "group_cited_summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps({k: out[k] for k in ["all_tasks", "binary_and_binarized"]}, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
