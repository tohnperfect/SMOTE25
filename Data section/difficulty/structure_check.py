"""Descriptive numbers for Toon's proposed manuscript structure (28 Oct 2026).

Reads only:
  out/dataset_records.csv          (1,654 entries; placeholder rows kept, flagged)
  difficulty/difficulty_groups_cited.csv (measured tasks; tasks with min_share_ge_half dropped)
Writes:
  difficulty/structure_check.json

No win/loss is used (paused by Toon 28 Oct). IR here is the single definition
n_maj / n_min computed from the files, not the printed IR.
Caveat: borderline/rare in measure.py do not yet apply Napierala &
Stefanowski's extra condition for 'rare' (handoff 28 Oct), so noise_index and
rare may change after that fix.
"""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", ""), errors="coerce")


def entry_level():
    d = pd.read_csv(ROOT / "out" / "dataset_records.csv")
    out = {"entries_total": int(len(d))}
    inst, feat, ncls = num(d.n_instances), num(d.n_features), num(d.n_classes)
    out["instances"] = {
        "reported": int(inst.notna().sum()),
        "q25_q50_q75": [float(v) for v in inst.quantile([.25, .5, .75])],
        "lt_1000": int((inst < 1000).sum()),
        "1000_9999": int(((inst >= 1000) & (inst < 10000)).sum()),
        "ge_10000": int((inst >= 10000).sum()),
    }
    out["features"] = {
        "reported": int(feat.notna().sum()),
        "q25_q50_q75": [float(v) for v in feat.quantile([.25, .5, .75])],
        "lt_20": int((feat < 20).sum()),
        "20_99": int(((feat >= 20) & (feat < 100)).sum()),
        "ge_100": int((feat >= 100).sum()),
    }
    out["classes"] = {
        "eq_2": int((ncls == 2).sum()),
        "gt_2": int((ncls > 2).sum()),
        "not_reported": int(ncls.isna().sum()),
    }
    out["category_counts"] = {k: int(v) for k, v in d.category.value_counts().items()}
    ct = pd.crosstab(d.category, ncls.map(lambda v: "not_reported" if pd.isna(v)
                                           else ("two" if v == 2 else "more")))
    out["category_by_classes"] = {c: {k: int(v) for k, v in row.items()}
                                  for c, row in ct.iterrows()}
    return out


def task_level():
    g = pd.read_csv(HERE / "difficulty_groups_cited.csv")
    g = g[g.min_share_ge_half.astype(str).str.lower() != "true"]
    cols = ["IR", "noise_index", "rare", "kDN_min", "n_min_per_feature", "safe"]
    res = {}
    for name, sub in [("all_tasks", g), ("binary_and_binarized", g[g.task_type != "ovr"])]:
        r = sub[cols].rank().corr().loc["IR"].drop("IR")
        s = sub.copy()
        s["ir_bin"] = pd.cut(s.IR, [0, 3, 9, 20, 50, float("inf")]).astype(str)
        tab = s.groupby("ir_bin", sort=False).agg(
            n=("IR", "size"), noise_median=("noise_index", "median"),
            safe_median=("safe", "median"), rare_median=("rare", "median"))
        res[name] = {
            "n_tasks": int(len(sub)),
            "task_types": {k: int(v) for k, v in sub.task_type.value_counts().items()},
            "spearman_with_IR": {k: round(float(v), 3) for k, v in r.items()},
            "by_IR_bin": {i: {k: (int(v) if k == "n" else round(float(v), 3))
                              for k, v in row.items()} for i, row in tab.iterrows()},
        }
    return res


def main():
    out = {"entry_level": entry_level(), "task_level": task_level()}
    (HERE / "structure_check.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
