"""Shared access to Toon's dataset/family rule T1 (28 Oct 2026). Single source: out/dataset_families.csv,
written by build/family_rule.py. Every script that counts datasets or families imports this module so
that all counts agree.

  dataset_key(name)  rule 1: the normalised name without '-', '_', spaces and dots (page-blocks = pageblocks)
  family_of(name)    rule 2/3: the main set a numbered or split version belongs to (yeast4 -> yeast)
  display(key)       the most used normalised name spelling for a dataset key or family (for tables)
"""
import csv, os, re
from collections import Counter

_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROWS = list(csv.DictReader(open(os.path.join(_HERE, "out", "dataset_families.csv"), encoding="utf-8")))
_BY = {r["normalized_name"]: r for r in _ROWS}
RULE = ("T1 (Toon, 28 Oct 2026): names differing only by '-', '_', spaces or dots are one dataset; numbered or split "
        "versions belong to their main set's family; non-standard names are not merged (build/family_rule.py)")


def _key(n):
    return re.sub(r"[-_ .]", "", n)


def dataset_key(n):
    return _BY[n]["dataset_key"] if n in _BY else _key(n)


def family_of(n):
    return _BY[n]["family"] if n in _BY else _key(n)


_spell = {}
for r in _ROWS:
    for k in (r["dataset_key"], r["family"]):
        _spell.setdefault(k, Counter())[r["normalized_name"]] += int(r["entries"])


def display(k):
    """Most used spelling among names whose dataset key equals k; the key itself if no name has it (e.g. krvsk)."""
    c = _spell.get(k, Counter())
    exact = [n for n in c if _key(n) == k]
    return max(exact, key=lambda n: (c[n], -len(n))) if exact else k
