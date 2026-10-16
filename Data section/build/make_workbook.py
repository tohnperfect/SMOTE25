# -*- coding: utf-8 -*-
"""
Build notes/SMOTE25_data_extraction.xlsx for the SMOTE25 survey Data section.

One row per (paper, dataset) in `extraction`; one row per paper in `papers`.
Skeleton rows are prefilled from an AI pass over the PDFs and are marked
ai_draft (unverified): every one must be checked against the paper and given a
page reference before it is used.

Run:  python3 make_workbook.py papers.json ds_rows.json out.xlsx
"""
import json, sys, re, datetime
from collections import OrderedDict
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment

sys.path.insert(0, __file__.rsplit('/',1)[0])
import lists as L
import drive_inventory as INV

FONT = "Arial"
HDR_FILL   = PatternFill("solid", fgColor="1F3B57")
HDR_FONT   = Font(name=FONT, size=10, bold=True, color="FFFFFF")
SUB_FILL   = PatternFill("solid", fgColor="DCE6F1")
FILLIN     = PatternFill("solid", fgColor="FFF2CC")   # yellow: you fill this in
AIDRAFT    = PatternFill("solid", fgColor="F2F2F2")   # grey: AI draft, verify it
REQUIRED   = PatternFill("solid", fgColor="FCE4D6")   # orange: required before use
HINT_FILL  = PatternFill("solid", fgColor="EDEDED")
THIN       = Side(style="thin", color="BFBFBF")
BORDER     = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
BODY       = Font(name=FONT, size=10)
BOLD       = Font(name=FONT, size=10, bold=True)
TITLE      = Font(name=FONT, size=14, bold=True)
NOTE       = Font(name=FONT, size=9, italic=True, color="595959")

# ---------------------------------------------------------------- column specs
# (header, width, fill-kind, validation-list-name, codebook description, who fills)
PAPER_COLS = [
 ("paper_id",            10, "key",  None,          "Stable short id, P001 onward. Never reuse or renumber.", "prefilled"),
 ("method_name",         22, "ai",   None,          "Acronym the paper uses for its own method.", "prefilled, verify"),
 ("authors",             24, "ai",   None,          "First author et al.", "prefilled, verify"),
 ("year",                 7, "ai",   None,          "Publication year of the version you read.", "prefilled, verify"),
 ("venue",               24, "ai",   None,          "Journal or conference name.", "prefilled, verify"),
 ("venue_type",          12, "fill", "VENUE_TYPE",  "journal / conference / workshop / preprint / thesis / book chapter.", "you"),
 ("doi_or_url",          26, "fill", None,          "DOI preferred. Needed for the bibliography and for re-checking.", "you"),
 ("task",                10, "ai",   "TASK",        "Problem setting the paper addresses.", "prefilled, verify"),
 ("role",                30, "fill", "ROLE",        "Decides whether the paper can enter the win/loss analysis at all.", "you"),
 ("has_results_table",   10, "fill", "YESNO",       "Does the paper report a per-dataset results table you can read win/loss from?", "you"),
 ("include_in_H1H2",     10, "fill", "YESNO",       "Include this paper in the hypothesis tests. Normally yes when has_results_table = yes.", "you"),
 ("n_datasets_claimed",   9, "ai",   None,          "Count the paper states in its text or abstract.", "prefilled, verify"),
 ("n_datasets_in_table",  9, "fill", None,          "Count you actually see in the characteristics table. A mismatch is itself a finding.", "you"),
 ("classifiers_used",    28, "fill", None,          "Semicolon separated, e.g. C4.5; SVM; kNN.", "you"),
 ("metrics_used",        24, "fill", None,          "Semicolon separated, e.g. AUC; G-mean; F1.", "you"),
 ("stat_test",           26, "fill", "STAT_TEST",   "Statistical test the paper applies to its comparison.", "you"),
 ("code_available",      11, "fill", "YESNO",       "Does the paper link runnable code?", "you"),
 ("code_url",            24, "fill", None,          "Link if any.", "you"),
 ("pdf_filename",        40, "ai",   None,          "File name in the shared Google Drive folder.", "prefilled"),
 ("drive_folder",        11, "ai",   None,          "Survey / Binary / Multiclass / Both.", "prefilled"),
 ("extraction_status",   14, "fill", "STATUS",      "Where you are with this paper.", "you"),
 ("extracted_by",        12, "fill", None,          "Initials.", "you"),
 ("double_checked_by",   13, "fill", None,          "Initials of the 10 to 20 percent re-check.", "you"),
 ("notes",               40, "fill", None,          "Anything odd about this paper.", "you"),
]

