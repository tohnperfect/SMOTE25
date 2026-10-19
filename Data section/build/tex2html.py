"""แปลง manuscript/data-section-draft.tex เป็น HTML ให้หน้า Atlas แสดงได้ (ใช้ pandoc)
macro ของร่างถูกแทนด้วย token ก่อนเข้า pandoc แล้วเปลี่ยนเป็น HTML ทีหลัง:
  \\claudedraft{} -> <span class="cd">  (ประโยคตีความที่ Claude เขียน ต้องเขียนใหม่ด้วยเสียงของ Toon)
  \\toon{}        -> <div class="toonbox">  (ช่องที่ Toon ต้องเขียนเอง)
  \\evidence{}    -> <div class="evid">  (ที่มาของตัวเลข)
  \\pcite{key}    -> <span class="cite">[key]</span>
  \\draftnum{}    -> <span class="dn">  (ตัวเลขที่ยังไม่ตรวจ)
"""
import re, subprocess, sys, os
def arg(s, i):
    """s[i] == '{' ; return (content, index after closing brace)"""
    d = 0
    for j in range(i, len(s)):
        if s[j] == "{": d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0: return s[i + 1:j], j + 1
    raise ValueError("unbalanced")
MAC = {"claudedraft": ("ZZCDS", "ZZCDE"), "toon": ("\n\nZZTOS ", " ZZTOE\n\n"), "evidence": ("\n\nZZEVS ", " ZZEVE\n\n"), "draftnum": ("ZZDNS", "ZZDNE")}
def sub_macros(s):
    out, i = [], 0
    pat = re.compile(r"\\(claudedraft|toon|evidence|draftnum|pcite)\{")
    while True:
        m = pat.search(s, i)
        if not m: out.append(s[i:]); break
        out.append(s[i:m.start()]); body, j = arg(s, m.end() - 1)
        if m.group(1) == "pcite": out.append("ZZCIS" + re.sub(r"[^A-Za-z0-9:\- ]", "", body) + "ZZCIE")
        else:
            a, b = MAC[m.group(1)]; out.append(a + sub_macros(body) + b)
        i = j
    return "".join(out)
def convert(tex):
    body = tex[tex.index("\\section{"):]
    body = re.sub(r"(?m)^%.*\n", "", body)
    body = body.replace("\\addlinespace", "\\midrule")
    body = re.sub(r"\\multicolumn\{2\}\{l\}\{(.*?)\}\\\\", r"\1 & \\\\", body)
    body = sub_macros(body)
    body = body.replace("\\textsc", "")
    html = subprocess.run(["pandoc", "-f", "latex", "-t", "html5", "--mathjax"], input=body, capture_output=True, text=True).stdout
    for a, b in [("ZZCDS", '<span class="cd">'), ("ZZCDE", "</span>"), ("ZZDNS", '<span class="dn">'), ("ZZDNE", "</span>"),
                 ("ZZCIS", '<span class="cite">['), ("ZZCIE", "]</span>")]:
        html = html.replace(a, b)
    html = re.sub(r"<p>\s*ZZTOS\s*", '<div class="toonbox"><b>[ช่องของ Toon]</b> ', html); html = re.sub(r"\s*ZZTOE\s*</p>", "</div>", html)
    html = re.sub(r"<p>\s*ZZEVS\s*", '<div class="evid"><b>Evidence:</b> ', html); html = re.sub(r"\s*ZZEVE\s*</p>", "</div>", html)
    html = html.replace("ZZTOS", '<b>[ช่องของ Toon]</b> ').replace("ZZTOE", "").replace("ZZEVS", "<b>Evidence:</b> ").replace("ZZEVE", "")
    # เลขตาราง: แทน [tab:x] ด้วยลำดับตาราง
    labels = re.findall(r'<div id="(tab:[^"]+)"', html)
    for n, lab in enumerate(labels, 1):
        html = re.sub(r'(<a href="#' + re.escape(lab) + r'"[^>]*>)\[?' + re.escape(lab) + r'\]?(</a>)', r"\g<1>" + str(n) + r"\2", html)
        html = html.replace('<div id="' + lab + '">', '<div id="' + lab + '" class="tabwrap"><div class="tabno">Table ' + str(n) + '</div>', 1)
    return html
if __name__ == "__main__":
    tex = open(sys.argv[1], encoding="utf-8").read(); print(convert(tex))
