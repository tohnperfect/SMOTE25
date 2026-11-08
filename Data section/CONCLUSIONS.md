# ข้อสรุปทั้งหมดของ Data section (SMOTE25)

ฉบับ 29 ต.ค. 2026 · Claude เขียนตามที่ Toon มอบหมาย ("อะไรที่ต้องตัดสินใจ ตัดสินใจเลย") · ตัวเลขทุกตัวในไฟล์นี้มาจากไฟล์ใน `out/` และ `difficulty/` ที่ระบุไว้ท้ายแต่ละหัวข้อ และตรงกับ `manuscript/data-section-draft.tex` (ตรวจด้วย `build/consistency_check.py`)

---

## 0. สิ่งที่ Claude ตัดสินแทนคืนนี้ (Toon ควรอ่านส่วนนี้ก่อน)

| เรื่อง | ตัดสินว่า | ถ้าไม่เห็นด้วย แก้ที่ |
|---|---|---|
| นิยาม win/loss | ใช้นิยามที่ Toon ตัดสิน 28 ต.ค.: ทุก metric ที่ paper รายงานคู่กับ SMOTE, classifier/เงื่อนไขตามกติกา A, เทียบค่าที่พิมพ์, เท่ากัน = เสมอ · กติกา A (metric เดียว) เหลือเป็นการตรวจความทนทาน | `build/winloss_allmetric.py` |
| ป้ายตัวเทียบใน all-metric | **แก้ความไม่สอดคล้อง**: เมื่อวาน all-metric ติดป้าย GAMO, MC-CCR, MC-RBO, NROMM, RBBoost, KNNOR เป็น plain SMOTE แต่ชุดกติกา A (ตรวจ 18–19 ต.ค.) จัดเป็น SMOTE แบบห่อ / ค่าเฉลี่ย / ข้ามตาราง · ใช้การจัดของกติกา A ทั้งสองชุด → plain 29 paper (เดิม 35) | `COMPARATOR_GROUP`, `EXCLUDED` ใน `build/winloss_allmetric.py` |
| ป้าย KEEL 2 คลาส (decisions-pending 2) | คง `repository-defined` แยก (ทางเลือก 3 ที่ Toon ใช้อยู่) | `keel_rule()` ใน `build/full_extraction.py` |
| H3 / granularity (decisions-pending 3) | ใช้ 6 ระดับ และวัด H3 เป็นสัดส่วน entry ที่ลิสต์แต่ไม่มีคู่ค่ากับ SMOTE | `build/hypotheses.py` |
| วิธีทดสอบ H1 | ตาม handoff: paper เป็น cluster · GEE (หลัก), conditional logit ภายใน paper, Bayesian mixed model (paper + dataset), Fisher เป็นค่าอ้างอิงหยาบ · α = 0.05 สองทาง (มาตรฐาน) | `build/hypotheses.py` |
| H2 | นิยาม: paper ที่มีชุดมาตรฐาน 1 ชุดพอดี + ชุดอื่น ≥ 1 · เข้าเกณฑ์ 2 paper จึงรายงานราย paper ไม่ทดสอบ | `build/hypotheses.py` |
| ประโยคสีน้ำเงิน 9 จุด + ช่อง [Toon] 4 ช่อง | เขียนเป็นข้อความฉบับสุดท้ายทั้งหมด ทุกจุดมีคอมเมนต์ `% Claude 29 Oct 2026 (Toon delegated all open decisions)` ให้ค้นได้ | `manuscript/data-section-draft.tex` |
| ชุด dataset อ้างอิง (ข้อ 15) | ใส่ใน manuscript (ตาราง `tab:data-reference`) คง 27 task ไม่ตัดตระกูลซ้ำ แต่เขียนเตือนให้รวมตามแหล่งเวลาทดสอบ | `difficulty/reference_collection.py` |
| สิ่งที่ไม่ได้ทำ | ไม่ merge เข้า main.tex / sections / references.bib (กติกา: แก้เฉพาะ Data section) แต่ทำฉบับพร้อม merge และคอมไพล์กับ template จริงผ่านแล้ว · ไม่ push | ดูหัวข้อ 11 |