EXTRACT_COLS = [
 ("row_id",                     8,  "key",  None,               "Stable row id. Never renumber.", "prefilled"),
 ("paper_id",                   9,  "key",  None,               "Links to the papers sheet.", "prefilled"),
 ("method_name",                18, "calc", None,               "Looked up from the papers sheet. Do not type here.", "formula"),
 ("dataset_name_as_printed",    30, "ai",   None,               "Exactly as the paper spells it, including suffixes like ecoli1 or yeast-2_vs_8. Do not normalise.", "prefilled, verify"),
 ("group_in_paper",             26, "ai",   None,               "Which block of the paper's own table or text this name came from, e.g. 'KEEL (Table 3)' or 'high-dimensional microarray'. Blank when the paper has a single undivided list.", "prefilled, verify"),
 ("is_aggregate",               11, "ai",   "YESNO",            "yes = this row stands for a group of datasets the paper never names individually (generated variants, undersampled copies, sets listed only in supplementary material). Such a row carries a count, not a dataset. Keep it as one row; do not invent member names.", "prefilled, verify"),
 ("aggregate_count",            10, "ai",   None,               "How many datasets this aggregate row stands for, as the paper states it or, where the paper does not, as the residual against its own headline count. Check which of the two it is in the notes.", "prefilled, verify"),
 ("dataset_family",             16, "fill", None,               "Your normalised grouping key, e.g. ecoli, yeast, glass. Used only for descriptive counts.", "you"),
 ("source_repo",                26, "fill", "SOURCE_REPO",      "Where the paper says it got the data.", "you"),
 ("data_type",                  12, "req",  "DATA_TYPE",        "THE KEY COLUMN. Original = standard benchmark used as distributed. Modified = any change to classes, instances or balance. Synthetic = generated by the authors. See the codebook for the decision rule.", "you"),
 ("modification_kind",          34, "fill", "MODIFICATION_KIND","What was changed. Leave as none when data_type = Original.", "you"),
 ("modification_detail",        34, "fill", None,               "Free text, e.g. 'class 4 as minority, rest merged' or 'minority undersampled to IR 20'.", "you"),
 ("n_instances",                10, "ai",   None,               "As printed for this dataset in this paper.", "prefilled where known, verify"),
 ("n_features",                 10, "ai",   None,               "As printed. Note whether the paper counts the class attribute.", "prefilled where known, verify"),
 ("n_minority",                 10, "ai",   None,               "Minority-class count as printed for this dataset in this paper. Blank when the paper prints only a total.", "prefilled where known, verify"),
 ("n_majority",                 10, "ai",   None,               "Majority-class count as printed. Blank when the paper prints only a total.", "prefilled where known, verify"),
 ("n_classes",                  9,  "ai",   None,               "As printed.", "prefilled where known, verify"),
 ("values_corrected",           11, "ai",   "YESNO",            "yes = at least one printed value on this row was checked against the dataset's own documentation and found wrong. The printed values stay in their columns; the corrected ones go in the *_corrected columns. Never overwrite what the paper printed: the discrepancy is itself a finding.", "prefilled, verify"),
 ("n_instances_corrected",      12, "ai",   None,               "Correct total where the printed one is wrong. Blank when the printed value is right or the discrepancy is unresolved.", "prefilled, verify"),
 ("n_minority_corrected",       12, "ai",   None,               "Correct minority count where the printed one is wrong.", "prefilled, verify"),
 ("n_majority_corrected",       12, "ai",   None,               "Correct majority count where the printed one is wrong.", "prefilled, verify"),
 ("n_features_corrected",       12, "ai",   None,               "Correct feature count where the printed one is wrong.", "prefilled, verify"),
 ("correction_basis",           46, "ai",   None,               "Which source establishes the correct value, and the arithmetic that settles which printed cell is wrong. Required whenever values_corrected = yes.", "prefilled, verify"),
 ("ir_as_reported",             13, "ai",   None,               "The number the paper prints. Do not recompute it here.", "prefilled where known, verify"),
 ("ir_definition",              30, "fill", "IR_DEFINITION",    "Which formula produced that number. If the paper does not say, choose 'not stated'.", "you"),
 ("ir_source",                  24, "fill", "IR_SOURCE",        "Whether the IR came from the paper or from your own calculation.", "you"),
 ("outcome_vs_best_baseline",   14, "req",  "OUTCOME",          "Proposed method against the best competing method in this paper's own table, on this dataset.", "you"),
 ("outcome_vs_original_smote",  14, "req",  "OUTCOME",          "Proposed method against plain SMOTE on this dataset. 'not comparable' when SMOTE is not among the baselines.", "you"),
 ("outcome_metric",             14, "fill", None,               "The single metric used to judge the two columns above. Must follow the rule fixed in win_loss_rule.", "you"),
 ("outcome_classifier",         14, "fill", None,               "The classifier whose row you read.", "you"),
 ("best_baseline_name",         18, "fill", None,               "Which method was the best baseline on this dataset.", "you"),
 ("smote_among_baselines",      12, "fill", "YESNO",            "Is plain SMOTE one of the compared methods anywhere in the paper?", "you"),
 ("stat_test_on_this_row",      12, "fill", "YESNO",            "Does the paper apply a test to this specific comparison?", "you"),
 ("significant",                11, "fill", "YESNONA",          "Result of that test.", "you"),
 ("featured_in_abstract_or_intro",14,"fill","YESNO",            "Is this dataset one the paper showcases in its abstract, introduction or a highlighted figure?", "you"),
 ("page_ref",                   16, "req",  None,               "REQUIRED. Page and table, e.g. 'p.418 Tab.5'. A row without this is not usable.", "you"),
 ("value_status",               24, "req",  "VALUE_STATUS",     "Provenance of this row. Rows left as ai_draft are excluded from the analysis.", "you"),
 ("verified_by",                11, "fill", None,               "Initials.", "you"),
 ("verified_date",              12, "fill", None,               "YYYY-MM-DD.", "you"),
 ("notes",                      34, "fill", None,               "Anything that does not fit a column.", "you"),
 ("ai_hint_data_type",          18, "hint", None,               "SUGGESTION ONLY from the AI pass. Never used by the analysis. Overwrite data_type yourself.", "ignore"),
 ("ai_hint_source",             26, "hint", None,               "SUGGESTION ONLY from the AI pass.", "ignore"),
]

