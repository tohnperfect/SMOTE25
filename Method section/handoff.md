# Handoff: Method section (SMOTE-family)

ส่วนที่ P (Supawit) รับผิดชอบใน survey `25 Years of SMOTE` ไฟล์นี้สรุปทุกอย่างที่ทำมาแล้ว
สถานะปัจจุบัน และสิ่งที่ต้องทำต่อ ให้คนที่รับช่วงต่อ (หรือแชทใหม่) เริ่มทำงานได้ทันทีโดยไม่ต้องถาม

อัปเดตล่าสุด: **8 พ.ย. 2026**

**ก่อนเริ่มงานทุกครั้ง** ให้ `git fetch` แล้วดูว่าทีมมี commit ใหม่หรือไม่ (Section 7 ของ Tan
และ Data section ของ Toon แก้ไฟล์คนละโฟลเดอร์ แต่ใช้ Method Map และ key ของ bibliography ร่วมกัน)

---

## สถานะโดยสรุป

| รายการ | ตัวเลข / สถานะ |
|---|---|
| Paper ใน corpus (SMOTE25 core corpus) | 76 |
| SMOTE-family (Core 34, Partial 3) | 37 |
| อ่าน PDF ครบทั้ง 37 เรื่อง | ทำแล้ว 28 ต.ค. 2026 (AI reader ภายใต้กติกาเดียวกัน, ยังต้องให้คนสุ่มตรวจ) |
| Binary only / Multiclass only / Binary + Multiclass | 24 / 5 / 8 |
| ขั้นตอนของ SMOTE ที่เปลี่ยน (seed / allocation / partner / placement / filter / pipeline) | 24 / 21 / 22 / 13 / 12 / 8 |
| Paper ที่มีผลเทียบกับ SMOTE รายชุดข้อมูล | 26 (25 รายชุด + KNNOR ค่าเฉลี่ย) |
| ในนั้นต่างจาก SMOTE ไม่เกิน ±0.03 (median) | 19 |
| Systematic search (นำร่องบน OpenAlex) | 14,589 records, เจอ SMOTE-family 36/37 |
| ร่าง paper | v2.3, 26 หน้า, compile ด้วย class ของ JAIR ผ่าน |
| Push ล่าสุด | `ea1eaa8` (29 ต.ค.); งานตั้งแต่ 29 ต.ค. ถึง 8 พ.ย. **ยังไม่ push** |

---

## กติกาที่ตัดสินแล้ว (โดย P)

1. **นิยาม SMOTE-family:** สร้างจุดด้วย `x_new = x_i + λ(x_j − x_i)` หรือกฎที่ขยายจากสมการนี้ 4 แบบ:
   λ แบบอื่น, บริเวณรอบเส้น, extrapolation (λ นอก [0,1]), convex combination ของมากกว่าสองจุด
   การสุ่มรอบจุดเดียวโดยไม่มีคู่ หรือสุ่มจาก distribution ที่ fit/เรียนรู้มา ไม่นับ
2. **ประเภทคลาส** (ดูจากสิ่งที่ paper ทำจริง):
   - Binary only: ทุกการทดลองที่สร้างข้อมูลเป็น 2 คลาส รวม dataset หลายคลาสที่ถูกยุบเหลือ 2 และการขยายที่เขียนไว้แต่ไม่ได้รัน
   - Multiclass only: คงไว้ ≥3 คลาส และไม่เคยรันกับ 2 คลาส
   - Binary + Multiclass: วิธีเดียวกันรันทั้งสองแบบโดยไม่ยุบ
   - ข้อมูลหลายชนิด (ภาพ/ตาราง/อนุกรมเวลา) จัดแยกตามชนิด แล้วรวม
   - **การทดลองใน supplementary นับ** (ตัดสิน 28 ต.ค.)
