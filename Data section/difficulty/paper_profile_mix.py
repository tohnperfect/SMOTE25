"""paper_profile_mix.py  which papers evaluate only flag-free or only flagged verified tasks (29 Oct 2026, Claude)
Reads difficulty_profile_final.csv (binary + binarised tasks, column papers). Papers with >= 3 verified tasks are
classified as: all tasks without a flag / all tasks with at least one flag / mixed. The '>= 3' cut is only so that
'all' means something; counts for >= 1 and >= 2 are also written so the choice can be seen.
Writes paper_profile_mix.json"""
import csv, json
from collections import defaultdict
P = [r for r in csv.DictReader(open("difficulty_profile_final.csv", encoding="utf-8")) if not r["origin"].startswith("one-vs")]
pp = defaultdict(list)
for r in P:
    for p in filter(None, r["papers"].split("; ")): pp[p].append(r["profile"])
out = {}
for m in (1, 2, 3):
    sel = {p: v for p, v in pp.items() if len(v) >= m}
    out[f"papers_with_at_least_{m}_tasks"] = dict(
        n=len(sel), all_flag_free=sorted(p for p, v in sel.items() if all(x == "none" for x in v)),
        all_flagged=sorted(p for p, v in sel.items() if all(x != "none" for x in v)),
        mixed=sum(1 for v in sel.values() if len(set(x == "none" for x in v)) == 2))
json.dump(out, open("paper_profile_mix.json", "w", encoding="utf-8"), indent=1)
print(json.dumps(out, indent=1))
