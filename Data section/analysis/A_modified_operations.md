# Analysis A — What "Modified" means in practice (331 entries)

Status: **completed, verified against the extracted notes; purposes verified against PDF text** (19 Oct 2026).
Script: `build/modified_operations.py` (rerunnable, stops if a quoted purpose is not found in the PDF).
Row-level table: `out/modified_operations_audit.csv` (331 rows). Counts: `out/modified_operations_summary.json`.

## Inputs and what was reused
- Top-level category comes unchanged from `out/dataset_records.csv` (`category = modified`, 331 entries, 39 papers).
  330 were labelled modified by the PDF reader; 1 by Toon's rule B. No entry was reclassified.
- Operation tags are assigned from the per-entry `preprocessing_note` (checked against the PDF on 18 Oct) using one
  rule per paper (the `R` table in the script; every rule names the page/table it rests on). Papers were not re-read
  wholesale. Targeted PDF searches were used only for (a) the authors' stated purpose and (b) three binarisation
  statements (k-means SMOTE p.14, HDE p.9, RSMOTE p.12, SVDD-WSMOTE p.22).
- Reviewer-assigned labels (tags, confidence) are kept apart from author statements (`purpose_stated_by_authors`
  holds only verbatim text found in the PDF).

## Counting rules
- Unit: dataset entry (one data set in one paper). Denominator 331 entries / 39 papers.
- An entry may carry several tags. Per-tag counts therefore sum to more than 331; the tag-combination table is
  mutually exclusive and sums to 331.
- `ops_conditional` records paper-level statements that may apply but cannot be tied to the entry (e.g. k-means
  SMOTE binarises multiclass bases but does not say which of its bases were multiclass). These are not counted.
- "Imbalance manipulation" (IM) is assigned only when the operation itself sets or raises the IR (sampling at a
  stated ratio or factor, or a stated aim). Class selection that changes the IR as a side effect is recorded as
  "changed as a consequence", not IM.

## Results
**Q1. Operations (entries / papers; tags overlap)**

| Operation | Entries (of 331) | Papers (of 39) |
|---|---:|---:|
| Class selection / task conversion (CS) | 175 | 29 |
| Sample reduction / undersampling (US) | 148 | 11 |
| Imbalance manipulation (IM) | 147 | 9 |
| Sample filtering / subset selection (SF) | 18 | 9 |
| Feature modification (FM) | 16 | 7 |
| Other documented (OT: label-noise injection, labels built by authors) | 4 | 3 |
| Insufficiently specified (IS) | 0 | 0 |

Mutually exclusive combinations: CS only 141; US+IM 131; CS+IM 11; CS+FM 9; SF 7; CS+US 6; US 5; CS+SF 4; FM 4;
US+SF+IM 3; FM+SF 3; CS+OT 2; CS+US+IM 2; OT 2; US+SF 1 (total 331).

**Q2. Multiple operations.** 172 of 331 entries (17 of 39 papers) carry more than one tag. Most of these (131) are
the US+IM pair: the minority class is randomly reduced in order to raise the IR.

**Concentration of IM.** The 147 IM entries come from 9 papers, and five papers supply 134 of them
(k-means SMOTE 49, G-SMOTE 42, RSMOTE 18, HDE 14, SVDD-WSMOTE 11). All nine were published 2007-2022, eight of them 2018 or later.

**Q3. Stated purpose.** A purpose sentence was found in 15 of 39 papers (191 of 331 entries). Themes (per paper):
obtaining two-class problems 7 (ADASYN, MWMOTE, RAMOBoost, RUSBoost, SMOTE, SMOTE-IPF, Safe-Level-SMOTE);
obtaining higher / more extreme imbalance 7 (G-SMOTE, HDE, k-means SMOTE, NBU, RSMOTE, SVDD-WSMOTE, ROS);
reducing data-set size 1 (SMOTEBoost). For the other 24 papers no purpose sentence was found by the targeted
search; this means "not found", not "not stated".

**Q4. Operations that change the task.** 177 entries (30 papers) change the class structure: 175 by class
selection/conversion, plus one label-noise version (SMOTE-IPF) and one data set labelled by the authors (SMOTE, Can).
Of the 175 CS entries, the dominant form is one-vs-rest (84 entries, 6 more with the class not stated, 8 with the
class only inferable from a name suffix); the rest keep a subset of classes, merge classes into groups, or apply a
threshold to the target. Undersampling, filtering and feature changes alter the sample or the representation but
keep the label definition.

**Q5. Missing information** (flags read from the notes; 93 of 331 entries carry at least one):
characteristics of the modified version not printed 55 (49 are k-means SMOTE's undersampled versions, omitted from
its Table 2); target IR not stated 18 (RSMOTE); minority class not stated or only inferable 15 (RACOG 6, RUSBoost 8,
INOS 1); original class count not stated 3 (INOS); affected data sets not named 2 (SOUP); subset selection rule not
described 1 (RACOG connect-4).

**Confidence.** explicitly reported 311; supported by indirect evidence 16 (RUSBoost class from suffix, SMOM classes
dropped as inferred from labels, GAMO CIFAR/SVHN, RACOG connect-4, SOUP); ambiguous 4 (RUSBoost SolarFlareF, INOS
TwoPats/Wafer/Yoga).

**Link to the paired comparisons (descriptive only).** Of the 143 primary-set rows (plain SMOTE, 541 rows) on
modified data, 110 are on CS-only entries, 29 on IM entries, 4 on other operations. Most IM entries never reach a
per-dataset comparison: k-means SMOTE and G-SMOTE (91 IM entries) report results without per-dataset SMOTE pairs.

## Interpretation (reviewer's reading, for Toon to accept or revise)
- "Modified" is not one operation. Two operations account for almost all of it: redefining the task (class
  selection, mostly one-vs-rest) and deliberately raising the IR by removing minority examples. These change
  different things: the first changes what is being predicted, the second keeps the task but makes the minority
  scarcer.
- The deliberate-IR group is concentrated in a few papers that generate several versions of each base set
  (factors x2..x20), so entry counts overstate how many distinct base data sets or papers are involved.
- Most papers do not say why they modified data; when they do, the reasons are practical (the method is binary;
  test more extreme imbalance) rather than a claim that the modified version better represents an application.
- Modification is not evidence of improper practice; the issue for interpretation is that a dataset name in a
  Modified entry does not identify the task or class distribution that was evaluated.

## Limits
- Tags depend on the notes; where a note is silent about an operation the paper performed elsewhere, the tag is
  missing (the conditional field captures the known cases).
- The purpose search is keyword-based (sentences containing a modification verb and a purpose phrase). A purpose
  expressed differently could be missed.
- Not reviewed by Toon yet.
