"""สร้างพรีวิว PDF ของ Data section จากไฟล์ใน repo เท่านั้น (เพิ่ม 19 ต.ค. 2026)

อ่าน   build/preview/preview.tex (wrapper) และ manuscript/data-section-draft.tex (หาเจอผ่าน TEXINPUTS)
เขียน  manuscript/data-section-draft-preview.pdf
ไฟล์ชั่วคราว (.aux .log) อยู่ในโฟลเดอร์ temp ของระบบ ลบทิ้งเมื่อจบ ไม่เหลือใน repo

ต้องมี  pdflatex (TeX Live หรือ MiKTeX) พร้อมแพ็กเกจ geometry, xcolor, booktabs, amsmath
วิธีรัน (จาก Data section/)
    python3 build/preview/build_preview.py            คอมไพล์สองรอบ แล้วคัดลอก PDF ไปที่ manuscript/
    python3 build/preview/build_preview.py --check    คอมไพล์อย่างเดียว ไม่เขียนทับ PDF ใน manuscript/
ผลที่คาด  "ok: N pages" และสรุป warning (Overfull/Underfull จาก \\pcite placeholder และกล่อง evidence เป็นของเดิม)
ถ้ามี error หรือ undefined reference สคริปต์จะหยุดและไม่เขียนทับ PDF เดิม
"""
import argparse, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # Data section/
WRAPPER = os.path.join(HERE, "build", "preview", "preview.tex")
OUTPDF = os.path.join(HERE, "manuscript", "data-section-draft-preview.pdf")

def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    if not shutil.which("pdflatex"):
        print("STOP: pdflatex not found on PATH"); return 2
    env = dict(os.environ)
    env["TEXINPUTS"] = os.pathsep.join([os.path.join(HERE, "manuscript"), os.path.join(HERE, "build", "preview"), ""])
    with tempfile.TemporaryDirectory() as tmp:
        for i in (1, 2):  # second pass resolves \ref
            r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory", tmp, WRAPPER],
                               cwd=HERE, env=env, capture_output=True, text=True, errors="replace")
            if r.returncode:
                print(f"STOP: pdflatex failed on pass {i}"); print(r.stdout[-3000:]); return 1
        log = open(os.path.join(tmp, "preview.log"), encoding="latin-1").read()
        undef = re.findall(r"(?:Reference|Citation) `[^']+' on page \d+ undefined", log)
        rerun = "Rerun to get cross-references right" in log
        pages = re.search(r"Output written on .*?\((\d+) pages?", log.replace("\n", ""), re.S)
        print(f"ok: {pages.group(1) if pages else '?'} pages; overfull {log.count('Overfull')}; underfull {log.count('Underfull')}; "
              f"undefined refs {len(undef)}; rerun needed {rerun}")
        if undef or rerun:
            print("STOP: unresolved references", undef[:5]); return 1
        if a.check: return 0
        shutil.copyfile(os.path.join(tmp, "preview.pdf"), OUTPDF)
        print("wrote", os.path.relpath(OUTPDF, HERE))
    return 0

if __name__ == "__main__":
    sys.exit(main())
