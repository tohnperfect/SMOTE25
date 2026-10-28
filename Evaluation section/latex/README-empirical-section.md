# Section 7 (empirical comparisons and evaluation practice): files for tohnperfect/SMOTE25, version 3

Copy these folders into the repository root; paths match the repo layout.

- `sections/07-empirical-comparisons.tex`: Section 7 (replaces the placeholder).
- `tables/empirical-*.tex`: eight tables input by the section (caption above, booktabs). New in v3:
  `empirical-reasons.tex` (reasons given for evaluation choices) and `empirical-beyond.tex`
  (evidence other than classifier scores).
- `figures/empirical-*.pdf`: nine figures; sources in `figures/src/` (pdflatex, standalone). New in v3:
  `empirical-influence.pdf` (citation ratio of each practice, adjusted for publication year).
- `sections/appendix-empirical-map.tex`: Appendix B, one row per study (longtable).
- `notes/main-tex-additions.tex`: the two lines to add to `main.tex`.
- `notes/empirical-bib-candidates.bib`: candidate entries for the corpus cite keys (built from coded
  metadata, verify before merging) plus 18 reference works with titles and DOIs from OpenAlex
  (KEEL, UCI, Demšar 2006, García and Herrera 2008, Saito and Rehmsmeier 2015, Hand and Till 2001,
  Cawley and Talbot 2010 and others). `fernandez2018smote` is already in references.bib.
- `notes/preview-compiled-with-stub-fonts.pdf`: compile check of the whole paper with this section
  (stub fonts and stub biblatex, so citations print as "(Ref.)").

What changed in v3
- Every subsection now says why studies made their choices (second, page-referenced reading of the
  71 empirical studies) and whether studies that follow a practice are cited more (OpenAlex,
  retrieved 2026-10-18; citation ratio adjusted for publication year, studies up to 2024).
- New analysis: which measure decides the selected settings, and what evidence other than
  classifier scores the studies give.
- Settings chosen on evaluation data are now split into explicit and implied evidence (35 studies
  in total, 25 explicit with a quote; pass 1 had 29).
- Two TODOs resolved with real references (MAUC: Hand and Till 2001; PR-AUC: Saito and Rehmsmeier
  2015). Nine `\TODO{...}` remain, including one asking a co-author to check the pass-2 quotes.
- Subsection order (29 Oct 2026): Notation and Measures moved from 7.2 to sit directly before
  Performance Measures in Use, so it is now 7.4 and the data and learner subsections are 7.2 and 7.3.
  Tables are numbered in order of appearance: Sources of Benchmark Data is Table 1, Reasons Given
  for Evaluation Choices Table 2, Families of Performance Measures Table 3. Labels are unchanged.

The pass-2 codes carry a quote and a page each; they are listed for checking in
`section07-pass2-verification.xlsx` (outside the repo). No em-dashes anywhere.
