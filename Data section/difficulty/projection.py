"""2-D pictures for the Atlas 'measured difficulty' tab (Toon 28 Oct 2026).

(1) Real tasks: every binary / binarised verifiable task (same rows and minority as measure.py, via
    measure.iter_tasks). Each minority example gets its Napierala type computed by measure.point_types on
    the full HVDM embedding; the picture is a PCA projection of that embedding to 2-D. The projection
    can put points together that are far apart in the full space, so the colours, not the positions,
    carry the measurement. Majority points are subsampled to MAJ_CAP for display (seeded); all minority
    points are kept.
(2) Illustrations: small synthetic 2-D sets, one per characteristic, labelled with the same
    point_types rule. They are drawings to explain the terms, not data from the corpus.
Writes projections.json (read by build/make_atlas.py). Needs the mirror files in src/ (fetch_mirrors.sh).
"""
import json

import numpy as np
from sklearn.decomposition import PCA

import measure as M

MAJ_CAP, SEED = 700, 0


def norm2(P):
    """Centre on the median and scale each axis by its 98th percentile of |value|; points beyond are drawn on
    the frame edge (clipped to [-1, 1]) so a few extreme points do not squash the rest. Display only."""
    P = P - np.median(P, 0)
    s = np.quantile(np.abs(P), 0.98, axis=0); s[s == 0] = 1.0
    return np.round(np.clip(P / s, -1, 1), 3)


def picture(XH, ymin, rng):
    I, mi, same, ptype = M.point_types(XH, ymin)
    pca = PCA(n_components=2, random_state=SEED).fit(XH)
    P = norm2(pca.transform(XH))
    maj = np.where(~ymin)[0]
    if len(maj) > MAJ_CAP:
        maj = np.sort(rng.choice(maj, MAJ_CAP, replace=False))
    return dict(maj=P[maj].tolist(), min=[[*P[g].tolist(), t] for g, t in zip(mi, ptype)],
                maj_total=int((~ymin).sum()), maj_shown=int(len(maj)),
                pca_var=[round(float(v), 3) for v in pca.explained_variance_ratio_],
                types={k: int((ptype == k).sum()) for k in "SBRO"})


def illustrations(rng):
    def blob(c, s, n):
        return rng.normal(c, s, size=(n, 2))
    sets = {}
    maj = blob([0, 0], 1.0, 300)
    sets["safe"] = (maj, blob([3.6, 3.6], 0.45, 40))
    sets["borderline"] = (maj, blob([1.1, 1.1], 0.55, 40))
    sets["rare"] = (rng.uniform(-3, 3, size=(320, 2)),
                    np.vstack([c + rng.normal(0, 0.06, size=(2, 2)) for c in rng.uniform(-2.6, 2.6, size=(12, 2))]))
    sets["outlier"] = (rng.uniform(-3, 3, size=(320, 2)), rng.uniform(-2.8, 2.8, size=(14, 2)))
    sets["noise"] = (maj, np.vstack([blob([1.0, 1.0], 0.6, 26), rng.uniform(-2.5, 2.5, size=(10, 2))]))
    sets["small_sample"] = (maj, blob([2.6, 2.6], 0.6, 6))
    sets["imbalance"] = (blob([0, 0], 1.0, 600), blob([2.4, 2.4], 0.6, 12))
    out = {}
    for k, (A, B) in sets.items():
        X = np.vstack([A, B]); ymin = np.r_[np.zeros(len(A), bool), np.ones(len(B), bool)]
        XH = X / (4 * X.std(0, ddof=1))  # HVDM on numeric attributes
        _, mi, _, ptype = M.point_types(XH, ymin)
        P = norm2(X)
        out[k] = dict(maj=P[~ymin].tolist(), min=[[*P[g].tolist(), t] for g, t in zip(mi, ptype)],
                      n_maj=int(len(A)), n_min=int(len(B)),
                      types={t: int((ptype == t).sum()) for t in "SBRO"})
    return out


def main():
    rng = np.random.default_rng(SEED)
    real = {}
    for f, src, how, X, dt, nominal, t, lab, ymin, who, nfeat, keep in M.iter_tasks():
        if t == "ovr" or ymin.mean() >= 0.5:
            continue
        XH = M.hvdm_embed(dt, nominal, ymin)
        real[f"{f}|{src}|{t}|{lab}|{int(len(ymin))}"] = picture(XH, ymin, rng)
    out = dict(meta=dict(maj_cap=MAJ_CAP, seed=SEED, k=M.K, distance="HVDM (Wilson & Martinez 1997)",
                         projection="PCA(2) of the HVDM embedding; types computed in full space; axes scaled by 98th percentile, beyond = clipped to frame"),
               real=real, illustrations=illustrations(np.random.default_rng(SEED + 1)))
    json.dump(out, open("projections.json", "w"), separators=(",", ":"))
    print(len(real), "real tasks;", {k: v["types"] for k, v in out["illustrations"].items()})


if __name__ == "__main__":
    main()
