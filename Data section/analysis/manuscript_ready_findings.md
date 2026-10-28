# Manuscript-ready findings for the Data Section (draft, not inserted)

Status: proposed text for Toon to accept, rewrite or reject. Nothing below has been put into
`manuscript/data-section-draft.tex`. Each paragraph names its evidence file. Findings, interpretation and
limitations are separated. Toon's own insight slots (`\toon{}`) are not filled here.

## F1. What "modified" covers (Analysis A; `out/modified_operations_audit.csv`)
**Finding.** Of the 331 entries classified as modified (39 papers), 175 change the classification task by selecting,
merging or binarising classes (29 papers), and 147 deliberately raise the imbalance ratio by removing minority
examples (9 papers). These two operations account for almost all modified entries; feature changes (16 entries) and
row filtering (18) are rare. A purpose for the modification was found in 15 of the 39 papers, either to obtain
two-class problems (7) or to test higher imbalance (7). Five papers supply 134 of the 147 entries with deliberately
raised imbalance, typically by producing several undersampled versions of each base data set.
**Interpretation.** A data set labelled modified may evaluate a different task (a chosen class against the rest) or
the same task under induced scarcity; the label alone does not say which.
**Limitation.** Tags are read from the extraction notes and page-referenced rules; purposes were located by a
targeted text search, so papers without a found purpose may still state one.

## F2. Where the SMOTE numbers come from (Analysis B; `out/baseline_provenance_papers.csv`)
**Finding.** Of the 57 papers that compare with SMOTE, 23 describe how SMOTE was implemented or configured, 29 do not,
one states that it retains previously published baseline scores (QC-SMOTE), and in four papers the SMOTE (or other
baseline) values are identical to those printed in another paper of the corpus without an explanation (MC-CCR and
MC-RBO with each other, NROMM with both, EMDO with AMDO). All identical-value cases lie in comparisons with a wrapped
SMOTE; none affects the 541 primary pairs. Of these 541 pairs, 216 from 13 papers combine a described SMOTE set-up
with a data entry of stated origin.
**Interpretation.** A reported win over SMOTE rests on a documented, same-study baseline for well under half of the
per-dataset evidence; identical values show that some baselines travel between papers.
**Limitation.** Identical numbers do not prove reuse; "not described" reflects a keyword search, not a full reading.

## F3. Many names, concentrated use (Analysis C; `out/benchmark_concentration.json`)
**Finding.** The 771 normalised names include 546 used by a single paper, which together carry one third of the
1,609 paper-name uses. Under rule T1 (28 Oct 2026) the names form 680 datasets (463 used by a single paper) and
459 source families; half of all uses fall on 104 names, 81 datasets or 37 families. The 33 datasets used by ten or
more papers (30 names) are small and low-dimensional: none of them is reported
with 10,000 or more instances or 100 or more features, whereas 9.1% and 4.7% of all entries reach those sizes.
**Interpretation.** The breadth suggested by the number of names comes largely from single-use data; the shared
benchmarks that allow comparison across papers cover a narrow range of size and dimensionality.
**Limitation.** About a fifth of entries do not report size; families follow rule T1 (build/family_rule.py), which flags 20 names whose printed feature counts contradict a merge and groups some numbered names by stem (to review).

## F4. Change over time (Analysis D; `out/temporal_comparison.json`)
**Finding.** Across 1972-2009, 2010-2019 and 2020-2026 (14, 26, 32 papers), modified entries fall from 38.5% to 10.5%
and repository-defined entries rise from 0% to 33.5%. Reporting of IR rises from 15% to 92% of entries while reporting
of minority-class size falls from 45% to 25%, and entries of unstated origin rise from 5% to 15%.
**Interpretation.** Task construction has moved from the authors to repositories; this changes where the
construction choices are documented rather than removing them.
**Limitation.** Period sizes are unequal and entry shares are driven by papers with many entries.

## F5. What is known about difficulty (Analyses E and F)
**Finding.** Size, features and classes are reported for 76-80% of entries, class proportions for 57%. Class overlap is
measured for 36 entries in two papers on different scales, and noise composition is described for five entries in
one paper; no corpus-wide statement about overlap, noise or sparsity is possible. Among 22 papers whose titles name a
data condition, the targeted condition is usually present in some experiment, but noise and overlap are mostly
tested on injected or generated data, separately from the per-dataset comparisons with SMOTE.
**Limitation.** Missing information is not taken as absence of a property; IR is not used as a proxy for difficulty.
