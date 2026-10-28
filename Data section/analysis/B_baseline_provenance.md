# Analysis B — Where the SMOTE baseline numbers come from

Status: **completed for the defined scope; evidence verified against PDF text; not reviewed by Toon** (19 Oct 2026).
Script: `build/baseline_provenance.py` (stops if any quoted statement is not found in the PDF).
Outputs: `out/baseline_provenance_papers.csv` (57 papers), `out/baseline_identical_values.csv` (row-level identical
values), `out/baseline_provenance_summary.json`.

## Reused, not redone
- Score pairs, tables and pages: `out/verified_outcomes.csv` (835 rows, checked against PDFs 18-19 Oct, mapping audit 19 Oct).
- Partitions (541 primary / 207 wrapper / 87 excluded): rules R4-R7 in `build/reconcile_counts.py`.
- Results granularity and "SMOTE in baselines": `ai-draft/full/*.json`.
- New work: (1) a keyword search of the 57 PDFs for SMOTE implementation/configuration and for statements that
  results were taken from elsewhere, each retained quote verified by script; (2) a scan of all 835 rows for values
  that are identical across papers; (3) a column-by-column check of EMDO Table 5 against AMDO's MAUC table.

## Fields (kept separate, not one label)
- **Provenance** (paper level)
  - B1 same study; the paper states how SMOTE was implemented or configured (library, tool or k).
  - B2 same study presumed: SMOTE and the proposed method appear in one results table under one described protocol,
    but no statement of how SMOTE was run was found.
  - B3 previously published scores imported, stated by the authors.
  - B4 scores identical to another corpus paper's published values; the paper does not say whether they were re-run.
- **Dataset equivalence** (proposed vs SMOTE score): same data entry in the same table for B1/B2; for B3/B4 what
  the paper states about the source's data.
- **Protocol equivalence**: same described protocol for B1/B2; for B3/B4 whether matching folds/protocol are stated.
- Identical values are recorded as a fact about numbers; they are not taken as proof of copying.

## Results
**Units.** Paper = one of the 57 papers that list SMOTE (plain or wrapped) as a baseline. Row = one per-dataset
score pair in `verified_outcomes.csv`. Paper and row counts are reported separately.

| Provenance | Papers (of 57) | ...with per-dataset pairs (42) | Primary rows (541) | Wrapper rows (207) |
|---|---:|---:|---:|---:|
| B1 configuration described | 23 | 17 | 253 (13 papers) | 76 (4 papers) |
| B2 presumed same study, configuration not found | 29 | 21 | 288 (17 papers) | 62 (4 papers) |
| B3 imported, stated | 1 (QC-SMOTE) | 0 | 0 | 0 |
| B4 identical to another paper, not explained | 4 | 4 | 0 | 69 (4 papers) |

(AMDO, the source of the EMDO values, is counted as B1.)

**The four flagged cases, as verified**
- *QC-SMOTE (B3).* The authors state that they "retain the published CatBoost baselines" of the VS-SMOTE benchmark
  (p.8) on the same D1-D30 data sets. This is an explicit import. QC-SMOTE prints only averages, so no per-dataset
  pair enters our sets. VS-SMOTE is not in the corpus, so the source values were not checked.
- *MC-CCR and MC-RBO (B4).* Their SMOTE-all mGM values (C5.0) are identical on all 20 shared data sets. Same author
  group; neither paper states a reuse, and which appeared first was not established.
- *NROMM (B4), new in this round.* Its SMOTE-all values (supplementary Table 8) are identical to those of MC-CCR and
  MC-RBO on all 20 data sets, and 12 of its "best other" values equal MC-RBO's own published scores. NROMM gives a
  SMOTE-all configuration (k = 5) but does not say the values come from those papers.
- *EMDO (B4).* EMDO states that its data sets are those of AMDO (p.14). In its MAUC table (Table 5, p.15) the Base,
  SSMOTE, GCS, ABNC, OSMOTE and AMDO columns (means and SDs) are identical to AMDO's MAUC table on all 9 shared data
  sets. Whether these columns were re-run is not stated. (The earlier note that EMDO's baseline values "were not
  identified as copied" was based on the extracted SMOTE column only, which differs because AMDO's extraction used
  OSMOTE and EMDO's used SSMOTE.)
- The corpus-wide scan found no other pair of papers sharing identical values on 3 or more data sets.

**Answers (with denominators)**
1. Papers with enough information to identify provenance: 28 of 57 (23 B1 + 1 B3 + 4 B4 identified from numbers);
   29 (B2) give no statement about how SMOTE was run.
2. Papers that clearly evaluate SMOTE in the same study with a described configuration and per-dataset pairs: 17 of 42.
3. Papers importing or showing reused scores: 1 stated (QC-SMOTE); 4 with identical values and no statement.
4. Dataset-version equivalence uncertain: within a paper, both scores are on the same data entry. Uncertainty
   arises in what that entry is: 108 of 541 primary rows are on data whose origin is not stated or that is not
   linked to a data entry; and in the B4 cases the identity of the data with the source paper is stated only by EMDO.
5. Protocol equivalence uncertain: 288 of 541 primary rows (B2: SMOTE settings not reported); in the wrapper set,
   also the 69 B4 rows, where folds and settings may come from another paper.
6. Rows that can reasonably support a direct per-dataset statement "better than SMOTE" (operational definition:
   primary set, B1, data entry identified with a stated origin): **216 of 541 rows, 13 of 30 papers**
   (proposed higher 165, equal 14, SMOTE higher 37). A further 217 rows (17 papers) meet the same conditions except
   that SMOTE's configuration is not reported. 108 rows are on data of unknown origin. These tiers say how much is
   documented, not whether the comparisons are wrong.

**Descriptive note.** In the wrapper set, the 69 B4 rows all show the proposed method higher (69 of 69).

## Limits
- The configuration search is keyword based; a paper classed B2 may describe SMOTE in wording the search missed.
  B2 means "not found", not "absent".
- B1 shows that the paper describes a SMOTE set-up; it does not prove that every number was produced in that run.
- Identical-value detection uses only the values in `verified_outcomes.csv` (plus the EMDO/AMDO table check);
  reuse of other columns elsewhere is not covered. Identical values may also arise from shared code and seeds.
- Not reviewed by Toon.
