"""Rewrite the two verified sheets of SMOTE25_data_extraction.xlsx from the current CSV files (8 Nov 2026, Claude).

apply_verification.py --xlsx wrote these sheets on 18 Oct; it cannot be rerun since 19 Oct (it would erase the outcome
mapping audit), so after build/add_synthetic_entries.py changed out/verified_datasets.csv (93 entries) and one row of
out/verified_outcomes.csv (OREM-M Toy category), this script copies the CSVs into the sheets in the same way
(strings that start with = + - @ are prefixed with ' so Excel does not read them as formulas). Other sheets untouched.
Run from Data section/:  python3 build/sync_workbook_verified.py
"""
import csv, os
import openpyxl
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
wb = openpyxl.load_workbook("SMOTE25_data_extraction.xlsx")
for name, f in [("datasets_verified", "out/verified_datasets.csv"), ("outcomes_verified", "out/verified_outcomes.csv")]:
    rows = list(csv.DictReader(open(f, encoding="utf-8-sig")))
    idx = wb.sheetnames.index(name) if name in wb.sheetnames else None
    if name in wb.sheetnames: del wb[name]
    ws = wb.create_sheet(name, idx); cols = list(rows[0]); ws.append(cols)
    for r in rows:
        ws.append([("'" + v) if isinstance(v, str) and v[:1] in "=+-@" and v else v for v in (r[c] for c in cols)])
    print(name, len(rows), "rows")
wb.save("SMOTE25_data_extraction.xlsx")
