"""Source-family rule for dataset names (Toon decision T1, 28 Oct 2026).

Toon's rule:
  1. Names that differ only by '-', '_', spaces or dots are the same dataset: page-blocks = pageblocks = page blocks.
  2. A numbered / split version of a main set is a SUBSET of that set and belongs to its family:
     yeast4, yeast-2_vs_4, yeast-0-5-6-7-9_vs_4 -> family yeast.
  3. Non-standard names are NOT merged: glass identification stays apart from glass.
Implementation (written so that every merge can be traced):
  key(n)  = normalised name (analyse_dataset_usage.norm) without '-', '_', ' ', '.'                      (rule 1)
  parent  = the longest OTHER corpus key c that is a prefix of key(n) such that
            (a) the remainder contains a split marker (a digit or 'vs'),
            (b) the boundary is clean: if c ends in a letter, the original name has a separator or a digit
                right after c, or the remainder starts with 'vs'; if c ends in a digit, the remainder does
                not start with a digit (aids 50000 is not a subset of aids 5000),
            (c) the printed numbers of features do not contradict it: when both medians are printed they
                differ by at most 1 (car1 with 9,182 features is not a split of car with 6)              (rule 2)
  stem    = a name with a split marker and no parent joins the family of the letters before its first
            digit when at least two corpus names share that stem (camel-1.0, camel-1.4, camel-1.6 -> camel);
            KEEL's chess splits share the stem kr-vs-k (krvsk), whose own name contains 'vs'
  family  = follow parents to the top; otherwise the stem; otherwise the name itself                      (rule 3)
Flags are informational: feature_mismatch (a prefix parent rejected by (c)), stem_family,
same_source_composition_differs / separate_different_dataset (Toon's decisions on the feature-mismatch names, table below),
prefix_without_split_marker (a longer name starts with another name but adds only letters: not merged).
Writes out/dataset_families.csv and out/dataset_families.json.
"""
import csv, json, re, statistics, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE / "build"))
from analyse_dataset_usage import norm  # noqa: E402

SPLIT = re.compile(r"\d|vs")
SEP = set("-_ .")


# Toon 28 Oct 2026 (T1 follow-up): 'page-block0' / 'pageblock1' are the same set as page-blocks (singular spelling)
KEY_ALIAS = [(re.compile(r"^pageblock(?!s)"), "pageblocks")]
# Toon 28 Oct 2026: names rejected as splits because their feature counts contradict the parent.
# 'join' = the same source under the same name (Toon: same family, composition differs);
# 'separate' = a different data set that only shares the prefix. Basis: source, size and features printed.
FEATURE_MISMATCH_DECISION = {
    "abalone8": ("join", "abalone", "SMOM: UCI abalone subset, 10 features after encoding sex"),
    "abalone10": ("join", "abalone", "SMOM: UCI abalone subset, 10 features after encoding sex"),
    "oil1": ("join", "oil", "OSS (Kubat & Matwin): oil-spill data, 44 of the attributes"),
    "oil2": ("join", "oil", "OSS (Kubat & Matwin): oil-spill data, 39 of the attributes"),
    "segment5": ("join", "segment", "RUSBoost: UCI segment, 2,310 instances, 20 features printed"),
    "vowel4": ("join", "vowel", "OREM-M: vowel, 10 features (UCI version; KEEL vowel0 has 13)"),
    "vowel5": ("join", "vowel", "OREM-M/SMOM: UCI vowel 990 instances, 10 features"),
    "vowel7": ("join", "vowel", "SMOM: UCI vowel 990 instances, 10 features"),
    "car1": ("separate", "", "FW-SMOTE: microarray data, 174 instances, 9,182 features; not UCI car"),
    "car2": ("separate", "", "FW-SMOTE: microarray data, 174 instances, 9,182 features; not UCI car"),
    "car3": ("separate", "", "FW-SMOTE: microarray data (174, 9,182); RUSBoost's car3 (1,728, 7) is UCI car but shares the name"),
    "car4": ("separate", "", "FW-SMOTE: microarray data, 174 instances, 9,182 features; not UCI car"),
    "drug200": ("separate", "", "Loyalty-SMOTE: drug200 (413, 5 features), a different set from drug consumption (1,886, 13)"),
    "wisconsin5": ("separate", "", "OREM-M: 32 features = Wisconsin diagnostic (WDBC), not the 9-feature Wisconsin original"),
    **{n: ("separate", "", "KEEL chess King-Rook vs King split (6 features); not the 15-feature 'kr' of OSS; family = krvsk (stem)")
       for n in ("kr-vs-k-one vs fifteen", "kr-vs-k-three vs eleven", "kr-vs-k-zero-one vs draw", "krvsk0vs15", "krvsk0vs8", "krvsk3vs11")},
}


def key(n):
    k = re.sub(r"[-_ .]", "", n)
    for pat, rep in KEY_ALIAS:
        k = pat.sub(rep, k)
    return k


def after(n, m):
    """character of the original name n that follows its first m non-separator characters ('' at the end)."""
    c = 0
    for i, ch in enumerate(n):
        if ch in SEP:
            continue
        c += 1
        if c == m:
            return n[i + 1] if i + 1 < len(n) else ""
    return ""


