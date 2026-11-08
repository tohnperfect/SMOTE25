# SMOTE25 Section 7 (Evaluation) handoff, 9 Nov 2026

Owner: Tan. HTML version: https://claude.ai/artifact/Uy2vnrnnFVHkpD2WuG5qSM (also in this folder: section07-handoff.html).

## Where things stand
- Latest draft: **v4.1** (8 Nov 2026). 14 subsections (7.1 to 7.14) plus Appendix A, 31 tables, 8 figures, 49-page preview PDF.
- v4.1 follows the Paper Picker picks: 226 docs (use 183, maybe 14, no 28; 7 notes, 2 edited texts).
- In the repo as a package: `Evaluation section/` now holds v4.1 (replacing v3; v3 is in Git history), the Paper Picker and this handoff. Not yet merged into main.tex.
- v4 is untouched but superseded (it has the threshold-moving error, fixed only in v4.1, and an unrequested 15-year-review paragraph).
- Thai for v4.1 exists only as a change log (second tab of the v4.1 page); v4 has a full Thai translation (v4/th/section07-th.md).

## Next actions (in order)
1. [Decide] Read v4.1 and accept it as the main draft. Read first: 7.3 (data and tasks), 7.4 (learner reasons), 7.11 (raw citations).
2. [Decide] Keep our illustrative runs? Now only the SMOTE-vs-None figure and the example results table remain in the text; details in Appendix A. If kept: rerun CV at least 5 times, add class-weighting and ROS baselines. If not: find another example table for 7.10.
3. [Decide] Full Thai translation of v4.1?
4. [Decide] Roadmap of 46 practices in the appendix? (picked "maybe", not included)
5. [Team] Agree the 7.3 boundary with Data (Toon / Kanvara001). Data numbers are ai_draft: do not cite them in the manuscript.
6. [Team] Labels for the Data and Method sections: \TODO refs in 7.3 and 7.14.
7. [Team] Co-author check of pass-2 quotes (\TODO in 7.1). Evidence: v3/section07-pass2-verification.xlsx. Spot check of 20 codes: 14 confirmed, 6 partly.
8. [Task] Merge v4.1 into the paper (main.tex on Overleaf). The package is in the repo at `Evaluation section/latex/`: copy sections/07-empirical-comparisons.tex, sections/07-empirical-appendix.tex (after \appendix), tables/, figures/ to the root; add \usepackage{array} and longtable to main.tex; verify notes/empirical-bib-candidates.bib and add to references.bib. Commit as Tan; Tan pushes from cmd.

## Pages (claude.ai artifacts, private until shared)
- v4.1 (latest): https://claude.ai/artifact/7HRYkw26k872LpYehEBNDa
- Paper Picker (picks in artifact db collection `picks`, 237 items): https://claude.ai/artifact/LvyVNKUoinsS2jFB3jZRb4
- Evaluation Data Book (D0 to D16, 61-question index): https://claude.ai/artifact/QD9SpbnXyZQd27crxxp2ws
- v4 (superseded): https://claude.ai/artifact/LmHmzdeTyvy6qzqnjTqffW
- Evaluation, Tan (8 questions + cause cards): https://claude.ai/artifact/DJKDt4ZU6yWUXaUYHzYy2t
- Evaluation Guide: https://claude.ai/artifact/ToYftCPiDTd36U2cZPPXcB
- Older (Oct 2026): Primer https://claude.ai/artifact/CK5PH6nLSqWshQw93NDB2m, Roadmap https://claude.ai/artifact/Y4cW1RFS9YnkRYi9jbkibb, Evaluation Section v2/v3 https://claude.ai/artifact/QrYUWJ3jFHen8qTsFyYUfx

## Files on Tan's computer (D:\WORKSPACE\claude-workspace\SMOTE\section07-empirical\)
- v4.1\: PDF, HTML, LaTeX zip, build-source zip, section07-v4.1-changes-th.md
- v4\: v4 draft files, 15-year review PDF, exported picks (smote25-section7-picks.json/.md)
- databook\: data book and picker HTML, build_databook.py, build_picker.py
- v3\: v3 draft, coded data, Tan page, guide, primer, roadmap, section07-pass2-verification.xlsx
- handoff\: this file, section07-handoff.html, smote25-section7-workspace-2026-11-09.zip (all code and data)
- Repo: SMOTE\Git\SMOTE25. Its `Evaluation section/` has the same set: v4.1 (HTML at the repo root, PDF, LaTeX), Paper Picker and `handoff/`. Raw experiment results: SMOTE\experiment\

