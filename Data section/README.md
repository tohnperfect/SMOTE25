# Data section

> **สถานะ 9 พ.ย. 2026:** งานวิเคราะห์ของ Data section ครบแล้ว · ข้อสรุปทั้งหมดอยู่ที่ `CONCLUSIONS.md` · manuscript: แก้ที่ `manuscript/data-section-draft.tex` → ฉบับพร้อม merge `manuscript/data-section-final.tex` + `.bib` → PDF รูปแบบ JAIR `manuscript/data-section-jair.pdf` · HTML หลัก `out/dataset-atlas.html` (เปิดในเบราว์เซอร์ได้เลย; `build/atlas_template.html` เป็นแค่แม่แบบ เปิดเองไม่ได้)
> ไฟล์สำรองรุ่นเก่า (`*.before_*`, `out/audit_backup/`, `ai-draft/full_backup_*`) ลบแล้ว 9 พ.ย. ดูย้อนหลังได้จาก git history · เอกสารทำงานรุ่นก่อนย้ายไป `_archive/` (ดู `_archive/README.md`)

วัสดุทั้งหมดของ **Data section** (ส่วนที่ Toon รับผิดชอบ) ของ survey `25 Years of SMOTE: What Has Been Done and How Did It Benefit Society?`
วารสารเป้าหมาย JAIR · เจ้าของ repo Supawit (P) · อัปเดตล่าสุด 9 พฤศจิกายน 2026

โฟลเดอร์นี้อยู่ระดับบนสุดของ repo แยกจาก `notes/` ของทีม และไม่ขึ้น Overleaf
**เริ่มอ่านที่ `handoff.md`** ไฟล์นี้เป็นแค่สถานะย่อและแผนที่ไฟล์

---

## section นี้อยู่ตรงไหนของทั้ง paper

| ส่วนของ paper | เจ้าของ | ความเกี่ยวข้องกับ section นี้ |
|---|---|---|
| Section 3 Review Methodology (`sections/03-methodology.tex`) | P | corpus 76 paper มาจากโฟลเดอร์ Drive `SMOTE25` (Survey / Binary / Multiclass / Both) ส่วน 3.3 Study Selection and Data Extraction เป็นที่ของ extraction sheet |
| Section 7 Empirical Comparisons (`section07-empirical-comparisons-draft.html`) | P | **ทับกับเราบางส่วน** หัวข้อ Corpus and Coding Scheme, Benchmark Data (RQ1) และ A Minimum Evaluation Standard รายละเอียดอยู่ในหัวคอมเมนต์ของ `manuscript/data-section-draft.tex` ยังไม่ได้ตกลงกับ P |
| Development brief (`notes/smote25-development-brief.md`) | P | มีมุม "Data angle" ทั้ง 3 part และ Reporting checklist 4 ข้อ ยังไม่ได้เคลียร์ว่าใครเป็นเจ้าของ checklist |
| ตำแหน่งใน `main.tex` | ยังไม่ตัดสิน | เปิดไฟล์ section ใหม่ หรือแทรกใน 02 / 03 / 07 |

**การแบ่งงาน** Toon ดูด้าน **ข้อมูล** คนอื่นดู methodology และ metric (บันทึก 14 ต.ค. ใน handoff)
ช่องใน workbook ที่เป็นเรื่อง metric, classifier, stat test เป็นอาณาเขตของคนอื่น

---

## ตัวเลข corpus ที่ต้องใช้ให้ตรงกัน

| ตัวเลข | ความหมาย |
|---|---|
| **76** | paper ทั้ง corpus ตรงกับ Section 7 ของ P ทุกเรื่อง คู่คีย์และ bibkey อยู่ใน `out/section7_key_map.csv` |
| **73** | paper ที่มีการประเมินผลบนข้อมูล ตัด ENN, AdaBoost, Survey: SMOTE Review (Pradipta 2021) นับ Tomek Links ตามที่ Toon ตัดสิน 18 ต.ค. |
| 71 | ตัวหารของ Section 7 ของ P ต่างจากเรา 2 เรื่อง คือ P ไม่นับ Tomek Links และนับ Hassanat 2022 (Stop Oversampling) เป็น survey |
| 73 | แถวใน evidence map ของ P (`notes/SMOTE25_evidence_map_v1.csv`) นับ Global-CS สองฉบับเป็นเรื่องเดียว และไม่นับ survey 2 เรื่อง |

**เวลาเขียนให้บอกทั้ง corpus และตัวหารเสมอ** ไม่งั้นผู้อ่านจะคิดว่า corpus ไม่ตรงกับ section อื่น

---

## สถานะวันนี้ (ตรวจกับ PDF แล้ว 18 ต.ค. 2026)

