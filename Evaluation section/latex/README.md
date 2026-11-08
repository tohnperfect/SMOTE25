# Section 7 (Empirical Comparisons and Benchmarks), draft v4.1, 8 November 2026

Revision of v4 that follows the choices and notes made in the paper picker (183 items "use", 14 "maybe", 28 "not used", 9 notes or edits).
v4 is unchanged. What changed and how each note was handled: th/section07-v4.1-changes-th.md (Thai) or the second tab of the HTML page.

Files
- sections/07-empirical-comparisons.tex: the section (14 subsections, 7.1 to 7.14). Assembled from sections/parts/p1.tex to p4.tex.
- sections/07-empirical-appendix.tex: appendix (illustrative runs, coding of the 71 studies); place after \appendix.
- tables/empirical-*.tex: 31 tables. The v4 tables come from v4/make_tables.py (thennow and learner-causes edited for v4.1);
  the 20 new tables come from make_tables_v41.py. Regenerate instead of editing numbers.
- figures/empirical-*.pdf: 8 figures (make_figures.py); the CD diagram and the G-mean/F1 threshold figure of v4 are dropped.
- cites_raw.json: median citations and median year with and without each practice (OpenAlex, 18 Oct 2026).
- preview/: compile check outside the JAIR class (preview.tex, all.bib) and the HTML reading copy.

Needs in main.tex: \usepackage{array} (column specs), longtable, booktabs, amsmath, graphicx.
Compile check: cd preview; TEXINPUTS=..: pdflatex preview; bibtex preview; pdflatex preview (twice).
