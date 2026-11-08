"""Why did the authors modify their data?  Quotes from the PDFs, checked automatically  (9 Nov 2026, Claude; Toon:
"in these papers, what did they modify the data for — to make it harder, to fit their method, ... how can we tell").

Unit: paper. Papers covered = the 39 papers with at least one entry of category 'modified' (out/modified_operations_audit.csv)
plus papers that inject noise into real data sets as an experimental condition without listing the noisy sets as entries
(found by a search of every PDF for noise-injection wording on 9 Nov; RBO, MC-CCR, MC-MBRC, MC-NCLWO).

Every row below is a sentence (or the part of it that carries the reason) copied from the paper. The script stops if a quote is
not found in the PDF text (pdftotext; NFKC, ligatures, whitespace and case normalised). Themes are named after what the
sentences say, not after a scheme of ours:
  two-class scope        the study or the method is about two-class problems, so multiclass data were made two-class
  create/raise imbalance the data were not imbalanced enough, so the authors made them (more) imbalanced
  robustness test        noise, outliers or missing values were added to see how the methods cope
  practical              data size, or making the training and test files agree
  basis: earlier work    the particular choice (which class is the minority, which noise scheme) is taken from earlier work
  basis: stated rule     the choice follows a rule written in the paper (e.g. smallest class vs rest)
  publishes modified data the modified files are made available by the authors
A paper with no row for a theme is "not stated" for it. "Not stated" means no sentence was found, not that there was no reason.

Runs on Toon's machine (needs paper/). Run from Data section/:  python3 build/modification_purpose.py
Writes out/modification_purpose_quotes.csv (one row per quote, with the PDF page where it was found).
"""
import csv, json, os, re, subprocess, sys, unicodedata
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)

SC, IMB, ROB, PR, BP, BR, PUB = ("two-class scope", "create/raise imbalance", "robustness test", "practical",
                                 "basis: earlier work", "basis: stated rule", "publishes modified data")
