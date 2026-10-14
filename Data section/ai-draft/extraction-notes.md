# SMOTE25 Data Section: extraction notes

Structured records for the Data section of the SMOTE25 survey, extracted from the PDFs in the project's Google Drive folders, with seven dataset characteristics tables supplied separately by toon and folded in.

- **Corpus**: 69 paper records (binary 37, multi-class 22, both 8, surveys 2). Static-SMOTE merged into DSRBF (same PDF).
- **Dataset registry**: 75 distinct names, 103 variants, built from the seven recovered tables.
- **Deliverables**: `SMOTE25_Data_Section_Explorer.html` (5 tabs), `smote25_data_records.json` (papers), `smote25_dataset_variants.json` (dataset variants).
- **Extraction confidence**: high 53, medium 16, low 0.

## Governing rules applied

1. **Never merge, never drop a variant.** Where a dataset name is published with a different instance count, class count, feature count or class distribution, each version is kept as its own row with the papers that used it and a note saying how it differs. The unit of record is the variant, not the name.
2. **Never drop an IR definition.** Nine measures are in circulation; all nine are catalogued and every quoted figure is labelled with the measure that produced it. Incompatible figures are retained and marked, not discarded, because the spread of definitions is itself a survey finding.
3. **Corrections are noted, not silently applied.** Where a cell was corrected against a source, the original printed value and the reason are kept alongside.

## Verified corrections applied

| Record | Was | Now | Basis |
|---|---|---|---|
| MC-RBO automobile | 150 instances | 159 | the paper's own distribution sums to 159; MC-NCLWO reports 159. Treated as a reporting error in MC-RBO |
| MC-RBO page-blocks | 5472 | 5473 | UCI record doi:10.24432/C5J590. The gap traces to a class printed as 87 where MC-NCLWO prints 88; 4913/329/115/88/28 sums to 5473 exactly |
| dermatology (canonical) | 358 | 366 | UCI record doi:10.24432/C5FK5P, which SOUP's counts match. The 358-instance KEEL version is kept as a separate variant: the 8 missing records are those with a missing age attribute, which also explains the 33 vs 34 feature count |
| MC-RBO ecoli distribution | 143/77/2/235/20/5/52 | 143/77/2/2/35/20/5/52 | the corrected reading sums to 336 and gives the stated IR of 71.50 |

## IR discrepancies: what causes them

Tested every candidate formula numerically against the published class distributions.

**vehicle (199/212/217/218).** MC-NCLWO and SHSampler report 1.10, which is exactly largest over smallest. MC-CCR and MC-RBO report 1.17. None of the nine measures reproduces 1.17 from this distribution: max/min 1.0955, mean of max/N_i 1.032, SMOM summed pairwise 5.31, above-mean over below-mean 3.25, max/mean 1.031, mean/min 1.063, N/(C*min) 1.063, second-max/min 1.091, CV 0.036. Getting 1.17 would require a denominator of 186.3 or a numerator of 232.8, and no class has either count. **Conclusion: not a definitional difference, a transcription error, and because MC-CCR and MC-RBO share one table it propagated across both papers.**

**car (1210/384/69/65).** MC-RBO 18.61 and MC-NCLWO 18.62 are the same value, 18.6154, truncated and rounded. MKC-SMOTE prints 18.91, which its own distribution does not give. 1210/64 = 18.9062, which rounds to 18.91. **Conclusion: the smallest class was almost certainly keyed as 64 instead of 65. Again a keying error, not a different formula.**

By contrast, the differences that ARE definitional are listed in the Datasets tab: CBHSID's Contraceptive 5.6 against 1.89 and Dermatology 36.94 against 5.55 cannot be explained by transcription and must come from an unstated formula, so those figures are kept but excluded from pooled comparisons.

## The 20 names that denote more than one dataset

Never pool these by name.

### abalone (2 variants, 2 paper rows)
- *variant*: instance count differs across papers: 3966, 4177
- *variant*: class count differs across papers: 2, 13
  - 3966 rows, 13 classes, 8 features, multi-class | MKC-SMOTE
  - 4177 rows, 2 classes, 8 features, binary (one-vs-rest) | EasyEnsemble / BalanceCascade