3. **เหตุผลการเลือก 76 papers** (ตัดสิน 8 พ.ย.): ใช้หลักเดียวกับ Fernández et al. (2018) คือผู้เขียนคัดเลือก
   วิธีที่สำคัญที่สุด (curated expert selection) ต่างกันตรงที่เรากำหนดนิยามว่าวิเคราะห์เป็น "วิธี" เฉพาะ
   37 SMOTE-family ส่วนอีก 39 เรื่องเป็นบริบท (เขียนไว้ในร่างส่วน 3.1 แล้ว)
   - ตรวจแล้ว: Fernández 2018 ไม่มีขั้นตอนการค้นอย่างเป็นระบบเลย มี >85 extensions, Table 1 ~90 วิธี (2004 ถึง 2017),
     จัดด้วย 7 คุณสมบัติ (initial selection, integration with undersampling, type of interpolation,
     dimensionality change, adaptive generation, relabeling, filtering) หน้า 868 ถึง 872
4. **เกณฑ์เลือกวิธีแนะนำ** (ตัดสิน 8 พ.ย.):
   - C1 ผลไม่แย่กว่า SMOTE ในตารางรายชุดข้อมูลของ paper เอง (median Δ ≥ 0)
   - C2 วิธีไม่ซับซ้อน: เปลี่ยน ≤ 2 ขั้นตอน, ไม่รันใน learner, ไม่ใช่ตัวสร้างที่เรียนรู้
   - C3 ไม่ทำให้ข้อมูลเดิมลดลง (ไม่ undersample/clean/ย้ายจุดเดิม) และอยู่ในนิยาม SMOTE-family
   - ผล: ผ่านครบ 3 ข้อ = SMOTE, ADASYN, CGMOS, FW-SMOTE (Binary), SMOM (Multiclass), RSMOTE (Binary + Multiclass)
   - ที่แนะนำในร่าง: Binary = SMOTE เป็นค่าเริ่มต้น (ADASYN / FW-SMOTE / CGMOS ถ้าต้องการ variant),
     Multiclass = SMOM (ทางเลือกง่ายกว่า: one-vs-one + SMOTE), Binary + Multiclass = RSMOTE

## เรื่องที่ยังรอ P ตัดสิน

| เรื่อง | ตอนนี้ใส่เป็น |
|---|---|
| GLOS: การรันปรับพารามิเตอร์บน Sonar (2 คลาส) นับไหม | Multiclass only (ชั่วคราว) |
| Loyalty-SMOTE: ใช้ข้อมูลหลายคลาสแต่เติมแค่คลาสเล็กสุด วัดผลแบบ binary | Binary only (ชั่วคราว) |
| OREM / OREM-M: สองรุ่นทดลองคนละแบบ, OREMBoost ทั้งคู่ | Binary + Multiclass |
| NROMM: Core หรือ Partial (จุด trapped ไม่ใช่ interpolation) | Core |
| ปีของ CISO: Method Map ใส่ 2026, key ของ Section 7 คือ `yadav2025ciso` | 2026 |
| SMOM: ไฟล์ PDF หลักใน Drive จริง ๆ คือ INOS | coded จาก supplement, ต้องอัปโหลดใหม่แล้วตรวจซ้ำ |
| ชื่อ corpus: ร่างเรา "SMOTE25 core corpus", Section 7 "SMOTE25 collection" | ต้องตกลงกับ Tan |
| ข้อความ "ยังไม่มีวิธีไหนเลือก k แบบปรับตามข้อมูล" | ยังไม่ได้ตรวจกับ PDF |
| C3: MWMOTE และ RSMOTE ตัด noise ออกจาก seed แต่ (ตามที่อ่าน) ไม่ลบออกจากข้อมูล | นับว่าไม่ลดข้อมูล |

---

## บันทึกการทำงาน

### 21 ต.ค. 2026: ร่าง Method section v1
ร่าง LaTeX ครั้งแรก (6 จุดตัดสินใจ, ตาราง 37 วิธี) จากฟิลด์ของ Method Map ยังไม่ได้อ่าน PDF

### 28 ต.ค. 2026: generation rule, อ่าน PDF ครบ 37 เรื่อง, หน้าสรุป
- เพิ่ม `class_rule` (Binary rule / One-vs-rest stated / Multiclass rule) และ `mc_strategy` ใน Method Map,
  ตรวจ 6 กรณีก้ำกึ่งกับ PDF (Loyalty-SMOTE เปลี่ยนเป็น Binary rule)