FILLKIND = {"key":SUB_FILL, "ai":AIDRAFT, "fill":FILLIN, "req":REQUIRED, "hint":HINT_FILL, "calc":None}


def style_header(ws, cols, row=1):
    for i,(h,w,kind,dv,desc,who) in enumerate(cols, start=1):
        c = ws.cell(row=row, column=i, value=h)
        c.font = HDR_FONT; c.fill = HDR_FILL; c.border = BORDER
        c.alignment = Alignment(vertical="center", wrap_text=True)
        ws.column_dimensions[get_column_letter(i)].width = w
        c.comment = Comment(desc, "codebook", width=320, height=110)
    ws.row_dimensions[row].height = 30
    ws.freeze_panes = ws.cell(row=row+1, column=4)


def add_validations(ws, cols, nrows, first=2):
    for i,(h,w,kind,dv,desc,who) in enumerate(cols, start=1):
        if not dv: continue
        vals = getattr(L, dv)
        n = len(vals)
        col = get_column_letter(i)
        ref = "lists!$%s$2:$%s$%d" % (chr(64+ (list(VOCABS).index(dv)+1)), chr(64+(list(VOCABS).index(dv)+1)), n+1)
        d = DataValidation(type="list", formula1=ref, allow_blank=True, showDropDown=False)
        d.error = "Pick a value from the drop-down, or leave blank."
        d.errorTitle = "Not in the list"
        ws.add_data_validation(d)
        d.add("%s%d:%s%d" % (col, first, col, first+nrows-1))