def main():
    R = [r for r in csv.DictReader(open(HERE / "out" / "dataset_records.csv", encoding="utf-8")) if r["is_placeholder"] == "no"]
    papers, entries, feats = defaultdict(set), Counter(), defaultdict(list)
    for r in R:
        n = r["normalized_name"]; papers[n].add(r["paper_key"]); entries[n] += 1
        try:
            feats[key(n)].append(float(r["n_features"]))
        except ValueError:
            pass
    names = sorted(papers)
    keys = {n: key(n) for n in names}
    allkeys = set(keys.values())
    fmed = {k: statistics.median(v) for k, v in feats.items() if v}
    parent, flag = {}, {}
    for n in names:
        k = keys[n]
        best = None
        for c in sorted((c for c in allkeys if c != k and k.startswith(c)), key=len, reverse=True):
            r = k[len(c):]
            if not SPLIT.search(r):
                if len(c) >= 4 and r.isalpha():
                    flag.setdefault(n, "prefix_without_split_marker")
                continue
            nxt = after(n, len(c))
            ok = (c[-1].isalpha() and (nxt in SEP or r[0].isdigit() or r.startswith("vs"))) or (c[-1].isdigit() and not r[0].isdigit())
            if not ok:
                continue
            if k in fmed and c in fmed and abs(fmed[k] - fmed[c]) > 1:
                flag[n] = "feature_mismatch"
                continue
            best = c
            break
        if best:
            parent[k] = best
            if flag.get(n) == "prefix_without_split_marker":
                del flag[n]
    decided = {}
    for n, (act, par, basis) in FEATURE_MISMATCH_DECISION.items():
        if n not in keys:
            continue
        k = keys[n]
        if act == "join":
            parent[k] = key(par); flag[n] = "same_source_composition_differs"
        else:
            flag[n] = "separate_different_dataset"
        decided[n] = dict(action=act, family=key(par) if act == "join" else k, basis=basis)
    stem = {}
    for n in names:
        k = keys[n]
        if k in parent or not SPLIT.search(k):
            continue
        if k.startswith("krvsk"):
            stem[k] = "krvsk"; continue
        m = re.match(r"^([a-z][a-z .\-_]*?[a-z])[-_ .]*\d", n)
        if m and len(key(m.group(1))) >= 3:
            stem[k] = key(m.group(1))
    sc = Counter(stem.values())
    stem = {k: s for k, s in stem.items() if sc[s] >= 2 or s == "krvsk"}
    for k, s in list(stem.items()):  # a stem that is itself a corpus name but rejected as parent stays apart
        if s in allkeys and any(flag.get(n) in ("feature_mismatch", "separate_different_dataset") for n in names if keys[n] == k):
            del stem[k]

    def root(k):
        seen = set()
        while k in parent and k not in seen:
            seen.add(k); k = parent[k]
        return stem.get(k, k)
    for n in names:
        if keys[n] in stem and root(keys[n]) == stem[keys[n]]:
            flag.setdefault(n, "stem_family")  # Toon 28 Oct: e.g. svmguide1-3 = one family, separate datasets
    rows = []
    for n in names:
        k = keys[n]; f = root(k)
        rows.append(dict(normalized_name=n, dataset_key=k, family=f, is_subset=f != k, parent=parent.get(k, ""),
                         flag=flag.get(n, ""), median_features=fmed.get(k, ""), papers=len(papers[n]), entries=entries[n]))
    with open(HERE / "out" / "dataset_families.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    fam_papers = defaultdict(set)
    for r in R:
        fam_papers[root(keys[r["normalized_name"]])].add(r["paper_key"])
    groups1 = defaultdict(list)
    for n in names:
        groups1[keys[n]].append(n)
    out = dict(rule="Toon T1, 28 Oct 2026 (see docstring of build/family_rule.py)",
               names=len(names), datasets_after_rule1=len(groups1), families=len(fam_papers),
               subset_names=sum(r["is_subset"] for r in rows),
               merged_by_rule1=sorted(sorted(v) for v in groups1.values() if len(v) > 1),
               flags=dict(Counter(flag.values())),
               flagged={f: sorted(n for n in names if flag.get(n) == f) for f in set(flag.values())},
               families_by_papers=sorted(((f, len(p)) for f, p in fam_papers.items()), key=lambda x: (-x[1], x[0]))[:40],
               feature_mismatch_decisions=decided,
               r3_comparison=dict(this_rule={f: len(fam_papers.get(f, ())) for f in ("yeast", "ecoli", "glass")},
                                  r3_prefix={"yeast": 39, "ecoli": 39, "glass": 36},
                                  note="ecoli +3: 'e. coli'/'e.coli' merged by rule 1; glass -1: 'glass identification' not merged (rule 3)"))
    json.dump(out, open(HERE / "out" / "dataset_families.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print({k: out[k] for k in ("names", "datasets_after_rule1", "families", "subset_names", "flags")}, out["r3_comparison"]["this_rule"])
    print("top:", out["families_by_papers"][:20])
    for f in ("feature_mismatch", "same_source_composition_differs", "separate_different_dataset", "stem_family"):
        print(f, out["flagged"].get(f, []))


if __name__ == "__main__":
    main()
