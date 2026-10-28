# Data section

> **28 ต.ค. 2026:** HTML หลักของ Data section คือ `out/dataset-atlas.html` (สร้างด้วย `python3 build/make_atlas.py`) ไฟล์ `../SMOTE25_Data_Section_Explorer.html` และ `ai-draft/Data_Section_Explorer.html` เป็นรุ่นเก่า เลิกใช้แล้ว

วัสดุทั้งหมดของ **Data section** (ส่วนที่ Toon รับผิดชอบ) ของ survey `25 Years of SMOTE: What Has Been Done and How Did It Benefit Society?`
วารสารเป้าหมาย JAIR · เจ้าของ repo Supawit (P) · อัปเดตล่าสุด 18 ตุลาคม 2026

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
ข้อควรระวัง ผู้ตรวจคือ Claude ไม่ใช่ Toon ซึ่งต่างจากข้อกำหนดข้อ 2 ของอาจารย์ Toon เลือกทางนี้เอง ต้องบอกอาจารย์ได้ว่าใครตรวจ

---

## ข้อกำหนดของอาจารย์ (บังคับ)

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

| ไฟล์ | คืออะไร | เชื่อถือได้แค่ไหน |
|---|---|---|
| `handoff.md` | **เริ่มอ่านที่นี่** สถานะรวม บันทึกการดำเนินงานทุกครั้ง เรื่องที่รอตัดสิน และกติกา | ปัจจุบัน |
| `manuscript/data-section-draft.tex` | ร่าง section พร้อมพรีวิว PDF ตัวเลขตรวจแล้ว ประโยคสีน้ำเงินต้องเขียนใหม่ | ร่าง ตัวเลข verified |
| `manuscript/overview.json` | เนื้อหาแท็บ "ร่าง manuscript" ใน Atlas: คำถาม สิ่งที่ผู้อ่านได้ ข้อค้นพบ และกล่องสังเคราะห์ (Claude ร่าง) | ให้ Toon ตรวจก่อนส่งอาจารย์ |
| `out/dataset-atlas.html` | หน้า SMOTE25 Dataset Atlas 5 แท็บ (แท็บแรกคือร่าง manuscript) สร้างจาก `build/make_atlas.py` + `build/atlas_template.html` + `build/tex2html.py` | ข้อมูล verified |
| `out/full_*.csv/json` | ผลอ่าน PDF ครบ 72 paper รวมด้วย `build/full_extraction.py` | ai_draft มีตารางและหน้า |
| `out/section7_key_map.csv` | คู่คีย์ paper ของเรากับคีย์และ bibkey ของ Section 7 สร้างจาก `build/section7_key_map.py` | จับคู่ครบ 76 เรื่อง |
| `out/verified_*.csv`, `out/visual_checks.json`, `out/uncertain_resolution.csv` | ข้อมูลที่ตรวจกับ PDF แล้ว และบันทึกการตรวจ | ตรวจแล้ว |
| `paper/` | PDF ทั้ง 100 ไฟล์ที่ Toon ดาวน์โหลดจาก Drive | **ห้าม commit** (อยู่ใน `.gitignore` ของโฟลเดอร์นี้) |
| `SMOTE25_data_extraction.xlsx` | ไฟล์ทำงานหลัก วิธีใช้อยู่ในชีต `README` | ชีต `*_verified` ตรวจแล้ว ชีต `extraction` เดิมยังไม่ตรวจ |
| `decisions-pending.md` | 4 เรื่องที่รอตัดสิน (3 เรื่องกับอาจารย์ 1 เรื่องของ Toon) | รอลายเซ็น |
| `section-outline.md` | โครง D1 ถึง D9 แต่ละหัวข้อต้องใช้หลักฐานอะไร และแมปไปหัวข้อใน draft | ร่าง 16 ต.ค. |
| `workplan.md` | แผน 8 เฟส พร้อมเกณฑ์ผ่าน | เป็นข้อเสนอ มีสถานะ 18 ต.ค. ด้านบน |
| `data-handling-corpus.md` | ภาพรวมการเลือกและจัดการข้อมูลทั้ง corpus | ai_draft |
| `mwmote-table5-audit.md` | ตรวจตาราง 5 ของ MWMOTE เทียบแหล่งข้อมูลต้นทาง | ตรวจกับแหล่งต้นทางแล้ว ยังไม่มี page_ref |
| `outcome-pilot.md` | pilot 10 paper ผลรายชุดเทียบ SMOTE | ถูกแทนด้วยรอบอ่านครบ เก็บเป็นร่องรอย |
| `dataset-usage-recon.md`, `dataset-name-topup.md` | รอบสำรวจ 6 ถึง 14 ต.ค. | ตัวเลขเก่า เก็บเป็นร่องรอย |
| `drive-inventory.md` | สารบัญไฟล์ใน Drive ครบ 100 ไฟล์ 76 เรื่อง | ตรวจนับครบแล้ว |
| `build/` | สคริปต์สร้าง workbook วิเคราะห์ และ Atlas | เชื่อถือได้ |
| `ai-draft/` | ผลสกัดด้วย AI เก็บเป็น audit trail | **ห้ามอ้างตัวเลขในตัว paper** |
| `MC-RBO - ... .pdf` | PDF ที่ Toon วางไว้ให้อ่านตารางที่เป็นรูป | **ห้าม commit** |

คำสั่ง regenerate ทั้งหมดอยู่ท้าย `handoff.md`
