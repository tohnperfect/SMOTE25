"""Rule NS (Toon 8 Nov 2026): "if the paper does not print the size but names the dataset, and the name is an original
dataset, count it as original".

Applied to entries whose category is `not stated`, whose paper prints no number of instances, and whose name was matched
to a public, unmodified file by name only (difficulty/verify_ext.py statuses V-name_only_ext and V-name_only_other: exact
name or a published alternative name of the same data set, never a KEEL split name). Such entries become `original`
with how_basis "rule NS". Entries with a printed size are not touched (Toon's rule speaks of the no-size case).

Reads  difficulty/verifiability_entries.csv, out/dataset_records.csv
Writes out/rule_ns_original.csv  (read by build/full_extraction.py; then run build/apply_category_overrides.py)
Run from Data section/:  python3 build/rule_ns.py
"""
import os
import pandas as pd
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
V = pd.read_csv("difficulty/verifiability_entries.csv", dtype=str).fillna("")
D = pd.read_csv("out/dataset_records.csv", dtype=str).fillna("")
M = D.merge(V[["record_id", "verif", "file", "file_src", "basis"]], on="record_id")
# category_by_reader = the reader's value; an entry already moved by this rule keeps qualifying on the next run
ns = M[((M.category == "not stated") | M.category_basis.str.startswith("rule NS")) & (M.n_instances == "")
       & M.verif.isin(["V-name_only_ext", "V-name_only_other"])]
out = ns[["record_id", "paper_key", "name_as_reported", "verif", "file", "file_src"]]
out.to_csv("out/rule_ns_original.csv", index=False)
print(len(out), "entries ->", "out/rule_ns_original.csv"); print(out.to_string(index=False))
