# RESEARCH THINKING HANDOFF
## SMOTE Family Survey — Data Section

> Saved verbatim on 19 Oct 2026 from the version Toon pasted into a new session.
> Reconciliation of its numbers against `out/verified_*.csv` is recorded in `handoff.md` section 4
> (entry "19 ตุลาคม 2026 รับ Research Thinking Handoff"). Do not edit the body below; add notes in `handoff.md`.
>
> **19 Oct 2026, later the same day (Toon approved targeted corrections):** sections 3.1, 4.2, 9.1, 9.2, 9.3, 9.5,
> 10.1, 11.2, 11.5 and 14 C/D carry "Update 19 Oct 2026 (verified)" notes. Original wording is kept and marked
> where superseded, so the reasoning trail survives. Every corrected number is reproduced by
> `build/reconcile_counts.py` (`out/reconcile_counts.json`, rules R1 to R6) from `out/verified_datasets.csv`,
> `out/verified_outcomes.csv` and `out/full_summary.json`, and matches `manuscript/data-section-draft.tex`.
> The main continuity document remains `handoff.md`.

> ### Current state at a glance (19 Oct 2026, final round; read this before sections 9-11)
> Numbers below are the **current** ones. Earlier figures further down (542 rows, 421 wins, 31 papers, "14 of 57",
> the 835-row percentages) are **historical values**, kept with their "Update 19 Oct 2026 (verified)" notes.
> All are reproduced by `python3 build/reconcile_counts.py` (40 checks, all passing; rule R7 defines the partitions)
> from `out/verified_datasets.csv`, `out/verified_outcomes.csv` and `out/full_summary.json`.
>
> | Comparison set (never pooled) | Rows | Papers | Proposed higher | SMOTE higher | Equal |
> |---|---:|---:|---:|---:|---:|
> | **Primary**: plain SMOTE, per-dataset pairs in one table | 541 | 30 | 420 | 82 | 39 |
> | **Eligible wrapper**: SMOTE inside a wrapper, reported separately | 207 | 12 | 175 | 26 | 6 |
> | **Excluded, kept for audit** | 87 | 2 | 36 | 48 | 3 |
> | All rows in `verified_outcomes.csv` | 835 | 44 | | | |
>
> - **KNNOR (aggregate only):** its single row (`verified_outcomes.csv` row 295) is a mean over 19 datasets
>   (.8363 vs .8238). It is reported separately and is not a per-dataset comparison (rule R4). It is 1 of the 87 excluded rows.
> - **RBBoost (cross-table, excluded):** all 86 rows pair RB-B from Supplementary Table 11 with ESM from Supplementary
>   Table 3; the paper never compares the two directly, so they fail the same-table rule (R6). Breakdown 63
>   repository-defined, 17 not stated, 6 original. Kept in the CSV for audit; no substitute pairing was made. See 9.3.
> - **Eligible wrapper by data type:** original 173 (11 papers), modified 30 (6), synthetic 4 (1); no
>   repository-defined, not stated or unmatched rows.
> - **Paper level:** 44 plain / 13 wrapper / 16 no SMOTE baseline; 13 plain-baseline papers give no per-dataset pair,
>   plus KNNOR with a mean only.
> - **Names:** 1,654 entries, 1,653 named (Tomek links placeholder set aside), 771 names, 546 in one paper;
>   exact-name ecoli 26, yeast 22, glass 19; family (prefix) 39, 39, 36.

**Purpose:** Consolidate the research context, evidence, findings, interpretations, and unresolved decisions for developing the Data Section of the SMOTE Family survey.

**Important context:** This is a continuation of an existing research project. The researcher already has an established Cowork conversation and a locally cloned repository. This handoff is intended to communicate research thinking and support decisions about the Data Section, not to restart the project or prescribe a new workflow.

**Primary repository:** https://github.com/tohnperfect/SMOTE25

**Key supporting material:** `SMOTE25_Data_Section_Explorer.html`, `manuscript/data-section-draft.tex`, `out/full_outcome_rows.csv`, and `ai-draft/full/*.json` are referenced by the existing Dataset Atlas. Their current availability and contents should be checked in the existing workspace when needed.

---

## 1. Overall Research Context

The paper is a survey of methods in the SMOTE Family. The Data Section examines the datasets used in the empirical literature and how dataset selection, construction, modification, and reporting affect the evaluation of oversampling methods.

The section should go beyond listing datasets or reporting summary statistics. Its purpose is to synthesize the evidence and explain what the literature's data practices mean for interpreting experimental results.

