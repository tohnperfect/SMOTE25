"""Remove who-decided / who-asked attributions from the text shown in the Atlas  (9 Nov 2026; requested: the Atlas shows
the content only -- no mention of Toon, and nothing about who decided or asked for what).

Applied by build/make_atlas.py to every string of the embedded data (D) and to the manuscript LaTeX shown in the Atlas.
Source files (handoff.md, out/*.csv, the .tex comments) are NOT changed: the provenance stays there.

Rules, in order (each is a plain text edit; the content of a note is kept, only the attribution is removed):
  - whole notes that only record who decided:            "Added 18 Oct 2026 by Claude after Toon decided to ...",
                                                         "Not reviewed by Toon (yet).", "(Claude 29 ต.ค. (Toon มอบให้ตัดสินแทน))"
  - an attribution inside a parenthesis that has content: "(header row counted, Toon 8 Nov)" -> "(header row counted)"
                                                         "(Toon, 28 Oct 2026; names ...)"   -> "(names ...)"
  - a parenthesis that holds only an attribution:         "(Toon 18 Oct)", "(Toon, 28 Oct 2026)", "(Toon ตัดสิน 28 ต.ค.: ...)" -> removed
  - attribution phrases in running text:                 "approved by Toon 18 Oct" -> "of 18 Oct", "Toon's rules" -> "the rules",
                                                         " by Toon", "ของ Toon", "Toon อนุมัติ(แล้ว)", "ตามที่ Toon ตัดสิน", ...
  - Claude as the writer/decider:                        "(Claude)", "(Claude, delegated)", "(proposed by Claude 19 Oct 2026)",
                                                         "external check 8 Nov (Claude)" -> "external check 8 Nov"
check(text) returns the remaining matches of /toon/i and of Claude so make_atlas.py can stop when a new pattern appears.
"""
import re

M = r"(?:Oct|Nov|ต\.ค\.|พ\.ย\.)"                       # month
DT = rf"\d{{1,2}}(?:/\d{{1,2}})?\s*{M}(?:\s*\d{{4}})?"     # 18 Oct, 28/29 Oct 2026, 8 พ.ย.

RULES = [
    (r"Added 18 Oct 2026 by Claude after Toon decided to count Tomek Links\.\s*", ""),
    (r"\s*Not reviewed by Toon(?: yet)?\.", ""),
    (r"\s*\(Claude[^()]*\(Toon[^()]*\)\)", ""),
    (r"\s*\((?:Claude|proposed by Claude)[^()]*\)", ""),
    (rf"\s*\({DT},\s*Claude;?\)?", ""),                    # "(9 Nov 2026, Claude;" (a cut source string)
    (rf"Toon,?\s+{DT};\s*", ""),                           # "(Toon, 28 Oct 2026; names ..." -> "(names ..."
    (rf",\s*Toon\s+{DT}", ""),                             # "(header row counted, Toon 8 Nov)" -> "(header row counted)"
    (r"\s*\((?:approved\s+)?(?:by\s+)?Toon[^()]*\)", ""),  # "(Toon 18 Oct)", "(Toon ตัดสิน 28 ต.ค.: ...)"
    (rf"^Toon\s+{DT}:\s*", ""),                            # "Toon 28 Oct 2026: main result ..."
    (rf"approved by Toon\s*\({DT}\):\s*", ""),
    (rf"approved by Toon\s+(?={DT})", "of "),
    (r"Toon's rules", "the rules"),
    (r"Toon's decision", "the decision"),
    (r" by Toon\b", ""),
    (rf"คำตัดสินของ Toon(?:\s*{DT})?", "คำตัดสิน"),
    (rf"\s*Toon อนุมัติ(?:แล้ว)?(?:\s*{DT})?", ""),
    (r"ตามที่ Toon ตัดสิน\s*", ""),
    (r"\s*ของ Toon", ""),
]
_C = [(re.compile(a, re.M), b) for a, b in RULES]


def text(s):
    for rx, rep in _C:
        s = rx.sub(rep, s)
    return re.sub(r"\(\s*\)", "", s)


def data(o):
    """Every string value and every key (keys such as "... (header row counted, Toon 8 Nov)" are shown as labels;
    "toon_check" in key names becomes "manual_check")."""
    if isinstance(o, dict):
        return {text(k.replace("toon_check", "manual_check")): data(v) for k, v in o.items()}
    if isinstance(o, list):
        return [data(v) for v in o]
    return text(o) if isinstance(o, str) else o


