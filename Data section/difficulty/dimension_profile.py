"""Dimensionality profile of the corpus (Toon, 28 Oct 2026: look at the data
before naming anything high- or low-dimensional).

Reads:
  out/dataset_records.csv          n_features as printed by each paper (1,654 entries)
  difficulty/difficulty_groups_cited.csv raw / encoded feature counts of verified tasks
Writes:
  difficulty/dimension_profile.json
  difficulty/dimension_by_name.csv   one row per normalised name
  difficulty/fig_dimension.png

Bins are display bins only (roughly log-spaced); they are NOT thresholds and
carry no high/low label. Units are kept separate: entry, name, paper, task.
Placeholder rows (Tomek) have no n_features and drop out with the missing values.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
BINS = [0, 5, 10, 20, 50, 100, 500, 1000, np.inf]
LABELS = ["1-5", "6-10", "11-20", "21-50", "51-100", "101-500", "501-1000", ">1000"]
PERIODS = [(1972, 2009), (2010, 2019), (2020, 2026)]  # same periods as Analysis D


def num(s):
    return pd.to_numeric(s.astype(str).str.replace(",", ""), errors="coerce")


def qs(x):
    x = x.dropna()
    return {q: float(x.quantile(q)) for q in [0.1, 0.25, 0.5, 0.75, 0.9]} | {
        "min": float(x.min()), "max": float(x.max()), "n": int(len(x))}


def binned(x):
    c = pd.cut(x.dropna(), BINS, labels=LABELS).value_counts().reindex(LABELS).fillna(0)
    n = int(c.sum())
    return {k: {"n": int(v), "pct": round(100 * v / n, 1)} for k, v in c.items()}


def shortest_interval(x, share):
    """Narrowest [lo, hi] of observed values that contains >= share of the values."""
    v = np.sort(x.dropna().values)
    k = int(np.ceil(share * len(v)))
    widths = v[k - 1:] - v[:len(v) - k + 1]
    i = int(np.argmin(widths))
    return {"lo": float(v[i]), "hi": float(v[i + k - 1]), "count": k, "of": int(len(v))}


def profile(x):
    return {"quantiles": qs(x), "bins": binned(x),
            "shortest_50pct": shortest_interval(x, .5),
            "shortest_80pct": shortest_interval(x, .8),
            "most_common_values": {str(int(k)): int(v) for k, v in
                                   x.dropna().value_counts().head(10).items()}}


def main():
    d = pd.read_csv(ROOT / "out" / "dataset_records.csv")
    d["nf"] = num(d.n_features)
    out = {"entries_total": int(len(d)), "entries_with_n_features": int(d.nf.notna().sum()),
           "entries_without_n_features": int(d.nf.isna().sum())}

    # 1. entry level (a popular dataset counts once per paper that uses it)
    out["entry_level"] = profile(d.nf)

    # 2. name level (one value per normalised name: median of printed values)
    rep = d[d.nf.notna()].groupby("normalized_name").agg(
        n_features_median=("nf", "median"), n_features_min=("nf", "min"),
        n_features_max=("nf", "max"), entries=("nf", "size"),
        papers=("paper_key", "nunique"))
    rep["values_differ"] = rep.n_features_min != rep.n_features_max
    rep.sort_values("entries", ascending=False).to_csv(HERE / "dimension_by_name.csv")
    out["name_level"] = profile(rep.n_features_median)
    out["name_level"]["names_with_n_features"] = int(len(rep))
    out["name_level"]["names_with_conflicting_printed_values"] = int(rep.values_differ.sum())

    # 3. paper level
    pp = d[d.nf.notna()].groupby("paper_key").nf.agg(["median", "max", "size"])
    out["paper_level"] = {
        "papers_with_any_n_features": int(len(pp)),
        "per_paper_median": profile(pp["median"]),
        "per_paper_max": profile(pp["max"]),
    }

    # 4. by category and period (entry level)
    out["by_category"] = {c: {"quantiles": qs(g.nf), "bins": binned(g.nf)}
                          for c, g in d.groupby("category") if g.nf.notna().any()}
    out["by_period"] = {}
    for lo, hi in PERIODS:
        g = d[(d.year >= lo) & (d.year <= hi)]
        out["by_period"][f"{lo}-{hi}"] = {"papers": int(g.paper_key.nunique()),
                                          "quantiles": qs(g.nf), "bins": binned(g.nf)}

    # 5. verified tasks: dimension from the files themselves
    t = pd.read_csv(HERE / "difficulty_groups_cited.csv")
    t = t[t.min_share_ge_half.astype(str).str.lower() != "true"]
    out["verified_tasks"] = {
        "n_tasks": int(len(t)),
        "raw": profile(t.n_features_raw.astype(float)),
        "encoded_one_hot": profile(t.n_features_encoded.astype(float)),
        "binary_and_binarized_raw": profile(
            t[t.task_type != "ovr"].n_features_raw.astype(float)),
    }

    # 6. how verifiability changes with printed dimension (entries with n_features)
    v = pd.read_csv(HERE / "verifiability_entries.csv")[["record_id", "verif"]]
    m = d[d.nf.notna()].merge(v, on="record_id", how="left")
    m["verified"] = m.verif.astype(str).str.startswith("V-")
    m["bin"] = pd.cut(m.nf, BINS, labels=LABELS)
    vb = m.groupby("bin", observed=False).verified.agg(["size", "sum"])
    out["verifiability_by_bin"] = {
        k: {"entries": int(r["size"]), "verified": int(r["sum"]),
            "pct": round(100 * r["sum"] / r["size"], 1) if r["size"] else None}
        for k, r in vb.iterrows()}
    hi = m[m.nf > 100]
    out["entries_over_100_features"] = {
        "entries": int(len(hi)), "papers": int(hi.paper_key.nunique()),
        "names": int(hi.normalized_name.nunique()),
        "max_papers_per_name": int(hi.groupby("normalized_name").paper_key.nunique().max()),
        "verif_status": {k: int(c) for k, c in hi.verif.value_counts().items()}}

    (HERE / "dimension_profile.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False))

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(1, 3, figsize=(15, 4.2))
    edges = np.logspace(0, np.log10(max(d.nf.max(), 10) * 1.1), 40)
    for a, (x, title) in zip(ax, [
            (d.nf, f"Entries (n={int(d.nf.notna().sum())})"),
            (rep.n_features_median, f"Distinct names (n={len(rep)})"),
            (t.n_features_raw.astype(float), f"Verified tasks, raw (n={len(t)})")]):
        a.hist(x.dropna(), bins=edges, color="#4C72B0", edgecolor="white")
        a.set_xscale("log")
        a.axvline(x.median(), color="#C44E52", ls="--", lw=1)
        a.text(x.median(), a.get_ylim()[1] * .92, f" median {x.median():g}",
               color="#C44E52", fontsize=9)
        a.set_title(title, fontsize=10)
        a.set_xlabel("Number of features (log scale)")
    ax[0].set_ylabel("Count")
    fig.suptitle("Printed / measured number of features in the SMOTE25 corpus", fontsize=11)
    fig.tight_layout()
    fig.savefig(HERE / "fig_dimension.png", dpi=150)

    s = out
    print(json.dumps({k: s[k] for k in ["entries_with_n_features", "entries_without_n_features"]}))
    for unit in ["entry_level", "name_level"]:
        print(unit, s[unit]["quantiles"], s[unit]["shortest_50pct"], s[unit]["shortest_80pct"])
        print("  bins", {k: v["n"] for k, v in s[unit]["bins"].items()})
        print("  common", s[unit]["most_common_values"])
    print("names conflicting", s["name_level"]["names_with_conflicting_printed_values"],
          "/", s["name_level"]["names_with_n_features"])
    print("paper max", s["paper_level"]["per_paper_max"]["quantiles"],
          {k: v["n"] for k, v in s["paper_level"]["per_paper_max"]["bins"].items()})
    print("paper median", s["paper_level"]["per_paper_median"]["quantiles"])
    for c, v in s["by_category"].items():
        print("cat", c, v["quantiles"]["n"], v["quantiles"][0.5], v["quantiles"][0.9], v["quantiles"]["max"])
    for p, v in s["by_period"].items():
        print("period", p, v["papers"], v["quantiles"]["n"], v["quantiles"][0.5], v["quantiles"][0.9],
              {k: x["pct"] for k, x in v["bins"].items()})
    print("verifiability", {k: (v["verified"], v["entries"]) for k, v in s["verifiability_by_bin"].items()})
    print("over100", s["entries_over_100_features"])
    for k in ["raw", "encoded_one_hot", "binary_and_binarized_raw"]:
        print("task", k, s["verified_tasks"][k]["quantiles"])


if __name__ == "__main__":
    main()
