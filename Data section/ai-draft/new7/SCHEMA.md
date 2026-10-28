# Output schema: one JSON object per paper

Rules (mandatory):
- Every non-"not stated" value MUST be backed by an entry in "evidence" with the PDF page number (as printed on the page if visible, else PDF page index, say which) and a VERBATIM quote (<= 40 words) copied from the paper.
- If the paper does not say something, write exactly "not stated in paper". Never guess. Never infer the author's reason.
- Dataset names: copy exactly as printed, including typos.
- If a table is an image and unreadable, say so in "notes".

{
 "key": "<method key given to you>",
 "pdf_title": "...",
 "task": "binary | multiclass | both",
 "n_datasets_claimed": <int or null>,
 "dataset_names": ["as printed", ...],
 "sources": [subset of: UCI, KEEL, OpenML, UCR, LibSVM, imbalanced-learn, Kaggle, Image, Text, Private, Synthetic, Other],
 "srcdet": "which datasets come from which repository, in your words",
 "crit": "the selection rationale the paper gives, close to its wording, or 'not stated in paper'",
 "crit_type": "own reason | cites prior work | generic only (e.g. 'widely used benchmark') | not stated",
 "benchmark_inherited_from": "prior work whose dataset list was reused, as the paper says, or 'not stated in paper'",
 "origin": [subset of: Natural, Binarised, Class-merged, Class-resized, Undersampled, Noise-injected, Induced profile, Generated],
 "imbalance_creation": "how two-class / imbalanced tasks were made (which class is minority, one-vs-rest, merging, undersampling to raise IR, noise), or 'none: used as distributed'",
 "minority_classes_stated": "yes, in text | yes, in table only | no | not applicable",
 "modification_declared_where": "data/experimental section | table only | elsewhere (say where) | not declared | not applicable",
 "missing_values": "...or not stated in paper",
 "nominal_features": "...or not stated in paper",
 "normalisation": "...or not stated in paper",
 "duplicates_or_filtering": "...or not stated in paper",
 "split_protocol": "e.g. 5-fold stratified CV x 5, or not stated in paper",
 "resampling_inside_training_folds": "yes, stated | no, resampled before split | not stated in paper",
 "characteristics_table": "yes (Table N) | no",
 "characteristics_columns": [subset of: N, features, classes, n_minority, n_majority, class_distribution, IR, percent_minority, other],
 "ir_definition": "formula/wording the paper uses, or 'not stated in paper'",
 "ir_print_format": "single ratio | majority:minority counts | proportion pair | percent minority | per-class | not printed",
 "data_availability": "link given (url) | repository named only | not stated in paper",
 "results_granularity": "per-dataset | per-dataset partial | aggregate only | ranking only | no comparison",
 "evidence": [{"field": "...", "page": "...", "quote": "..."}],
 "notes": "anything odd: typos, sums that do not add up, image tables, supplementary-only info"
}