The intended writing style is formal academic English, concise but sufficiently analytical, with clear topic sentences, evidence-supported interpretations, and traceable references.

The section should distinguish three levels of information:

1. **Observed evidence:** Counts, dataset characteristics, experimental results, and reporting practices extracted from papers.
2. **Review-level analysis:** Categories assigned under explicit review rules, cross-paper comparisons, and identified inconsistencies.
3. **Interpretation:** What these observations suggest about benchmark diversity, comparability, and the strength of the available evidence.

These levels must not be conflated. In particular, reviewer-assigned classifications should not be presented as if the original authors explicitly reported them.

## 2. Central Argument of the Data Section

### Proposed central thesis

The SMOTE literature uses a broad collection of named datasets, but the diversity of dataset names does not necessarily translate into equivalent diversity of underlying data distributions. The datasets used in experiments are not always original, unchanged datasets: some are repository-defined classification tasks, others are modified by researchers, and some are synthetically generated. Furthermore, dataset versions, class definitions, imbalance-ratio calculations, and reporting granularity vary across papers.

These practices matter because the results reported by different studies may not represent directly comparable experimental conditions. Consequently, the apparent performance of a SMOTE-based method should be interpreted in the context of the data on which it was evaluated, how those data were constructed, and how the comparison was reported.

This argument should guide the entire section.

### The narrative flow

1. **What data does the literature use?** Establish the scale, coverage, and recurrence of datasets.
2. **How do researchers construct their experimental datasets?** Distinguish original data from repository-defined, modified, and synthetic data.
3. **How comparable are datasets that share the same name?** Examine differences in sample counts, class definitions, preprocessing, and IR calculations.
4. **How does the evidence vary across data categories?** Summarize reported comparisons with SMOTE while acknowledging the limits of cross-paper comparisons.
5. **What can readers reasonably conclude from the available evidence?** Explain the implications for interpreting the reported results without turning the section into an unrelated algorithm review.

The central message is not that the literature uses bad datasets or that modified datasets are inherently inappropriate. Rather, the literature contains different types of experimental evidence, and those differences need to be visible when interpreting results.

## 3. Corpus and Dataset Coverage

### 3.1 Overall corpus

The current Dataset Atlas reports:

- 76 papers in the overall corpus.
- 73 empirical papers with dataset-based evaluations.
- 1,654 dataset entries extracted from the empirical papers.
- 771 distinct dataset names after normalizing differences in capitalization and punctuation.
- 546 normalized dataset names appearing in only one paper.
- `yeast` and `ecoli` appearing in 39 of the 73 empirical papers each.
- `glass` appearing in 36 of the 73 empirical papers.