def tex(src):
    """The manuscript as shown in the Atlas: comment-only lines (working notes) and the two markup macros that refer to
    who writes what (\\claudedraft, \\toon; neither is used in the text) are left out; everything else is unchanged."""
    out = []
    for ln in src.split("\n"):
        if ln.lstrip().startswith("%"):
            continue
        if ln.startswith(("\\providecommand{\\claudedraft}", "\\providecommand{\\toon}")):
            continue
        out.append(ln)
    return text(re.sub(r"\n{3,}", "\n\n", "\n".join(out)))


def check(s):
    return sorted(set(m.group(0) for m in re.finditer(r".{0,40}(?:[Tt][Oo][Oo][Nn]|Claude).{0,40}", s)))


# ---- handoff.md / CONCLUSIONS.md shown in the Atlas Handoff tab (9 Nov 2026: tab kept, names removed) ----
# The log is written around requests and decisions; removing the names leaves Thai clauses without a subject, which reads
# naturally ("Toon รันบน Windows" -> "รันบน Windows"). Order: drop lines that only name a person, phrases with a role
# word, parentheses that only attribute, then the bare names.
MD_RULES = [
    (r"^.*ผู้รับผิดชอบ section นี้: Toon.*\n", ""),
    (r"`?\\toon(?:\{\})?`?", "ช่องเขียนเอง"),                     # LaTeX macro names named after people
    (r"`?\\claudedraft(?:\{\})?`?", "ประโยคร่าง"),
    (r"`Claude outputs/`", "`(โฟลเดอร์ผลงานส่วนตัว)`"),          # folder name, not an attribution
    (r"Claude outputs/", "(โฟลเดอร์ผลงานส่วนตัว)"),
    (r"Claude-Session", "Session"),
    (r"Co-Authored-By: Claude[^\n`]*", "Co-Authored-By: ..."),
    (rf"คำตัดสินของ Toon(?:\s*{DT})?", "คำตัดสิน"),
    (r"(?:ตามที่|ตาม)\s*Toon\s*(?:สั่ง|ขอ|ตัดสิน|อนุมัติ|ยืนยัน|เลือก|ต้องการ|บอก)", ""),
    (r"Toon\s*(?:สั่ง|ขอ)ให้\s*(?:Claude\s*)?", ""),
    (r"(?:ยัง)?ไม่(?:ได้)?ผ่าน(?:การทบทวนของ)?\s*Toon", "ยังไม่ทบทวน"),
    (r"[,;]?\s*Toon\s*ยังไม่(?:ได้)?ทบทวน", ""),
    (r"ที่ Toon\s*", "ที่"),
    (r"ให้ Toon\s*", "ให้"),
    (r"รอ Toon\s*", "รอ"),
    (r"ของ Toon\s*", ""),
    (r"ไม่ใช่ Toon", ""),
    (r"\s*\((?:Claude|Toon)[^()]{0,120}\)", ""),               # (Claude, Toon สั่ง), (Toon แจ้ง), (Toon: "...")
    (r"\s*\([^()]{0,40}\b(?:Claude|Toon)\b[^()]{0,40}\)", ""),
    (r"Toon's\s+", "the "),
    (r"ความรู้ทั่วไปของ Claude\s*", "ความรู้ทั่วไป"),
    (r"โดย Claude\s*", ""),
    (r"(?:ฝั่ง|ทำจาก) Claude", lambda m: m.group(0).replace("Claude", "cloud")),
    (r"`double_checked_by` = Claude", "`double_checked_by` = ผู้ตรวจรอบสอง"),
    (r"\bToon\b[:,]?\s*", ""),
    (r"\bClaude\b(?:'s)?[:,]?\s*", ""),
    (r"(\S) +\*\*(?=[\s)·,:.]|$)", r"\1**"),              # "**คำตัดสิน **" -> "**คำตัดสิน**"
]
_MDC = [(re.compile(a, re.M), b) for a, b in MD_RULES]


def md(s):
    s = text(s)
    for rx, rep in _MDC:
        s = rx.sub(rep, s)
    return re.sub(r"\(\s*\)", "", s)