---

## 1. ขอบเขตของข้อมูลที่สกัด

- corpus 76 paper ใช้ 73 paper ที่มีการประเมินผลบนข้อมูล (ตัด ENN, AdaBoost, review ของ Pradipta; นับ Tomek Links ตามที่ Toon ตัดสิน) · Section 7 ของ P นับ 71
- dataset entry 1,654 รายการ (มีชื่อ 1,653) ทุกค่ามีตาราง/หน้า และตรวจกับ PDF รอบสองครบ (Toon ตรวจด้วย 28 ต.ค.)
- ผลเทียบกับ SMOTE: กติกา A (metric เดียวต่อ paper) 835 แถว · ทุก metric 2,497 แถว (dataset × metric) จาก 44 paper · ค่าของ metric เดิมลอกซ้ำอิสระตรงกัน 839/839 แถว; metric อื่นอ่านครั้งเดียว
- แหล่ง: `out/verified_datasets.csv`, `out/verified_outcomes.csv`, `out/winloss_allmetric_rows.csv`, `out/winloss_allmetric_crosscheck.csv`

## 2. ภูมิทัศน์ของ benchmark: จำนวนชุดไม่เท่ากับจำนวนแหล่ง

- 1,653 entry → 771 ชื่อ → 680 dataset (กฎ T1 ข้อ 1) → 459 source family (T1 ข้อ 2–3)
- 463/680 dataset ใช้ใน paper เดียว · ครึ่งของการใช้ทั้งหมดตกอยู่ที่ 37 family
- นับเป็น dataset: ecoli 29, yeast 22, glass 19 paper · นับรวม split: ecoli 42, yeast 39, glass 35 จาก 73 paper
- split จากแหล่งเดียวกันเปลี่ยน task (yeast 14 ชุด IR 2.5–41.4, noise 0.29–0.86) แต่ไม่เปลี่ยน domain/feature (yeast 7–8 feature) และอาจใช้ minority ชุดเดียวกัน (yeast4 กับ yeast-0-5-6-7-9_vs_4 ใช้ minority 51 ตัวเดียวกัน)
- ผลบน split ของแหล่งเดียวกันไม่อิสระ: 11 paper, 282 แถว, 262 คู่ · ชนะ/แพ้ไม่กระจุก (0.60 เท่าสุ่ม) แต่ขนาดของความได้เปรียบใกล้กันกว่า (ระยะอันดับ 0.29 vs 0.34, p = 0.005; ตัดทีละ paper p 0.002–0.048)
- ตารางผู้สมัคร benchmark 18 dataset กลุ่ม F/D/V (Toon อนุมัติ 28 ต.ค.)
- แหล่ง: `out/reconcile_counts.json`, `out/dataset_families.csv`, `out/benchmark_concentration.json`, `difficulty/family_spread.json`, `out/family_dependence.json`, `out/benchmark_candidates.json`

## 3. การเลือกและดัดแปลงข้อมูล

- entry: original 534, repository-defined 470, modified 331, synthetic 120, บอกไม่ได้ 199
- เหตุผลการเลือก (paper): ให้เหตุผลเอง 48, อ้างงานก่อน 14, "widely used" อย่างเดียว 3, ไม่บอก 8 · ยกรายชื่อ benchmark จากงานก่อน 20 paper (ยกทั้งชุด 11)
- modified 331 entry 39 paper: เปลี่ยนโครงสร้างคลาส 177 (30 paper; one-vs-rest 84) · เพิ่ม IR โดยตั้งใจ 147 (9 paper; 131 entry เป็นคู่ undersampling + เพิ่ม IR คือสุ่มลด minority ตาม Analysis A) · บอกเหตุผลการดัดแปลง 15/39 paper
- **ประกาศ/ไม่ประกาศ**: 93/331 entry ขาดข้อมูลที่ต้องใช้ทำซ้ำ (ไม่พิมพ์ลักษณะชุดที่ได้ 55, ไม่บอก IR เป้าหมาย 18, ไม่บอก minority 15) · 8/37 paper ที่ binarize ไม่บอกว่าคลาสไหนเป็น minority · 28 entry ที่ดัดแปลงโดยไม่พิมพ์ลักษณะ จับคู่กับไฟล์สาธารณะไม่ได้
- แหล่ง: `out/data_handling_summary.json`, `out/modified_operations_summary.json`, `analysis/A_modified_operations.md`

