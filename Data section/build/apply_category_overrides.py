"""Copy category decisions made in build/full_extraction.py into the verified files (8 Nov 2026, Claude).

out/verified_datasets.csv and out/verified_outcomes.csv are out/full_*.csv plus verification columns (and, for outcomes,
the 19 Oct mapping audit). apply_verification.py cannot be rerun without erasing that audit, so when a category rule
changes in full_extraction.py (EXTERNAL: OREM-M Toy; RULE_NS: Toon 8 Nov) only the category columns are copied:
  datasets  how_obtained_final, how_basis           row by row (same order; paper and name must agree)
  outcomes  how_obtained, how_basis                 rows matched by (paper, dataset), in order; rows carrying a
                                                    19 Oct mapping_audit note are skipped (their values are audited)
Nothing else is touched. Prints every changed row. Then run build/sync_workbook_verified.py and the rest of the chain.
Run from Data section/ after python3 build/full_extraction.py:  python3 build/apply_category_overrides.py
"""
import csv, os
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)

def rd(f): return list(csv.DictReader(open(f, encoding="utf-8-sig")))
def wr(f, rows):
    with open(f, "w", newline="", encoding="utf-8-sig") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

F, V = rd("out/full_datasets.csv"), rd("out/verified_datasets.csv")
assert len(F) == len(V), "STOP: full_datasets and verified_datasets differ in length"
n = 0
for f, v in zip(F, V):
    assert (f["paper"], f["name"]) == (v["paper"], v["name"]), f"STOP: row order differs at {f['paper']} {f['name']}"
    if (f["how_obtained_final"], f["how_basis"]) != (v["how_obtained_final"], v["how_basis"]):
        print("dataset", v["paper"], "|", v["name"], "|", v["how_obtained_final"], "->", f["how_obtained_final"])
        v["how_obtained_final"], v["how_basis"] = f["how_obtained_final"], f["how_basis"]; n += 1
wr("out/verified_datasets.csv", V)

FO, VO = rd("out/full_outcome_rows.csv"), rd("out/verified_outcomes.csv")
assert len(FO) == len(VO), "STOP: outcome files differ in length"
m = 0
for f, v in zip(FO, VO):
    assert f["paper"] == v["paper"], f"STOP: outcome order differs at {f['paper']} {f['dataset']}"
    if v.get("mapping_audit", "").strip():          # rows corrected by the 19 Oct mapping audit keep their audited values
        continue
    assert f["dataset"] == v["dataset"], f"STOP: outcome order differs at {f['paper']} {f['dataset']}"
    if (f["how_obtained"], f["how_basis"]) != (v["how_obtained"], v["how_basis"]):
        print("outcome", v["paper"], "|", v["dataset"], "|", v["how_obtained"], "->", f["how_obtained"])
        v["how_obtained"], v["how_basis"] = f["how_obtained"], f["how_basis"]; m += 1
wr("out/verified_outcomes.csv", VO)
print(n, "dataset rows,", m, "outcome rows changed")
