# SMOTE25 development brief: origin, additions, applications

Prepared 8 October 2026 for the SMOTE25 JAIR survey. Companion files: `smote25-overview.html` (interactive page) and `SMOTE25_evidence_map_v1.csv` (coded corpus, 73 works).

The paper is told as a development story in three parts, each read on three angles (data, algorithm, evaluation):

1. **Origin (2002):** SMOTE as published, on all three angles.
2. **What has been added:** milestones since 2002, per angle, plus counts from the team corpus.
3. **Applications:** where SMOTE-based methods reached real problems, and how strong that evidence is.

Status labels for references: Verified (checked in this pass), Partly verified, In team Drive (PDF in the SMOTE25 folders), Preprint, To verify (from memory; confirm before citing). Facts from the 2002 paper carry page numbers from the JAIR pagination. No quotations are reproduced; all wording is paraphrase.

## Storyline map

| Angle | Part 1. In 2002 | Part 2. What has been added | Part 3. In applications |
|---|---|---|---|
| Data | Binary problems with continuous features: 9 datasets, imbalance from 1.9:1 (Pima) to 52:1 (Can). The difficulty is framed as overfitting from replicated minority points. | Borderline and noisy examples, overlap, sub-concepts, multiclass relations, then regression, multi-label, time series, graphs, images, streams and fairness. Works naming a difficulty beyond the ratio: 7 of 12 (2002 to 2009), 36 of 40 (since 2018). | Real data in at least 12 domains, almost all analysed retrospectively. High-dimensional, spatial and encoded categorical data bring their own traps. |
| Algorithm | k = 5 minority neighbours, a random point on the segment, N% amounts, combined with random undersampling; SMOTE-NC and SMOTE-N for nominal features. | Seed weighting, partner choice, cleaning, boosting, shaped regions, fitted distributions and learned generators. Leaving the plain segment: 4 of 22 generators before 2018, 17 of 31 since. | Plain SMOTE and its classic hybrids dominate the application studies collected; a few domains use newer variants such as Geometric SMOTE or k-means SMOTE. |
| Evaluation | C4.5, Ripper and Naive Bayes; ROC curves swept by sampling levels, AUC and the convex hull. All eight C4.5 AUC gains over undersampling are below 0.01, and no significance test is run. | Non-parametric tests and KEEL, precision-recall curves and MCC, leakage-safe splits, calibration checks and strong-learner baselines. A test is mentioned by 15 of 16 works in 2010 to 2017 and 27 of 40 since 2018. | An evidence ladder: almost all level a (retrospective), a few level b (external validation), one level c (prospective), no verified level d (deployment with measured impact). |

## Part 1. SMOTE in 2002

Source: Chawla, Bowyer, Hall, Kegelmeyer (2002). SMOTE: Synthetic Minority Over-sampling Technique. JAIR 16:321-357 (doi:10.1613/jair.953).

### Data angle

- Binary classification only. The authors note SMOTE could target one class of a multiclass problem, but study two-class problems. (pp. 333-334)
- Motivated by fraud detection, telecommunications, text classification, oil spills and mammography, where accuracy is misleading. (pp. 321-322)
- The one difficulty designed for: replicating minority points makes decision regions very specific and overfits; synthetic points let the minority region spread into feature space. (pp. 326-328)
- Implicit assumption of continuous features in a meaningful Euclidean feature space; nominal features need the Section 6 extensions. (p. 328)
- SMOTE-NC adds the median of the continuous standard deviations for every differing nominal feature, interpolates continuous values and takes nominal values by majority vote of the neighbours. On Adult it did worse than undersampling. (pp. 348-349)
- SMOTE-N uses the modified Value Difference Metric and a per-feature majority vote. Proposed, not evaluated. (pp. 349-351)

| Dataset | Majority | Minority | Imbalance ratio | Minority share | Note |
|---|---|---|---|---|---|
| Pima Indian Diabetes | 500 | 268 | 1.87 | 34.9% | UCI; diabetes in a population near Phoenix |
| Phoneme | 3,818 | 1,586 | 2.41 | 29.3% | ELENA project; nasal vs oral sounds; 5 features |
| Adult | 37,155 | 11,687 | 3.18 | 23.9% | 48,842 samples; 6 continuous and 8 nominal features |
| E-state | 46,869 | 6,351 | 7.38 | 11.9% | NCI yeast anticancer drug screen; electrotopological descriptors |
| Satimage | 5,809 | 626 | 9.28 | 9.7% | Smallest of 6 classes against the rest |
| Forest Cover | 35,754 | 2,747 | 13.02 | 7.1% | Ponderosa Pine vs Cottonwood/Willow, from the 7-class data |
| Oil | 896 | 41 | 21.85 | 4.4% | Oil slick vs look-alike (Kubat, Holte, Matwin 1998) |
| Mammography | 10,923 | 260 | 42.01 | 2.3% | 11,183 samples; calcifications |
| Can | 435,512 | 8,360 | 52.09 | 1.9% | 443,872 samples from a Sandia simulation (ExodusII), via AVATAR |