Q = [
 ("ADASYN", SC, "since our interest here is to test the learning capabilities from two-class imbalanced problems"),
 ("ADASYN", BP, "according to various literary results from similar experiments"),
 ("ADASYN", BP, "as suggested in [17]"),
 ("Borderline-SMOTE", SC, "as we only study two-class problem in this paper"),
 ("Safe-Level-SMOTE", SC, "because we only study the two-class imbalanced problem"),
 ("MWMOTE", SC, "We transform them to two-class problems because of our interest"),
 ("RAMOBoost", SC, "we also consider only two-class imbalanced problems in our current study"),
 ("RAMOBoost", BP, "we modified those datasets following suggestions in literature to make them into two-class datasets"),
 ("RAMOBoost", ROB, "In order to systematically investigate the robustness of RAMOBoost, we manually introduce class label noise and attribute noise"),
 ("RUSBoost", SC, "Since this paper considers only the binary classification problem, it was necessary to transform some of the data sets to have a binary class"),
 ("SMOTE", SC, "Since our system currently works for binary classes we extracted data for two classes from this dataset and ignored the rest"),
 ("SMOTE-IPF", SC, "Multi-class datasets are modiﬁed to obtain two-class imbalanced problems"),
 ("SMOTE-IPF", ROB, "to introduce additional class or attribute noise into these real-world datasets and to study its impact on compared SMOTE generalizations"),
 ("SMOTE-IPF", BP, "The same two noise introduction schemes proposed by the authors of that paper are used in this work"),
 ("Cluster-SMOTE", SC, "We can accommodate this limitation by focusing our approach and treating this as a 2-class problem"),
 ("NBU", IMB, "were undersampled to obtained higher class imbalance degrees"),
 ("NBU", SC, "the undersampling criteria for binary-class problems"),
 ("G-SMOTE", IMB, "In order to test the performance of the algorithm on more extreme cases of imbalance"),
 ("HDE", IMB, "To evaluate the proposed HD-Ensemble for extreme case, we manually created 14 highly imbalanced datasets"),
 ("HDE", PUB, "All the 42 datasets adopted in our experiments have been uploaded to GitHub"),
 ("k-means SMOTE", IMB, "In order to generate additional datasets with even higher imbalance ratios"),
 ("k-means SMOTE", PUB, "All modified and simulated datasets used in the study are made available"),
 ("RSMOTE", IMB, "artificially imbalanced to obtain higher imbalanced ratios"),
 ("RSMOTE", ROB, "To verify the effectiveness of our method for imbalanced learning with label noise"),
 ("ROS (Buda)", IMB, "to make them artificially imbalanced"),
 ("SVDD-WSMOTE", IMB, "to simulate the scenarios with higher imbalance ratios"),
 ("SVDD-WSMOTE", BR, "where the class with relatively a few numbers of instances are regarded as the minority class"),
 ("GAMO", IMB, "are not significantly imbalanced in nature, therefore we have created their imbalanced variants"),
 ("COG-OS", IMB, "we prepared the imbalanced data sets with rare classes via sampling on various binary data sets"),
 ("COG-OS", PR, "So for the evaluation concern we deleted these new subclasses"),
 ("SMOTEBoost", PR, "in order to reduce the size of the data set"),
 ("SMOTEBoost", PR, "we modified the data sets in order to have similar distributions in the training and test data"),
 ("SMOTEBoost", BP, "as was done in [24]"),
 ("CISO", BR, "binarized by the smallestclass-versus-rest rule"),
 ("GMMSampling", BP, "The classification of classes into majority and minority categories was taken from the previous paper on SOUP"),
 ("DSRBF / Static-SMOTE", PUB, "All the datasets and the corresponding partitions have been included in a public website"),
 ("SPE", ROB, "To simulate the situation of missing values"),
 ("RBO", ROB, "we measured the inﬂuence of the label noise on the classiﬁcation performance"),
 ("MC-CCR", ROB, "we evaluated how the presence of the label noise affects the predictive performance of MC-CCR"),
 ("MC-MBRC", ROB, "How does label noise affect the performance of MC-MBRC?"),
 ("MC-NCLWO", ROB, "To assess the robustness of the MC-NCLWO method in feature noise environments"),
]
# Noise injected into real data as an experimental condition (9 Nov search of all PDFs). 'entries' says whether the noisy sets
# are dataset entries of the corpus; where they are not, the base sets stay in their own category.
NOISE = [
 ("SMOTE-IPF", "class noise + attribute noise", "20%, 40%", "9 real-world sets (acl + 8 KEEL)", "yes (2 modified entries)", "Sec 4.2"),
 ("RAMOBoost", "class label noise + attribute noise", "several levels (Tables XVIII, XXI)", "Abalone", "no", "Sec IV, p.16-17"),
 ("RSMOTE", "label noise (minority labels flipped)", "10%, 20%, 30%", "all binary sets", "no", "p.12"),
 ("RSMOTE", "one outlier added", "one point", "fourclass", "yes (1 modified entry)", "Sec 4.3.1, p.10"),
 ("RBO", "label noise; feature noise", "0-20% (label)", "the benchmark sets (Experiments 3-4)", "no", "p.8"),
 ("MC-CCR", "random label noise", "0-25% in steps of 5%", "the multiclass benchmark sets", "no", "Sec 4.4, p.9"),
 ("MC-MBRC", "label noise (labels randomly replaced)", "0-30% in steps of 5%", "real data sets (Fig. 6)", "no", "Sec 5.3, p.10-11"),
 ("MC-NCLWO", "Gaussian feature noise", "5-30% in steps of 5%", "four data sets", "no", "p.15"),
 ("SPE", "missing values (values replaced by 0)", "several levels", "the benchmark sets", "no", "p.10"),
]
P2PDF = {"CTGAN / TVAE": "CTGAN", "DSRBF / Static-SMOTE": "DSRBF", "EasyEnsemble / BalanceCascade": "EasyEnsemble", "RACOG / wRACOG": "RACOG",
         "ROS (Buda)": "ROS-Buda", "SMOTE-ENN / SMOTE-Tomek": "SMOTE-ENN", "k-means SMOTE": "k-means-SMOTE"}
PM = json.load(open("out/pdf_map.json", encoding="utf-8"))
def nz(s):
    s = unicodedata.normalize("NFKC", s).replace("­", "")
    return re.sub(r"\s+", " ", s).lower()
CACHE = {}
def pages(k):
    if k not in CACHE:
        pk = P2PDF.get(k, k)
        if pk not in PM: sys.exit(f"STOP: no PDF for {k}")
        fl = ([PM[pk]["main"]] if PM[pk].get("main") else []) + list(PM[pk].get("supp", []))
        out = []
        for i, f in enumerate(fl):
            for j, t in enumerate(subprocess.run(["pdftotext", f, "-"], capture_output=True, text=True).stdout.split("\f"), 1):
                out.append(((("supp " if i else "") + f"p.{j}"), nz(t)))
        CACHE[k] = out
    return CACHE[k]
rows = []
for k, theme, q in Q:
    hit = [p for p, t in pages(k) if nz(q) in t]
    if not hit: sys.exit(f"STOP: quote for {k} not found in PDF: {q}")
    rows.append(dict(paper_key=k, theme=theme, quote=q, pdf_page=";".join(hit)))
with open("out/modification_purpose_quotes.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with open("out/noise_injection_papers.csv", "w", newline="", encoding="utf-8") as fh:
    w = csv.writer(fh); w.writerow(["paper_key", "what_was_added", "levels", "data_sets", "noisy_sets_are_entries", "where_in_paper"]); w.writerows(NOISE)
print(len(rows), "quotes found in the PDFs;", len({r["paper_key"] for r in rows}), "papers")
