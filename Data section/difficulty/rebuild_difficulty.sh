#!/usr/bin/env bash
# Rebuild every difficulty output in order (8 Nov 2026, Claude). Run from Data section/difficulty.
# Needs the mirror files in src/ (fetch_mirrors.sh + fetch_mirrors_ext.sh; not stored in git) and statsmodels.
set -eu
python3 mirrors_ext.py            # -> file_catalog_ext.csv (extended GitHub mirrors)
python3 verify_ext.py             # verifiability_entries_28oct.csv -> verifiability_entries.csv, verify_ext_summary.json
python3 measure.py                # -> difficulty_measures.csv (HVDM, Napierala types)          (~15 min)
python3 group_cited.py            # -> difficulty_groups_cited.csv, group_cited_summary.json
python3 profile_final.py          # -> difficulty_profile_final.csv, profile_final_summary.json
python3 fig_noise.py
python3 structure_check.py
python3 category_options.py
python3 dimension_profile.py
python3 family_spread.py
python3 paper_profile_mix.py
python3 reference_collection.py && python3 reference_collection_check.py
python3 fig_manuscript.py         # -> ../manuscript/figures/data-difficulty.{pdf,png}
python3 projection.py             # -> projections.json (Atlas)                                   (~5 min)
cd ..
python3 build/name_level_types.py
python3 build/name_level_extras.py
python3 build/difficulty_outcomes.py
