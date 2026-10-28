"""Reference collection of verified tasks to recommend to readers (handoff item 15, 28 Oct 2026).
No experiment is run; every value is copied from files that already exist.

Reads  difficulty_profile_final.csv  (profile_final.py; one row per verified task)
       keel_official_check.csv       (72 KEEL files compared with the official KEEL table)
       verifiability_entries.csv     (entry -> file, to find the names the corpus prints for a file)
       ../out/dataset_families.csv   via ../build/families.py (Toon's family rule T1)
Writes reference_collection.csv           one row per selected task, with the rule that selected it
       reference_collection_summary.json  coverage of the selection against all 113 tasks
       reference_collection_proposal.tex  the table inserted in the manuscript (tab:data-reference)

Universe: the 113 binary and binarised tasks. One-vs-rest tasks (171) are our construction and no paper
evaluated them, so they are not recommended.
Selection uses no threshold of our own. The only cut-offs are the cited ones already in the profile:
  flags    small disjuncts rare >= 0.20, outliers > 0.20 (Napierala & Stefanowski 2016, sec. 6.2),
           small sample n_min/d < 10 (Jain, Duin & Mao 2000, sec. 3)
  IR band  <=1.5 / 1.5-3 / 3-9 / >9 (Fernandez et al. 2008, sec. 5)
Cell = flag profile x IR band (every non-empty cell is covered).
  core    the task in the cell used by most corpus entries (ties: more papers, then name)  -> comparability
  low     the task in the cell with the lowest noise_index  (ties: more entries, then name) -> spread
  high    the task in the cell with the highest noise_index (ties: more entries, then name) -> spread
A task chosen by several roles is one row.
Run from Data section/difficulty:  python3 reference_collection.py
"""
import csv, json, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "build"))
import families as FAM  # noqa: E402

IR_ORDER = ["<=1.5", "1.5-3 low", "3-9 medium", ">9 high"]
PROFILE_ORDER = ["none", "small_sample", "small_sample + outlier_flag",
                 "small_disjuncts + small_sample + outlier_flag"]
CITE = {"flags": "napierala2016types (sec. 6.2); jain2000statistical (sec. 3)",
        "ir_band": "fernandez2008study (sec. 5)"}


def load():
    rows = [r for r in csv.DictReader(open(HERE / "difficulty_profile_final.csv", encoding="utf-8"))
            if not r["origin"].startswith("one-vs")]
    for r in rows:
        for k in ("N", "n_min", "n_features_raw", "entries"):
            r[k] = int(float(r[k]))
        for k in ("IR", "noise_index", "borderline", "outlier", "rare", "safe", "n_min_per_feature"):
            r[k] = float(r[k])
        r["n_papers"] = len([p for p in r["papers"].split("; ") if p])
        r["task"] = r["file"] + (f" [minority: {r['minority_label'].strip()}]"
                                 if r["origin"].startswith("binarised") else "")
    dup = {f for f, c in Counter(r["file"] for r in rows if not r["origin"].startswith("binarised")).items() if c > 1}
    for r in rows:  # e.g. hepatitis: PMLB file (155 rows) and UCI file (80 rows after dropping missing values)
        if r["file"] in dup:
            r["task"] += f" ({r['source']}, N={r['N']})"
    return rows


