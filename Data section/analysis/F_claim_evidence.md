# Analysis F — Do evaluated data match the data conditions papers target?

Status: **completed for a defined subset** (19 Oct 2026). Not reviewed by Toon.
Script: `build/claim_evidence.py`. Outputs: `out/claim_evidence_matrix.csv` (27 claim rows), `out/claim_evidence_summary.json`.

## Subset and why
Papers that (a) have per-dataset SMOTE pairs (primary or wrapper set, 42 papers) and (b) name a data condition in
their **title** (multi-class, highly imbalanced / massive, noise, overlap, difficulty factors): 22 papers, 27 claimed
conditions. The claim is the condition stated in the title, not inferred from the algorithm's name; abstracts were
not coded. Results describe these 22 papers only.

## Operational labels
- Multi-class: share of the evaluated entries (those linked to the paper's SMOTE pairs) with three or more classes.
  aligned = all; partially supported = some; not aligned = none; insufficient = class count missing for half or more.
  A title naming both binary and multi-class data is aligned when both kinds are present.
- High imbalance: this analysis' threshold, numeric IR >= 10 (papers define IR differently). Same four labels.
- Noise / overlap / difficulty factors: aligned = a curated, PDF-checked evidence item shows the condition measured,
  used for selection, or injected; insufficient = no such item (not "absent").
- Massive data: sizes reported, no threshold.

## Results (claim rows)
| Condition | aligned | partially | insufficient | other |
|---|---:|---:|---:|---:|
| multi-class (14) | 10 | 2 (DSRBF 8/13, GDHS 14/20 entries multi-class) | 2 (SHSampler, SOUP: class counts not extracted) | |
| overlap (5) | 5 (GOIO, MC-MBRC, NBU, SVDD-WSMOTE injected/generated; MLOS measured and used for selection) | | | |
| noise (4) | 3 (MC-CCR, RSMOTE injected; SMOTE-IPF inherent + injected) | | 1 (NROMM) | |
| high imbalance (2) | 1 (MLOS, all IR 10.7-129.4) | | 1 (SPE, IR not numeric) | |
| difficulty factors (1) | | | 1 (SHSampler) | |
| massive data (1) | | | | SPE: 284,807 instances (one evaluated entry) |

Points that matter for interpreting comparisons with SMOTE:
- For every noise claim that is aligned, the noise experiments are separate from the per-dataset SMOTE pairs we
  extracted (those pairs are from the no-added-noise condition). The same holds for the overlap experiments of GOIO,
  MC-MBRC and NBU, which use generated data. A paper can therefore support its targeted condition and its superiority
  over SMOTE with different data.
- Overlap is aligned in all five titled papers, but in four of them the evidence comes from generated or injected
  overlap; only MLOS measures overlap on its real data sets.
- Baseline provenance (Analysis B) of the 22 papers: B1 8, B2 10, B4 4 (MC-CCR, MC-RBO, EMDO, NROMM).

## Limits
- Titles only; claims made in abstracts or conclusions are not coded.
- The IR >= 10 threshold is ours; IR definitions differ by paper.
- Noise/overlap labels depend on the curated evidence (14 papers reviewed); "insufficient" can change if the keyword
  passages are reviewed.
