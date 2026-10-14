#!/usr/bin/env python3
"""Merge the 2026-10-14 dataset-name top-up into papers.json.

Every name added here is ai_draft (unverified) with no page_ref. The point of
this pass is to turn toon's job from typing names into ticking them.

Usage: python3 build/merge_topup.py papers.json build/topup_raw.json papers_v2.json
"""
import json, sys, copy

papers_in, topup_in, out_path = sys.argv[1], sys.argv[2], sys.argv[3]

P = json.load(open(papers_in))
T = json.load(open(topup_in))
META = T.pop("_meta")

# paper-level fields for the seven papers that had no record at all.
# Only fields the extraction actually reported are filled; everything else is
# left explicitly not-extracted rather than guessed.
NEW = {
 "INOS":          {"family":"oversampling","sources":["UCR"],
                   "origin":["Binarised"],"cls":"2"},
 "SMOTE-IPF":     {"family":"oversampling + filtering","sources":["Synthetic","UCI","KEEL"],
                   "origin":["Natural","Synthetic","Noise-injected"],"cls":"2"},
 "HDE":           {"family":"ensemble","sources":["KEEL","LibSVM"],
                   "origin":["Natural","Undersampled"],"cls":"2"},
 "NROMM":         {"family":"oversampling","sources":["KEEL"],
                   "origin":["Natural"],"cls":"3-10"},
 "GOIO":          {"family":"generative","sources":["UCI","imbalanced-learn","Synthetic"],
                   "origin":["Natural","Synthetic"],"cls":"2"},
 "DGOT":          {"family":"generative","sources":["UCI","imbalanced-learn"],
                   "origin":["Natural"],"cls":"2-11"},
 "Loyalty-SMOTE": {"family":"oversampling","sources":["UCI","KEEL","Kaggle"],
                   "origin":["Natural"],"cls":"2-n"},
}

by_key = {p["key"]: p for p in P}
added, updated = [], []

for key, t in T.items():
    flat, seen = [], set()
    for g in t["groups"]:
        for n in g["names"]:
            if n not in seen:
                seen.add(n); flat.append(n)
    n_named = sum(len(g["names"]) for g in t["groups"])
    n_agg   = sum(a["count"] for a in t["aggregates"] if not a.get("derived"))
    n_der   = sum(a["count"] for a in t["aggregates"] if a.get("derived"))

    patch = {
        "dsgroups":   t["groups"],
        "dsagg":      t["aggregates"],
        "dsn":        flat,
        "nd_named":   n_named,
        "nd_agg":     n_agg,
        "nd_derived": n_der,
        "nd_distinct_named": len(flat),
        "ds_table_ref":  t["table_ref"],
        "ds_status":     t["status"],
        "ds_note":       t["note"],
        "dsn_src":       "topup_2026_10_14 (ai_draft, unverified, no page_ref)",
    }

    if key in by_key:
        p = by_key[key]
        p["dsn_prev"] = p.get("dsn", [])          # keep the old partial list for audit
        p.update(patch)
        if t.get("n_claimed") is not None:
            p["nd_claimed"] = t["n_claimed"]
        updated.append(key)
    else:
        p = {"key": key,
             "title": t["title"], "authors": t["authors"],
             "year": t["year"], "venue": t["venue"], "task": t["task"],
             "nd": t.get("n_claimed"), "nd_claimed": t.get("n_claimed"),
             "ndnote": "", "srcdet": "", "crit": "",
             "irmin": None, "irmax": None, "irnote": "",
             "smin": None, "smax": None, "fmin": None, "fmax": None,
             "dom": [], "spec": [], "specnote": "", "prep": "",
             "results_granularity": t.get("results_granularity",""),
             "classifiers": t.get("classifiers",""),
             "metrics": t.get("metrics",""),
             "stat_test": t.get("stat_test",""),
             "ev": t.get("note",""),
             "conf": "names only - paper-level fields not yet extracted",
             "_new": True}
        p.update(NEW.get(key, {}))
        p.update(patch)
        P.append(p); by_key[key] = p
        added.append(key)

P = sorted(P, key=lambda x: (x.get("year") or 0, x["key"]))
json.dump(P, open(out_path,"w"), indent=1, ensure_ascii=False)

print("merged %d papers: %d updated, %d added" % (len(T), len(updated), len(added)))
print("added:", ", ".join(added))
print("total papers now:", len(P))

# ---- reconciliation report -------------------------------------------------
print("\n%-28s %7s %7s %7s %7s  %s" % ("paper","claimed","named","agg","gap","status"))
tot_claim = tot_named = tot_agg = 0
for key in sorted(T, key=lambda k: -(T[k].get("n_claimed") or 0)):
    t = T[key]; p = by_key[key]
    c = t.get("n_claimed") or 0
    n, a = p["nd_named"], p["nd_agg"]
    gap = c - n - a
    tot_claim += c; tot_named += n; tot_agg += a
    flag = "" if gap == 0 else ("  <-- %+d" % -gap)
    print("%-28s %7d %7d %7d %7d  %s%s" % (key, c, n, a, gap, t["status"], flag))
print("%-28s %7d %7d %7d %7d" % ("TOTAL", tot_claim, tot_named, tot_agg,
                                 tot_claim-tot_named-tot_agg))