| รายการ | ตัวเลข |
|---|---|
| paper ใน corpus / ที่มีการประเมินผลบนข้อมูล | 76 / 73 |
| อ่าน PDF ครบแล้ว | 73 จาก 73 มีตารางและหน้ากำกับทุกค่า |
| dataset entry (`out/verified_datasets.csv`) | 1,654 แถว **ตรวจกับ PDF แล้วทุกแถว** |
| ชื่อ dataset ที่ต่างกันหลัง normalise | 771 (แทน 605 ของรายชื่อ 6 ต.ค.) |
| ผลเทียบวิธีที่เสนอกับ SMOTE รายชุด (`out/verified_outcomes.csv`) | 835 แถว 44 paper **ตรวจกับ PDF แล้วทุกแถว** (plain SMOTE 542 แถว 31 paper: ชนะ 421 เสมอ 39 แพ้ 82 ตามกติกา A) |
| ข้อที่ผู้อ่านไม่มั่นใจ | 454 ข้อ ไล่ครบแล้วใน `out/uncertain_resolution.csv` |
| workbook | ชีตใหม่ `datasets_verified`, `outcomes_verified`, `uncertain_resolution` ชีต `extraction` เดิมยังเป็นรายชื่อ 6 ต.ค. |
| ผู้ตรวจ | Claude ตรวจทุกแถวกับ PDF · Toon ตรวจกับ PDF แล้ว (Toon แจ้ง 28 ต.ค. 2026; ไม่ได้บันทึกค่าที่ตรวจ จึงไม่มีอัตราไม่ตรงกันให้รายงาน) |

**ตัวเลขใน `out/verified_*.csv` ใช้เขียน manuscript ได้แล้ว** (ตรวจรอบสองกับ PDF ในเครื่อง 18 ต.ค. ด้วยสคริปต์ `build/verify_pdf.py` และเปิดภาพหน้าดูเองสำหรับตารางที่เป็นรูป บันทึกใน `out/visual_checks.json`)
ข้อควรระวัง ผู้ตรวจคือ Claude ไม่ใช่ Toon ซึ่งต่างจากหลักการข้อ 2 Toon เลือกทางนี้เอง ต้องบอกได้ว่าใครตรวจ

---

## หลักการทำงาน (บังคับ)

1. ต้องมี insight ของ Toon เอง ไม่ใช่บทสรุปที่เครื่องสร้าง
2. ทุกค่าที่มาจาก AI ต้องเปิด paper ต้นฉบับตรวจเอง
3. เริ่มจาก "สิ่งที่เราสงสัย" แล้วหาหลักฐานมาตอบ ไม่ใช่เริ่มจากตารางสรุป

## กติกาของข้อมูล (ฉบับเต็มอยู่ใน handoff ข้อ 9)

1. ทุกช่องต้องย้อนกลับไปหาหน้าใน paper ได้ แถวที่ไม่มี `page_ref` หรือยัง `ai_draft` ถูกตัดออกจากการวิเคราะห์
2. เขียน `not stated in paper` แทนการเดา สัดส่วนที่ไม่ระบุเป็น finding ในตัวเอง
3. ห้ามตัดข้อมูลออก dataset ชื่อเดียวกันแต่เนื้อในต่างกัน เก็บทุกเวอร์ชันเป็นคนละแถว
4. นิยาม IR ใส่ให้ครบทุกแบบ ติดป้ายว่าค่าไหนมาจากนิยามไหน
5. ชื่อ dataset ลอกตามที่ paper พิมพ์ รวมคำที่พิมพ์ผิด
6. กลุ่มที่ paper สร้างเองโดยไม่ตั้งชื่อ ห้ามแต่งชื่อขึ้นมา
7. paper ที่รายงานแค่ผลรวม เขียนได้แค่ว่า *ข้อสรุปพิสูจน์เท็จไม่ได้จากสิ่งที่ตีพิมพ์* ไม่ใช่ว่าโกงหรือไม่น่าเชื่อถือ
8. ค่าที่ paper พิมพ์อยู่คอลัมน์เดิมเสมอ ค่าที่แก้อยู่คอลัมน์ `_corrected` พร้อม `correction_basis`
9. ตรวจซ้ำแบบ blind 10 ถึง 20 เปอร์เซ็นต์ แล้วบันทึกอัตราที่ไม่ตรงกัน ตัวเลขนี้รายงานได้ใน methodology

## แนวทางการเขียน manuscript

- ทุกย่อหน้าเรียง **finding → evidence → interpretation → ผู้อ่านควรทำอะไร** ตั้งต้นจากคำถามของผู้อ่าน
- บททดสอบ ถ้า AI เขียนย่อหน้านั้นได้โดยไม่ต้องใช้ข้อมูลที่เราเก็บเอง แปลว่ายังไม่ผ่าน
- ประโยค `\claudedraft{}` ใน draft ต้องเขียนใหม่ด้วยเสียงของ Toon ทุกประโยค ช่อง `\toon{}` เป็นของ Toon
- ไม่มี em-dash · สะกดแบบ British ให้ตรงกับ Section 7 ของ P · หัวข้อและ caption เป็น Title Case
- ตารางใช้ booktabs (caption อยู่เหนือตาราง `\midrule` เฉพาะระหว่างหัวตารางกับเนื้อ) ทุกรูปต้องมี `\Description{}`
- อ้างอิงด้วย `\textcite{}` หรือ `\parencite{}` ระหว่างที่ references.bib ยังไม่มี entry ให้ใช้ `\pcite{bibkey}` ตามคีย์ของ Section 7
- ไม่แก้ไฟล์ class หรือสไตล์ใน preamble ของ JAIR