## 4. ชื่อเดียวกันไม่ใช่ข้อมูลเดียวกัน

- 192 dataset ที่พิมพ์ขนาดใน ≥ 2 paper: 90 มีมากกว่าหนึ่งขนาด (thyroid 7,200/720; dermatology 358/366; ecoli 336/327/310/301; pima 768/769/635/590)
- นิยาม IR ที่พิมพ์จริงอย่างน้อย 9 แบบ บางแบบแปลงหากันไม่ได้; MC-CCR และ MC-RBO พิมพ์ IR ของ vehicle 1.17 ซึ่งไม่มีนิยามใดให้ค่านี้
- MWMOTE: Satimage กับ Statlandsat เป็นชุดเดียวกัน (ทั้งชุดกับไฟล์ train) นับเป็น 2 ชุด
- แหล่ง: `out/reconcile_counts.json` (size_variation), `out/full_summary.json`, `mwmote-table5-audit.md`

## 5. ความยากของข้อมูลที่ตรวจได้ (อัปเดต 8 พ.ย. 2026: ดึง mirror เพิ่ม)

- ตรวจได้ **864 entry 65 paper 172 ไฟล์** (เดิม 28 ต.ค. 643/61/131) → **151 task binary/binarise** (594 entry, 45 paper) + OvR 305 task รายงานแยก
- รอบ 8 พ.ย.: `difficulty/verify_ext.py` ใช้กติกาเดิม (ขนาดที่พิมพ์ต้องตรงไฟล์) กับ mirror ใหม่บน GitHub/PyPI (KEEL standard 2 ชุดอิสระ, PMLB ทั้งหมด, UCI++, Weka-UCI, PROMISE, NASA MDP, jbrownlee) + ตารางชื่อเรียกอื่นของ dataset เดียวกัน · entry ที่ตรวจได้เพิ่ม 221 (85 ชื่อ, 49 paper) · ค่าของ 291 task เดิมได้ซ้ำทุกคอลัมน์
- วิธี: Napierala & Stefanowski (k = 5, กติกา rare เต็ม) ระยะ HVDM · ธงมีอ้างอิง: small disjuncts (rare ≥ 20%), outliers > 20%, small sample (n_min/d < 10) · noise index รายงานเป็นค่าต่อเนื่อง · กรอบ "ความยากจากลักษณะข้อมูล" อ้าง López et al. 2013, Jo & Japkowicz 2004
- 151 task: small sample 103 (68%), outliers 38 (25%), small disjuncts 15 (10%), ไม่ติดธง 45 (30%) · โปรไฟล์ 6 แบบ (S 67, none 45, S+O 21, D+S+O 14, O 3, D+S 1) · noise มัธยฐาน 0.44 [0.25, 0.74]
- IR บอกได้น้อยว่า minority อยู่ตรงไหน: rank correlation กับ noise 0.18; กลุ่มไม่ติดธงมี noise 0–0.84 (≥ 0.5 มี 13 task)
- มิติ: มัธยฐาน 9 feature; 59 entry ที่ > 100 feature ตรวจได้แค่ 2 (musk); task ที่วัดได้ ≤ 167 feature
- ราย paper (≥ 3 task, 35 paper): ผสม 32, ไม่ติดธงล้วน 2 (COG-OS, SMOTE-ENN), ติดธงล้วน 1 (MLOS)
- **ชุดอ้างอิง** 33 task (13 ช่อง profile × แถบ IR) ครอบ noise 0–1, IR 1.1–46.5, N 100–11,183; 15 ไฟล์ตรงกับตาราง KEEL ทางการ; yeast 5, ecoli 2, glass 2, cleveland 2
- ชื่อที่ยังวัดไม่ได้ 490/771: ไม่พบไฟล์ 309 (200 ชื่ออ้างแหล่งสาธารณะ UCI/KEEL/คลังอื่น วัดได้ถ้าได้ไฟล์), synthetic 109, ขนาดไม่ตรง 51, สร้าง task ซ้ำไม่ได้ 19, อื่น 2 (`out/name_level_extras.json`)
- แหล่ง: `difficulty/verify_ext_summary.json`, `difficulty_profile_final.csv`, `profile_final_summary.json`, `paper_profile_mix.json`, `reference_collection.csv`, `dimension_profile.json`

