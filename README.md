# 25 Years of SMOTE: What Has Been Done and How Did It Benefit Society?

A survey paper, written in LaTeX, reviewing a quarter century of research on the
**Synthetic Minority Over-sampling Technique (SMOTE)**, from the original algorithm
by Chawla, Bowyer, Hall and Kegelmeyer (*Journal of Artificial Intelligence Research*,
2002) to its many extensions, and the real-world impact these methods have had.

## Aims

1. **What has been done**: map and categorize the SMOTE family of methods
   (variants, hybrids, and successors) developed between 2002 and the present.
2. **How did it benefit society**: document where SMOTE-based methods have been
   applied (e.g., healthcare and medical diagnosis, fraud detection, cybersecurity,
   manufacturing fault detection, environmental and social sciences) and the
   measurable benefits reported.
3. **What comes next**: identify open problems, limitations, and research gaps
   that motivate future oversampling methods (feeding into a planned
   "SMOTE Improvement 2027" paper).

## Scope

| Dimension      | Coverage                                                              |
|----------------|-----------------------------------------------------------------------|
| Time span      | 2002 – 2027                                                           |
| Problem types  | Binary and multiclass imbalanced classification                       |
| Method types   | SMOTE variants, hybrid sampling, cleaning-based, cluster-/density-based, kernel/manifold, deep generative (GAN/VAE/diffusion) comparisons |
| Applications   | Domains where SMOTE-based methods were deployed or evaluated          |

## Literature Organization

Source papers are kept in the Google Drive folder **`SMOTE25`**, split into:

| Folder        | Contents                                              |
|---------------|-------------------------------------------------------|
| `Survey/`     | Existing reviews and surveys of imbalanced learning / SMOTE |
| `Binary/`     | Methods and applications for binary imbalance         |
| `Multiclass/` | Methods and applications for multiclass imbalance     |
| `Both/`       | Works addressing both binary and multiclass settings  |

## Planned Paper Outline

1. Introduction
2. Background: the class imbalance problem and the original SMOTE
3. Review methodology (search strategy, inclusion/exclusion criteria, PRISMA-style flow)
4. Taxonomy of SMOTE variants
5. SMOTE for multiclass imbalance
6. Applications and societal benefits
7. Empirical comparisons and benchmarks reported in the literature
8. Limitations, open challenges, and future directions
9. Conclusion

## Repository Structure

The paper uses the official **JAIR LaTeX template** (JAIR Author Kit, September 2025:
`jair.cls` 2025/08/15 on top of ACM `acmart`, BibLaTeX + Biber, `acmauthoryear` style).

```
.
├── README.md
├── main.tex                # Main LaTeX document (preamble from the JAIR template)
├── jair.cls                # JAIR class            ┐
├── acmart.cls              # ACM base class        │ from the JAIR Author Kit:
├── acmauthoryear.bbx       # BibLaTeX style        │ DO NOT MODIFY (JAIR returns
├── acmauthoryear.cbx       # BibLaTeX cite style   │ papers with style changes)
├── acmdatamodel.dbx        # BibLaTeX data model   ┘
├── references.bib          # Bibliography (BibLaTeX)
├── sections/               # One .tex file per section + reproducibility appendix
├── tables/                 # Summary tables of reviewed methods
├── figures/                # Figures (timeline, taxonomy, PRISMA)
├── notes/                  # Reading notes and extraction sheets (not uploaded to Overleaf)
└── template/jair-authorkit # Original JAIR Author Kit, unmodified (example .tex + PDF)
```

## Building the Paper

The template needs **pdfLaTeX + Biber** (not BibTeX).

```bash
latexmk -pdf main.tex
# or
pdflatex main && biber main && pdflatex main && pdflatex main
```

### Overleaf

1. Upload archive: `SMOTE25_overleaf.zip` (contains `main.tex`, the class files,
   `references.bib`, `sections/`, `tables/`, `figures/`).
2. Overleaf: **New Project → Upload Project** → choose the zip.
3. Menu → Settings: **Compiler = pdfLaTeX**, **TeX Live version = latest**,
   **Main document = main.tex**. Overleaf runs Biber automatically.

### Before submission

- Fill every `[bracketed]` placeholder (author surnames, e-mails, ORCID, corresponding
  author, department) and remove every `\TODO{...}`.
- Keep `\documentclass[manuscript, screen, review]{jair}` for submission; use
  `\documentclass[]{jair}` for the camera-ready version.
- Answer the Reproducibility Checklist (Appendix A).
- Cite with `\textcite{key}` (narrative) or `\cite{key}` / `\parencite{key}` (parenthetical).

## Author

Supawit (P), M.Sc. student, Statistics and Data Science, Faculty of Science,
Khon Kaen University · VI Lab

## Status

🚧 Project initialized; JAIR LaTeX template set up. Literature collection and taxonomy in progress.
