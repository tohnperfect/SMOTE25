# Analysis C — How concentrated is the benchmark evidence?

> **อัปเดต 28 ต.ค. 2026 (กฎ T1 ของ Toon):** ระดับ family เดิมในไฟล์นี้ใช้ heuristic ซึ่งถูกแทนแล้ว ตัวเลขปัจจุบันอยู่ใน `out/benchmark_concentration.json`:
> ชื่อ 771 (ใช้ paper เดียว 546, ครอบครึ่ง use 104) · dataset ตามกฎ T1 ข้อ 1 = 680 (ใช้ paper เดียว 463, ครอบครึ่ง 81) · family ตาม T1 = 459 (ใช้ paper เดียว 323, ครอบครึ่ง 37, top-20 = 37.8%) [รวม pageblock = page-blocks และ 8 ชื่อ same-source ตามคำตัดสิน 28 ต.ค.] ·
> dataset ที่ใช้ ≥ 10 paper = 33 (ชื่อ = 30) และไม่มีชุดใดใน 33 ชุดนี้ที่พิมพ์ ≥ 10,000 instance หรือ ≥ 100 feature


Status: **completed (descriptive; computed from verified data entries)** 19 Oct 2026. Not reviewed by Toon.
Script: `build/benchmark_concentration.py`. Outputs: `out/benchmark_concentration.json`, `out/benchmark_top_names.csv`.

## Why recomputed
`out/dataset_usage_draft.json` and `out/family_usage.json` were computed in draft mode from `ai-draft/papers.json`
(not the verified data). This analysis uses `out/dataset_records.csv` (verified 18 Oct; 1,653 named entries after
rule R1 sets aside the Tomek placeholder; 72 papers have named entries). The name normalisation is the existing
`norm()`, so the 771 / 546 figures reproduce the manuscript values.

## Units
- **entry**: one data set in one paper as extracted (a paper that builds six undersampled versions of one base set
  contributes six entries).
- **use**: a distinct (paper, normalised name) pair; 1,609 uses. This is the unit for "how many papers use a name".
- **base family** (heuristic, sensitivity only): the leading alphabetic part of a name, e.g. `yeast-0-2-5-6_vs_3-7-8-9`
  -> `yeast`; groups KEEL derivatives with their source name but may also join unrelated names that share a word.

## Results
| Measure | by name (771) | by base family (446) |
|---|---:|---:|
| names/families used by one paper only | 546 (70.8% of names; 33.9% of uses) | 304 (68.2%; 26.4%) |
| used by 10 or more papers | 30 | 23 |
| share of uses on the 10 / 20 / 50 most used | 11.9% / 19.9% / 35.7% | 23.5% / 36.4% / 54.0% |
| names needed to cover half of all uses | 104 | 41 |
| effective number (inverse Simpson) | 263.7 | 105.7 |
| Gini of uses per name | 0.45 | 0.53 |

Counting entries instead of uses changes little (top-20 share 20.1% vs 19.9%), because most repeated entries
within a paper are different names (e.g. KEEL yeast1...yeast6), not repeats of one name.

- Most used names (papers): ecoli 26, yeast 22, pima 21, vehicle 21, haberman 20, glass 19, balance 16, wine 16,
  satimage 15, yeast4 15 (full top 20 with printed characteristics in `out/benchmark_top_names.csv`).
- 64 of 72 papers use at least one name that 5 or more papers use; in the median paper 46% of its names are such
  shared names. 6 papers use only names no other paper uses (Cluster-SMOTE, ClusterCentroids, INOS, OSS, SHRINK, SPE).

**What the heavily reused benchmarks represent (values as printed; denominators are entries with a value)**

| | all named entries | entries of the 30 names used by >= 10 papers |
|---|---:|---:|
| instances reported / median / 90th pct | 1,324 / 800 / 7,200 | 351 / 625 / 2,310 |
| share with >= 10,000 instances | 9.1% | 0% |
| features reported / median / 90th pct | 1,254 / 9 / 41 | 338 / 8 / 19 |
| share with >= 100 features | 4.7% | 0% |
| classes reported: share two-class / share >= 5 classes | 68.4% / 18.6% | 49.4% / 25.7% |

## Answers
- **Concentrated?** Partly. Names are spread thin (half of all uses need 104 names; effective number about 264), so
  the literature is not dominated by a handful of names. At the level of base families the picture is more
  concentrated: 41 families carry half of all uses, and the 20 most used families carry 36%.
- **Papers vs entries.** The distribution is almost the same in both units; the difference between "771 names" and
  "how much evidence" is mainly the long tail of single-paper names (546 names, one third of uses).
- **Do the reused benchmarks cover different characteristics?** Within the reported values, the 30 most reused names
  are all small and low-dimensional: none has 10,000 or more instances or 100 or more features, while such data
  appear among the single-use and rarely used names. Larger and high-dimensional data in the corpus therefore come
  mainly from names few papers share.
- **Underrepresented characteristics** that the data support: large (>= 10,000 instances) and high-dimensional
  (>= 100 features) data among the shared benchmarks. Domain or feature type cannot be assessed from this
  inventory (no field), so no claim is made about missing domains.

## Limits
- 20% of entries lack instance counts and 24% lack feature counts; values are as printed and can differ across
  papers for the same name (see the size-variation finding: 78 of 198 names).
- The family heuristic is coarse; it is used only to show the direction of the effect.
- Reuse is not treated as a flaw: shared benchmarks make comparison across papers possible.