Feature counts are stated in the paper only for Phoneme and Adult; other counts shown elsewhere are repository values.

### Algorithm angle

1. For each minority point, find its k = 5 nearest neighbours among minority points only. (pp. 328-329)
2. Pick neighbours according to the amount N%: at 200%, two of the five, one synthetic point toward each. (p. 328)
3. Place the new point at a random position on the segment: the point plus a random number in [0, 1] times the difference. (p. 328)
4. For amounts below 100%, apply SMOTE to a random subset of the minority; amounts are assumed to be multiples of 100. (p. 329)
5. Randomly undersample the majority to a target ratio (levels from 10% to 2000%) and train the learner. (pp. 331, 337)

- In the published pseudo-code the random gap is drawn per attribute, not once per point as in most modern implementations. Worth a footnote. (p. 329)
- No complexity analysis, runtime figures or code release; the mammography data came from the USF Intelligent Systems Lab. (pp. 328-329)

### Evaluation angle

- Learners: C4.5 (release 8), Ripper and Naive Bayes. (pp. 331-332)
- Operating points: fixed oversampling with swept undersampling levels; Ripper loss ratio from 0.9 to 0.001; Naive Bayes priors up to 50 times the majority; C4.5 leaf thresholds on Phoneme. (pp. 332-345)
- Metrics: true and false positive rates over 10-fold cross-validation, AUC by the trapezoidal rule, and the ROC convex hull to find potentially optimal classifiers. (pp. 332-339)
- Headline: SMOTE was not the best in 4 of 48 experiments (Pima with Naive Bayes, Oil with Ripper, Can with overlapping curves, Adult with SMOTE-NC). (p. 352)
- No variances, confidence intervals or significance tests; dominance is read visually in ROC space.
- Training-set sizes suggest SMOTE was applied inside the training folds, but the paper does not say so explicitly. (pp. 328-329)

| Dataset (C4.5) | AUC, undersampling | Best SMOTE level | AUC, SMOTE | Gain |
|---|---|---|---|---|
| Pima | 0.7242 | 100% | 0.7307 | +0.0065 |
| Phoneme | 0.8622 | 200% | 0.8661 | +0.0039 |
| Satimage | 0.8900 | 400% | 0.8975 | +0.0075 |
| Forest Cover | 0.9807 | 300% | 0.9849 | +0.0042 |
| Oil | 0.8524 | 500% | 0.8537 | +0.0013 |
| Mammography | 0.9260 | 400% | 0.9330 | +0.0070 |
| E-state | 0.6811 | 200% | 0.6828 | +0.0017 |
| Can | 0.9535 | 50% | 0.9560 | +0.0025 |

Table 3, p. 345, as parsed from the PDF; re-check against the printed page. Ripper and Naive Bayes AUCs are not tabulated.

### Where SMOTE could hurt, already in 2002

- **Adult:** SMOTE-NC, and even SMOTE on the continuous features alone, did no better than undersampling; the authors point to synthetic points overlapping the majority. (p. 349)
- **Can:** The mesh geometry meant synthetic points could land in uninteresting places inside the surface. (p. 337)
- **Oil:** No clear improvement over one-sided selection. (p. 346)

### The paper's own roadmap (future work, p. 348)

| Future-work item | Later methods that take it up (our mapping) |
|---|---|
| Choose k adaptively | No clear successor identified in the corpus (check) |
| Other strategies for creating synthetic points | Safe-Level-SMOTE (2009), MDO (2016), Geometric SMOTE (2019), GAMO (2019) |
| Focus on examples that are misclassified | Borderline-SMOTE (2005), ADASYN (2008), RAMOBoost (2010) |
| Use majority-class neighbours | Safe-Level-SMOTE (2009), MWMOTE (2014) |

### Limitations visible today

- Binary problems and mostly continuous features
- A single fixed k
- AUC margins mostly below 0.01, without uncertainty estimates
- No precision-recall curves, F-measure, G-mean or MCC
- No calibration check, although changing class priors distorts probabilities
- Weak learners only; boosting arrived with SMOTEBoost in 2003
- No public code
- Real-domain data (oil spills, mammography, drug screening, simulation) analysed retrospectively; no operational use reported

## Part 2. What has been added since 2002

