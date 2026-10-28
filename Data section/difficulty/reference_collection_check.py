"""Independent check of reference_collection.csv (28 Oct 2026). Recomputes the selection with pandas
from difficulty_profile_final.csv and compares every copied value. Exit 1 on any mismatch."""
import sys
from pathlib import Path
import pandas as pd

H = Path(__file__).resolve().parent
P = pd.read_csv(H / "difficulty_profile_final.csv")
P = P[~P.origin.str.startswith("one-vs")].copy()
P["minority_label"] = P.minority_label.fillna("").astype(str).str.strip()
P["n_papers"] = P.papers.str.split("; ").map(len)
S = pd.read_csv(H / "reference_collection.csv", keep_default_na=False)
K = pd.read_csv(H / "keel_official_check.csv").set_index("file")
fails = []
ok = lambda c, m: None if c else fails.append(m)

ok(len(P) == 113, "universe != 113")
# 1 every selected row equals its source row
for _, s in S.iterrows():
    src = P[(P.file == s.file) & (P.minority_label == str(s.minority_label)) & (P.source == s.source)]
    ok(len(src) == 1, f"{s.task}: source rows {len(src)}"); src = src.iloc[0]
    for a, b in [("N", "N"), ("n_min", "n_min"), ("d", "n_features_raw"), ("entries", "entries")]:
        ok(int(s[a]) == int(src[b]), f"{s.task} {a}")
    for c in ["IR", "noise_index", "borderline", "outlier", "rare", "safe", "n_min_per_feature"]:
        ok(abs(float(s[c]) - float(src[c])) < 1e-9, f"{s.task} {c}")
    ok(s.profile == src.profile and s.ir_band == src.ir_band, f"{s.task} cell")
    ok(abs(src.borderline + src.outlier - src.noise_index) < 0.0015, f"{s.task} noise != b+o")
    if s.file in K.index:
        k = K.loc[s.file]
        ok((s.official_check.startswith("N/d/IR match")) == bool(k.N_ok and k.F_ok and k.IR_ok), f"{s.task} official")
        ok(int(k.N) == int(s.N), f"{s.task} official N")
    else:
        ok(s.official_check == "not compared", f"{s.task} official absent")
# 2 recompute the selection independently
P["task"] = P.apply(lambda r: r.file + (f" [minority: {r.minority_label}]" if r.origin.startswith("binarised") else ""), axis=1)
_d = P[~P.origin.str.startswith("binarised")].file.value_counts()
_d = set(_d[_d > 1].index)
P["task"] = P.apply(lambda r: r.task + (f" ({r.source}, N={r.N})" if r.file in _d else ""), axis=1)
want = {}
for (p, b), g in P.groupby(["profile", "ir_band"]):
    core = g.sort_values(["entries", "n_papers", "task"], ascending=[False, False, True]).iloc[0].task
    low = g.sort_values(["noise_index", "entries", "task"], ascending=[True, False, True]).iloc[0].task
    high = g.sort_values(["noise_index", "entries", "task"], ascending=[False, False, True]).iloc[0].task
    for role, t in [("core", core), ("low", low), ("high", high)]:
        want.setdefault(t, []).append(role)
got = {r.task: r.roles.split("+") for _, r in S.iterrows()}
ok(set(want) == set(got), f"task sets differ: {set(want) ^ set(got)}")
for t in want:
    ok(sorted(want[t]) == sorted(got.get(t, [])), f"{t} roles {want[t]} vs {got.get(t)}")
ok(S.groupby(["profile", "ir_band"]).ngroups == P.groupby(["profile", "ir_band"]).ngroups, "cells not all covered")
print("checks", "FAIL" if fails else "PASS", len(S), "rows")
for f in fails: print(" -", f)
sys.exit(1 if fails else 0)