VOCABS = OrderedDict([
 ("SOURCE_REPO",L.SOURCE_REPO), ("DATA_TYPE",L.DATA_TYPE), ("MODIFICATION_KIND",L.MODIFICATION_KIND),
 ("IR_DEFINITION",L.IR_DEFINITION), ("IR_SOURCE",L.IR_SOURCE), ("OUTCOME",L.OUTCOME),
 ("YESNO",L.YESNO), ("YESNONA",L.YESNONA), ("VENUE_TYPE",L.VENUE_TYPE), ("TASK",L.TASK),
 ("ROLE",L.ROLE), ("STAT_TEST",L.STAT_TEST), ("STATUS",L.STATUS), ("VALUE_STATUS",L.VALUE_STATUS),
])


# ------------------------------------------------------------------ hints
ORIGIN_TO_HINT = {
 "Natural":"Original", "Binarised":"Modified", "Class-merged":"Modified",
 "Class-resized":"Modified", "Undersampled":"Modified", "Noise-injected":"Modified",
 "Induced profile":"Modified", "Generated":"Synthetic",
}
AGG = re.compile(r"(variants?|simulated\s*\d|\d+\s+(simulated|artificial|synthetic|KEEL|UCI)|sets\b)", re.I)

def hint_type(p, name):
    if re.search(r"simulat|artificial|synthetic|MADELON|checkerboard|^art\d|Circle", name, re.I):
        return "Synthetic"
    origins = p.get("origin") or []
    if len(origins)==1:
        return ORIGIN_TO_HINT.get(origins[0], "")
    if "Natural" in origins and len(origins)>1:
        return ""          # ambiguous at paper level: the row-level call is yours
    return ORIGIN_TO_HINT.get(origins[0], "") if origins else ""

def hint_source(p):
    s = p.get("sources") or []
    return "; ".join(s)


