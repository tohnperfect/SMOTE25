"""Handoff as its own HTML page: out/handoff.html  (9 Nov 2026; requested: the handoff in a separate file, not a tab of the Atlas).

Reads  handoff.md, CONCLUSIONS.md (converted with build/md2html.py; text shown through build/atlas_scrub.md(), so the page
       carries no names of who asked or decided -- the .md files themselves are unchanged)
Writes out/handoff.html  (one self-contained page: switch between handoff.md and CONCLUSIONS.md, table of contents, search)
       --body PATH  also writes the page without the <!doctype>/<html>/<head>/<body> wrapper (for publishing as an artifact)
Run from Data section/:  python3 build/make_handoff_html.py
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); os.chdir(HERE)
sys.path.insert(0, os.path.join(HERE, "build"))
import md2html, atlas_scrub

HO = atlas_scrub.md(open("handoff.md", encoding="utf-8").read())
CO = atlas_scrub.md(open("CONCLUSIONS.md", encoding="utf-8").read())
ho_html, ho_toc = md2html.convert(HO)
co_html, _ = md2html.convert(CO)
date = re.search(r"## 0\. สถานะปัจจุบัน \(([^)]+)\)", HO)
DATA = dict(handoff=dict(html=ho_html, toc=ho_toc, lines=HO.count("\n") + 1), conc=dict(html=co_html),
            updated=date.group(1) if date else "")

BODY = r"""<title>SMOTE25 Data Handoff</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anuphan:wght@500;600;700&family=IBM+Plex+Sans+Thai:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
/* Layout: working log beside its own table of contents; same palette and faces as the Dataset Atlas. */
:root{
  --bg:#f5f7f6; --panel:#ffffff; --ink:#18221f; --ink2:#4a5753; --ink3:#7b8783;
  --line:#dbe2df; --accent:#1f6f62; --accent-soft:#e2efec; --warn-soft:#fbefdc;
  --f-display:"Anuphan","IBM Plex Sans Thai",system-ui,sans-serif;
  --f-body:"IBM Plex Sans Thai",system-ui,-apple-system,"Segoe UI",sans-serif;
  --f-mono:"IBM Plex Mono",ui-monospace,Menlo,Consolas,monospace;
}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){
  --bg:#111816; --panel:#18211e; --ink:#e3ebe8; --ink2:#a9b6b2; --ink3:#7a8884;
  --line:#2a3633; --accent:#5fc0ad; --accent-soft:#1d3430; --warn-soft:#3a2c17; color-scheme:dark}}
:root[data-theme="dark"]{
  --bg:#111816; --panel:#18211e; --ink:#e3ebe8; --ink2:#a9b6b2; --ink3:#7a8884;
  --line:#2a3633; --accent:#5fc0ad; --accent-soft:#1d3430; --warn-soft:#3a2c17; color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--f-body);font-size:15px;line-height:1.6}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--panel)}
.wrap{max-width:1180px;margin:0 auto;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
header{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--panel);border-bottom:1px solid var(--line)}
header .wrap{display:flex;flex-wrap:wrap;align-items:center;gap:10px 20px;padding-block:12px}
h1{font-family:var(--f-display);font-size:20px;font-weight:700;margin:0;text-wrap:balance}
h1 small{font-family:var(--f-mono);font-size:12px;font-weight:400;color:var(--ink3);margin-left:8px}
.seg{display:flex;gap:4px}
.seg button{font:500 14px var(--f-body);color:var(--ink2);background:none;border:1px solid transparent;border-radius:6px;padding:6px 12px;cursor:pointer}
.seg button[aria-pressed="true"]{color:var(--accent);background:var(--accent-soft)}
.find{display:flex;gap:8px;align-items:center;margin-left:auto;min-width:0}
input[type=search]{font:14px var(--f-body);color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:6px;padding:7px 10px;width:min(300px,100%);min-width:0}
.count{font-family:var(--f-mono);font-size:12px;color:var(--ink3);white-space:nowrap}
button:focus-visible,input:focus-visible,a:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
main{display:grid;grid-template-columns:250px minmax(0,1fr);gap:20px;align-items:start;padding-block:20px 48px}
@media (max-width:820px){main{grid-template-columns:minmax(0,1fr)} .find{margin-left:0;width:100%} input[type=search]{width:100%}}
nav.toc{position:sticky;top:calc(env(safe-area-inset-top,0px) + 76px);max-height:calc(100vh - 100px);overflow:auto;font-size:13px;border:1px solid var(--line);border-radius:8px;background:var(--panel);padding:10px 12px}
@media (max-width:820px){nav.toc{position:static;max-height:240px}}
nav.toc a{display:block;color:var(--ink2);text-decoration:none;padding:2px 0;overflow-wrap:anywhere}
nav.toc a:hover{color:var(--accent)} nav.toc .l3{padding-left:12px;font-size:12px;color:var(--ink3)}
.doc{min-width:0;overflow-wrap:anywhere;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:8px 22px 24px}
.doc h1,.doc h2{font-family:var(--f-display);font-size:19px;margin:24px 0 8px;padding-top:12px;border-top:1px solid var(--line);text-wrap:balance}
.doc h3{font-family:var(--f-display);font-size:15.5px;margin:18px 0 6px;color:var(--accent);text-wrap:balance}
.doc p,.doc li{font-size:14px;max-width:80ch}
.doc blockquote{margin:8px 0;padding:6px 12px;border-left:3px solid var(--accent);background:var(--accent-soft);border-radius:0 6px 6px 0}
.doc pre{background:var(--bg);border:1px solid var(--line);border-radius:6px;padding:10px;overflow:auto;font-size:12.5px}
.doc code{font-family:var(--f-mono);font-size:12.5px;background:var(--bg);padding:0 3px;border-radius:3px}
.doc .tbl{overflow-x:auto}
.doc table{border-collapse:collapse;font-size:13px;margin:8px 0}
.doc th,.doc td{border:1px solid var(--line);padding:4px 8px;text-align:left;vertical-align:top}
.doc th{background:var(--bg);font-weight:600}
.doc mark{background:var(--warn-soft);color:var(--ink)}
.hide{display:none}
footer{font-size:12.5px;color:var(--ink3);padding-block:0 32px}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
</style>
<header><div class="wrap">
  <h1>SMOTE25 Data Handoff <small id="upd"></small></h1>
  <div class="seg" role="group" aria-label="เลือกเอกสาร">
    <button type="button" id="b-handoff" aria-pressed="true">handoff.md</button>
    <button type="button" id="b-conc" aria-pressed="false">CONCLUSIONS.md</button>
  </div>
  <div class="find"><input type="search" id="q" placeholder="ค้นในเอกสาร (เช่น verify_ext, synthetic, Kaggle)" aria-label="ค้นในเอกสาร"><span class="count" id="n"></span></div>
</div></header>
<main class="wrap">
  <nav class="toc" id="toc" aria-label="สารบัญ"></nav>
  <article class="doc" id="doc"></article>
</main>
<footer class="wrap" id="src"></footer>
<script>
const D = __DATA__;
const $ = s => document.querySelector(s);
const esc = s => String(s).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let cur = "handoff";
function render(){
  const d = D[cur];
  $("#doc").innerHTML = d.html;
  $("#doc").querySelectorAll("table").forEach(t => { const w = document.createElement("div"); w.className = "tbl"; t.replaceWith(w); w.appendChild(t); });
  if (d.toc) $("#toc").innerHTML = d.toc.filter(t => t[0] <= 3).map(t => `<a href="#${t[1]}" class="l${t[0]}">${esc(t[2])}</a>`).join("");
  else $("#toc").innerHTML = [...$("#doc").querySelectorAll("h1,h2,h3")].map((h,i) => { h.id = "c-"+i; return `<a href="#c-${i}" class="l${h.tagName[1]}">${esc(h.textContent)}</a>`; }).join("");
  $("#q").value = ""; $("#n").textContent = "";
}
$("#toc").addEventListener("click", e => { const a = e.target.closest("a"); if (!a) return; e.preventDefault();
  const el = document.getElementById(a.getAttribute("href").slice(1)); if (el) el.scrollIntoView({block:"start"}); });
["handoff","conc"].forEach(k => $("#b-"+k).addEventListener("click", () => { cur = k;
  ["handoff","conc"].forEach(x => $("#b-"+x).setAttribute("aria-pressed", x === k)); render(); }));
$("#q").addEventListener("input", e => {
  const q = e.target.value.trim().toLowerCase(); const blocks = [...$("#doc").children];
  if (!q) { blocks.forEach(b => b.classList.remove("hide")); $("#n").textContent = ""; return; }
  let n = 0, lastH = null;
  blocks.forEach(b => { const hit = b.textContent.toLowerCase().includes(q); const isH = /^H[1-6]$/.test(b.tagName);
    if (isH) { lastH = b; b.classList.add("hide"); }
    if (hit) { n++; b.classList.remove("hide"); if (lastH) lastH.classList.remove("hide"); } else if (!isH) b.classList.add("hide"); });
  $("#n").textContent = n + " ช่วงที่พบ";
});
$("#upd").textContent = D.updated ? "สถานะ " + D.updated : "";
$("#src").textContent = `ที่มา: handoff.md (${D.handoff.lines.toLocaleString()} บรรทัด) และ CONCLUSIONS.md ในโฟลเดอร์ Data section · สร้างด้วย build/make_handoff_html.py`;
render();
</script>
"""

page_body = BODY.replace("__DATA__", json.dumps(DATA, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"))
left = atlas_scrub.check(page_body)
if left:
    sys.exit("STOP: names left in the handoff page (add a rule to build/atlas_scrub.py): " + " | ".join(left[:10]))
full = ('<!doctype html>\n<html lang="th">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + page_body.replace("<header>", "</head>\n<body>\n<header>", 1) + "</body>\n</html>\n")
open("out/handoff.html", "w", encoding="utf-8").write(full)
if "--body" in sys.argv:
    open(sys.argv[sys.argv.index("--body") + 1], "w", encoding="utf-8").write(page_body)
print("out/handoff.html", len(full), "bytes; handoff", DATA["handoff"]["lines"], "lines;", len(ho_toc), "headings")