def main():
    rows = load()
    assert len(rows) == 113, len(rows)
    keel = {r["file"]: r for r in csv.DictReader(open(HERE / "keel_official_check.csv", encoding="utf-8"))}
    names = {}
    for e in csv.DictReader(open(HERE / "verifiability_entries.csv", encoding="utf-8")):
        if e["verif"].startswith("V") and e["file"]:
            names.setdefault(e["file"], Counter())[e["name"].strip().lower()] += 1
    for r in rows:
        fams = Counter()
        for n, c in names.get(r["file"], {}).items():
            fams[FAM.family_of(n)] += c
        r["family_t1"] = FAM.display(fams.most_common(1)[0][0]) if fams else ""
        r["printed_names"] = "; ".join(n for n, _ in names.get(r["file"], Counter()).most_common())
        k = keel.get(r["file"])
        r["official_check"] = ("not compared" if k is None else
                               "N/d/IR match official KEEL table" if all(k[c] == "True" for c in ("N_ok", "F_ok", "IR_ok"))
                               else f"N {k['N_ok']} d {k['F_ok']} IR {k['IR_ok']} (IR {k['IR']} vs {k['IR_official']})")

    cells = {}
    for r in rows:
        cells.setdefault((r["profile"], r["ir_band"]), []).append(r)
    chosen = {}
    for (prof, band), sub in cells.items():
        picks = {
            "core": max(sub, key=lambda r: (r["entries"], r["n_papers"], [-ord(c) for c in r["task"]])),
            "low": min(sub, key=lambda r: (r["noise_index"], -r["entries"], r["task"])),
            "high": max(sub, key=lambda r: (r["noise_index"], r["entries"], [-ord(c) for c in r["task"]])),
        }
        for role, r in picks.items():
            c = chosen.setdefault(r["task"], {"row": r, "roles": []})
            c["roles"].append(role)

    order = lambda c: (PROFILE_ORDER.index(c["row"]["profile"]), IR_ORDER.index(c["row"]["ir_band"]),
                       c["row"]["noise_index"])
    out = []
    for c in sorted(chosen.values(), key=order):
        r = c["row"]
        out.append({
            "roles": "+".join(c["roles"]), "profile": r["profile"], "ir_band": r["ir_band"],
            "cell_tasks": len(cells[(r["profile"], r["ir_band"])]),
            "task": r["task"], "file": r["file"], "minority_label": r["minority_label"].strip(),
            "origin": r["origin"], "source": r["source"], "family_t1": r["family_t1"],
            "N": r["N"], "n_min": r["n_min"], "d": r["n_features_raw"], "IR": r["IR"],
            "n_min_per_feature": r["n_min_per_feature"], "noise_index": r["noise_index"],
            "borderline": r["borderline"], "outlier": r["outlier"], "rare": r["rare"], "safe": r["safe"],
            "entries": r["entries"], "n_papers": r["n_papers"], "papers": r["papers"],
            "printed_names": r["printed_names"], "official_check": r["official_check"],
            "version_note": r["version_note"],
            "provenance": "difficulty_profile_final.csv row file=%s minority=%s; measures: measure.py (HVDM, k=5)"
                          % (r["file"], r["minority_label"].strip()),
        })
    with open(HERE / "reference_collection.csv", "w", encoding="utf-8", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader(); w.writerows(out)

    def rng(xs):
        return [round(min(xs), 3), round(max(xs), 3)]
    allr, sel = rows, [c["row"] for c in chosen.values()]
    fam_sel = Counter(r["family_t1"] for r in sel)
    summ = {
        "universe": {"tasks": len(allr), "entries": sum(r["entries"] for r in allr),
                     "cells_nonempty": len(cells), "families_t1": len({r["family_t1"] for r in allr})},
        "selection": {"tasks": len(sel), "entries": sum(r["entries"] for r in sel),
                      "core": sum("core" in c["roles"] for c in chosen.values()),
                      "cells_covered": len({(r["profile"], r["ir_band"]) for r in sel}),
                      "families_t1": len(fam_sel),
                      "families_with_more_than_one_task": {k: v for k, v in fam_sel.items() if v > 1},
                      "sources": dict(Counter(r["source"] for r in sel)),
                      "official_check": dict(Counter(o["official_check"] for o in out)),
                      "version_note": sum(bool(r["version_note"]) for r in sel)},
        "ranges_universe_vs_selection": {k: {"all": rng([r[k] for r in allr]), "selected": rng([r[k] for r in sel])}
                                         for k in ("noise_index", "IR", "N", "n_features_raw", "n_min", "n_min_per_feature")},
        "cells": {f"{p} | {b}": {"tasks": len(s), "selected": sorted(o["task"] for o in out
                                                                       if o["profile"] == p and o["ir_band"] == b)}
                  for (p, b), s in sorted(cells.items(), key=lambda kv: (PROFILE_ORDER.index(kv[0][0]),
                                                                        IR_ORDER.index(kv[0][1])))},
        "rules": {"universe": "binary + binarised tasks in difficulty_profile_final.csv (OvR excluded)",
                  "cell": "flag profile x IR band; cut-offs cited only: " + json.dumps(CITE),
                  "core": "most corpus entries in the cell; ties more papers, then task name",
                  "low/high": "lowest / highest noise_index in the cell; ties more entries, then task name",
                  "own_thresholds": "none"},
        "status": "Claude 28 Oct 2026; adopted 29 Oct 2026 under Toon's delegation; in the manuscript (tab:data-reference)",
    }
    (HERE / "reference_collection_summary.json").write_text(json.dumps(summ, indent=2, ensure_ascii=False),
                                                            encoding="utf-8")

    short = {"none": "none", "small_sample": "S", "small_sample + outlier_flag": "S+O",
             "small_disjuncts + small_sample + outlier_flag": "D+S+O"}
    tex = ["% Table generated by difficulty/reference_collection.py (do not edit by hand); in data-section-draft.tex since 29 Oct 2026.",
           "\\begin{table}[t]\\centering\\small",
           "\\caption{A Reference Collection of Verifiable Two-Class Tasks. One row per selected task; "
           "Role: core = most used task in its cell, low/high = lowest/highest noise index in its cell. "
           "Profile: S small sample, O outliers, D small disjuncts; Noise: noise index; Entries: corpus entries that use the task.}",
           "\\label{tab:data-reference}",
           "\\begin{tabular}{@{}llllrrrrrr@{}}", "\\toprule",
           "Task & Role & Profile & IR band & $N$ & $N_{\\min}$ & $d$ & IR & Noise & Entries\\\\", "\\midrule"]
    BAND_TEX = {"<=1.5": "$\\leq$1.5", "1.5-3 low": "1.5--3", "3-9 medium": "3--9", ">9 high": "$>$9"}
    esc = lambda s: s.replace("_", "\\_").replace("&", "\\&")
    for o in out:
        tex.append(f"\\texttt{{{esc(o['task'])}}} & {o['roles']} & {short[o['profile']]} & "
                   f"{BAND_TEX[o['ir_band']]} & "
                   f"{o['N']:,} & {o['n_min']:,} & {o['d']} & {o['IR']:.1f} & {o['noise_index']:.2f} & {o['entries']}\\\\")
    tex += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    (HERE / "reference_collection_proposal.tex").write_text("\n".join(tex) + "\n", encoding="utf-8")
    print(json.dumps(summ["selection"], ensure_ascii=False))


if __name__ == "__main__":
    main()
