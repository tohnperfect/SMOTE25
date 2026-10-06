# 25 Years of SMOTE: What Has Been Done and How Did It Benefit Society?

A survey paper, written in LaTeX, reviewing a quarter century of research on the
**Synthetic Minority Over-sampling Technique (SMOTE)** — from the original algorithm
by Chawla, Bowyer, Hall and Kegelmeyer (*Journal of Artificial Intelligence Research*,
2002) to its many extensions, and the real-world impact these methods have had.

## Aims

1. **What has been done** — map and categorize the SMOTE family of methods
   (variants, hybrids, and successors) developed between 2002 and the present.
2. **How did it benefit society** — document where SMOTE-based methods have been
   applied (e.g., healthcare and medical diagnosis, fraud detection, cybersecurity,
   manufacturing fault detection, environmental and social sciences) and the
   measurable benefits reported.
3. **What comes next** — identify open problems, limitations, and research gaps
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

## Planned Repository Structure

```
.
├── README.md
├── main.tex            # Main LaTeX document
├── sections/           # One .tex file per section
├── figures/            # Figures and diagrams (timeline, taxonomy, PRISMA)
├── tables/             # Summary tables of reviewed methods
├── references.bib      # BibTeX bibliography
└── notes/              # Reading notes and extraction sheets
```

## Building the Paper

```bash
latexmk -pdf main.tex
# or
pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

## Author

Supawit (P) — M.Sc. student, Statistics and Data Science, Faculty of Science,
Khon Kaen University · VI Lab

## Status

🚧 Project initialized — literature collection and taxonomy in progress.
