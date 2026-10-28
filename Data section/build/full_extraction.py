"""รวมผลอ่าน PDF ครบ 72 paper (18 ต.ค. 2026) เป็นตารางและตัวนับ

อ่าน  ai-draft/full/<key>.json   ผลอ่านต่อ paper ตาม ai-draft/full/SCHEMA.md (มีตาราง หน้า และ uncertain)
เขียน out/full_datasets.csv        1 แถวต่อ dataset ต่อ paper พร้อมคุณลักษณะที่ paper พิมพ์ และ how_obtained
      out/full_outcome_rows.csv    1 แถวต่อ dataset ที่มีค่าของวิธีที่เสนอและ SMOTE ในตารางเดียวกัน
      out/full_uncertain.csv       ทุกข้อที่ผู้อ่านไม่มั่นใจ พร้อม paper
      out/full_summary.json        ตัวนับ
ไม่ได้ตัดสินแพ้ชนะ diff = proposed - smote (กลับเครื่องหมายถ้า metric ยิ่งต่ำยิ่งดี) raw_sign ดูแค่ค่าที่พิมพ์
รันจาก Data section/:  python3 build/full_extraction.py
"""
import csv, glob, json, os, re, statistics as st
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
def P(*a): return os.path.join(HERE, *a)

def num(s):
    if s is None: return None
    m = re.search(r"-?\d+(?:\.\d+)?|-?\.\d+", str(s).replace(",", ""))
    return float(m.group()) if m else None

def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).lower())

def smote_kind(name):
    n = str(name or "").lower()
    if re.search(r"static|ovo|round|-all|smote-all|smoteos|smoteover|osmote|ssmote|\+\s*adaboost|esm|ensemble|\+cn|ovo-smo", n):
        return "SMOTE variant (multiclass/ensemble wrapper)"
    return "plain SMOTE" if "smote" in n or n.strip() in ("smo", "smt", "smt.") else "other"


KEEL_FAM = r"(abalone|ecoli|glass|yeast|page-?blocks|shuttle|vowel|vehicle|new-?thyroid|cleveland|led7digit|winequality(-red|-white)?|pima|haberman|segment|iris|poker|kr-vs-k|zoo|flare-?f?|dermatology|lymphography|ozone|kddcup|habarman|ecoli0|glass0)"
KEEL_BIN = re.compile(r"(\bvs\b|_vs_|-vs-|vs\d|\dvs|^" + KEEL_FAM + r"[-_]?\d)", re.I)
NATIVE_BIN = {"pima", "pimaindiandiabetes", "diabetes", "haberman", "habarman", "harberman", "wisconsin", "breastw", "breastcancerwisconsin",
    "breastcancer", "breastcancerorig", "breastcancerorigin", "breastcancerorigional", "bcancerorig", "wdbc", "wpbc", "ionosphere", "sonar",
    "german", "creditg", "germannumer", "australian", "heart", "statlogheart", "liver", "bupa", "liverdisorders", "spambase", "phoneme",
    "mammography", "spect", "spectf", "hepatitis", "banknote", "blood", "transfusion", "adult", "magic", "musk", "hillvalley", "titanic",
    "appendicitis", "credit", "creditcard", "default", "shoppers", "telcocustomerchurn", "customerchurn", "bank", "bankfull", "banksmall"}

def keel_rule(x, task):
    """แทนค่า not stated ด้วยกฎที่ Toon อนุมัติ (ค่าเดิมของผู้อ่านเก็บไว้ใน how_obtained)
    18 ต.ค. รอบแรก
      1. ชื่อตรงรูปแบบไฟล์ KEEL สองคลาส (x_vs_y, yeast4, abalone9-18) -> repository-defined (แยกหมวด ยืนยันอีกครั้ง 23:34)
      2. paper multiclass ใช้ชื่อสามัญโดยไม่บอกว่าดัดแปลง -> original
    18 ต.ค. รอบตรวจครบ (คำตอบ Toon 23:2x)
      A. ชุดที่เป็นสองคลาสโดยกำเนิด paper ไม่บอกอะไร -> original (ติดป้ายว่ามาจากกฎ ไม่ใช่จาก paper)
      B. ผู้เขียนตัดแถวที่มี missing value หรือตัด attribute -> modified
      C. ข้อมูลเฉพาะของผู้เขียน -> modified เมื่อผู้เขียนกำหนดคลาสเอง ไม่งั้น original (ตรงกับที่ผู้อ่านจัดไว้แล้ว ไม่ต้องแก้ค่า)"""
    h = x.get("how_obtained") or "not stated"
    det = str(x.get("how_obtained_detail") or "").lower()
    if h in ("original", "repository-defined", "not stated") and re.search(r"missing value|incomplete (data|record)|removed (the )?(attribute|feature)|attribute .{0,20}(removed|dropped)|after removing|without (the )?'?sex|nominal attribute.{0,20}(removed|dropped)", det):
        return "modified", "rule B: rows or attributes removed by authors (Toon 18 Oct)"
    if h != "not stated": return h, "reader (PDF)"
    nm = str(x.get("name") or "").split("(")[0].replace(" ", "")
    if KEEL_BIN.search(nm): return "repository-defined", "rule: KEEL file-name pattern (Toon 18 Oct)"
    if re.sub(r"[^a-z0-9]", "", nm.lower()) in NATIVE_BIN and (num(x.get("n_classes")) or 2) <= 2:
        return "original", "rule A: native two-class set, paper silent (Toon 18 Oct)"
    if task == "multiclass" or (num(x.get("n_classes")) or 0) > 2:
        return "original", "rule: multiclass common name, no modification stated (Toon 18 Oct)"
    return "not stated", "reader (PDF)"

