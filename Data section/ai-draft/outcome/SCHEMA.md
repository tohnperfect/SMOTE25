# Outcome extraction schema: proposed method vs SMOTE, per dataset (pilot)

Goal: copy RAW numbers so that any win/tie/loss rule can be applied later. Do NOT decide who wins.

Rules (mandatory)
- Every number must be copied exactly as printed (keep the printed decimals; keep "±" std separately if printed).
- Every table you use must have its table number and PDF page. If a table is an image, render the page and read it; say so in notes.
- If something is not in the paper write "not stated in paper". Never guess.
- Dataset names: copy exactly as printed, including typos.

Choosing what to copy (fixed rule, apply in order)
1. Proposed method: the paper's main named method. If it has several variants, take the one the abstract/conclusion highlights; list the others in notes.
2. SMOTE baseline: the plain/original SMOTE (Chawla et al. 2002) as the paper names it. Do NOT substitute Borderline-SMOTE, ADASYN etc. If plain SMOTE is absent, set smote_in_baselines = "no" and still fill best_other.
3. Metric priority: G-mean > AUC > F-measure/F1 > accuracy. Pick the highest-priority metric that has a per-dataset table containing both the proposed method and SMOTE. For multiclass papers the multiclass analogue counts (MG / mGM for G-mean, MAUC for AUC, macro-F for F1).
4. Classifier: the one highlighted in the abstract; else the first one reported. Keep it fixed for the whole paper.
5. Condition: if tables vary a condition (noise level, IR level), take the no-noise / original condition; list other conditions in notes.

Output JSON (one object per paper)
{
 "key": "<method key given to you>",
 "smote_in_baselines": "yes | no",
 "smote_name_as_printed": "...",
 "baselines_all": ["as printed", ...],
 "results_tables": [{"table": "Table N", "page": "...", "metric": "...", "classifier": "...", "granularity": "per-dataset | aggregate only | ranking only", "is_image": true/false}],
 "chosen": {"table": "...", "page": "...", "metric": "...", "classifier": "...", "condition": "...", "higher_is_better": true/false, "why_this_choice": "which rule step decided it"},
 "rows": [{"dataset_as_printed": "...", "proposed": "number as printed", "proposed_std": "... or null", "smote": "... or null", "smote_std": "... or null", "best_other_value": "...", "best_other_name": "...", "marks": "bold/underline/significance symbols as printed, or ''"}],
 "summary_rows": [{"label": "Average | Avg rank | Wins ...", "proposed": "...", "smote": "..."}],
 "stat_test": "test name + what it compared, or not stated in paper",
 "win_claim": {"quote": "verbatim claim of superiority from abstract or conclusion (<=40 words)", "page": "..."},
 "notes": "anything odd: image tables, datasets in results table that are not in the characteristics table or vice versa, missing values, mismatched names"
}