def build(papers_json, dsrows_json, out):
    P = json.load(open(papers_json, encoding="utf-8"))
    DSR = json.load(open(dsrows_json, encoding="utf-8"))

    # per-dataset numbers recovered from the seven tables, keyed by (paper, printed name)
    def norm_name(x):
        x = re.sub(r"\([^)]*\)", " ", str(x))      # drop our own annotations
        x = re.sub(r"[^a-z0-9]+", "", x.lower())
        return x
    recovered = {}
    for r in DSR:
        recovered[(r["paper"], norm_name(r["raw"]))] = r

    # papers present in Drive but with no record yet: add them empty, to be filled from the PDF
    have = {x["key"] for x in P}
    for key,title,year,venue,fn in INV.MISSING:
        if key in have: continue
        P.append({"key":key,"title":title,"year":year,"venue":venue,"authors":"",
                  "task":"","nd":None,"dsn":[],"origin":[],"sources":[],
                  "conf":"not extracted","_new":True})

    P = sorted(P, key=lambda x: (x["year"], x["key"]))
    for i,p in enumerate(P, start=1):
        p["_id"] = "P%03d" % i

    wb = openpyxl.Workbook()

    # ---------------- lists ----------------
    ws = wb.active; ws.title = "lists"
    for j,(name,vals) in enumerate(VOCABS.items(), start=1):
        c = ws.cell(row=1, column=j, value=name); c.font = HDR_FONT; c.fill = HDR_FILL
        ws.column_dimensions[get_column_letter(j)].width = max(14, min(34, len(name)+4))
        for k,v in enumerate(vals, start=2):
            cc = ws.cell(row=k, column=j, value=v); cc.font = BODY
    ws.sheet_state = "visible"

    # ---------------- papers ----------------
    wp = wb.create_sheet("papers")
    style_header(wp, PAPER_COLS)
    idx = {h:i for i,(h,*_rest) in enumerate(PAPER_COLS, start=1)}
    for r,p in enumerate(P, start=2):
        vals = {
          "paper_id": p["_id"], "method_name": p["key"], "authors": p.get("authors",""),
          "year": p.get("year"), "venue": p.get("venue",""), "task": p.get("task",""),
          "n_datasets_claimed": p.get("nd"),
          "pdf_filename": " | ".join(INV.INVENTORY.get(p["key"], ([],[ ]))[1]) or
                          next((fn for k,_t,_y,_v,fn in INV.MISSING if k==p["key"]), ""),
          "drive_folder": " + ".join(INV.INVENTORY.get(p["key"], (["Both"],[]))[0]),
          "notes": ("Dataset names extracted 2026-10-14; paper-level fields (role, metrics, code, IR) still open."
                    if p.get("_new") else None),
        }
        for h,i in idx.items():
            c = wp.cell(row=r, column=i, value=vals.get(h))
            c.font = BODY; c.border = BORDER
            kind = PAPER_COLS[i-1][2]
            if FILLKIND[kind]: c.fill = FILLKIND[kind]
            c.alignment = Alignment(vertical="top", wrap_text=(PAPER_COLS[i-1][1] > 20))
    add_validations(wp, PAPER_COLS, len(P))

    # ---------------- extraction ----------------
    we = wb.create_sheet("extraction")
    style_header(we, EXTRACT_COLS)
    eidx = {h:i for i,(h,*_rest) in enumerate(EXTRACT_COLS, start=1)}
    row = 2; rid = 1
    for p in P:
        # (name, group label, aggregate-or-None)
        items = []
        groups = p.get("dsgroups")
        if groups:
            seen = set()
            for g in groups:
                for nm in g["names"]:
                    if nm in seen: continue
                    seen.add(nm); items.append((nm, g["label"], None))
        else:
            for nm in (p.get("dsn") or []):
                items.append((nm, "", None))
        for a in (p.get("dsagg") or []):
            items.append(("[aggregate] %s" % a["label"], a["label"], a))
        if not items:
            items = [("[fill in from the paper]" if p.get("_new")
                      else "[no dataset named in the paper]", "", None)]

        for nm, grp, agg in items:
            rec = None if agg else recovered.get((p["key"], norm_name(nm)))
            vals = {
              "row_id": "R%04d" % rid,
              "paper_id": p["_id"],
              "method_name": '=IFERROR(INDEX(papers!$B:$B,MATCH($B%d,papers!$A:$A,0)),"")' % row,
              "dataset_name_as_printed": nm,
              "n_instances": rec["N"] if rec else None,
              "n_features":  rec["F"] if rec else None,
              "n_minority":  rec.get("n_min") if rec else None,
              "n_majority":  rec.get("n_maj") if rec else None,
              "n_classes":   rec["C"] if rec else None,
              "values_corrected":      (rec.get("corrected") if rec else None),
              "n_instances_corrected": (rec.get("N_corr") if rec else None),
              "n_minority_corrected":  (rec.get("min_corr") if rec else None),
              "n_majority_corrected":  (rec.get("maj_corr") if rec else None),
              "n_features_corrected":  (rec.get("F_corr") if rec else None),
              "correction_basis":      (rec.get("corr_basis") if rec else None),
              "ir_as_reported": rec["ir"] if rec else None,
              "group_in_paper": grp,
              "is_aggregate": "yes" if agg else "no",
              "aggregate_count": agg["count"] if agg else None,
              "value_status": "ai_draft (unverified)",
              "ai_hint_data_type": ("Synthetic" if agg and re.search(r"simulat|artificial|synthetic|generat|undersampl", agg["description"], re.I)
                                    else hint_type(p, nm)),
              "ai_hint_source": hint_source(p),
              "notes": (agg["description"] if agg else
                        ("aggregate entry, expand into individual datasets when verifying" if AGG.search(nm) else None)),
            }
            for h,i in eidx.items():
                v = vals.get(h)
                # Excel อ่านข้อความที่ขึ้นต้นด้วย = + - @ เป็นสูตร ยกเว้นสูตรที่เราตั้งใจใส่เอง
                if isinstance(v, str) and v[:1] in "=+-@" and h != "method_name":
                    v = "'" + v
                c = we.cell(row=row, column=i, value=v)
                c.font = BODY; c.border = BORDER
                kind = EXTRACT_COLS[i-1][2]
                if FILLKIND[kind]: c.fill = FILLKIND[kind]
                c.alignment = Alignment(vertical="top", wrap_text=(EXTRACT_COLS[i-1][1] > 24))
            row += 1; rid += 1
    add_validations(we, EXTRACT_COLS, row-2)
    we.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(EXTRACT_COLS)), row-1)
    wp.auto_filter.ref = "A1:%s%d" % (get_column_letter(len(PAPER_COLS)), len(P)+1)
    return wb, P, row-2