## 6. ผลชนะ SMOTE มาจากไหน

**ภาพรวม (plain SMOTE, ทุก metric)**
- 29 paper, 524 dataset, 1,511 แถว (metric ต่อ paper มัธยฐาน 3, 1–6): ชนะ 1,107 เสมอ 102 แพ้ 286 เทียบไม่ได้ 16 → แถวที่ตัดสินได้ 1,495 (520 dataset) ชนะ 79.5% ของ ชนะ+แพ้ (CI 77.3–81.5; ถ้านับ tie เป็นตัวหารด้วยได้ 74%) · 23/29 paper มีอย่างน้อยหนึ่งแถวที่ SMOTE ชนะ
- ความทนทาน: หนึ่งผลต่อ dataset 409/35/76 · กติกา A 521 แถว 402/39/80

**แยก metric** — สัดส่วนชนะของที่ตัดสินได้: AUC/G-mean/F/recall 76–83%, accuracy 91%, MCC 83% แต่ precision 57% และ specificity 14%
| metric | paper | แถว | ชนะ | เสมอ | แพ้ |
|---|---:|---:|---:|---:|---:|
| AUC | 19 | 403 | 309 | 30 | 64 |
| G-mean | 19 | 380 | 283 | 29 | 64 |
| F-measure | 18 | 287 | 217 | 16 | 50 |
| Recall | 12 | 193 | 130 | 21 | 42 |
| Precision | 7 | 113 | 62 | 5 | 46 |
| Accuracy | 4 | 69 | 62 | 1 | 6 |
| MCC | 3 | 52 | 40 | 0 | 8 |
| AUC-PR | 1 | 7 | 3 | 0 | 0 |
| Specificity | 1 | 7 | 1 | 0 | 6 |

(แถว = รวมที่เทียบไม่ได้: G-mean 4, F-measure 4, MCC 4, AUC-PR 4)

**แยกชนิดข้อมูล (สัดส่วนชนะของที่ตัดสินได้)**: original 79.3%, repository-defined 81.2%, modified 74.9%, synthetic 100% (1 paper), บอกไม่ได้ 87.6%

**H1 (modified/synthetic ชนะบ่อยกว่า original) — ไม่ได้รับการสนับสนุน**
- ดิบ 75.7% (371/490) vs 79.3% (329/415)
- GEE OR 0.68 [0.43, 1.08] p 0.10 · ภายใน paper OR 0.61 [0.38, 0.97] p 0.04 (11 paper) · mixed model OR 0.75 [0.58, 0.97]
- ทิศทางกลับด้านกับสมมติฐาน แต่ไม่ทน: หนึ่งผลต่อ dataset 0.64 (p 0.15) / 0.46 (p 0.13); กติกา A 0.80 (p 0.47) / 0.61 (p 0.31); ราย paper 3 vs 7 เท่ากัน 3 (sign p 0.34)
- repository-defined ไม่ต่างจาก original (OR 1.19, p 0.61); "บอกที่มาไม่ได้" ชนะดิบสูงสุดถ้าไม่นับ synthetic (1 paper 15/15) แต่หายเมื่อคุม paper (OR 0.99)

**H2 (ใส่ชุดมาตรฐานชุดเดียวเพื่อความน่าเชื่อถือ)** — เข้าเงื่อนไข 2 paper (MWMOTE 1+19, RUSBoost 1+14) ชนะบนชุดมาตรฐานทั้งคู่ บนข้อมูลดัดแปลง/บอกที่มาไม่ได้ชนะ 52/65 = 80.0% (ไม่รวม 2 dataset ของ MWMOTE ที่จับคู่ record ไม่ได้; ถ้ารวม 54/71) เท่ากับข้อมูลแบบเดียวกันใน 21 paper ที่มีชุดมาตรฐาน ≥ 2 และมีข้อมูลอื่นด้วย 482/600 = 80.3% → ไม่พบรูปแบบ ทดสอบไม่ได้เพราะน้อยเกินไป · 5 paper เทียบเฉพาะชุดมาตรฐาน, INOS เฉพาะชุดดัดแปลง

