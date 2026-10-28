# Analysis E — Can data difficulty be described beyond IR?

Status: **completed as a coverage audit** (19 Oct 2026). A descriptive difficulty analysis is **not** justified for
overlap, noise or sparsity (see below). Not reviewed by Toon.
Script: `build/characteristics_coverage.py`. Output: `out/characteristics_coverage.json`.

## Reused
Verified fields of `out/dataset_records.csv`; curated difficulty evidence `out/difficulty_evidence.json` (26 items,
quotes checked against PDFs); protocol text from `ai-draft/full/*.json`; paper-level preprocessing text from
`out/data_handling_matrix.csv` (ai_draft). No re-extraction was run.

## Coverage (unit: named data entries, 1,653; papers with named entries, 72)
| Property | Entries with a value | Papers with any | Source status |
|---|---:|---:|---|
| Number of instances | 1,326 (80.2%) | 59 | verified |
| Number of features | 1,254 (75.9%) | 57 | verified |
| Number of classes | 1,280 (77.4%) | 61 | verified |
| Minority size | 504 (30.5%) | 33 | verified |
| Class proportions in any form (minority size or distribution) | 939 (56.8%) | 54 | verified |
| Feature type (numeric / categorical / mixed) | 128 mention it (7.7%) | 10 | no dedicated field; mentions in notes only |
| Measured class overlap | 36 (2.2%) | 2 (MLOS R-value, GDHS Fdr) | curated, quotes and values checked |
| Described noise/borderline composition | 5 (0.3%) | 1 (SMOTE-IPF, cited analysis) | curated |
| Sparsity | 0 | 0 | no statement in curated evidence |
| Papers that inject or generate difficulty experimentally | - | 12 | curated |

Evaluation protocol of the extracted results table (paper level, 72): repeated k-fold CV 28, k-fold CV 21,
hold-out split 12, not captured in either extraction 9, no results table 2. Of these, 17 papers were classified
only from the ai_draft preprocessing text. Placement of preprocessing relative to resampling is mentioned for 3
papers in the ai_draft text (CISO, G-SMOTE, QC-SMOTE).

## Distribution where data exist
Size profile (from Analysis C): median 800 instances (90th pct 7,200), median 9 features (90th pct 41); 68.4% of
entries with a class count are two-class. Measured overlap exists for 36 entries in two papers, each with its own
measure (augmented R-value, Fdr); the two scales cannot be pooled.

## Conclusion
- Size, dimensionality and number of classes are reported for three quarters or more of entries and support a
  descriptive profile (used in Analysis C).
- Class proportions are available for just over half of entries; IR is available for 80% but under at least nine
  definitions.
- Overlap, noise and sparsity cannot be characterised for the corpus: direct evidence covers 2.5% of entries in
  3 papers, measured on incompatible scales. Missing evidence is not evidence that the data lack these properties,
  and IR is not used as a proxy.
- Feature type and preprocessing placement are not extracted; current mentions are too sparse to analyse.

## Recommended bounded follow-up (only if the section needs it)
1. Feature type for the 30 names used by 10+ papers (Analysis C), from the papers' own tables only.
2. Protocol for the 9 papers whose evaluation design was not captured, from their experimental-setup section.
3. Review of the keyword passages (`out/difficulty_candidates.csv`) for the 30 papers in the primary comparison set,
   to see whether any reports a measured data property.