## Decisions made
- 14-subsection structure from the picker target list; "Why G-mean" and "G-mean vs F1" are subsections of 7.6.
- Illustrative runs: dropped CD diagram, G-mean/F1 threshold figure, IR example, G-mean/F1 winner agreement, Spearman, rank and Holm tables. Kept SMOTE vs None (427/550) and the example results table.
- 15-year review kept in 7.1 with a table of whether later work followed it.
- Citations: raw medians with median year per group, no regression ratios; association only.
- UCI/KEEL counted without overlap: UCI only 33, KEEL only 13, both 20, neither 5.
- Learner sentence: "median 3 families per study (range 1 to 6), with 9 of 24 studies using a single family", with the 12-family table.
- Threshold moving is a baseline in 3 studies (Global-CS 2010, DSRBF 2011, Buda 2018), not 1.

## Key numbers (data.json, 71 empirical studies; periods up to 2009 (14), 2010-15 (13), 2016-20 (20), 2021-26 (24))
- Corpus: 76 papers, 71 empirical, 37 SMOTE family (Binary 24, Multiclass 5, both 8); binary 39, multi-class 19, both 13.
- Data: UCI 53, KEEL 33 (from 2013); median datasets 6.5 before 2010 to 23 since 2021; 52 modify data, 10 release the modified versions.
- Learners 2021-26: 12 families (32 names); median 3 per study (1 to 6); single family 9/24; SVM 13, CART 12, k-NN 9.
- Competitors: median 7; SMOTE 50; no-resampling 52 (86% to 54%); cost-sensitive 5; class weighting 1; threshold moving 3.
- Measures: 27 (5 families + 1); median 3 per study; G-mean 41 (29% to 71%); declared primary AUC 16, G-mean 7; definition issue 14.
- Beyond scores: direct checks 6; 2-D plots 33; scores only 23.
- Protocol: repeated partitions 43; resample-on-training stated 34; tuning on evaluation data 35; nested 9; fixed 20; unclear 7.
- Tests: 52 use one; corrected multiple comparisons 27; uncorrected pairwise only 19; Bayesian 3; no test 64% to 17%; Demsar cited 19.
- Reporting: per-dataset tables 58; SD 24; CD diagram 4; code 27.
- Citations: median 1,738 (up to 2009) vs 21 (since 2021). Same direction in every period only for 3 practices: SMOTE as competitor (more), metric-definition issue and no-resampling baseline (fewer).
- Conclusions: 68 of 69 proposers report their method best; CISO 2025 the only one with no advantage over simple baselines; 7-point standard: only RBO meets all 7, median 3.
- Illustrative runs: 110 KEEL x 5 samplers x 5 learners, one 5-fold run; SMOTE beats None 427/550 by G-mean, 175/550 by PR-AUC.

## How to rebuild
1. Unzip handoff\smote25-section7-workspace-2026-11-09.zip to /home/claude/ in a Claude cloud session (scripts use absolute paths /home/claude/smote25).
2. Coded data: data.json (76), v2/analysis.json.
3. Tan page: evalpage/facts.py, why_facts.py, exp.py (SMOTE/experiment/results_*.csv), build_evalpage.py.
4. Data book and picker: databook/build_databook.py, build_picker.py (item ids stable if text unchanged).
5. v4.1: make_figures.py, make_tables_v41.py, concatenate sections/parts/p1-p4.tex into 07-empirical-comparisons.tex, compile preview (TEXINPUTS=..: pdflatex; bibtex; pdflatex x2), make_page.py.
6. Picker selections: ArtifactData list on the Paper Picker, collection `picks`.

## Standing rules
- No em-dashes in deliverables. Do not cite Data ai_draft numbers. Every number from coded data, rechecked.
- Ask before changing delivered work; add nothing unrequested; explain only when asked.
- Commit only when asked, as Tan <pharamut@kkumail.com> with Co-Authored-By and Claude-Session lines. Claude never handles GitHub credentials; Tan pushes: `cd /d D:\WORKSPACE\claude-workspace\SMOTE\Git\SMOTE25` then `git push`.
- No destructive git commands; deleting in device folders needs permission.

## Team
- Method: P / S1xzy (37 SMOTE-family list).
- Data: Toon / Kanvara001 (per-dataset detail; numbers ai_draft).
- Evaluation (Section 7): Tan.
