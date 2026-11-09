# Evaluation section (Section 7: Empirical Comparisons and Benchmarks)

Latest version (v4.1, 8 Nov 2026) of the Section 7 draft and the material behind it.
Older versions (v3, 29 Oct 2026) are in the Git history only.

| File | What it is |
|------|------------|
| `../SMOTE25_Evaluation_Section.html` | Section 7 draft v4.1 (repository root). English text with Appendix A; the second tab lists what changed from v4 (Thai). Open in a browser. |
| `SMOTE25_Evaluation_Section.pdf` | The same draft compiled outside the JAIR class (49 pages, with the appendix and references). |
| `section07-v4.1-changes-th.md` | What changed from v4 and how each Paper Picker note was handled (Thai). |
| `SMOTE25_Paper_Picker.html` | Every analysis of the evaluation data book split into 237 items to mark use / maybe / no, assign to a subsection, edit and annotate. v4.1 follows the picks made on the claude.ai version of this page. Opened as a file it starts empty and keeps choices in that browser only; export them as JSON or Markdown from the page. |
| `handoff/` | Handoff for whoever continues: `section07-handoff.html` (Thai, open in a browser), the same content as Markdown, and `smote25-section7-workspace-2026-11-09.zip` (all code and data needed to rebuild every page, table and figure). |
| `SMOTE25_Evaluation_Roadmap.html` | From v3: how evaluation practice changed 1997 to 2026, and the reasoning behind the main findings. Thai and English. |
| `SMOTE25_Evaluation_Primer.html` | From v3: background to read first (Thai): what each measure computes, protocols, tuning, statistical tests, the citation analysis, glossary. |
| `section07-pass2-verification.xlsx` | Every second-pass code with its quote and page, for a co-author to check against the PDFs. |
| `section07-coded-data.json` | Coded evaluation designs of the 76 papers (71 with experiments). Unchanged since v3. |
| `section07-build-source.zip` | Scripts and parts that generate the v4.1 tables, figures, HTML and PDF. |
| `latex/` | Repo-ready LaTeX for Section 7 v4.1 and its appendix (sections, 31 tables, 8 figures, bib candidates). See `latex/README.md`. |

## Merging into the paper (not done yet)

The manuscript still uses the placeholder `sections/07-empirical-comparisons.tex`. To merge:

1. Copy `latex/sections/07-empirical-comparisons.tex`, `latex/tables/` and `latex/figures/` into the repository root folders.
2. Copy `latex/sections/07-empirical-appendix.tex` to `sections/` and add `\input{sections/07-empirical-appendix}` after `\appendix` in `main.tex`.
3. Add `\usepackage{array}` and `\usepackage{longtable}` to the preamble of `main.tex` (the section also needs booktabs, amsmath and graphicx).
4. Verify the entries in `latex/notes/empirical-bib-candidates.bib` and add them to `references.bib`.
5. Resolve the four `\TODO{...}` notes: the co-author check of the second-pass quotes, the references to the Data and Method sections, and whether the illustrative runs stay (if so, repeat the cross-validation at least five times).

`latex/notes/main-tex-additions.tex` still lists the v3 lines (appendix-empirical-map); follow the steps above instead.

Section order in v4.1: 7.1 corpus and coding, 7.2 from SMOTE (2002) to today, 7.3 benchmark data and tasks,
7.4 base learners, 7.5 competitors and baselines, 7.6 performance measures, 7.7 evidence beyond classifier scores,
7.8 validation protocol and the choice of settings, 7.9 statistical testing, 7.10 reporting results,
7.11 why evaluation practice changed, 7.12 what the comparisons conclude, 7.13 a protocol for a new SMOTE-family study,
7.14 limitations; Appendix A: illustrative runs and the coding of the studies.
Counts from the Data section workbook (all rows ai_draft) are not used in the manuscript text.
