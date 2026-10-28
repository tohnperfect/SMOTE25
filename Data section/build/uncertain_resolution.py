"""จัดหมวดและสถานะของทุกข้อใน out/full_uncertain.csv หลังรอบตรวจกับ PDF 18 ต.ค. 2026
เขียน out/uncertain_resolution.csv (paper, item, category, resolution)
หมวด judgment ต้องรอกติกาจาก Toon (ดู handoff บันทึก 18 ต.ค. รอบตรวจครบ)
"""
import csv, json, os, re
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
U = list(csv.DictReader(open("out/full_uncertain.csv", encoding="utf-8-sig")))
V = json.load(open("out/visual_checks.json", encoding="utf-8"))
vis_papers = {v["paper"] for v in V}
RULES = [
 ("rule A: native two-class set, paper silent", r"natively (binary|2-class|two-class)|native two-class|single class in table|natively 2-class"),
 ("rule B: rows/attributes removed (missing values, nominal attribute)", r"missing values|removed incomplete|removing 'sex'|dropped attribute|row removal"),
 ("rule C: authors' own or private data / simulation", r"own project data|authors constructed|own data sets|simulation data|from refs|private"),
 ("rule D: binarisation stated in general but not per dataset", r"which (of the|uci|datasets|\d+)|not say (which|how)|per dataset|which ones|does not say whether|not determinable|binarized not stated|not stated per"),
 ("rule E: KEEL / imbalanced-learn name, origin not stated", r"keel|imbalanced-learn|#t ="),
]
def classify(t):
    l = t.lower()
    if re.search(r"how_obtained|could (alternatively )?be (considered|read)|marked (modified|original|synthetic)|classed|set 'original'|set 'modified'", l):
        for name, pat in RULES:
            if re.search(pat, l):
                if name[:6] in ("rule A", "rule B", "rule C", "rule E"):
                    return "judgment: data type", "resolved 18 Oct by Toon's " + name + " (applied in build/full_extraction.py keel_rule)"
                return "judgment: data type", "resolved 18 Oct by SCHEMA definition: " + name + " -> not stated, unless rule A or the multiclass rule applies (see how_basis)"
        return "judgment: data type", "resolved 18 Oct: reader label kept or replaced by the fixed rules (see how_obtained_final and how_basis)"
    if re.search(r"image|render|dpi|visual|text extraction|garbled|split in extraction|interleaved", l):
        return "value read from image or garbled text", "resolved 18 Oct: value checked against rendered page or row-level text match" 
    if re.search(r"typo|misprint|sums? to|does not add|\+.*=|!=|vs .* printed|inconsisten|but table|while table|says .* but|duplicate|swapped|appear(s)? out of order|header", l):
        return "inconsistency in the paper", "kept as finding: value copied as printed, inconsistency belongs to the paper"
    if re.search(r"not printed|not stated|not given|left null|only .* printed|not recorded|not extracted|not digitised|no per-dataset", l):
        return "value not printed", "no action: field stays null / not stated in paper (rule 2)"
    if re.search(r"chose|chosen|choice|taken as|proposed (method|variant)|first reported|condition", l):
        return "extraction rule applied", "no action: follows ai-draft/full/SCHEMA.md choosing rule"
    if re.search(r"page ind|pdf page|printed p|pagination", l):
        return "page index", "resolved 18 Oct: PDF page checked on local copy"
    if re.search(r"match|row order|mapped|names differ|name mismatch|spelling", l):
        return "name matching", "resolved 18 Oct: pairs confirmed on rendered tables where checked; else kept with note"
    return "note", "no action: informational"
out = []
for r in U:
    c, res = classify(r["item"])
    out.append({"paper": r["paper"], "item": r["item"], "category": c, "resolution": res,
                "paper_visually_checked": "yes" if r["paper"] in vis_papers else "no"})
with open("out/uncertain_resolution.csv", "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=list(out[0])); w.writeheader(); w.writerows(out)
from collections import Counter
print(Counter(o["category"] for o in out)); print(Counter(o["resolution"] for o in out if o["category"].startswith("judgment")))
