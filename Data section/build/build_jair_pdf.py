"""Compile the Data section with the JAIR template (8 Nov 2026, Claude).

Reads   manuscript/jair/data-section-jair.tex (wrapper with main.tex's JAIR preamble),
        manuscript/data-section-final.tex, manuscript/data-section-final.bib, manuscript/figures/*
        jair.cls, acmart.cls, acmauthoryear.{bbx,cbx}, acmdatamodel.dbx from the repo root (read only)
Writes  manuscript/data-section-jair.pdf
Needs   pdflatex, biber, biblatex, libertine, newtx, inconsolata (TeX Live: texlive-fonts-extra, texlive-bibtex-extra, biber)
Stops   on any undefined citation or reference, or any LaTeX error.
Run from Data section/:  python3 build/build_jair_pdf.py
"""
import os, re, shutil, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(HERE)
JDIR = os.path.join(HERE, "manuscript", "jair")
env = dict(os.environ, TEXINPUTS=f".:{REPO}:", BIBINPUTS=f".:{os.path.join(HERE, 'manuscript')}:", BSTINPUTS=f".:{REPO}:")
# biber looks for the datamodel and the .bbx/.cbx through kpathsea as well
env["BIBINPUTS"] += f"{REPO}:"

def run(cmd):
    r = subprocess.run(cmd, cwd=JDIR, env=env, capture_output=True, text=True, errors="replace")
    return r.returncode, r.stdout + r.stderr

for step in (["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "data-section-jair.tex"],
             ["biber", "data-section-jair"],
             ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "data-section-jair.tex"],
             ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "data-section-jair.tex"]):
    rc, out = run(step)
    if rc != 0:
        print(out[-3000:]); sys.exit(f"STOP: {' '.join(step)} failed")
log = open(os.path.join(JDIR, "data-section-jair.log"), encoding="latin-1").read()
undef = re.findall(r"(Citation|Reference) [`']([^']+)' .*undefined", log)
if undef:
    sys.exit(f"STOP: undefined {undef}")
pages = re.search(r"Output written on .*?\((\d+) pages", log)
over = len(re.findall(r"Overfull \\hbox", log))
shutil.copy(os.path.join(JDIR, "data-section-jair.pdf"), os.path.join(HERE, "manuscript", "data-section-jair.pdf"))
print("ok", pages.group(1) if pages else "?", "pages; overfull hboxes:", over, "-> manuscript/data-section-jair.pdf")