def strip_variants(nm):
    s = str(nm or ""); out = {norm(s)}
    for inner in re.findall(r"\(([^)]*)\)", s): out.add(norm(inner))
    outer = re.sub(r"\([^)]*\)", "", s); out.add(norm(outer))
    out.add(norm(re.sub(r"^(hddt|keel|uci)\s+", "", s, flags=re.I)))
    return {o for o in out if o}

def match(nm, dmap, i, rows, dsl):
    for c in strip_variants(nm):
        if c in dmap: return dmap[c], "name"
    for c in strip_variants(nm):
        cand = [v for kk, v in dmap.items() if kk and len(c) >= 3 and (kk.startswith(c) or c.startswith(kk))]
        if len(cand) == 1: return cand[0], "prefix"
    inres = [x for x in dsl if str(x.get("in_results_table", "")).startswith("yes")]
    if len(inres) == len(rows) and i < len(inres):
        return dmap.get(norm(inres[i].get("name"))), "row order (check)"
    return None, "unmatched"

STD = {"original", "repository-defined"}
papers, ds_rows, out_rows, unc_rows = [], [], [], []
for f in sorted(glob.glob(P("ai-draft/full/*.json"))):
    d = json.load(open(f, encoding="utf-8"))
    k = d.get("key"); o = d.get("outcome") or {}; ch = o.get("chosen") or {}
    hib = ch.get("higher_is_better", True)
    if isinstance(hib, str): hib = hib.lower() not in ("false", "no")
    dmap = {}
    for x in d.get("datasets", []) or []:
        r = dict(paper=k, name=x.get("name"), group=x.get("group", ""), source_repo=x.get("source_repo"),
                 n_instances=x.get("n_instances"), n_features=x.get("n_features"), n_classes=x.get("n_classes"),
                 n_minority=x.get("n_minority"), n_majority=x.get("n_majority"), class_distribution=x.get("class_distribution"),
                 ir_printed=x.get("ir_printed"), how_obtained=x.get("how_obtained"), how_obtained_detail=x.get("how_obtained_detail"),
                 in_results_table=x.get("in_results_table"), ref=x.get("ref"))
        r["how_obtained_final"], r["how_basis"] = keel_rule(x, d.get("task"))
        ds_rows.append(r); dmap.setdefault(norm(x.get("name")), r)
    sk = smote_kind(o.get("smote_name_as_printed")) if o.get("smote_in_baselines") == "yes" else "not a baseline"
    rows_with_smote = 0; idx = 0
    for r in o.get("rows", []) or []:
        p, s = num(r.get("proposed")), num(r.get("smote"))
        if p is None or s is None: continue
        rows_with_smote += 1
        nm = r.get("dataset_as_printed"); dr, how_match = match(nm, dmap, idx, o.get("rows") or [], d.get("datasets") or [])
        idx += 1
        diff = round((p - s) if hib else (s - p), 6)
        out_rows.append(dict(paper=k, dataset=nm, match=how_match, how_obtained=(dr or {}).get("how_obtained_final", "unmatched"),
                             how_basis=(dr or {}).get("how_basis", ""), how_obtained_reader=(dr or {}).get("how_obtained", ""),
                             how_obtained_detail=(dr or {}).get("how_obtained_detail", ""), source_repo=(dr or {}).get("source_repo", ""),
                             n_instances=(dr or {}).get("n_instances"), n_features=(dr or {}).get("n_features"),
                             n_classes=(dr or {}).get("n_classes"), ir_printed=(dr or {}).get("ir_printed"),
                             metric=ch.get("metric"), classifier=ch.get("classifier"), table=ch.get("table"), page=ch.get("page"),
                             smote_name=o.get("smote_name_as_printed"), smote_kind=sk,
                             proposed=r.get("proposed"), smote=r.get("smote"), diff=diff,
                             raw_sign="+" if diff > 0 else "-" if diff < 0 else "=",
                             best_other=r.get("best_other_name"), best_other_value=r.get("best_other_value"), marks=r.get("marks")))
    for u in d.get("uncertain", []) or []:
        unc_rows.append(dict(paper=k, item=u))
    papers.append(dict(key=k, task=d.get("task"), n_datasets_claimed=d.get("n_datasets_claimed"), n_datasets_listed=len(d.get("datasets", []) or []),
                       characteristics_table=d.get("characteristics_table"), ir_definition=d.get("ir_definition"),
                       results_granularity=o.get("results_granularity"), smote_in_baselines=o.get("smote_in_baselines"),
                       smote_name=o.get("smote_name_as_printed"), smote_kind=sk, metric=ch.get("metric"), classifier=ch.get("classifier"),
                       table=ch.get("table"), page=ch.get("page"), rows_with_smote=rows_with_smote,
                       summary=o.get("summary_rows", []), claim=o.get("win_claim", {}), stat_test=o.get("stat_test"),
                       n_uncertain=len(d.get("uncertain", []) or []), notes=d.get("notes", "")))

