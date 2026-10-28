# Evaluation section (Section 7: Empirical Comparisons and Benchmarks)

Latest version (v3, 29 Oct 2026) of the Section 7 draft and the material behind it.
Older versions are in the Git history only.

| File | What it is |
|------|------------|
| `../SMOTE25_Evaluation_Section.html` | Section 7 draft, English only (repository root). Open in a browser. |
| `SMOTE25_Evaluation_Section_bilingual.html` | Same draft in English and Thai side by side, with the evidence explorer, LaTeX export and coding notes. |
| `SMOTE25_Evaluation_Roadmap.html` | How evaluation practice changed 1997 to 2026, and the reasoning behind the four main findings (citations, data, evaluation without a classifier, model selection). Thai and English. |
| `SMOTE25_Evaluation_Primer.html` | Background to read first (Thai): what each measure computes and how measures differ, protocols, tuning, statistical tests, the citation analysis, glossary. |
| `section07-pass2-verification.xlsx` | Every second-pass code with its quote and page, for a co-author to check against the PDFs. |
| `section07-coded-data.json` | Coded evaluation designs of the 76 papers (71 with experiments). |
| `section07-build-source.zip` | Scripts and data that generate the pages and the LaTeX files. |
| `latex/` | Repo-ready LaTeX for Section 7 and Appendix B (sections, tables, figures with sources, bib candidates, compile preview). See `latex/README-empirical-section.md`. |

## Merging into the paper (not done yet)

The manuscript still uses the placeholder `sections/07-empirical-comparisons.tex`. To merge:

1. Copy `latex/sections/`, `latex/tables/` and `latex/figures/` into the repository root.
2. Apply the two lines in `latex/notes/main-tex-additions.tex` to `main.tex`.
3. Verify the entries in `latex/notes/empirical-bib-candidates.bib` and add them to `references.bib`.
4. Resolve the nine `\TODO{...}` notes, including the check of the second-pass quotes.

Section order in v3: 7.1 corpus, 7.2 data, 7.3 learners, 7.4 notation and measures, 7.5 measures in use,
7.6 protocol and tuning, 7.7 statistical testing, 7.8 reporting, 7.9 outcomes, 7.10 threats, 7.11 standard.
Counts from the Data section workbook (all rows ai_draft) are not used in the manuscript text.