- อ่าน PDF ครบ 37 เรื่องด้วย 19 subagent ตามกติกา `pdf-check/coding_rules.md` ผลอยู่ใน `pdf-check/*.json`
  - จัดประเภทคลาสใหม่ตามกติกาของ P: 24 / 5 / 8
  - คำอธิบายรายวิธีว่าต่อยอดจาก SMOTE อย่างไร พร้อมเลขหน้า
  - แก้ขั้นตอนที่เปลี่ยนจาก SMOTE 21 จาก 36 variants (ค่าเดิมเก็บใน `smote_via_v1`)
- หน้าสรุป `binary-multiclass-summary.html`: 3 ประเภท, Timeline แบบ interactive, paper ที่ใช้ข้อมูลประเภทอื่น
  (INOS อนุกรมเวลา, GAMO ภาพและตาราง, KNNOR ตารางและภาพ จัดแยกตามชนิดข้อมูล)
- ร่าง v2: ทั้งส่วน Method พร้อมช่องว่างให้ทีม Datasets และ Performance Metrics
- push: `92be361`, `339e6cc`

### 29 ต.ค. 2026: หน้า SMOTE Family at 25, ภาพ, systematic search
- หน้า `smote-family-overview.html` (อังกฤษ) 4 หน้าต่าง: Definitions (สมการคลิกได้, corpus, systematic search),
  Counts and roadmap, Keep oversampling? (จุดยืน + หลักฐาน 8 ข้อ), What the reader gets — push `ea1eaa8`
- ร่าง: นิยาม SMOTE-family เป็นสมการใน Intro, generation template Eq. (2), Figure 1 (6 จุดตัดสินใจบนสมการ),
  ส่วน 6.1 ถึง 6.6 แต่ละจุดมีสมการ (Eq. 3 ถึง 8) และภาพของตัวเอง (Fig. 2 ถึง 7)
- Systematic search (ส่วน 3.2): โปรโตคอล (Scopus/WoS/OpenAlex/arXiv + snowballing, เกณฑ์ I1 ถึง I3, E1 ถึง E4,
  PRISMA 2020) และรันนำร่องบน OpenAlex: ชุดคำค้น S5 ได้ 14,589 records, เจอ SMOTE-family 36/37
  (พลาด LS), เจอ corpus 57/75; OpenAlex มี abstract แค่ 17/37 เรื่อง จึง**ต้องรันจริงใน Scopus/WoS**
- ตรวจ Fernández 2018 ว่าเลือก paper อย่างไร (ผลด้านบน)

### 8 พ.ย. 2026: Δ vs SMOTE, วิธีที่แนะนำ, เหตุผลของ corpus
- `build/delta_vs_smote.py`: คำนวณ median Δ (วิธี − SMOTE) จาก `Data section/out/verified_outcomes.csv`
  (คะแนนที่ตรวจกับ PDF แล้ว 18 ต.ค.), สเกล 0 ถึง 1, เทียบ plain SMOTE ถ้ามี ไม่งั้นเทียบ SMOTE ใน wrapper (†)
  ตัดแถว Loyalty-SMOTE ที่ค่าพิมพ์ผิด (9100) ออก 1 แถว ผลอยู่ใน `search/delta_vs_smote.json`
- Table 3 เพิ่มคอลัมน์ "Δ vs SMOTE" เช่น `+.015 (5/5)` = median Δ และจำนวนชุดข้อมูลที่ชนะ
- ส่วนใหม่ "Which SMOTE-Family Method to Use" (ส่วน 10) พร้อม Table 7 วิธีที่ผ่าน C2 และ C3
- ส่วน 3.1 เขียนเหตุผลของการเลือก 76 papers ตามที่ P ตัดสิน
- ร่าง v2.3 (26 หน้า)

---

## ไฟล์ในโฟลเดอร์