Corpus counts (73 primary works in the Drive folders): works naming a difficulty beyond the imbalance ratio rose from 7 of 12 (2002 to 2009) to 36 of 40 (since 2018); generators leaving the plain segment went from 4 of 22 before 2018 to 17 of 31 since; a significance test is mentioned by 15 of 16 works in 2010 to 2017 and 27 of 40 since 2018; MCC appears in 5 works and precision-recall curves in 6; code links appear in 27 works, all from 2018 on.

### Data angle

In 2002, SMOTE assumed binary problems with continuous features and designed for one difficulty: replicated minority points make decision regions too specific. Its own Adult and Can results already hinted at overlap and geometry problems.

| Year | Milestone | What it added | Reference | Status |
|---|---|---|---|---|
| 2002 | SMOTE-NC and SMOTE-N | Mixed and nominal features | Chawla et al., JAIR 16:321-357 (doi:10.1613/jair.953) | Verified |
| 2005 | Borderline-SMOTE | Borderline ("danger") minority examples become the focus | Han, Wang, Mao, ICIC 2005, LNCS 3644 | In team Drive |
| 2010 | SPIDER2 | Noise- and borderline-aware selective preprocessing | Napierala, Stefanowski, Wilk, RSCTC 2010 | In team Drive |
| 2012 | Multiclass imbalance analysis | Settings with several minority and majority classes | Wang and Yao, IEEE TSMC-B 42(4):1119-1130 | To verify |
| 2013 | Binarization for multiclass imbalance | One-vs-one and one-vs-all decomposition combined with SMOTE | Fernandez et al., Knowledge-Based Systems 42:97-110 | In team Drive |
| 2013 | Data intrinsic characteristics | Overlap, small disjuncts, density, noise and dataset shift named as the real difficulty | Lopez et al., Information Sciences 250:113-141 | To verify |
| 2013 | SMOTE in high dimensions | SMOTE shrinks variance and adds correlation; weaker than undersampling in high dimensions | Blagus and Lusa, BMC Bioinformatics 14:106 (doi:10.1186/1471-2105-14-106) | Verified |
| 2013 | SMOTER | Regression with rare extreme target values | Torgo et al., EPIA 2013, LNCS 8154 | Partly verified |
| 2013 | INOS | Oversampling for imbalanced time series | Cao et al., IEEE TKDE 2013 | In team Drive |
| 2015 | MLSMOTE | Multi-label imbalance | Charte et al., Knowledge-Based Systems 89:385-397 | To verify |
| 2016 | Example typology | Safe, borderline, rare and outlier minority examples | Napierala and Stefanowski, J. Intelligent Information Systems 46:563-597 | To verify |
| 2018 | k-means SMOTE | Within-class imbalance and small disjuncts through clustering | Douzas, Bacao, Last, Information Sciences 465:1-20 | In team Drive |
| 2021 | GraphSMOTE | Imbalanced node classification in a graph neural network embedding | Zhao, Zhang, Wang, WSDM 2021, pp. 833-841 | Partly verified |
| 2021 | Fair-SMOTE | Balances classes and protected subgroups together; removes biased labels | Chakraborty, Majumder, Menzies, ESEC/FSE 2021 (doi:10.1145/3468264.3468537) | Verified |
| 2022 | Imbalanced data streams | Taxonomy and benchmark for imbalanced, drifting streams | Aguiar, Krawczyk, Cano, arXiv 2204.03719 (https://arxiv.org/abs/2204.03719) | Preprint |
| 2023 | DeepSMOTE | SMOTE in a learned latent space for images | Dablain, Krawczyk, Chawla, IEEE TNNLS 34(9):6390-6404 | Verified |
| 2025 | Continuous Fair SMOTE | Fairness-aware SMOTE for data streams | LNCS chapter, 2025 (doi:10.1007/978-3-032-04558-4_27) | Verified |
| 2025 | MLOS | Highly imbalanced, overlapped data with Mahalanobis local information | Expert Systems with Applications 2025 | In team Drive |

### Algorithm angle

In 2002, SMOTE drew a random point on the segment between a minority point and one of its five nearest minority neighbours, combined with random undersampling. Its future-work list asked for adaptive k, other ways to place points and a focus on misclassified examples.

| Year | Milestone | What it added | Reference | Status |
|---|---|---|---|---|
| 2003 | SMOTEBoost | SMOTE inside each boosting round (stage 5) | Chawla, Lazarevic, Hall, Bowyer, PKDD 2003 | In team Drive |
| 2004 | SMOTE + Tomek links, SMOTE + ENN | Cleaning after generation (stage 4) | Batista, Prati, Monard, SIGKDD Explorations 6(1):20-29 | In team Drive |
| 2005 | Borderline-SMOTE | Seeds restricted to borderline examples (stage 1) | Han, Wang, Mao 2005 | In team Drive |
| 2006 | Cluster-SMOTE | Cluster-wise SMOTE for network intrusion (stages 1 and 2) | Cieslak, Chawla, Striegel 2006 | In team Drive |
| 2008 | ADASYN | Density-adaptive seed weighting (stage 1) | He, Bai, Garcia, Li, IJCNN 2008 | In team Drive |
| 2009 | Safe-Level-SMOTE | Gap biased toward the safer endpoint (stages 2 and 3) | Bunkhumpornpat et al., PAKDD 2009 | In team Drive |
| 2010 | RAMOBoost and RUSBoost | Ranked oversampling inside boosting; the undersampling boosting baseline (stage 5) | Chen, He, Garcia 2010; Seiffert et al. 2010 | In team Drive |
| 2014 | MWMOTE | Majority-weighted informative seeds and cluster-constrained partners (stages 1 and 2) | Barua et al., IEEE TKDE 26(2):405-425 | Partly verified |
| 2015 | SMOTE-IPF and RACOG | Ensemble noise filter after SMOTE (stage 4); Gibbs-sampling generation | Saez et al. 2015; Das, Krishnan, Cook 2015 | In team Drive |
| 2016 | MDO | Mahalanobis-distance generation for multiclass data (stages 3 and 6) | Abdi and Hashemi, IEEE TKDE 2016 | In team Drive |
| 2017 | imbalanced-learn | The standard Python toolbox for SMOTE and its relatives | Lemaitre, Nogueira, Aridas, JMLR 18(17):1-5 | To verify |
| 2018 | k-means SMOTE | Cluster selection and density-based allocation (stages 1 and 2) | Douzas, Bacao, Last 2018 | In team Drive |
| 2019 | Geometric SMOTE and RBO | Shaped generation regions; potential-guided generation for noisy data (stage 3) | Douzas and Bacao 2019; Koziarski, Krawczyk, Wozniak 2019 | In team Drive |
| 2019 | GAMO and CTGAN/TVAE | Learned deep generators enter oversampling | Mullick, Datta, Das, ICCV 2019; Xu et al., NeurIPS 2019 | In team Drive |
| 2019 | smote-variants | 85 oversampling variants implemented in one library | Kovacs, Neurocomputing 366:352-354 (doi:10.1016/j.neucom.2019.06.100) | Verified |
| 2022 | GDO and SOS | Gaussian-distribution generation; score-based diffusion for tabular data | Xie et al., IEEE TKDE 2022; Kim, Lee, Park, KDD 2022 | In team Drive |
| 2023 | OREM and NROMM | Reliable expansion of minority regions; noise-robust generation | IEEE TKDE 2023; Pattern Recognition 2023 | In team Drive |
| 2023-26 | LLM-based tabular synthesis | Language-model row generation used as an oversampler | Not verified in this pass | To verify |
| 2025-26 | GOIO, DGOT and Loyalty-SMOTE | Overlap-aware latent diffusion, diffusion-GAN generation, loyalty-weighted SMOTE | IEEE TKDE 2025 and 2026; Neural Networks 2026 | In team Drive |

### Evaluation angle

In 2002, SMOTE was judged by ROC curves, AUC and the ROC convex hull over 10-fold cross-validation with three learners, without significance tests, calibration or precision-recall summaries.

| Year | Milestone | What it added | Reference | Status |
|---|---|---|---|---|
| 2006 | Demsar | Friedman, Nemenyi and Wilcoxon tests for comparisons over many datasets | JMLR 7:1-30 | To verify |
| 2006 | Davis and Goadrich | How ROC and precision-recall curves relate | ICML 2006 | To verify |
| 2008 | Garcia and Herrera | Post-hoc procedures for all pairwise comparisons | JMLR 9:2677-2694 | To verify |
| 2009 | He and Garcia | The first major survey of imbalanced learning | IEEE TKDE 21(9):1263-1284 | Verified |
| 2010 | Garcia et al. | Advanced non-parametric tests for computational intelligence | Information Sciences 180(10):2044-2064 | To verify |
| 2009, 2011 | KEEL dataset repository | Shared imbalanced benchmark partitions (software from 2009) | Alcala-Fdez et al., J. Multiple-Valued Logic and Soft Computing 17:255-287 | Partly verified |
| 2015 | Saito and Rehmsmeier | Precision-recall plots are more informative than ROC on imbalanced data | PLOS ONE 10(3):e0118432 | To verify |
| 2016 | Krawczyk | Open challenges and future directions | Progress in Artificial Intelligence 5(4):221-232 | Verified |
| 2018 | Fernandez et al. | The 15-year SMOTE review in JAIR | JAIR 61:863-905 | Verified |
| 2018 | Santos et al. | Oversampling before cross-validation creates over-optimism | IEEE Computational Intelligence Magazine 13(4):59-76 (doi:10.1109/MCI.2018.2866730) | Verified |
| 2019 | Kovacs | 85 oversamplers compared on 104 datasets with four classifiers | Applied Soft Computing 83:105662 (doi:10.1016/j.asoc.2019.105662) | Verified |
| 2019 | Song, Guo, Shepperd | Large study of imbalanced learning for defect prediction | IEEE TSE 45(12):1253-1269 (doi:10.1109/TSE.2018.2836442) | Verified |
| 2020 | Chicco and Jurman | MCC preferred over F1 and accuracy for binary evaluation | BMC Genomics 21:6 | To verify |
| 2020 | Tantithamthavorn et al. | Rebalancing effects depend on measure and classifier, and change model interpretation | IEEE TSE 46(11):1200-1219 (doi:10.1109/TSE.2018.2876537) | Verified |
| 2021 | Vandewiele et al. | Oversampling before splitting inflated preterm-birth results | Artificial Intelligence in Medicine 111:101987 (doi:10.1016/j.artmed.2020.101987) | Verified |
| 2022 | Elor and Averbuch-Elor | Balancing helps weak learners but not strong gradient boosting with tuned thresholds | arXiv 2201.08528 (https://arxiv.org/abs/2201.08528) | Preprint |
| 2022 | van den Goorbergh et al. | Rebalancing miscalibrates clinical risk models without improving AUC | JAMIA 29(9):1525-1534 (doi:10.1093/jamia/ocac093) | Verified |
| 2022 | Hassanat et al. | Synthetic points often fall in majority regions | arXiv 2202.03579 (in team Drive) (https://arxiv.org/abs/2202.03579) | Preprint |
| 2023 | Hassanat et al. | On medical data, many synthetic samples fall outside the minority class | IEEE ISCC 2023 (doi:10.1109/ISCC58397.2023.10218211) | Verified |
| 2024 | Piccininni et al. | Calibration and discrimination after random resampling | J. Biomedical Informatics 155:104666 (doi:10.1016/j.jbi.2024.104666) | Verified |
| 2024 | Elreedy, Atiya, Kamalov | Theoretical distribution of SMOTE samples | Machine Learning 113:4903-4923 (doi:10.1007/s10994-022-06296-4) | Partly verified |
| 2025 | Carriero et al. | Imbalance corrections overestimate risk for machine-learning models too | Statistics in Medicine (doi:10.1002/sim.10320) | Verified |
| 2025 | Abdelhay et al. | Registered scoping review of resampling in clinical prediction models (protocol) | PLOS ONE (doi:10.1371/journal.pone.0330050) | Verified |
| 2025-26 | CISO (arXiv 2501.15790) | Per-instance safety guarantees, 11,460 fold-level evaluations; the paper calls its protocol preregistered, but no registry entry was located | arXiv 2501.15790, version 2 (https://arxiv.org/abs/2501.15790) | Preprint |

## Part 3. Real-world applications

### Reach

32,390 citations (OpenAlex work W2148143831 (doi:10.1613/jair.953), retrieved 8 October 2026); field-weighted citation impact 51.26; top 1% (99.87th percentile).

| Year | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Citations | 295 | 368 | 444 | 529 | 601 | 808 | 1,246 | 1,799 | 2,535 | 3,361 | 3,549 | 3,960 | 4,184 | 4,693 | 3,074 |

2026 runs to early September. The field breakdown query (group by primary topic field) returned HTTP 429 and must be re-run.

### Evidence ladder

| Level | Meaning | Found in this pass |
|---|---|---|
| a (Retrospective) | Benchmark or retrospective analysis of real data | Almost every applied study collected |
| b (External validation) | External or temporal validation | A few clinical models, such as a sepsis model validated on MIMIC-III and eICU |
| c (Prospective) | Prospective study in a live setting | One: Mayo Clinic emergency department surge forecasting (2026) |
| d (Deployed with impact) | Deployment with a measured effect on real decisions | None verified |

### Domain map

| Domain | Problem and imbalance | SMOTE variants | Representative studies | Evidence | Reported benefit | Caveats |
|---|---|---|---|---|---|---|
| Healthcare and public health | Diagnosis, mortality, sepsis and preterm-birth prediction; the minority is often under 30% | SMOTE, SMOTE-ENN, random oversampling | van den Goorbergh et al. 2022, JAMIA (ovarian cancer case study) (doi:10.1093/jamia/ocac093); Vandewiele et al. 2021, Artificial Intelligence in Medicine (preterm birth) (doi:10.1016/j.artmed.2020.101987); Early sepsis model, external validation on MIMIC-III and eICU (PMC11345914; journal and authors to confirm) (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC11345914/); Jones et al. 2026, Mayo Clinic Proceedings: Digital Health 4(2):100365 (emergency department surge forecasting) (doi:10.1016/j.mcpdig.2026.100365) | a, b, c | The sepsis model kept AUC 0.86 on MIMIC-III and 0.82 on eICU. The Mayo system ran prospective hourly forecasts for about 2,400 hours (May to August 2025) with AUC 0.87 to 0.91. | Rebalanced logistic models gained no AUC but overestimated minority risk (JAMIA 2022). Leakage inflated more than 20 preterm-birth studies. In the Mayo study, class weighting performed comparably to SMOTE. |
| Finance | Card fraud (public ULB data: 492 frauds, about 0.17%) and credit default | SMOTE, k-means SMOTE, filtered SMOTE | Information 2024, 15(8):478 (doi:10.3390/info15080478); Frontiers in Artificial Intelligence 2026 (ULB and IEEE-CIS data) (doi:10.3389/frai.2026.1871972); Brown and Mues 2012, Expert Systems with Applications (imbalanced credit benchmark, no SMOTE) (doi:10.1016/j.eswa.2011.09.033) | a | In Information 2024, undersampling reached recall 92.86% with low precision, while SMOTE gave the better F1 (73.47%). | Public benchmark data dominate. A 2025 SMOTE fraud paper in Scientific Reports was retracted in December 2025. Random forests and gradient boosting held up without synthetic data in Brown and Mues. |
| Cybersecurity | Rare attack classes in NSL-KDD, UNSW-NB15 and CICIDS2017 | SMOTE with Gaussian-mixture undersampling; Cluster-SMOTE (2006, in the corpus) | Zhang, Huang, Wu, Li 2020, Computer Networks 177:107315 (doi:10.1016/j.comnet.2020.107315) | a | Detection rates of 99.74% (binary) and 96.54% (multiclass) on UNSW-NB15, and 99.85% on CICIDS2017. | These benchmarks carry known artefacts; no evaluation inside a security operations centre was found. |
| Software engineering | Defect-prone modules; fairness of machine-learning software | SMOTE, random over- and undersampling, Fair-SMOTE | Tantithamthavorn, Hassan, Matsumoto 2020, IEEE TSE (doi:10.1109/TSE.2018.2876537); Song, Guo, Shepperd 2019, IEEE TSE (doi:10.1109/TSE.2018.2836442); Chakraborty, Majumder, Menzies 2021, ESEC/FSE (doi:10.1145/3468264.3468537) | a | Gains depend on the measure and the classifier; Fair-SMOTE lowered bias metrics while keeping recall and F1. | Rebalancing also changes which features a defect model ranks as important. |
| Manufacturing and industry | Bearing fault diagnosis with few fault samples | BE-G-SMOTE, SMOTENC | Wang, Liu, Wu, Liu 2023, J. Computational Design and Engineering 10(5):1930-1940 (doi:10.1093/jcde/qwad081); Jin et al. 2024, Measurement Science and Technology 35(1):015121 (doi:10.1088/1361-6501/ad016a) | a | Better diagnosis on 12 cross-device bearing tasks (figures not captured). | Laboratory test rigs rather than plant deployments. |
| Energy and utilities | Electricity theft (SGCC data: 42,372 consumers, 2014 to 2016) | SMOTE, k-means SMOTE, SMOTE-Tomek, SMOTE-ENN | Scientific Reports 2025 (doi:10.1038/s41598-025-93140-z); Review of electricity-theft case studies (venue to confirm) (https://www.sciencedirect.com/science/article/pii/S2590174525000972) | a | Accuracy up to 94.7% on SGCC. | Theft cases are often synthesised from benign profiles; wind-turbine and grid-fault studies not yet verified. |
| Environment and geoscience | Landslide susceptibility (one study: 16 landslide vs 1,309 stable slope units, about 82:1) | SMOTE, SMOTE-Tomek, SMOTE-ENN | PLOS ONE 2025 (Taiping Township) (doi:10.1371/journal.pone.0323487); Lishui City landslide mapping with SMOTE (authors to confirm) (https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6388203/); Kubat, Holte, Matwin 1998, oil-spill detection (SHRINK; in the corpus) | a | Higher ROC with SMOTE-Tomek; susceptibility maps produced. | Spatial autocorrelation can leak between neighbouring units; flood, wildfire and air-quality studies not verified. |
| Transportation and safety | Crash injury severity (fatal class 2.5% in one dataset) | SMOTE, Borderline-SMOTE, ADASYN, SMOTE-ENN | Scientific Reports 2025 (doi:10.1038/s41598-025-10970-7); Electronics 2025, 14(17):3377 (doi:10.3390/electronics14173377) | a | SMOTE and Borderline-SMOTE worked best with Extra Trees in the Scientific Reports study. | Crash records are under-reported and mislabelled. |
| Education | Student dropout and at-risk prediction | SMOTE, SMOTE-NC with undersampling | Flores, Heras, Julian 2022, Electronics 11(3):457 (DOI to confirm); Korean national dropout study (165,715 students), reported in arXiv 2412.09483 (https://arxiv.org/abs/2412.09483); Information 2023, 14(1):54 (comparison of sampling methods) (https://www.mdpi.com/2078-2489/14/1/54) | a | Korean study: ROC-AUC barely moved (0.988 vs 0.991) while PR-AUC fell from 0.898 to 0.724 with SMOTE. | ROC-AUC hides minority losses; early-warning flags raise fairness questions. |
| Bioinformatics and life sciences | Drug-target interaction, bioactivity, microarrays | SMOTE | Blagus and Lusa 2013, BMC Bioinformatics 14:106 (doi:10.1186/1471-2105-14-106); Mahmud et al. 2019, IEEE Access (iDTi-CSsmoteB) (doi:10.1109/ACCESS.2019.2910277); The E-state drug screen in the original 2002 paper | a | Drug-target prediction gains reported (figures not captured). | In high dimensions SMOTE is mostly ineffective unless variable selection comes first. |
| Remote sensing and agriculture | Minority land-cover classes; crop disease images | Geometric SMOTE, SMOTE with class weights | Douzas, Bacao, Fonseca, Khudinyan 2019, Remote Sensing 11(24):3040 (doi:10.3390/rs11243040); Wheat rust detection with imbalanced data (https://pmc.ncbi.nlm.nih.gov/articles/PMC11130404) | a | Geometric SMOTE outperformed other oversamplers on LUCAS land cover. | Spatial leakage; synthetic pixels may be physically implausible. |
| Business and society | Fairness in hiring, credit and justice benchmarks | Fair-SMOTE, Continuous Fair SMOTE | Chakraborty, Majumder, Menzies 2021, ESEC/FSE (doi:10.1145/3468264.3468537); Continuous Fair SMOTE 2025 (doi:10.1007/978-3-032-04558-4_27) | a | Bias metrics reduced on benchmark datasets. | Churn, social-media and public-service studies not verified yet. |

### Documented versus claimed benefit

- Reach is documented. The 2002 paper has 32,390 citations in OpenAlex, with about sixteen times more citations in 2025 than in 2012, and applied work spans at least twelve domains.
- Benefit is mostly claimed. Nearly all applied studies are retrospective, many report accuracy on rebalanced test sets, and one prominent 2025 fraud paper was retracted.
- The best evidence is a sepsis model that held AUC 0.82 to 0.86 on two external ICU databases (level b), and one prospective emergency department system at Mayo Clinic that ran a SMOTE-trained XGBoost model live for about 2,400 hours (level c). Its own sensitivity analysis found class weighting comparable, so it shows a SMOTE-trained model can be operated, not that SMOTE caused the benefit.
- No peer-reviewed report of a SMOTE-trained model in production with a measured effect on decisions was found (level d). The defensible claim: SMOTE lowered the barrier to modelling rare outcomes in socially important domains, and the bottleneck for benefit is now validation, calibration and deployment science rather than new variants.

### Risks in applied settings

- **Miscalibrated risk.** Random over- or undersampling and SMOTE gave clinical logistic models no better AUC but systematically overestimated minority-class risk; the same pattern appears for SVM, XGBoost and random forests. Recalibrate, or move the decision threshold instead. Sources: van den Goorbergh et al. 2022 (doi:10.1093/jamia/ocac093); Carriero et al. 2025 (doi:10.1002/sim.10320); Piccininni et al. 2024 (doi:10.1016/j.jbi.2024.104666).
- **Leakage.** Oversampling before splitting creates over-optimism. Near-perfect preterm-birth results collapsed once the split came first; more than 20 studies were affected (21 or 24 depending on the source). Sources: Santos et al. 2018 (doi:10.1109/MCI.2018.2866730); Vandewiele et al. 2021 (doi:10.1016/j.artmed.2020.101987).
- **Unrealistic samples.** Synthetic points can land in majority regions, distort high-dimensional data, or interpolate between encoded categories. The 2002 Adult and Can results already showed this. Sources: Blagus and Lusa 2013 (doi:10.1186/1471-2105-14-106); Hassanat et al. 2023 (doi:10.1109/ISCC58397.2023.10218211).
- **Strong learners.** With gradient boosting and tuned thresholds, balancing often adds nothing; one preprint finds gains in some tuned-F1 settings. On Korean dropout data SMOTE lowered PR-AUC for boosted trees. Sources: Elor and Averbuch-Elor 2022 (preprint) (https://arxiv.org/abs/2201.08528); Brown and Mues 2012 (doi:10.1016/j.eswa.2011.09.033); Sakho et al. 2024 (preprint) (https://arxiv.org/abs/2402.03819).
- **Interpretation drift.** Rebalancing changes which features a model treats as important, which matters wherever models are used to explain causes. Sources: Tantithamthavorn et al. 2020 (doi:10.1109/TSE.2018.2876537).
- **Fairness.** Class imbalance interacts with protected subgroups; plain SMOTE gives no subgroup guarantee, which is why fairness-aware variants appeared. Sources: Fair-SMOTE 2021 (doi:10.1145/3468264.3468537); Continuous Fair SMOTE 2025 (doi:10.1007/978-3-032-04558-4_27).
- **Privacy.** Each SMOTE point is a convex combination of two real records and sits close to them, so SMOTE output should be treated as personal data. This is a reasoning point; no peer-reviewed analysis was verified.
- **Research integrity.** A 2025 SMOTE fraud-detection paper in Scientific Reports, reporting 99.5% accuracy, was retracted in December 2025 after concerns about its data and references. Sources: Retraction note (doi:10.1038/s41598-025-33135-y).

## Proposed outline

- **Part 1. Origin (2002): SMOTE on all three angles**
  - 1.1 Data: binary, continuous features, imbalance from 1.9:1 to 52:1 over 9 datasets; replication overfitting as the framed problem.
  - 1.2 Algorithm: k = 5 interpolation, N% amounts, below-100% subsampling, undersampling combination, SMOTE-NC and SMOTE-N.
  - 1.3 Evaluation: ROC sweeps, AUC and the convex hull; 4 exceptions in 48 experiments; small margins and no significance tests.
  - 1.4 The paper's own future-work list as the roadmap for Part 2.
- **Part 2. What has been added, per angle**
  - 2.1 Data: borderline and noise (2005 to 2010), intrinsic characteristics and typology (2013 to 2016), multiclass (2012 to 2020), new tasks and fairness (2013 to 2025).
  - 2.2 Algorithm: milestones mapped to pipeline stages and operator families; software milestones (2017, 2019).
  - 2.3 Evaluation: statistical tests and KEEL (2006 to 2011), metrics (PR, MCC), then protocols and critiques (2018 to 2026).
- **Part 3. Real-world applications and societal benefit**
  - 3.1 Reach: citations and their growth.
  - 3.2 Domain map with an evidence level for every study.
  - 3.3 The evidence ladder: almost all a, some b, one c, no verified d.
  - 3.4 Risks in applied settings.
  - 3.5 Agenda: a reporting checklist and the case for deployment studies.

## Key messages

1. SMOTE succeeded because it was simple, model-agnostic and geometrically intuitive, not because its original margins were large.
2. Twenty-five years of additions mostly answer questions the 2002 paper raised itself: where to generate, how to avoid overlap, how to handle nominal and multiclass data.
3. Evaluation matured from ROC dominance to statistical tests to leakage-safe, calibration-aware comparisons against strong baselines; much applied work has not caught up.
4. Societal reach is large; documented societal benefit is rare. The next contribution is validation and deployment evidence, not variant number 100.

## Reporting checklist (proposed for the paper)

- [ ] Split the data before any resampling; resample inside training folds only.
- [ ] Report PR-AUC and a calibration measure alongside ROC-AUC.
- [ ] Compare against class weighting and threshold tuning with a strong learner such as gradient boosting.
- [ ] State the evidence level (a to d) of every application claim.

## Open items

- Domains not yet covered: wind turbines, aviation, flood, wildfire, air quality, insurance fraud, bankruptcy, phishing, spam, malware, effort estimation, miRNA, churn, social media.
- The OpenAlex field breakdown of citing works failed (HTTP 429); re-run it, grouped by field and by domain.
- About 20 references from the research pass are not yet verified (marked To verify on this page).
- The Drive corpus holds no application papers beyond SHRINK, Cluster-SMOTE, A-SUWO and GDO; create an Applications subfolder for Part 3.
- Conflicts to resolve: preterm-birth studies affected (21 or 24); arXiv 2501.15790 changed title and content between versions; the AUC table above was parsed from a PDF with layout noise.

## Method

- Corpus: the four SMOTE25 Drive folders as listed on 6 October 2026 (100 files, 73 primary works, 2 surveys).
- Research pass on 8 October 2026: publisher pages, PubMed/PMC, arXiv, Crossref and OpenAlex, plus the team Drive. Each reference carries a status label.
- Codes and evidence markers for the 73 corpus works are in `SMOTE25_evidence_map_v1.csv`; they are a first pass and must be checked against the full texts.