### balance (2 variants, 5 paper rows)
- *variant*: class count differs across papers: 2, 3
  - 625 rows, 3 classes, 4 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO, SOUP
  - 625 rows, 2 classes, 4 features, binary (one-vs-rest) | EasyEnsemble / BalanceCascade

### car (2 variants, 6 paper rows)
- *variant*: class count differs across papers: 2, 4
- *ir*: MKC-SMOTE reports IR 18.91, but max over min of its own distribution gives 18.62
  - 1728 rows, 4 classes, 6 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO, MKC-SMOTE, SOUP
  - 1728 rows, 2 classes, 6 features, binary (one-vs-rest) | EasyEnsemble / BalanceCascade

### cleveland (4 variants, 5 paper rows)
- *variant*: instance count differs across papers: 297, 303
- *variant*: class count differs across papers: 4, 5
  - 297 rows, 5 classes, 13 features, multi-class | MC-RBO, MC-CCR
  - 297 rows, 5 classes, 13 features, multi-class | MC-NCLWO
  - 303 rows, 5 classes, multi-class | SOUP
  - 303 rows, 4 classes, multi-class | SOUP

### contraceptive (3 variants, 7 paper rows)
- *variant*: class count differs across papers: 2, 3
- *undefined*: CBHSID reports IR 5.6 without stating the definition
  - 1473 rows, 3 classes, 9 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO, MKC-SMOTE, SOUP
  - n/r rows, 3 classes, 9 features, multi-class | CBHSID
  - 1473 rows, 2 classes, 9 features, binary (one-vs-rest) | EasyEnsemble / BalanceCascade

### dermatology (3 variants, 5 paper rows)
- *variant*: instance count differs across papers: 358, 366
- *variant*: feature count differs across papers: 33, 34
- *undefined*: CBHSID reports IR 36.94 without stating the definition
  - 358 rows, 6 classes, 33 or 34 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO
  - 366 rows, 6 classes, multi-class | SOUP
  - n/r rows, 6 classes, 34 features, multi-class | CBHSID

### ecoli (3 variants, 5 paper rows)
- *variant*: class count differs across papers: 5, 8
  - 336 rows, 8 classes, 7 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO
  - 336 rows, 5 classes, 7 features, multi-class | MKC-SMOTE
  - 336 rows, 5 classes, multi-class | SOUP

### flare (2 variants, 4 paper rows)
- *variant*: instance count differs across papers: 1066, 1389
  - 1066 rows, 6 classes, 11 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO
  - 1389 rows, 6 classes, multi-class | SOUP

### glass (2 variants, 5 paper rows)
- *variant*: class count differs across papers: 5, 6
  - 214 rows, 6 classes, 9 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO, SOUP
  - 214 rows, 5 classes, 9 features, multi-class | MKC-SMOTE

### haberman (2 variants, 2 paper rows)
- *variant*: more than one class distribution is published under this name
- *undefined*: CBHSID reports IR 2.78 without stating the definition
  - n/r rows, 2 classes, 3 features, binary (KEEL two-class task) | CBHSID
  - 306 rows, 2 classes, 3 features, binary (one-vs-rest) | EasyEnsemble / BalanceCascade

### led7digit (2 variants, 4 paper rows)
- *variant*: class count differs across papers: 6, 10
  - 500 rows, 10 classes, 7 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO
  - 500 rows, 6 classes, multi-class | SOUP

### letter (2 variants, 2 paper rows)
- *variant*: instance count differs across papers: 10723, 20000
- *variant*: class count differs across papers: 2, 10
- *ir*: EasyEnsemble / BalanceCascade reports IR 24.3, but max over min of its own distribution gives 24.35
  - 10723 rows, 10 classes, 16 features, multi-class | MKC-SMOTE
  - 20000 rows, 2 classes, 16 features, binary (one-vs-rest) | EasyEnsemble / BalanceCascade

