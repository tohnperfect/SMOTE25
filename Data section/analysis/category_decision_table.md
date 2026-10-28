# Dataset category definitions — decision table

Status: **documentation of the rules already in force** (19 Oct 2026). No entry was reclassified.
Rule sources: `handoff.md` §1 (advisor's three-way scheme); the 18 Oct decisions recorded in `how_basis` of
`out/verified_datasets.csv` (multiclass common-name rule, KEEL file-name rule, rule A, rule B); `decisions-pending.md`
item 2 (repository-defined is an interim choice awaiting the advisor); `keel_rule()` in `build/analyse_dataset_usage.py`.

Two layers are kept apart in the data:
- what the reader found in the paper (`category_by_reader`, `preprocessing_note`);
- the category assigned by the review (`category`, with its basis in `category_basis`).

| Observed situation | Category rule | Evidence required | Uncertainty handling | Corpus example |
|---|---|---|---|---|
| A named public data set is used, and the paper states or shows no change to classes, rows or features | Original | Paper text or table naming the data set/source; no described change | "Original" means no reported change. It does not mean verified byte identity; the version is usually not stated | DGOT satimage (UCI, #T = minority) |
| Paper is silent; the data set is natively two-class | Original by **rule A** (reviewer-assigned, Toon 18 Oct) | Two-class status consistent with the paper's characteristics table | Labelled `rule A` in `category_basis` (56 entries); report separately from reader-assigned | CBHSID Haberman |
| Paper is silent; a common multiclass name is used with its full class set | Original by the multiclass common-name rule (reviewer-assigned, 18 Oct) | Name and class count consistent with the source | Labelled in `category_basis` (192 entries) | to fill from `category_basis` (link dropped before lookup) |
| A task supplied by a repository (KEEL imbalanced files, imbalanced-learn) with class binarisation done by the repository | Repository-defined (**interim**, decisions-pending item 2) | File-name pattern (e.g. `yeast-0-2-5-6_vs_3-7-8-9`) or a stated repository task | KEEL file-name rule labelled (108 entries); can be folded into Original or Modified via `keel_rule()` once decided | RBBoost KEEL sets; DGOT optical_digits (#T = 8) |
| Authors change class definitions, rows, features or class sizes | Modified | Paper statement or table; operation and page in `out/modified_operations_audit.csv` | Operation tags and confidence from Analysis A; rule B moved 1 entry where rows or attributes were removed | MWMOTE Table 5 class mappings; G-SMOTE undersampled versions |
| Authors generate the data | Synthetic | Paper describes the generator or simulation | Data built by the authors from raw logs or simulation output and labelled by them are not Synthetic (Analysis A tags them OT, e.g. SMOTE "Can") | SMOTE-IPF subclus/clover/paw; MADELON variants |
| The paper does not allow any of the above to be decided | Not stated | The reader recorded it as such and no rule resolved it | Kept as Not stated (199). The cross-paper audit `out/not_stated_audit.csv` gives partial 32 / mismatch 27 / unresolved 140 without reclassifying | Loyalty-SMOTE (40 entries), CGMOS (26) |

Notes
- A reported "original" data set is not evidence of identical data across papers: 78 of the 198 names that carry a
  size in two or more papers carry different sizes.
- Repository-defined remains an interim label. Any change must be applied through `keel_rule()` and propagated by
  rerunning `build/dataset_records.py`, `build/reconcile_counts.py` and `build/make_atlas.py`.