**ความยากที่วัดได้กับผลชนะ (exploratory)** — 89 ไฟล์, 22 paper, 440 แถว (8 พ.ย.; เดิม 72/20/374)
- noise index +0.1 → odds ชนะ ×1.13 [1.01, 1.26] p 0.03; ภายใน paper ×1.17 p 0.01; หนึ่งผลต่อไฟล์ ×1.19 p 0.03
- IR ไม่สัมพันธ์ (×0.91 ต่อ IR สองเท่า, p 0.48); ธง small sample / outlier / small disjuncts ไม่สัมพันธ์เมื่อดูทีละตัว
- อ่านว่า: ผลชนะ SMOTE ที่รายงานไว้มีแนวโน้มอยู่บนข้อมูลที่ minority เป็น borderline/outlier มาก ไม่ใช่บนข้อมูลที่ IR สูง

**SMOTE แบบอื่น (รายงานแยก)** 12 paper 558 แถว: Static-SMOTE 79 (69/3/7) · OVO-SMOTE 148 (101/6/41) · SMOTE-all 239 (231/0/8) · ห่อกับ learner อื่น 92 (71/2/19) · **ตัดออก**: KNNOR (มีแต่ค่าเฉลี่ย), RBBoost (ค่าคนละตาราง ไม่เคยเทียบตรง), MC-MBRC (หัวคอลัมน์ไม่ระบุว่าคือ SMOTE)

แหล่ง: `out/winloss_allmetric_summary.json`, `out/allmetric_links.csv`, `out/hypotheses.json`, `out/hypotheses_paper_split.csv`, `out/difficulty_outcomes.json`

## 7. ผู้อ่านตรวจย้อนผลได้ไหม (H3)

- granularity 73 paper: รายชุด 47 (64.4%), รายชุดบางส่วน 8, กราฟ 5, ค่าเฉลี่ย 5, อันดับ 3, ไม่เทียบ 5
- 14/57 paper ที่ใช้ SMOTE เป็น baseline ไม่มีคู่ค่ารายชุดกับ SMOTE ใน paper (กราฟ 5, ค่าเฉลี่ย 4 + KNNOR, อันดับ 3, review 1)
- **H3 ได้รับการสนับสนุน**: ใน 43 paper ที่มีผลรายชุดเทียบ SMOTE, 119/952 entry ที่ลิสต์ (12.5%, CI 10.5–14.8) ไม่มีคู่ค่ากับ SMOTE · มาจาก 12 paper (SMOTE-IPF 32/41, Loyalty-SMOTE 30/59, GDO 12/52) · synthetic 38/47, บอกที่มาไม่ได้ 44/166, modified 5/180, repository-defined 7/189 · ข้อควรระวัง: บางชุดอาจอยู่ในตารางผลอื่นของ paper แต่ไม่มีคู่กับ SMOTE
- ยกผล baseline ข้าม paper 3 กรณี: MC-CCR ↔ MC-RBO (SMOTE-all เท่ากันทุกค่า 20 ชุด, กลุ่มเดียวกัน), QC-SMOTE ยกจาก VS-SMOTE, EMDO ↔ AMDO (เท่ากันทุกค่า 9 ชุด, คนละกลุ่ม, ไม่ประกาศ)
- แหล่ง: `out/full_summary.json`, `out/h3_entries.csv`, `out/hypotheses.json`, `out/baseline_provenance_summary.json`

## 8. ข้อแนะนำ 8 ข้อ (ใน manuscript ทุกข้อชี้กลับไปที่หัวข้อ)