def wcsv(path, rows):
    with open(P(path), "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader()
        for r in rows: w.writerow({kk: (json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v) for kk, v in r.items()})
wcsv("out/full_datasets.csv", ds_rows); wcsv("out/full_outcome_rows.csv", out_rows); wcsv("out/full_uncertain.csv", unc_rows)

def agg(sub):
    return dict(rows=len(sub), papers=len({r["paper"] for r in sub}),
                proposed_higher=sum(r["raw_sign"] == "+" for r in sub), smote_higher=sum(r["raw_sign"] == "-" for r in sub),
                equal=sum(r["raw_sign"] == "=" for r in sub))
plain = [r for r in out_rows if r["smote_kind"] == "plain SMOTE"]
S = dict(_note="ai_draft ทุกค่า diff เทียบข้าม paper ไม่ได้ (คนละ metric/หน่วย) ชนิดข้อมูลมาจากที่ผู้อ่านจัดตามคำนิยามใน SCHEMA.md",
         papers=len(papers), datasets_listed=len(ds_rows), uncertain_items=len(unc_rows),
         granularity=dict(Counter(p["results_granularity"] for p in papers)),
         smote_baseline=dict(Counter(p["smote_kind"] for p in papers)),
         papers_with_rows_vs_smote=sorted(p["key"] for p in papers if p["rows_with_smote"]),
         how_obtained_all=dict(Counter(r["how_obtained_final"] for r in ds_rows)),
         how_obtained_reader_only=dict(Counter(r["how_obtained"] for r in ds_rows)),
         match_methods=dict(Counter(r["match"] for r in out_rows)),
         outcome_all=agg(out_rows), outcome_plain=agg(plain),
         by_how_obtained_all={t: agg([r for r in out_rows if r["how_obtained"] == t]) for t in sorted({r["how_obtained"] for r in out_rows})},
         by_how_obtained_plain={t: agg([r for r in plain if r["how_obtained"] == t]) for t in sorted({r["how_obtained"] for r in plain})})
# per paper x type
bp = defaultdict(dict)
for k in sorted({r["paper"] for r in out_rows}):
    sub = [r for r in out_rows if r["paper"] == k]
    for t in sorted({r["how_obtained"] for r in sub}): bp[k][t] = agg([r for r in sub if r["how_obtained"] == t])
S["by_paper_and_type"] = bp
# papers that win on every standard row / lose some standard row
std_by_paper = {k: [r for r in out_rows if r["paper"] == k and r["how_obtained"] in STD] for k in bp}
S["papers_with_standard_rows"] = sorted(k for k, v in std_by_paper.items() if v)
S["papers_without_standard_rows"] = sorted(k for k, v in std_by_paper.items() if not v)
S["standard_rows_where_smote_higher"] = [(r["paper"], r["dataset"], r["proposed"], r["smote"]) for r in out_rows if r["how_obtained"] in STD and r["raw_sign"] == "-"]
json.dump(dict(summary=S, papers=papers), open(P("out/full_summary.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in S.items() if k not in ("by_paper_and_type", "standard_rows_where_smote_higher")}, ensure_ascii=False, indent=1))
print("smote higher on standard rows:", len(S["standard_rows_where_smote_higher"]))