> **Update 19 Oct 2026 (verified):** (1) 771 and 546 exclude one entry, the Tomek links placeholder
> `[two-class uniform 2-D example from ref. [4], not named]` (`verified_datasets.csv` row 1558), because it is a
> description, not a dataset name (rule R1, Toon's decision). The row stays in the CSV and in the 1,654 total, so the
> counts are 1,654 entries, 1,653 named entries, 771 names, 546 single-paper names (772 and 547 with the placeholder).
> (2) "Normalizing capitalization and punctuation" is not what the code does: `norm()` in
> `build/analyse_dataset_usage.py` lower-cases, drops text in parentheses and treats underscores and spaces alike;
> hyphens and dots are kept (removing all punctuation would give 678 names).
> (3) 39, 39 and 36 are **family (prefix) counts**, i.e. the name together with its derived splits such as `yeast4`.
> By exact name: ecoli 26, yeast 22, glass 19 papers. The manuscript now states both.

The Atlas identifies the 73-paper denominator as the set of papers with empirical dataset evaluations, excluding ENN, AdaBoost, and the survey *SMOTE Review*. The Atlas also notes that Section 7 of the paper uses a denominator of 71 papers. This difference must be preserved and explained where relevant rather than silently using 73 throughout the manuscript.

### 3.2 What these numbers mean

The 1,654 entries describe dataset use across papers, whereas the 771 names describe normalized dataset-name diversity. Neither number independently establishes how many distinct underlying data distributions were evaluated.

The fact that 546 names occur in only one paper suggests that many datasets have limited recurrence in the reviewed corpus. At the same time, the repeated use of yeast, ecoli, and glass shows that some datasets appear in a substantial share of the literature.

These observations support a distinction between:

- the number of dataset entries;
- the number of normalized dataset names;
- the frequency with which each name is used; and
- the diversity of the underlying data and experimental tasks.

**Interpretive caution:** The 771 normalized names must not be described as 771 verified, genuinely distinct underlying datasets. Name normalization cannot establish whether two entries represent the same data version, different subsets, or different classification tasks.

### 3.3 Dataset diversity as a research question

The key question is not simply whether the literature uses many datasets. It is whether the evidence covers meaningfully different data conditions.

Relevant dimensions include:

- data source and dataset version;
- binary versus multiclass structure;
- sample size;
- feature dimensionality;
- class distribution and imbalance ratio;
- class-selection rules and preprocessing;
- the presence of overlap, noise, or other difficult characteristics when these are explicitly supported by evidence.

The current summary contains some evidence about dataset-name recurrence, sample-size discrepancies, and class construction. It does not yet establish a comprehensive distribution of sample sizes, dimensionalities, overlap levels, or noise levels across all datasets. Such distributions should only be reported if they can be supported by the underlying extraction data.

## 4. Dataset Categories and How Experimental Data Are Constructed

### 4.1 Current category counts

| Dataset category | Entries |
|---|---:|
| Original | 534 |
| Repository-defined | 470 |
| Modified | 331 |
| Synthetic | 120 |
| Not stated | 199 |
| **Total** | **1,654** |

- **Original:** Data used in their distributed form, according to the review's current classification rules.
- **Repository-defined:** Classification tasks or binary variants supplied by a repository, such as KEEL or imbalanced-learn, according to the final category definition.
- **Modified:** Data whose class selection, class distribution, thresholding, feature set, or other relevant properties have been changed by the researchers.
- **Synthetic:** Data generated by the researchers rather than taken directly from an existing empirical dataset.
- **Not stated:** The available paper does not provide sufficient evidence to assign one of the preceding categories.

The precise boundaries between categories must follow the project's recorded classification decisions. In particular, the treatment of repository-defined datasets remains associated with a pending decision in the existing Atlas. The final manuscript should not redefine these categories independently of that decision.

### 4.2 Author-reported information versus review classification

The initial extraction could not classify 555 of the 1,654 entries. Applying review rules allowed another 356 entries to be classified, leaving 199 entries in the current `Not stated` category.

This distinction is important. It indicates that the review could infer or establish a category for some entries using available evidence even when the initial extraction did not identify the category.

However, the initial 555 unclassified entries should not automatically be described as 555 cases in which the original authors failed to report the dataset type. The distinction between extraction status and the original paper's reporting must be preserved.

The manuscript should state explicitly how the categories were assigned and how author-reported information was distinguished from reviewer-assigned classifications.

> **Update 19 Oct 2026 (verified):** 555 = entries whose category the PDF reader could not assign from the paper
> (`how_obtained` = not stated in `verified_datasets.csv`). The 356 reassigned by Toon's rules of 18 Oct
> (`how_basis`): multiclass common name with no stated change -> original 192; KEEL file-name pattern ->
> repository-defined 108; native two-class set, paper silent (rule A) -> original 56. Separately, rule B moved one
> reader-labelled original entry to modified (rows or attributes removed). Hence original 287 -> 534,
> repository-defined 362 -> 470, modified 330 -> 331, not stated 555 -> 199. The 555 describe what a reader could
> tell from the paper, not an author's intent; keep that wording.

### 4.3 Why dataset construction matters

The category counts support a key observation: the empirical literature does not evaluate SMOTE-based methods exclusively on unchanged original datasets.

Repository-defined tasks, researcher-modified datasets, and synthetic datasets account for substantial parts of the extracted corpus. These are legitimate experimental choices, but they represent different forms of evidence.

- A repository-defined binary task may use a class definition selected by the repository rather than by the current paper's authors.
- A researcher-modified dataset may use a particular class as the minority class or alter the class distribution.
- A synthetic dataset may be designed to represent a particular data configuration.
- An original dataset may still require interpretation in light of its version, preprocessing, and the particular task used.

Therefore, dataset category should be treated as contextual information for interpreting experimental findings, not as a quality ranking.

## 5. Dataset Selection Practices

| Dataset selection practice | Papers |
|---|---:|
| Provide a rationale for dataset selection | 48 |
| Cite previous work as the selection rationale | 14 |
| Describe datasets only as widely used | 3 |
| Provide no selection rationale | 8 |

These categories sum to 73 under the current extraction.

- 20 papers reuse benchmark lists from previous studies.
- 11 of these papers adopt the entire earlier benchmark list.

### Interpretation

The evidence suggests that benchmark selection is often connected to existing literature. This can support comparability and continuity with earlier evaluations, but repeated use of familiar datasets does not automatically establish broad coverage of data conditions.

The relevant research question is whether the benchmark selection is appropriate for the method's intended scope and whether the rationale is sufficiently transparent for readers to understand what kinds of data the evaluation represents.

The manuscript should avoid treating benchmark reuse as inherently problematic. The finding concerns selection and evidence coverage, not a blanket judgment about whether commonly used datasets should be retained.

## 6. Dataset Modification and Imbalance Construction

### 6.1 Binarization and minority-class definition

The current extraction identifies 37 papers that perform binarization. Of these, 8 do not identify which class is treated as the minority class.

This matters because the minority-class definition determines the classification task being evaluated. In multiclass-to-binary transformations, selecting different classes or merging classes differently can produce different tasks even when the original dataset name remains unchanged.

The section should therefore distinguish between the original dataset and the derived classification task.

### 6.2 Deliberately changing the imbalance ratio

The current notes identify 125 dataset entries from five papers—G-SMOTE, HDE, NBU, RSMOTE, and k-means SMOTE—that randomly undersample the minority class to increase the imbalance ratio.

The reported median IR is:

- Modified datasets: 15.0.
- Original datasets: 7.6.

These numbers suggest that the modified datasets in the current extraction tend to have a higher median imbalance ratio than the original datasets.

However, the manuscript should verify the precise unit of analysis, IR definition, and category membership before making a direct comparison. The result should not be interpreted as evidence that all modified datasets are more imbalanced, nor should it imply that a higher IR necessarily means more overlap, more noise, or greater difficulty on every other dimension.

### 6.3 Original-only and mixed-category evaluations

Of the 73 empirical papers:

- 11 use original datasets only.
- Most of those 11 papers are associated with multiclass methods; the notes identify MC-CCR, MC-RBO, MDO, SCUT, and EMDO among the relevant examples.
- 55 use two or more dataset categories.

These observations suggest that many evaluations combine datasets with different construction histories. This increases the importance of identifying which categories support a particular result.

The 11 original-only papers and the 55 mixed-category papers should not be treated as mutually exhaustive groups unless the underlying classification confirms that all 73 papers are assigned consistently and that no paper is missing from the count.

### 6.4 Repository-specific patterns

**KEEL**
- 486 dataset entries.
- 313 entries use binary two-class files predefined by KEEL.
- 6 entries are classified as author-modified.

**UCI**
- 424 dataset entries.
- 193 entries are classified as author-modified.
- 68 entries are not stated.

These counts suggest that, in the reviewed corpus, KEEL is frequently used through repository-defined binary tasks, whereas UCI entries more often involve author modification.

This is a finding about the current corpus, not a universal claim about KEEL or UCI as repositories. The exact category definitions and the treatment of repository-defined tasks must be finalized before this comparison appears in the manuscript.

## 7. The Same Dataset Name Does Not Guarantee the Same Experimental Data

### 7.1 Differences in reported sample size

The current audit identifies 198 normalized dataset names with reported sample sizes in at least two papers. Of these, 78 have different reported sizes across papers.

Examples include:

- `thyroid`: 7,200 versus 720 instances.
- `dermatology`: 358 versus 366 instances.
- `pima`: 768, 769, 635, and 590 instances.

These differences show that dataset names alone may be insufficient to establish that the same observations or the same experimental task were used.

Potential explanations may include different versions, subsets, class selection, preprocessing, or reporting errors. Unless the source papers establish the reason, the review should not assign a specific explanation to a discrepancy.

### 7.2 Inconsistent imbalance-ratio definitions

The extraction identifies at least nine different IR definitions across the reviewed papers. Some definitions cannot be directly converted into one another.

This is important because a reported IR is only interpretable in relation to its formula and class-counting convention. Without that information, comparisons between datasets or studies may be misleading.

The section should avoid presenting IR values from different definitions as directly comparable unless the underlying quantities can be reconciled.

### 7.3 Examples from the MWMOTE audit

- Statlog Landsat is counted as two datasets.
- Some generic dataset names are ambiguous.
- An attribute was removed from Abalone without explicit disclosure in the relevant account.
- The reported vehicle IR values in MC-CCR and MC-RBO cannot be derived from the formulas currently known to the review.

These are examples of discrepancies that require traceable evidence from the source papers. They should be used selectively to illustrate broader issues rather than presented as a list of accusations.

### Central interpretation

The problem is not simply that dataset names may be inconsistent. It is that the name does not necessarily specify the complete experimental object.

For meaningful comparison, the data source, version, sample count, feature set, class definitions, preprocessing operations, and IR calculation may all be relevant.

This is one of the strongest candidate findings for the Data Section because it connects dataset curation directly to the interpretation of experimental results.

## 8. What Makes These Datasets Difficult?

This question is part of the intended analytical scope, but the current summary does not establish a complete, corpus-wide profile of data difficulty.

- **Class imbalance:** The degree of imbalance and the formula used to calculate it.
- **Class overlap:** Whether minority and majority observations occupy overlapping regions.
- **Noise:** Whether labels or feature values are noisy, or whether the paper explicitly identifies noisy observations.
- **Dimensionality:** The number and type of features, including whether high dimensionality is a stated challenge.
- **Sample size:** Whether the dataset is small, large, or otherwise relevant to the method's intended use.
- **Class structure:** Whether the task is binary or multiclass and how minority classes are defined.
- **Data construction:** Whether the task is original, repository-defined, modified, or synthetic.

The current figures about IR, sample-size discrepancies, binarization, and dataset modification provide evidence about some of these dimensions. They do not, by themselves, establish the prevalence of class overlap or noise across the corpus.

**Writing rule:** Do not infer that a dataset is noisy or has severe class overlap merely because its IR is high. Report these characteristics only when they are documented in the papers or can be established through a clearly defined and reproducible analysis of the underlying data.

## 9. Reported Comparisons Against SMOTE

The review contains two comparison summaries that must remain separate until their inclusion criteria have been fully reconciled.

### 9.1 Paper-level comparison coverage

- 44 papers compare a proposed method against plain SMOTE.
- 13 papers compare against SMOTE within a wrapper.
- 16 papers do not compare with SMOTE at all.

These counts sum to 73 under the current extraction.

Only 31 papers provide per-dataset scores for both the proposed method and plain SMOTE in the same table under the current paired-comparison rule.

> **Update 19 Oct 2026 (verified):** 44/13/16 are **paper-level** baseline counts (`smote_kind` in `out/full_summary.json`,
> classified from the printed SMOTE name) and are correct. They are not the same set as "papers with comparison
> rows": 44 papers also have rows in `verified_outcomes.csv`, but those are 31 plain + 13 wrapper, a coincidence of
> numbers. "31" is superseded: KNNOR's only row (`verified_outcomes.csv` row 295) is a mean over its 19 datasets, not
> a per-dataset pair (rule R4). Under the manuscript rule, **30 papers** give per-dataset plain-SMOTE pairs; KNNOR is
> reported separately as an aggregate (.8363 vs .8238). All 13 wrapper papers have rows, but RBBoost's are excluded
> (see 9.3), leaving **12 eligible wrapper papers**.

The section should distinguish comparisons with plain SMOTE from comparisons with a wrapped SMOTE procedure. These are not necessarily equivalent baselines.

### 9.2 The 542 paired comparisons (historical; current primary set is 541 rows, 30 papers)

- Proposed method wins: 421.
- Ties: 39.
- SMOTE wins: 82.

| Dataset category | Comparisons | Proposed method wins | SMOTE wins | Ties |
|---|---:|---:|---:|---:|
| Original | 167 | 133 | 29 | 5 |
| Repository-defined | 119 | 90 | 13 | 16 |
| Modified | 143 | 109 | 30 | 4 |
| Synthetic | 5 | 5 | 0 | 0 |
| Cannot be told | 104 | 82 | 9 | 13 |
| Unmatched dataset rows | 4 | 2 | 1 | 1 |
| **Total** | **542** | **421** | **82** | **39** |

The current notes also report 286 comparisons on standard datasets, defined as original plus repository-defined data. Within those 286 comparisons, SMOTE wins 42 times and ties 21 times.

The category totals in the table add to 542. The interpretation of `Cannot be told` and `Unmatched dataset rows` should remain faithful to the Atlas's operational definitions and should not be merged with other categories without justification.

> **Update 19 Oct 2026 (verified):** the table above is the pre-correction version and is kept for provenance. The 542 rows
> include KNNOR's aggregate row, which was one of the 4 unmatched rows. The primary set used in the manuscript is
> **541 per-dataset rows from 30 papers: proposed 420, SMOTE 82, ties 39**. Only two cells change:
> Unmatched 4/2/1/1 -> **3/1/1/1** (2 papers), Total 542/421/82/39 -> **541/420/82/39**. All other rows, and the
> 286 standard rows (SMOTE 42, ties 21), are unchanged. In the 541 rows, 3 are unmatched and 15 matched by row order.
>
> **Update 19 Oct 2026, outcome-mapping audit (verified against the paper tables by Toon):** AB-SMOTE "Employee Attrition"
> had been given Haberman's characteristics by row order; its own Table I entry is "not stated". It moves from Original to
> Cannot be told: Original **166** (132/29/5), Cannot be told **105** (83/9/13), standard rows **285** (SMOTE 42, ties 21).
> Totals 541/420/82/39 are unchanged. Four other rows were re-linked with no change of category (AB-SMOTE Harberman,
> RUSBoost CONTRACEPTIVE and SATIMG, DGOT bankruptcy). Audit trail: `out/outcome_mapping_audit.csv`.

### 9.3 The separate 835-comparison summary (historical framing; see the update below)

- Original datasets: approximately 81% wins and 16% losses.
- Modified datasets: approximately 79% wins and 18% losses.
- Not stated: approximately 73% wins and 17% losses.
- Repository-defined KEEL datasets: approximately 63% wins and 26% losses.
- Synthetic datasets: 9 wins out of 9 comparisons.

These figures are from a different summary with different inclusion criteria from the 542 paired comparisons.

> **Update 19 Oct 2026 (verified):** the statement above is **superseded**. The 835 rows are not a separately defined summary;
> they are every row in `verified_outcomes.csv`, i.e. the plain rows **plus** the wrapper rows, with the same
> `raw_sign`. The percentages above pool plain and wrapper baselines and are kept only as history. Decomposition:
> 835 = 541 plain per-dataset (30 papers) + 1 KNNOR aggregate + 207 eligible wrapper rows (12 papers)
> + 86 RBBoost rows excluded from every comparison set.
> **RBBoost exclusion (Toon's decision, 19 Oct):** all 86 rows pair RB-B from Supplementary Table 11 (Boosting family)
> with ESM from Supplementary Table 3 (Data-processing family). Checked against the supplement text: every RB-B value
> matches Table 11, every ESM value matches Table 3, ESM is not a column of Table 11 and RB-B is not a column of Table 3.
> The protocol is shared (G-mean; J48 with Laplace smoothing; ensembles of 100; stratified 5x2 CV, paper p.101), but the
> paper compares methods only within families (p.102), so the pairs fail the same-table rule. The rows stay in the CSV
> for audit (63 repository-defined, 17 not stated, 6 original). No substitute pairing (E-RB, SMOTEBoost) was made.
> Consequence for the "repository-defined 63% wins, 26% losses" line: it was driven by RBBoost. On eligible rows,
> repository-defined appears **only** in the plain set: 119 rows, 9 papers, 90 / 13 / 16; the eligible wrapper set has
> no repository-defined rows. Eligible wrapper rows by type: original 173 (11 papers, 144 / 24 / 5), modified 30
> (6 papers, 27 / 2 / 1), synthetic 4 (1 paper, 4 / 0 / 0); total 207, 175 / 26 / 6. Plain and wrapper are never pooled.

**Do not combine the 542 and 835 counts, use them as interchangeable denominators, or present their percentages as if they were calculated from one common table.** The criteria that determine inclusion in each summary must be checked before either is used as a central manuscript result.

### 9.4 How to interpret these comparisons

The current summaries indicate that proposed methods frequently report better scores than their SMOTE baselines in the selected comparisons. However, these are results reported across different papers, datasets, metrics, experimental protocols, and potentially different baselines.

The evidence does not constitute a new controlled experiment in which all methods are evaluated under one shared protocol. Consequently, the observed win rates should not be interpreted as proof that a dataset category causes a particular method to perform better.

The comparison results are most useful for examining how reported performance is distributed across data categories and how much contextual information is needed to interpret the apparent wins.

### 9.5 Standard versus nonstandard data in the paired comparisons

- 29 of the 31 paired-comparison papers include at least one standard dataset, where standard means original or repository-defined.
- Two papers compare only on nonstandard or unidentifiable data: INOS and KNNOR.

> **Update 19 Oct 2026 (verified):** with 30 per-dataset papers, **29 of the 30** include a standard dataset and only **INOS**
> compares solely on nonstandard or unidentifiable data. KNNOR is not counted here because its only comparison is an
> aggregate. The six standard-only papers are unchanged.
- Six papers compare only on standard data: GDO, MC-MBRC, MKC-SMOTE, OREM-M, SCUT, and SPE.

The distinction between standard and nonstandard datasets is useful for characterizing the evidence base, but the manuscript should retain the project's exact definition of standard datasets. The label should not imply that standard datasets are inherently more valid or that modified datasets are inherently inferior.

## 10. Reporting Granularity and Verifiability

### 10.1 How papers report results

| Reporting format | Papers |
|---|---:|
| Per-dataset result table | 47 |
| Partial per-dataset results | 8 |
| Plots only | 5 |
| Averages only | 5 |
| Ranks only | 3 |
| No comparison | 5 |
| **Total** | **73** |

Among 57 papers comparing with plain or wrapped SMOTE, 14 do not provide complete paired per-dataset scores in the paper.

> **Update 19 Oct 2026 (verified):** 13, not 14. The 13 plain-baseline papers without rows are Borderline-SMOTE, Safe-Level-SMOTE,
> Cluster-SMOTE, k-means SMOTE, GLOS (plots), G-SMOTE, CISO, SplitBal, QC-SMOTE (averages), MDO, RBO, MC-NCLWO
> (ranks) and Hassanat et al. (per-dataset partial, no pair). "14" counted KNNOR twice (also among the 31). KNNOR is
> now described as a fourteenth paper whose pair exists only as a mean. 44 plain = 30 with per-dataset pairs
> + 13 without + KNNOR. (RBBoost has per-dataset values in its supplement, so it is not in this list; its pairs are
> excluded for the cross-table reason in 9.3.)

The table should make clear that reporting formats describe how results are presented, not whether the experimental methods themselves are valid.

### 10.2 Baseline reuse cases

- QC-SMOTE copies baseline values from VS-SMOTE.
- MC-CCR's SMOTE-all values are identical to those in MC-RBO across 20 datasets.
- EMDO's baseline columns duplicate AMDO values on 9 shared datasets; the paper states that the datasets are the same, but the current notes say the baseline values were not identified as copied.

These cases need careful wording and source-specific verification. Identical values may warrant investigation, but the manuscript should not imply misconduct or definitively characterize a value as copied without sufficient evidence.

### 10.3 Implications

When papers report only aggregate scores, rankings, or selected plots, readers may be unable to determine how a method performs across individual datasets or how it compares with the baseline on the same tasks.

This creates a limit on what the survey can reconstruct from published evidence. It also explains why the number of papers claiming improvements is not equivalent to the number of independently verifiable paired comparisons.

The Data Section should focus on this consequence for evidence interpretation. A detailed list of reporting recommendations may belong in a separate reporting or reproducibility section if another part of the manuscript already covers that topic.

## 11. Proposed Section Structure

A conceptual proposal, to be reconciled with the existing manuscript and the division of responsibilities among coauthors.

### 11.1 Data Extraction and Classification
Corpus, unit of analysis, name normalization, category definitions, author-reported vs reviewer-assigned.
Key evidence: 76 papers; 73 empirical; 1,654 entries; 771 normalized names; 199 not stated after review rules.

### 11.2 The Benchmark Landscape
Key evidence: 546 names in one paper; yeast and ecoli 39 papers each; glass 36; 48 papers give a selection rationale; 20 reuse previous lists, 11 adopt a full list.
> **Update 19 Oct 2026 (verified):** 1,653 named entries (Tomek placeholder set aside) -> 771 names; 39/39/36 are family counts,
> exact-name counts ecoli 26, yeast 22, glass 19 (see 3.1).

### 11.3 How Datasets Are Selected and Constructed
Key evidence: category counts; 37 papers binarize, 8 do not identify the minority class; 125 entries from five papers undersample the minority class; median IR modified 15.0 vs original 7.6; KEEL vs UCI patterns; 11 original-only papers, 55 multi-category.

### 11.4 The Same Dataset Name Is Not Necessarily the Same Data
Key evidence: 78 of 198 repeatedly reported names have different sample counts; thyroid, dermatology, pima; at least nine IR definitions; MWMOTE audit examples.

### 11.5 Reported Comparisons Across Data Categories
Key evidence: 44 plain / 13 wrapped / 16 none; 31 papers with paired per-dataset scores; 542 comparisons (421 / 82 / 39); standard vs nonstandard coverage. Treat the 835 summary as a distinct analysis.
> **Update 19 Oct 2026 (verified):** 44 / 13 / 16 at paper level (unchanged); **30 papers, 541 comparisons (420 / 82 / 39)**;
> KNNOR aggregate reported separately; wrapper comparisons reported separately, 207 eligible rows from 12 papers;
> RBBoost's 86 cross-table rows excluded and disclosed; 835 is the total of all rows, not a distinct analysis (see 9.3).

### 11.6 Implications for Interpreting the Evidence
- Dataset-name diversity is not the same as data-distribution diversity.
- Experimental tasks may differ even when their dataset names match.
- Dataset construction and IR definitions influence how comparisons should be interpreted.
- Published comparison results are constrained by the reporting granularity and comparability of the underlying experiments.

## 12. Recommended Tables and Their Purpose

- **Table 1: Dataset coverage and classification** — scope and operational categories (papers, entries, normalized names, category counts, not stated, author-reported vs reviewer-assigned note).
- **Table 2: Dataset construction practices** — original / repository-defined / modified / synthetic with definitions and examples; binarization and minority-class selection; class-distribution modification; repository patterns if still relevant.
- **Table 3: Paired comparisons by dataset category** — the 542 comparisons; caption must state unit, inclusion criteria, denominator, and win/tie definition.

A separate compact table may be useful for sample-size discrepancies or IR definitions. Avoid tables that duplicate the prose.

## 13. Writing and Interpretation Principles

1. Concise, formal academic English.
2. One central claim per paragraph, with evidence and proportionate interpretation.
3. Keep observed counts separate from interpretation.
4. Distinguish author-reported information from review-assigned classifications.
5. Define the unit of analysis for every count.
6. State denominators and inclusion criteria for every proportion or win rate.
7. Keep the 542 and 835 summaries separate.
8. Do not infer overlap or noise from IR alone.
9. Do not assume identical names mean identical observations or tasks.
10. Do not imply original data are always superior or synthetic data inherently unsuitable.
11. Avoid causal language for observational cross-paper evidence.
12. Use cautious language ("suggests", "indicates", "within the reviewed corpus").
13. Use examples selectively.
14. Verify citations, keys, tables and cross-references against the manuscript and sources.
15. Avoid duplicating algorithm mechanisms or recommendations assigned to other sections.

## 14. Unresolved Decisions and Checks

- **A. Denominator consistency** — 73 (Atlas) vs 71 (Section 7).
- **B. Dataset-category definitions** — treatment of repository-defined tasks (KEEL, imbalanced-learn) pending.
- **C. Author-reported vs reviewer-assigned** — what the 555 and 356 represent.
  **Resolved 19 Oct 2026:** see the update in 4.2 (192 + 108 + 56 rule assignments; rule B moved one entry).
- **D. 542 vs 835** — inclusion rules, units, treatment of wrapped SMOTE.
  **Resolved 19 Oct 2026:** 835 = all rows (plain + wrapper); primary set 541 plain per-dataset rows (30 papers);
  KNNOR aggregate separate; eligible wrapper 207 rows (12 papers); RBBoost 86 rows excluded (cross-table). See 9.3.
- **E. Standard-dataset definition** — original + repository-defined.
- **F. Dataset-name discrepancies** — report without assigning cause unless established.
- **G. IR definitions** — which formulas are comparable; no pooled summaries across incompatible definitions.
- **H. Difficulty characteristics** — no corpus-wide noise/overlap prevalence yet.
- **I. Baseline reuse cases** — verify papers, tables, values; neutral language.
- **J. Reporting recommendations** — coordinate with the author of other sections.

## 15. Expected Outcome

A coherent English LaTeX Data Section that tells one connected story:

**The SMOTE literature contains many dataset names, but the underlying experimental evidence varies in dataset origin, task construction, imbalance definition, and reporting detail. These differences do not automatically invalidate reported results, but they limit how directly those results can be compared across papers. Understanding the data behind the evaluations is therefore essential to interpreting the evidence on SMOTE-based methods.**

## 16. Session Continuity and Handoff Maintenance

- 16.1 Monitor session capacity; prepare an updated handoff before the limit, not at the last moment.
- 16.2 Before ending, update the handoff with: current progress; key findings and decisions; evidence and verification status; files and locations; unfinished tasks; known issues and risks; prioritized next actions; working state.
- 16.3 Distinguish: completed and verified / completed but not verified / in progress / pending / blocked. A written draft is not "completed"; record verification separately.
- 16.4 Carry forward decisions and uncertainties (542 vs 835, category definitions, denominators, IR, version discrepancies, baseline comparisons). Never silently replace an uncertain value.
- 16.5 On resuming, read the latest handoff, confirm the status of top-priority tasks, do not redo or overwrite work without reason. Claims must remain traceable to evidence.
- 16.6 End-of-session checklist: update handoff; record verified findings and decisions; list unfinished and blocked tasks; prioritize next steps; record files and locations; list claims needing verification; confirm edits are saved; state where to resume.

Priority rule: maintaining a reliable handoff takes precedence over starting a new substantial task when remaining capacity is insufficient. When updating, preserve all still-relevant information.