| ไฟล์ | คืออะไร |
|---|---|
| `handoff.md` | ไฟล์นี้ **เริ่มอ่านที่นี่** |
| `README.md` | สรุปสั้นและวิธีสร้างใหม่ |
| `manuscript/method-section-draft.tex` | ร่าง paper ส่วน Method (v2.3) |
| `manuscript/generated/` | ตาราง 37 วิธี, Table 7, คำอธิบายรายวิธี **สร้างจาก script ห้ามแก้มือ** |
| `manuscript/figures/` | Figure 1 และ Figure 2 ถึง 7 (PDF) ต้นฉบับ TikZ อยู่ใน `figures/src/` |
| `manuscript/*-preview.pdf` | PDF ตัวอย่าง (ไม่ขึ้น git) |
| `smote-family-overview.html` | หน้า SMOTE Family at 25 (4 หน้าต่าง) |
| `binary-multiclass-summary.html` | หน้าสรุปประเภทคลาสพร้อม Timeline |
| `pdf-check/` | กติกาการอ่าน PDF และผลราย paper |
| `search/` | ผลค้น OpenAlex, การตรวจ abstract, Δ vs SMOTE |
| `build/` | script ทั้งหมด (ดูวิธีรันด้านล่าง) |

## สร้างใหม่ (รันจากระดับบนสุดของ repo)

```bash
python "Method section/build/delta_vs_smote.py"
python "Method section/build/make_tex.py" SMOTE25_Method_Map_1.html "Method section/manuscript/generated"
python "Method section/build/make_summary2.py" SMOTE25_Method_Map_1.html "Method section/binary-multiclass-summary.html" "Method section/build/summary_template2.html"
python "Method section/build/make_overview.py" SMOTE25_Method_Map_1.html "Method section/smote-family-overview.html" "Method section/build/overview_template.html"
python "Method section/build/search_openalex.py"
```

- ภาพ: `pdflatex` ไฟล์ใน `manuscript/figures/src/` แล้วคัดลอก PDF ขึ้นไปที่ `manuscript/figures/`
- `add_class_rule.py`, `merge_pdf_check.py`, `decide_supplement.py` แก้ Method Map ไปแล้ว **ห้ามรันซ้ำ**
- ถ้าแก้ Method Map (เช่นตัดสินเรื่องที่รอ) ให้รัน 4 คำสั่งแรกใหม่ ตัวเลขในตารางและหน้า HTML จะตามข้อมูล
  แต่**ตัวเลขที่พิมพ์ในเนื้อความของร่าง (เช่น 24/5/8, 19 จาก 26) ต้องแก้มือ**

## ข้อควรระวัง

- คำอธิบายรายวิธีและการจัดประเภทมาจาก AI ที่อ่าน PDF: ใน paper ต้องระบุว่าเป็นการสกัดข้อมูลโดยมีเครื่องช่วย
  และให้คนสุ่มตรวจ (เช่น 5 ถึง 8 เรื่อง)
- ประโยคสีน้ำเงิน (`\claudedraft`) เป็นการตีความที่ Claude เขียน **ต้องเขียนใหม่ด้วยคำของ P** (อาจารย์กำหนด)
- Δ vs SMOTE มาจากตารางของผู้เขียนแต่ละ paper เอง คนละ metric คนละ protocol เทียบข้าม paper ไม่ได้
- หน้าต่าง "Keep oversampling?" เป็นจุดยืน ไม่ใช่ข้อค้นพบ หลักฐานสองชิ้นที่หนักที่สุดเป็น preprint

## ขั้นต่อไป

1. ตัดสินเรื่องที่รอ (ตารางด้านบน) แล้วรันสร้างใหม่
2. ทีม: รันชุดคำค้น S5 ใน Scopus และ Web of Science, คัดกรอง, รายงาน PRISMA (ส่วน 3.2)
3. ใส่ bibliography keys ที่ยังเป็น `\pcite` ลง `references.bib` (มี candidates ใน
   `Evaluation section/latex/notes/empirical-bib-candidates.bib` ของ Tan) และสร้าง `wang2012multiclass`
4. ตกลงตำแหน่งของร่างใน `sections/` ของ Overleaf กับทีม (แทน `04-taxonomy.tex` หรือ `\input`)
5. อัปเดตหน้า SMOTE Family at 25 ให้มี Δ vs SMOTE และวิธีที่แนะนำ (ยังไม่ได้ทำ)