def add_readme(wb, npapers, nrows):
    ws = wb.create_sheet("README", 0)
    ws.column_dimensions["A"].width = 3
    ws.column_dimensions["B"].width = 34
    ws.column_dimensions["C"].width = 86
    ws["B2"] = "SMOTE25 survey, Data section: extraction workbook"; ws["B2"].font = TITLE
    ws["B3"] = "Built %s. One row per (paper, dataset) in `extraction`; one row per paper in `papers`." % datetime.date.today()
    ws["B3"].font = NOTE

    rows = [
      ("", ""),
      ("THE RULE", "Every cell must be traceable to a page in the paper. A row with no page_ref, or with "
                   "value_status still 'ai_draft', is excluded from the analysis. Write 'not stated in paper' "
                   "rather than guessing; the proportion of papers that do not state something is itself a finding."),
      ("", ""),
      ("Colour legend", ""),
      ("  grey", "Prefilled by an AI pass over the PDFs. UNVERIFIED. Check it against the paper and correct it."),
      ("  yellow", "You fill this in."),
      ("  orange", "Required before the row counts: data_type, the two outcome columns, page_ref, value_status."),
      ("  light grey, far right", "ai_hint_* columns. Suggestions only. The analysis never reads them."),
      ("  blue", "Key or looked up. Do not edit."),
      ("", ""),
      ("Order of work per paper", ""),
      ("  1", "Open the PDF. Fill the paper's row in `papers` first, especially role and has_results_table."),
      ("  2", "If has_results_table = no (surveys, theory papers), set include_in_H1H2 = no and stop. "
              "Those papers still contribute to the descriptive sections."),
      ("  3", "Go to the characteristics table. For each dataset, correct the prefilled row in `extraction` "
              "and set data_type, modification_kind, n, features, classes, IR and page_ref."),
      ("  4", "Go to the results table. For each dataset, set outcome_vs_best_baseline and "
              "outcome_vs_original_smote using the rule fixed in the win_loss_rule sheet."),
      ("  5", "Set value_status to 'verified against paper' and fill verified_by and verified_date."),
      ("", ""),
      ("Before any extraction starts", "Fix the win/tie/loss rule with your advisor and record the decision in the "
                                        "win_loss_rule sheet. Changing it later means re-reading every results table."),
      ("", ""),
      ("Double-check", "Re-extract 10 to 20 percent of rows blind and compare. Record disagreements; the rate "
                       "is reportable as a reliability figure in the methodology section."),
    ]
    r = 5
    for a,b in rows:
        ws.cell(row=r, column=2, value=a).font = BOLD if a and not a.startswith("  ") else BODY
        c = ws.cell(row=r, column=3, value=b); c.font = BODY
        c.alignment = Alignment(wrap_text=True, vertical="top")
        if b: ws.row_dimensions[r].height = max(14, 12 * (len(b)//95 + 1) + 4)
        r += 1

    r += 1
    ws.cell(row=r, column=2, value="Live progress").font = BOLD
    r += 1
    prog = [
      ("Papers in the sheet",            '=COUNTA(papers!$A$2:$A$10000)'),
      ("Papers marked done",             '=COUNTIF(papers!$U$2:$U$10000,"done")+COUNTIF(papers!$U$2:$U$10000,"double-checked")'),
      ("Extraction rows",                '=COUNTA(extraction!$A$2:$A$20000)'),
      ("Rows verified",                  '=COUNTIF(extraction!$Z$2:$Z$20000,"verified against paper")+COUNTIF(extraction!$Z$2:$Z$20000,"corrected")'),
      ("Rows with a page reference",     '=COUNTA(extraction!$Y$2:$Y$20000)'),
      ("Rows usable in H1/H2",           '=COUNTIFS(extraction!$Z$2:$Z$20000,"verified against paper",extraction!$P$2:$P$20000,"<>")'),
      ("Percent verified",               '=IFERROR(C%d/C%d,0)' % (r+3, r+2)),
    ]
    for i,(lab,f) in enumerate(prog):
        ws.cell(row=r+i, column=2, value=lab).font = BODY
        c = ws.cell(row=r+i, column=3, value=f); c.font = BODY
        c.number_format = "0.0%" if lab.startswith("Percent") else "#,##0"
    return ws


def add_codebook(wb):
    ws = wb.create_sheet("codebook")
    heads = ["sheet","column","who fills it","allowed values","definition"]
    widths = [12, 30, 20, 40, 92]
    for j,(h,w) in enumerate(zip(heads,widths), start=1):
        c = ws.cell(row=1, column=j, value=h); c.font = HDR_FONT; c.fill = HDR_FILL; c.border = BORDER
        ws.column_dimensions[get_column_letter(j)].width = w
    r = 2
    for sheet, cols in (("papers", PAPER_COLS), ("extraction", EXTRACT_COLS)):
        for (h,w,kind,dv,desc,who) in cols:
            allowed = ", ".join(getattr(L, dv)) if dv else ("free text" if kind!="calc" else "formula")
            for j,v in enumerate([sheet,h,who,allowed,desc], start=1):
                c = ws.cell(row=r, column=j, value=v); c.font = BODY; c.border = BORDER
                c.alignment = Alignment(wrap_text=True, vertical="top")
            ws.row_dimensions[r].height = 28
            r += 1
    ws.freeze_panes = "A2"

    r += 2
    ws.cell(row=r, column=1, value="Decision rule for data_type").font = TITLE
    r += 1
    rule = [
     ("Original",  "The dataset is used exactly as the repository distributes it: same instances, same classes, "
                   "same labels. A standard KEEL two-class file such as yeast4 counts as Original, because KEEL "
                   "distributes it that way, even though it was originally derived from a multiclass UCI set."),
     ("Modified",  "The authors changed the data: binarised a multiclass set themselves, merged or dropped classes, "
                   "subsampled instances, undersampled the minority to raise the IR, injected noise, or imposed an "
                   "imbalance profile. If the paper had to describe what it did to the data, it is Modified."),
     ("Synthetic", "The data points were generated by the authors from a distribution or a generator, including "
                   "2-D illustrative sets, Gaussian mixtures, checkerboards and MADELON variants."),
     ("Not stated","The paper names a dataset but says nothing about how it was prepared, and the numbers do not "
                   "match the standard distribution. Record this rather than guessing: the count of such rows is a finding."),
     ("Borderline: KEEL two-class files",
                   "Treat as Original. Record the provenance in modification_detail so the choice can be revisited."),
     ("Borderline: same paper, several versions",
                   "One row per version actually used, each with its own data_type."),
    ]
    for a,b in rule:
        ws.cell(row=r, column=1, value=a).font = BOLD
        c = ws.cell(row=r, column=2, value=b); c.font = BODY
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        ws.row_dimensions[r].height = 42
        r += 1
    return ws


WIN_OPTIONS = [
 ("A",
  "Single pre-registered metric per paper",
  "Before reading a paper, fix a metric priority order, for example G-mean, then AUC, then F1, then accuracy. "
  "Use the highest-priority metric that paper reports. On that metric compare the proposed method with the best "
  "competing method on that dataset. Win if higher, loss if lower, tie if equal to the precision printed or if the "
  "paper's own test says the difference is not significant.",
  "One row per dataset, no ambiguity, every paper contributes, the rule is stated in one sentence in the methodology.",
  "Discards information when a paper reports several metrics that disagree. The priority order is a judgement call "
  "that a reviewer can question, so it must be justified.",
  "Highest usable N. H1 and H2 both testable on close to the full corpus.",
  "RECOMMENDED as the primary definition"),
 ("B",
  "Majority vote across all reported metrics",
  "For a dataset, count the metrics on which the proposed method beats the best baseline. Win if it beats on more "
  "than half, loss if it loses on more than half, tie otherwise.",
  "Uses everything the paper reports and is robust to a lucky metric.",
  "Papers report different numbers of metrics, so rows are not equally informative. Metrics are strongly correlated, "
  "so the vote is not as independent as it looks. Harder to describe precisely.",
  "Similar N to option A. Expect more ties, which weakens both tests slightly.",
  "good robustness check"),
 ("C",
  "Statistical significance only",
  "Win only when the paper itself reports a significant improvement on that dataset. Tie when the difference is not "
  "significant. Papers with no statistical test contribute no rows.",
  "The most conservative and the least arguable. Directly answers whether claimed wins are supported.",
  "Most papers in this corpus apply no per-dataset test, so a large share of the data is thrown away, and the papers "
  "that remain are the more rigorous ones, which biases the estimate in the opposite direction from the hypothesis.",
  "Sharply reduced N. H2 in particular may become untestable.",
  "report as a sensitivity analysis, not as the main result"),
 ("D",
  "Rank of the proposed method",
  "Record the rank of the proposed method among all methods compared on that dataset, rather than a binary outcome.",
  "Keeps more information than win/loss and handles papers with many baselines well. Suits a mixed-effects model with "
  "a continuous or ordinal response.",
  "Ranks depend on how many baselines the paper chose, so they are not comparable across papers without normalising. "
  "Harder to explain in a survey.",
  "Same N as option A, but the hypotheses must be restated in terms of mean normalised rank.",
  "optional second response variable"),
]

def add_win_loss(wb):
    ws = wb.create_sheet("win_loss_rule")
    ws.column_dimensions["A"].width = 5
    ws.column_dimensions["B"].width = 34
    for col in "CDEF": ws.column_dimensions[col].width = 46
    ws.column_dimensions["G"].width = 30
    ws["B2"] = "Decide this with your advisor BEFORE extraction starts"; ws["B2"].font = TITLE
    ws["B3"] = ("The win/tie/loss definition determines H1 and H2. Changing it after extraction means re-reading every "
                "results table, so fix it first and record the decision below.")
    ws["B3"].font = NOTE
    ws.merge_cells("B3:G3")

    heads = ["", "Option", "How it works", "Strengths", "Weaknesses", "Effect on H1 / H2", "Status"]
    for j,h in enumerate(heads, start=1):
        c = ws.cell(row=5, column=j, value=h); c.font = HDR_FONT; c.fill = HDR_FILL; c.border = BORDER
    r = 6
    for (k,name,how,pro,con,eff,status) in WIN_OPTIONS:
        for j,v in enumerate([k,name,how,pro,con,eff,status], start=1):
            c = ws.cell(row=r, column=j, value=v)
            c.font = BOLD if j in (1,2) else BODY
            c.border = BORDER; c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.row_dimensions[r].height = 92
        r += 1

    r += 1
    ws.cell(row=r, column=2, value="Sub-decisions that go with whichever option you pick").font = BOLD
    r += 1
    subs = [
     ("What counts as the best baseline",
      "The best-performing competing method in that paper's own table, excluding the proposed method and its own "
      "ablations. Record its name in best_baseline_name so a weak-baseline pattern becomes visible."),
     ("Why a second outcome column",
      "outcome_vs_original_smote is recorded separately. A method can beat plain SMOTE and still lose to a stronger "
      "baseline, and the gap between the two columns is itself a result worth reporting."),
     ("Which classifier",
      "When a paper reports several, use the one it highlights in its abstract or text. If none is highlighted, use "
      "the first listed and keep it consistent within the paper. Record it in outcome_classifier."),
     ("Ties with no test",
      "When no statistical test is reported, call a difference a tie if the two values are equal at the precision "
      "printed. Do not invent a threshold such as one percent unless you fix it here and apply it everywhere."),
     ("Datasets the paper reports but excludes from its comparison",
      "Record the row with outcome 'not comparable' rather than deleting it. Those rows still count for the "
      "descriptive sections."),
    ]
    for a,b in subs:
        ws.cell(row=r, column=2, value=a).font = BODY
        c = ws.cell(row=r, column=3, value=b); c.font = BODY
        c.alignment = Alignment(wrap_text=True, vertical="top")
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        ws.row_dimensions[r].height = 40
        r += 1

    r += 1
    ws.cell(row=r, column=2, value="DECISION").font = TITLE
    r += 1
    for lab in ["Option chosen", "Metric priority order", "Decided with", "Date", "Notes"]:
        ws.cell(row=r, column=2, value=lab).font = BOLD
        c = ws.cell(row=r, column=3, value=None)
        c.fill = FILLIN; c.border = BORDER; c.font = BODY
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=7)
        r += 1
    return ws


def main():
    papers_json, dsrows_json, out = sys.argv[1], sys.argv[2], sys.argv[3]
    wb, P, nrows = build(papers_json, dsrows_json, out)
    add_readme(wb, len(P), nrows)
    add_codebook(wb)
    add_win_loss(wb)
    wb.move_sheet("lists", offset=len(wb.sheetnames))
    wb["lists"].sheet_state = "hidden"
    order = ["README","win_loss_rule","papers","extraction","codebook","lists"]
    wb._sheets = [wb[s] for s in order]
    wb.save(out)
    print("papers:", len(P), "extraction rows:", nrows, "->", out)

if __name__ == "__main__":
    main()