### penbased (2 variants, 2 paper rows)
- *variant*: more than one class distribution is published under this name
- *undefined*: CBHSID reports IR 1.95 without stating the definition
  - 1100 rows, 10 classes, 16 features, multi-class | MC-NCLWO
  - n/r rows, 10 classes, 16 features, multi-class | CBHSID

### pima (2 variants, 2 paper rows)
- *variant*: more than one class distribution is published under this name
- *undefined*: CBHSID reports IR 1.87 without stating the definition
  - n/r rows, 2 classes, 8 features, binary (KEEL two-class task) | CBHSID
  - 768 rows, 2 classes, 8 features, binary (one-vs-rest) | EasyEnsemble / BalanceCascade

### thyroid (3 variants, 4 paper rows)
- *variant*: instance count differs across papers: 720, 7200
- *undefined*: CBHSID reports IR 39.17 without stating the definition
  - 7200 rows, 3 classes, 21 features, multi-class | MC-RBO, MC-CCR
  - 720 rows, 3 classes, 21 features, multi-class | MC-NCLWO
  - n/r rows, 3 classes, 21 features, multi-class | CBHSID

### vehicle (3 variants, 5 paper rows)
- *variant*: class count differs across papers: 2, 3, 4
- *ir*: MC-RBO reports IR 1.17, but max over min of its own distribution gives 1.1
- *ir*: MC-CCR reports IR 1.17, but max over min of its own distribution gives 1.1
  - 846 rows, 4 classes, 18 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO
  - 846 rows, 3 classes, multi-class | SOUP
  - 846 rows, 2 classes, 18 features, binary (one-vs-rest) | EasyEnsemble / BalanceCascade

### vehicle1 (2 variants, 2 paper rows)
- *variant*: feature count differs across papers: 18, 19
- *variant*: more than one class distribution is published under this name
- *undefined*: CBHSID reports IR 2.9 without stating the definition
  - n/r rows, 2 classes, 18 features, binary (KEEL two-class task) | CBHSID
  - 846 rows, 2 classes, 19 features, binary (one-vs-rest) | RUSBoost

### winequality-red (2 variants, 4 paper rows)
- *variant*: class count differs across papers: 4, 6
  - 1599 rows, 6 classes, 11 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO
  - 1599 rows, 4 classes, multi-class | SOUP

### yeast (3 variants, 5 paper rows)
- *variant*: class count differs across papers: 8, 9, 10
  - 1484 rows, 10 classes, 8 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO
  - 1484 rows, 8 classes, 8 features, multi-class | MKC-SMOTE
  - 1484 rows, 9 classes, multi-class | SOUP

### zoo (2 variants, 4 paper rows)
- *variant*: class count differs across papers: 5, 7
  - 101 rows, 7 classes, 16 features, multi-class | MC-RBO, MC-CCR, MC-NCLWO
  - 101 rows, 5 classes, 16 features, multi-class | MKC-SMOTE

## Still outstanding

**MWMOTE Table 5.** Both Drive copies carry Tables 5 to 12 as images, so no cell values survive text extraction. Only 8 of 20 dataset names appear anywhere in the text (Glass, Libra, Vehicle, Satimage, Breast Cancer Original, Breast Tissue, Pima, Yeast), via the Fig. 7 caption. The paper states only that the sets come from UCI, use continuous features only, and were chosen to vary in samples, features, classes and IR. MWMOTE therefore contributes no per-dataset numbers.

## Other flagged inconsistencies

- GDHS lists Vehicle with IR 0.31, below 1 and probably a typo.
- SOS sums Satimage to 6372 rather than the standard 6435.
- AB-SMOTE's Wine Quality class counts do not reconcile with its stated total.
- A-SUWO's Table 3.1 has internal arithmetic inconsistencies (Glass 70+138 does not equal 214).
- OBU states IR from 1.87 but its Table 1 lists Glass1 at 1.82.
- MC-RBO's Hayes-Roth row prints four values for three classes; the first repeats the instance count.
- SOUP's cleveland variants sum to 303 against the UCI 297, matching MC-RBO rather than MC-NCLWO.