1. บอก repository, version, ทั้งชุดหรือไฟล์ train
2. บอกคลาส minority และเหตุผลในเนื้อความ
3. ประกาศการดัดแปลงทุกแบบ และพิมพ์ขนาด/จำนวนคลาสของชุดที่ใช้จริง
4. บอกสูตร IR
5. รายงานจำนวน source family คู่กับจำนวน dataset และรวม split ของแหล่งเดียวกันเวลาทดสอบนัยสำคัญ
6. รายงานผลรายชุดเทียบ plain SMOTE ทุก metric แยกชุดมาตรฐานกับชุดดัดแปลง
7. แยกชุดจูนกับชุดวัดผล และรัน baseline เอง
8. รายงานตัววัดว่า minority อยู่ตรงไหน (safe/borderline/rare/outlier) คู่กับ IR

## 9. ข้อจำกัดที่ต้องเขียนไว้

- ผลชนะเป็นการเทียบค่าที่ paper พิมพ์ ไม่ใช่การทดลองซ้ำ และสเกลเทียบข้าม paper ไม่ได้ (ใช้ paper เป็น cluster ทุกโมเดล)
- หน่วย dataset × metric ให้น้ำหนัก paper ที่รายงานหลาย metric มากกว่า จึงรายงานหนึ่งผลต่อ dataset และกติกา A คู่กันเสมอ
- metric อื่นนอกจาก metric ของกติกา A อ่านจาก PDF ครั้งเดียว (ไม่มีการลอกซ้ำอิสระ)
- ความยากวัดจากไฟล์ mirror (keel-ds, imbalanced-databases, PMLB + 8 พ.ย.: KEEL standard 2 ชุด, UCI++, Weka-UCI, PROMISE, jbrownlee); 72 ไฟล์ KEEL ตรงกับตารางทางการ, KEEL standard สองชุดตรงกัน 67/67 ไฟล์ ที่เหลือยังไม่ได้เทียบเพราะเข้าเว็บ KEEL/UCI ไม่ได้
- การเชื่อมความยากกับผลชนะเป็น exploratory (89 ไฟล์ 22 paper ไฟล์เล็ก มิติต่ำ)
- H2 มีแค่ 2 paper

## 10. วิธีรันซ้ำ (จาก `Data section/`)

```
python3 build/reconcile_counts.py --check        # 47/47
python3 build/winloss_allmetric.py               # all-metric + กลุ่มตัวเทียบ
python3 build/allmetric_links.py                 # ผูกแถวกับ record และชนิดข้อมูล
python3 build/hypotheses.py                      # H1–H3 (ต้องมี statsmodels)
python3 build/difficulty_outcomes.py             # ความยากกับผลชนะ
python3 difficulty/reference_collection.py && python3 difficulty/reference_collection_check.py
python3 build/make_atlas.py && python3 build/atlas_analysis_checks.py && python3 build/consistency_check.py
python3 build/preview/build_preview.py           # พรีวิว PDF
python3 build/make_final.py                      # ฉบับพร้อม merge
```

## 11. สิ่งที่ยังต้องใช้คน (Claude ทำแทนไม่ได้หรือไม่ควรทำ)

1. **Toon ทบทวนสิ่งที่ Claude ตัดสินแทน** (หัวข้อ 0) โดยเฉพาะข้อความที่มีคอมเมนต์ `% Claude 29 Oct 2026` ใน draft ซึ่งเป็นการตีความ
2. **อาจารย์ยืนยัน** นิยาม win/loss และการตีความ H1 (ผลกลับด้านกับข้อสังเกตเดิม)
3. **merge กับ P**: คัดลอก `manuscript/data-section-final.tex` ไป `sections/`, เพิ่ม `\input` ใน main.tex, ต่อ `manuscript/data-section-final.bib` เข้า `references.bib`, คัดลอก `manuscript/figures/data-difficulty.pdf` ไป `figures/` (ทดสอบแล้ว: main.tex + ส่วนนี้คอมไพล์ด้วย biber ได้ 17 หน้า ไม่มี undefined citation/reference จากส่วนนี้) และตกลงเรื่องเนื้อหาที่ซ้อนกับ Section 7
4. **git push** (commit แล้ว ยังไม่ push)
5. เทียบไฟล์ mirror ที่เหลือกับไฟล์ทางการ เมื่อเปิด domain sci2s.ugr.es / archive.ics.uci.edu ได้
