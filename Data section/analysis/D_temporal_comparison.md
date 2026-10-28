# Analysis D — Earlier and later papers

> **Update 29 Oct 2026 (rule R8, Toon):** MC-MBRC (2024) left the primary set. 2020–2026 primary rows 356 (17 papers) → 336 (16); original 116 → 96; signs +281/−48 → +263/−46; the 69 rows of unknown origin are unchanged (now 20.5% of 336). Current values in `out/temporal_comparison.json`.

Status: **completed (descriptive)** 19 Oct 2026. Not reviewed by Toon.
Script: `build/temporal_comparison.py`. Output: `out/temporal_comparison.json` (every count with its denominator).

## Periods and why
1972-2009 / 2010-2019 / 2020-2026, the grouping already used in `out/data_handling_summary.json` and the Atlas.
Years are taken from `out/dataset_records.csv`. Papers with named data entries: 14 / 26 / 32 (72 in all; the Tomek
placeholder paper has no named entry). With 14 papers in the first period, a finer split would leave single-digit
groups. The older paper-level summary counts 15 papers in 1972-2009 because it includes Tomek Links (1976), whose only data entry is the unnamed placeholder.

## Results (counts / denominator)
| Indicator (unit) | 1972-2009 | 2010-2019 | 2020-2026 |
|---|---|---|---|
| Entries | 130 | 740 | 783 |
| Original, % of entries | 46.2 | 22.4 | 39.3 |
| Repository-defined, % of entries | 0.0 | 28.1 | 33.5 |
| Modified, % of entries | 38.5 | 26.9 | 10.5 |
| Synthetic, % of entries | 10.0 | 12.0 | 2.2 |
| Not stated, % of entries | 5.4 | 10.5 | 14.6 |
| Papers using any modified data | 12/14 | 17/26 | 10/32 |
| Papers using only original or repository-defined data | 1/14 | 5/26 | 12/32 |
| Papers with class selection/conversion (A) | 11/14 | 11/26 | 7/32 |
| Papers with deliberate IR manipulation (A) | 1/14 | 4/26 | 4/32 |
| Modifying papers stating a purpose (A) | 4/12 | 7/17 | 4/10 |
| Entries reporting instances / features / classes, % | 80.8 / 72.3 / 82.3 | 83.8 / 72.8 / 85.1 | 76.8 / 79.3 / 69.3 |
| Entries reporting minority size, % | 44.6 | 34.2 | 24.6 |
| Entries reporting an IR, % | 15.4 | 78.9 | 91.6 |
| Papers stating their IR definition | 2/14 | 14/26 | 18/32 |
| Uses on names shared by >= 5 papers (C) | 56/130 (43.1%) | 275/698 (39.4%) | 377/781 (48.3%) |
| Uses on single-paper names (C) | 37/130 (28.5%) | 279/698 (40.0%) | 230/781 (29.4%) |
| Papers with a SMOTE baseline | 7/14 | 21/26 | 29/32 |
| ...of these, B1 / B2 / B3 / B4 (B) | 3 / 4 / 0 / 0 | 10 / 11 / 0 / 0 | 10 / 14 / 1 / 4 |
| Primary comparison rows (papers) | 24 (3) | 161 (10) | 356 (17) |
| ...on modified data | 17 | 80 | 46 |
| ...on data of unstated origin | 0 | 36 | 69 |
| Selection rationale given ("own reason"), ai_draft only | 11/14 | 21/26 | 16/32 |

## Observations (no ranking of periods)
- The mix of data changes: early papers mostly modify UCI data themselves; from 2010 repository-defined (mainly KEEL)
  tasks appear and in 2020-2026 they are a third of entries, while modified entries fall to about a tenth.
  Part of what was "modification by the authors" earlier now arrives as a repository-defined task.
- IR reporting becomes near universal (15% -> 92% of entries) and half of the later papers define their IR, while
  minority-class size is printed less often (45% -> 25%).
- Entries whose origin cannot be told rise (5% -> 15%), and in 2020-2026 they supply 69 of 356 primary comparison rows.
- All explicit import and identical-value baseline cases (B3, B4) are in 2020-2026; the B1 share is similar across
  periods (3/7, 10/21, 10/29).
- Reliance on shared benchmarks is highest in 2020-2026 (48% of uses on names used by >= 5 papers).
- The first period contributes only 3 papers with primary rows; comparisons of win shares across periods are not
  reported because the papers differ in metric, classifier and size.

## Limits
- Period sizes differ (14 / 26 / 32 papers); entry-level shares are dominated by papers with many entries
  (e.g. k-means SMOTE, G-SMOTE).
- The selection-rationale codes are ai_draft (not checked against the PDFs) and are shown only for orientation.
- "Original" includes entries assigned by Toon's rules of 18 Oct (rule A and the multiclass common-name rule), which
  record reviewer judgement where the paper is silent.
