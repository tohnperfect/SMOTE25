"""Small Markdown -> HTML converter for handoff.md (8 Nov 2026, Claude; Toon asked for the whole handoff inside the Atlas).

Covers what handoff.md uses: ATX headings, paragraphs, bullet and numbered lists (nested by indent), pipe tables,
blockquotes, fenced code, horizontal rules, **bold**, `code`, ~~strike~~ and [text](url). No external dependency, so
build/make_atlas.py runs on any machine. Headings get stable ids (h-<n>) for the table of contents.
"""
import html, re

def _inline(t):
    t = html.escape(t, quote=False)
    t = re.sub(r"`([^`]+)`", lambda m: "<code>" + m.group(1) + "</code>", t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    t = re.sub(r"~~(.+?)~~", r"<s>\1</s>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    return t

def convert(md):
    lines = md.replace("\r\n", "\n").split("\n")
    out, toc, i, hid = [], [], 0, 0
    def is_table(k):
        return k + 1 < len(lines) and lines[k].strip().startswith("|") and re.match(r"^\s*\|?\s*:?-{2,}", lines[k + 1] or "")
    while i < len(lines):
        ln = lines[i]
        s = ln.strip()
        if not s:
            i += 1; continue
        if s.startswith("```"):
            j = i + 1; buf = []
            while j < len(lines) and not lines[j].strip().startswith("```"):
                buf.append(lines[j]); j += 1
            out.append("<pre><code>" + html.escape("\n".join(buf)) + "</code></pre>"); i = j + 1; continue
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1)); hid += 1; txt = m.group(2).strip()
            toc.append((lvl, f"h-{hid}", re.sub(r"[`*]", "", txt)))
            out.append(f'<h{lvl} id="h-{hid}">{_inline(txt)}</h{lvl}>'); i += 1; continue
        if re.match(r"^(-{3,}|\*{3,})$", s):
            out.append("<hr>"); i += 1; continue
        if is_table(i):
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")]); i += 1
            head, body = rows[0], rows[2:]
            t = "<div class=\"tbox\"><table><thead><tr>" + "".join(f"<th>{_inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
            t += "".join("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>" for r in body) + "</tbody></table></div>"
            out.append(t); continue
        if s.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                buf.append(lines[i].strip()[1:].lstrip()); i += 1
            out.append("<blockquote>" + convert("\n".join(buf))[0] + "</blockquote>"); continue
        if re.match(r"^(\s*)([-*]|\d+\.)\s+", ln):
            # list block (nested by indentation)
            stack, html_ = [], []
            while i < len(lines) and (re.match(r"^(\s*)([-*]|\d+\.)\s+", lines[i]) or (lines[i].startswith("  ") and lines[i].strip() and stack)):
                mm = re.match(r"^(\s*)([-*]|\d+\.)\s+(.*)$", lines[i])
                if not mm:   # continuation line of the previous item
                    html_[-1] = html_[-1][:-5] + " " + _inline(lines[i].strip()) + "</li>"; i += 1; continue
                ind, mark, txt = len(mm.group(1)), mm.group(2), mm.group(3)
                tag = "ol" if mark[0].isdigit() else "ul"
                while stack and ind < stack[-1][0]:
                    html_.append(f"</{stack.pop()[1]}>")
                if not stack or ind > stack[-1][0]:
                    stack.append((ind, tag)); html_.append(f"<{tag}>")
                html_.append(f"<li>{_inline(txt)}</li>"); i += 1
            while stack: html_.append(f"</{stack.pop()[1]}>")
            out.append("".join(html_)); continue
        buf = []
        while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,6}\s|```|>|\||(\s*)([-*]|\d+\.)\s)", lines[i].strip()):
            buf.append(lines[i].strip()); i += 1
        if not buf:
            buf = [s]; i += 1
        out.append("<p>" + "<br>".join(_inline(b) for b in buf) + "</p>")
    return "\n".join(out), toc