---

## ไฟล์ในโฟลเดอร์

| ไฟล์ | คืออะไร | สถานะ |
|---|---|---|
| `handoff.md` | **เริ่มอ่านที่นี่** สถานะรวม (ข้อ 0) กติกา คำสั่ง rebuild และบันทึกการดำเนินงานทุกรอบ | ปัจจุบัน |
| `CONCLUSIONS.md` | ข้อสรุปและตัวเลขทั้งหมดของ section พร้อมไฟล์ต้นทาง | ปัจจุบัน |
| `manuscript/data-section-draft.tex` | ต้นฉบับที่แก้ (มีหมายเหตุ `\evidence{}` บอกที่มาของตัวเลข) · พรีวิวแบบมีมาร์กอัป `data-section-draft-preview.pdf` | ปัจจุบัน |
| `manuscript/data-section-final.tex`, `.bib`, `data-section-jair.pdf` | ฉบับพร้อม merge (ตัดหมายเหตุภายใน) และ PDF รูปแบบ JAIR (`manuscript/jair/`) | ปัจจุบัน |
| `manuscript/overview.json` | เนื้อหาแท็บ "ร่าง manuscript" ใน Atlas | ปัจจุบัน |
| `manuscript/proposal_dataset_landscape.tex`, `data-section-refs.bib` | ข้อเสนอเดิมของหัวข้อ landscape (ถูกอ้างในหมายเหตุ evidence) และ bib ต้นทางที่ `make_final.py` ใช้ | ใช้อยู่ |
| `out/dataset-atlas.html` | SMOTE25 Dataset Atlas (ข้อความที่แสดงไม่มีชื่อผู้ตัดสิน/ผู้สั่ง: `build/atlas_scrub.py`) สร้างด้วย `build/make_atlas.py` + `build/atlas_template.html` | ปัจจุบัน |
| `out/handoff.html` | handoff.md + CONCLUSIONS.md เป็นหน้า HTML แยก (สารบัญ, ค้นหา; ไม่มีชื่อผู้ตัดสิน/ผู้สั่ง) สร้างด้วย `build/make_handoff_html.py` | 
| `out/` | ข้อมูลที่สกัดและตรวจแล้ว (`verified_*.csv`, `dataset_records.csv`) และผลวิเคราะห์ทุกชุด (`*.json`, `*.csv`) | สร้างจากสคริปต์ |
| `difficulty/` | การตรวจกับไฟล์สาธารณะและวัดความยาก (`verify_ext.py`, `measure.py`, `rebuild_difficulty.sh`); `difficulty/src/` คือ mirror และไฟล์ทางการที่ดาวน์โหลด (ไม่อยู่ใน git, สร้างใหม่ด้วย `fetch_mirrors*.sh` และ `official_manifest.csv`) | ปัจจุบัน |
| `build/` | สคริปต์ทั้งหมด (สกัด ตรวจ วิเคราะห์ manuscript Atlas checks) | ปัจจุบัน |
| `analysis/` | เอกสารวิธีของ Analysis A–F และตารางนิยามหมวด (Atlas ใช้) | ปัจจุบัน |
| `ai-draft/` | ผลอ่าน PDF ราย paper (`full/*.json` เป็นต้นทางของ `build/full_extraction.py`; `outcome/` ผลเทียบ SMOTE) และ `extraction-notes.md` | audit trail ห้ามอ้างตัวเลขจากที่นี่โดยตรง ใช้ `out/verified_*.csv` |
| `blind/` | ชุดสุ่มตรวจซ้ำแบบ blind (`build/blind_check.py`) | ปัจจุบัน |
| `SMOTE25_data_extraction.xlsx` | workbook (ชีต `*_verified` ตรงกับ `out/verified_*.csv` ด้วย `build/sync_workbook_verified.py`) | ปัจจุบัน |
| `decisions-pending.md` | บันทึกคำตัดสินเรื่องนิยาม (ปิดครบแล้ว 29 ต.ค.; `build/hypotheses.py` อ้าง) | ปิดแล้ว |
| `mwmote-table5-audit.md` | ตรวจตาราง 5 ของ MWMOTE เทียบแหล่งต้นทาง (manuscript อ้าง) | ใช้อยู่ |
| `paper/` | PDF ของ paper ทั้งหมด | **ห้าม commit** (อยู่ใน `.gitignore`) |
| `_archive/` | เอกสารทำงานรุ่นก่อน (แผนงาน โครงร่าง รอบสำรวจแรก pilot) เก็บไว้เป็นประวัติ ตัวเลขในนั้นเก่าแล้ว | ประวัติ ไม่ใช่สถานะปัจจุบัน |

คำสั่ง regenerate ทั้งหมดอยู่ท้าย `handoff.md`
