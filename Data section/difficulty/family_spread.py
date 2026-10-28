"""Spread of difficulty among KEEL two-class files cut from the same source (Toon 28 Oct 2026).

Reads  difficulty_profile_final.csv (binary files only; family = leading letters of the KEEL file name for
       yeast, ecoli and glass, which is the same grouping as rule T1 gives for these files)
Writes family_spread.json (used in the Benchmark Landscape paragraph of the manuscript draft)
"""
import json
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent


def main():
    g = pd.read_csv(HERE / "difficulty_profile_final.csv")
    b = g[g.origin == "binary file"].copy()
    b["family"] = b.file.str.extract(r"^([a-z]+)")[0]
    out = {}
    for f in ["yeast", "ecoli", "glass"]:
        s = b[b.family == f]
        lo, hi = s.loc[s.noise_index.idxmin()], s.loc[s.noise_index.idxmax()]
        out[f] = dict(tasks=int(len(s)), n_features=sorted(set(int(x) for x in s.n_features_raw)),
                      IR=[round(float(s.IR.min()), 1), round(float(s.IR.max()), 1)],
                      noise=[round(float(s.noise_index.min()), 2), round(float(s.noise_index.max()), 2)],
                      lowest_noise=[lo.file, round(float(lo.noise_index), 2)], highest_noise=[hi.file, round(float(hi.noise_index), 2)],
                      profiles={k: int(v) for k, v in s.profile.value_counts().items()})
    # same minority shared by two files (yeast4 and yeast-0-5-6-7-9_vs_4: class 4, 51 examples)
    out["shared_minority_example"] = b[b.file.isin(["yeast4", "yeast-0-5-6-7-9_vs_4"])][["file", "N", "n_min", "noise_index"]].to_dict("records")
    json.dump(out, open(HERE / "family_spread.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
