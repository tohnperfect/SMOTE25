# All-metric win/loss extraction (proposed vs plain SMOTE), fixed classifier

Purpose: for each paper, copy the RAW per-dataset numbers of the proposed method and plain SMOTE
for EVERY evaluation metric the paper reports, using the SAME classifier and condition that the
earlier extraction already fixed (`existing_chosen` in the task file). Do NOT decide winners
yourself beyond copying; a script will compute win/tie/loss later.

Inputs: /home/claude/allmetric/tasks/<KEY>.json
  - pdfs: local PDF paths (main paper first, then supplementary if any)
  - existing_chosen: table/page/metric/classifier/condition chosen earlier (rule A)
  - existing_datasets: dataset names as printed in the earlier extraction

Tools: `pdftotext -layout` for text; for tables that are images or garbled, render the page
(`pdftoppm -r 150 -f N -l N -png`) into /home/claude/allmetric/render/<KEY>/ and look at it with Read.
Never guess a number. If unreadable, write "unreadable" and explain in notes.

Rules
1. Classifier and condition: keep exactly `existing_chosen.classifier` and `.condition`.
   If the paper reports a metric only for a DIFFERENT classifier, list it under
   `metrics_other_classifier_only` (name + table) but do not copy numbers.
   If existing_chosen.classifier is an average over classifiers, use the same averaging.
2. Metrics: every metric with a per-dataset table (or per-dataset figure with printed numbers)
   that contains BOTH the proposed method and plain SMOTE. Include the existing chosen metric too
   (it is used to cross-check against the earlier extraction).
   Plain SMOTE = Chawla et al. 2002 as the paper names it; not Borderline-SMOTE/ADASYN/SMOTE-ENN etc.
3. Proposed method: same as existing extraction (main named method; if variants, the one highlighted).
   State which column you used.
4. Copy numbers exactly as printed (keep decimals). Std in separate field if printed.
5. Also copy what the PAPER ITSELF reports about winning for each metric, if anything:
   bold/underline marks per row, W/T/L summary rows, average rows, average ranks, stat tests
   (test name, what was compared, p-values or "significant" marks vs SMOTE). Copy verbatim.
6. higher_is_better per metric (e.g. error/cost: false). If unclear, "not stated in paper".

Output: write /home/claude/allmetric/out/<KEY>.json :
{
 "key": "...",
 "classifier": "as fixed",
 "condition": "as fixed",
 "proposed_column": "as printed",
 "smote_column": "as printed",
 "metrics": [
   {"metric": "as printed", "metric_family": "G-mean|AUC|F-measure|accuracy|balanced-accuracy|recall|precision|specificity|MCC|kappa|other",
    "table": "Table N", "page": "PDF page N (printed p.X)", "is_image": true/false, "higher_is_better": true/false,
    "is_existing_chosen": true/false,
    "rows": [{"dataset_as_printed": "...", "proposed": "...", "proposed_std": null, "smote": "...", "smote_std": null, "marks": "as printed or ''"}],
    "paper_reported": {"summary_rows": [{"label": "...", "proposed": "...", "smote": "..."}],
                        "wtl_vs_smote": "verbatim or 'not stated in paper'",
                        "stat_test": "verbatim or 'not stated in paper'"}}
 ],
 "metrics_other_classifier_only": [{"metric": "...", "table": "...", "classifiers": "..."}],
 "metrics_without_smote": [{"metric": "...", "table": "..."}],
 "notes": "anything odd"
}
Validate the JSON with `python3 -m json.tool` before finishing.
