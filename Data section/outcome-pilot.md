# Pilot: วิธีที่เสนอชนะ SMOTE บน dataset แบบไหน

> **สถานะ 18 ต.ค. 2026 ถูกแทนด้วยรอบอ่านครบ 72 paper** (`out/full_outcome_rows.csv`, `out/full_summary.json`)
> 10 paper ใน pilot ถูกอ่านใหม่ด้วย schema เต็มแล้ว เก็บไฟล์นี้ไว้เป็นร่องรอยของการออกแบบ schema เท่านั้น
> ป้าย Original / Repository-defined / Modified / Synthetic ในไฟล์นี้คือชุดป้ายเดียวกับที่ใช้ใน draft


สร้าง 18 ตุลาคม 2026 · ข้อมูลดิบ `ai-draft/outcome/<key>.json` · ตาราง `out/outcome_pilot_rows.csv` · ตัวนับ `out/outcome_pilot_summary.json`
สร้างใหม่ด้วย `python3 build/outcome_pilot.py` (ตาราง md นี้สร้างจาก JSON สองไฟล์นั้น)

**สถานะ ai_draft ทั้งหมด** ค่าในตารางคัดโดย subagent จากตารางผลของ paper (มีเลขตารางและหน้ากำกับ) ยังไม่มีใครตรวจซ้ำ
ชนิดข้อมูลรายแถว Claude ให้ (`ai-draft/outcome/row_data_type.json` มีเหตุผลทุกแถว)

## วิธีเก็บ

ตาม `ai-draft/outcome/SCHEMA.md` **เก็บค่าดิบ ไม่ตัดสินแพ้ชนะ** เพราะนิยาม win/tie/loss ยังรออาจารย์ (decisions-pending เรื่องที่ 1)
เลือกตารางด้วยกติกาตายตัว metric: G-mean > AUC > F1 > accuracy, classifier: ตัวที่ abstract ชู ไม่งั้นตัวแรก, เงื่อนไข: ไม่ใส่ noise
SMOTE = SMOTE ดั้งเดิมเท่านั้น ไม่นับ Borderline-SMOTE หรือ ADASYN แทน

**10 paper เลือกแบบเจาะจงให้หลากหลาย ไม่ใช่สุ่ม** Borderline-SMOTE, ADASYN, Safe-Level-SMOTE, G-SMOTE, RBO, KNNOR, MDO, MC-CCR, CISO, GOIO

## 1. paper รายงานผลรายชุดเทียบกับ SMOTE ไหม

| paper | metric ที่เลือก | classifier | สิ่งที่ได้ |
|---|---|---|---|
| ADASYN | G mean | decision tree | 5 แถว จาก TABLE II หน้า PDF p.5 (printed p.1326) |
| Borderline-SMOTE | F-value | C4.5 | ไม่มีตัวเลขรายชุด |
| CISO | PR-AUC | HGB (histogram-based gradient … | ไม่มีตัวเลขรายชุด · Mean rank (HGB, lower is better): วิธีที่เสนอ 5.11 / SMOTE 5.78 |
| G-SMOTE | G-MEAN | LR | ไม่มีตัวเลขรายชุด · Average (Table 2, mean CV score across 69 datasets) LR G-MEAN: วิธีที่เสนอ 0.856 / SMOTE 0.841 |
| GOIO | F1-score | not stated in paper: Table V r… | 23 แถว จาก Table V หน้า 10 (journal p. 6459) |
| KNNOR | G (G-score, mean over 19 datas… | SVM | ไม่มีตัวเลขรายชุด · Mean over 19 datasets (G, SVM, Table 5): วิธีที่เสนอ .8363 / SMOTE .8238 |
| MC-CCR | mGM [%] (multi-class geometric… | C5.0 | 20 แถว จาก Table 6 หน้า PDF p.10 (journal p.10) |
| MDO | G-mean (mean rank over 20 data… | C4.5 | ไม่มีตัวเลขรายชุด · Avg rank (G-mean, C4.5, Table 2): วิธีที่เสนอ 1.9500 / SMOTE 2.3750 |
| RBO | G-mean (average rank over 24 d… | CART | ไม่มีตัวเลขรายชุด · Avg rank (G-mean, CART, no noise, Table 2): วิธีที่เสนอ 5.1667 / SMOTE 4.1667 |
| Safe-Level-SMOTE | not stated in paper | not stated in paper | ไม่มีตัวเลขรายชุด |

**มีตัวเลขรายชุดของทั้งวิธีที่เสนอและ SMOTE แค่ 3 จาก 10 เรื่อง** (ADASYN, GOIO, MC-CCR)
อีก 7 เรื่อง รายงานเป็นกราฟเส้นอย่างเดียว (Borderline-SMOTE, Safe-Level-SMOTE) หรือเป็นค่าเฉลี่ยและอันดับเท่านั้น
RBO และ KNNOR บอกว่าผลรายชุดอยู่บน GitHub หรือเอกสารเพิ่มเติม ซึ่งไม่ได้อยู่ใน Drive จึงยังไม่ได้อ่าน
ตัวเลขข้อนี้จะใช้ได้ต่อเมื่อ decisions-pending เรื่องที่ 3 (ชั้นความละเอียดของการรายงาน) ตัดสินแล้ว

**สิ่งที่อ่านจากค่าเฉลี่ยและอันดับโดยตรง ไม่ได้ตีความ**
- RBO Table 2 (CART, ไม่มี noise, G-mean) อันดับเฉลี่ย RBO 5.1667 SMOTE 4.1667 (อันดับยิ่งต่ำยิ่งดี) ส่วน F-measure RBO 4.1250 SMOTE 5.0000
- CISO รายงานเองว่าเทียบเท่า SMOTE ทางสถิติบน PR-AUC (Holm-corrected Wilcoxon p = 1.000, W/T/L 15/10/12)
- MDO อันดับเฉลี่ย G-mean 1.9500 เทียบ SMOTE 2.3750 ต่างกัน 0.4250 น้อยกว่า CD 1.2490 ในตาราง 3 ของ paper เอง

## 2. แยกตามชนิดข้อมูล (3 paper ที่มีตัวเลขรายชุด)

diff = วิธีที่เสนอ − SMOTE ตามค่าที่พิมพ์ หน่วยเป็นหน่วยของ metric ใน paper นั้น **เทียบข้าม paper ไม่ได้**
(MC-CCR พิมพ์เป็นเปอร์เซ็นต์ อีกสองเรื่องเป็นทศนิยม)

| paper | ชนิดข้อมูล | ชุด | วิธีที่เสนอสูงกว่า | SMOTE สูงกว่า | median diff | min | max | ชุดที่ SMOTE สูงกว่า |
|---|---|---|---|---|---|---|---|---|
| ADASYN | Modified | 3 | 3 | 0 | 0.0152 | 0.015 | 0.0703 | - |
| ADASYN | Original | 2 | 2 | 0 | 0.0106 | 0.0041 | 0.0171 | - |
| GOIO | Modified | 6 | 6 | 0 | 0.0771 | 0.0233 | 0.1032 | - |
| GOIO | Original | 6 | 6 | 0 | 0.0271 | 0.01 | 0.058 | - |
| GOIO | Repository-defined | 6 | 5 | 1 | 0.0371 | -0.0154 | 0.1047 | sick_euthyroid |
| GOIO | Synthetic | 5 | 5 | 0 | 0.049 | 0.0398 | 0.0609 | - |
| MC-CCR | Original | 20 | 20 | 0 | 14.255 | 7.86 | 36.76 | - |

**ข้อจำกัดที่ต้องรู้ก่อนอ่านตาราง**
- "สูงกว่า" คือค่าที่พิมพ์มากกว่า ยังไม่ได้ดู std หรือ significance รายชุด ซึ่งเป็นนิยามที่ยังไม่ตัดสิน
- MC-CCR เทียบกับ "SMOTE-all" คือ SMOTE ที่ใช้ round-robin กับข้อมูลหลายคลาส ไม่ใช่ SMOTE แบบ binary ตรง ๆ
- GOIO ไม่บอกว่าตาราง V ใช้ classifier ตัวไหน subagent เข้าใจว่าเฉลี่ยจาก 5 ตัว ยังไม่ได้ยืนยัน
- ADASYN มีแค่ 5 ชุด และมี baseline อื่นตัวเดียวคือ decision tree ที่ไม่ resample
- การจัดชนิดข้อมูล "Repository-defined" ขึ้นกับ decisions-pending เรื่องที่ 2

## 3. ทุกแถว

| paper | dataset ตามที่พิมพ์ | ชนิดข้อมูล | วิธีที่เสนอ | SMOTE | diff | baseline อื่นที่ดีที่สุด |
|---|---|---|---|---|---|---|
| ADASYN | Vehicle | Modified | 0.9168 | 0.9018 | 0.015 | Decision tree 0.8834 |
| ADASYN | Pima Indian Diabetes | Original | 0.6625 | 0.6454 | 0.0171 | Decision tree 0.6430 |
| ADASYN | Vowel recognition | Modified | 0.9622 | 0.9470 | 0.0152 | Decision tree 0.9256 |
| ADASYN | Ionosphere | Original | 0.8530 | 0.8489 | 0.0041 | Decision tree 0.8371 |
| ADASYN | Abalone | Modified | 0.6291 | 0.5588 | 0.0703 | Decision tree 0.5227 |
| GOIO | default | Original | 0.6597 | 0.6095 | 0.0502 | SOS 0.6582 |
| GOIO | shoppers | Original | 0.7244 | 0.6923 | 0.0321 | MLOS 0.7217 |
| GOIO | bank_full | Original | 0.7161 | 0.7008 | 0.0153 | MLOS 0.7066 |
| GOIO | bank_small | Original | 0.6742 | 0.6642 | 0.01 | MLOS 0.6793 |
| GOIO | avila_0vs5 | Modified | 0.8595 | 0.7777 | 0.0818 | GAMO 0.8533 |
| GOIO | artificial_0.5_10 | Synthetic | 0.6197 | 0.5710 | 0.0487 | SOS 0.6216 |
| GOIO | optical_digits | Repository-defined | 0.8696 | 0.8350 | 0.0346 | GAMO 0.9194 |
| GOIO | avila_0vs6 | Modified | 0.7926 | 0.7202 | 0.0724 | GAMO 0.8257 |
| GOIO | sick_euthyroid | Repository-defined | 0.7151 | 0.7305 | -0.0154 | GAMO 0.7451 |
| GOIO | avila_0vs7 | Modified | 0.8220 | 0.7237 | 0.0983 | GAMO 0.8341 |
| GOIO | scene | Repository-defined | 0.5645 | 0.5373 | 0.0272 | MLOS 0.5570 |
| GOIO | abalone_15 | Modified | 0.6441 | 0.5999 | 0.0442 | MLOS 0.6187 |
| GOIO | thyroid_sick | Repository-defined | 0.7564 | 0.7168 | 0.0396 | GAMO 0.7284 |
| GOIO | abalone_6 | Modified | 0.9164 | 0.8931 | 0.0233 | GAMO 0.9150 |
| GOIO | artificial_0.3_5 | Synthetic | 0.5253 | 0.4753 | 0.05 | SOS 0.5239 |
| GOIO | artificial_0.5_5 | Synthetic | 0.5912 | 0.5422 | 0.049 | SOS 0.5804 |
| GOIO | artificial_1_5 | Synthetic | 0.6992 | 0.6383 | 0.0609 | SOS 0.6859 |
| GOIO | wine_quality | Repository-defined | 0.6286 | 0.5653 | 0.0633 | MLOS 0.5886 |
| GOIO | taiwanses | Original | 0.6030 | 0.5809 | 0.0221 | SOS 0.5861 |
| GOIO | artificial_0.5_2.5 | Synthetic | 0.5344 | 0.4946 | 0.0398 | SOS 0.5344 |
| GOIO | mammography | Repository-defined | 0.8023 | 0.6976 | 0.1047 | GAMO 0.7979 |
| GOIO | bankruptcy | Original | 0.5295 | 0.4715 | 0.058 | SOS 0.5374 |
| GOIO | page-blocks_0vs3 | Modified | 0.9075 | 0.8043 | 0.1032 | GAMO 0.9078 |
| MC-CCR | Automobile | Original | 75.68 | 51.86 | 23.82 | SMOM 78.75 |
| MC-CCR | Balance | Original | 62.22 | 40.57 | 21.65 | SMOM 58.65 |
| MC-CCR | Car | Original | 95.03 | 81.16 | 13.87 | MDO 95.73 |
| MC-CCR | Cleveland | Original | 30.98 | 18.00 | 12.98 | MDO 26.45 |
| MC-CCR | Contraceptive | Original | 49.72 | 38.15 | 11.57 | SMOM 52.60 |
| MC-CCR | Dermatology | Original | 94.88 | 79.34 | 15.54 | S-SMOTE 95.23 |
| MC-CCR | Ecoli | Original | 70.98 | 51.72 | 19.26 | S-SMOTE 67.54 |
| MC-CCR | Flare | Original | 64.71 | 55.98 | 8.73 | S-SMOTE 61.92 |
| MC-CCR | Glass | Original | 71.06 | 55.41 | 15.65 | MDO / SMOM 67.97 |
| MC-CCR | Hayes-roth | Original | 85.16 | 70.52 | 14.64 | SMOM 86.82 |
| MC-CCR | Led7digit | Original | 80.44 | 57.85 | 22.59 | MDO 78.19 |
| MC-CCR | Lymphography | Original | 77.36 | 40.60 | 36.76 | SMOM 73.99 |
| MC-CCR | Newthyroid | Original | 92.17 | 80.69 | 11.48 | SMOM 93.46 |
| MC-CCR | Pageblocks | Original | 82.55 | 71.64 | 10.91 | MDO 79.06 |
| MC-CCR | Thyroid | Original | 81.48 | 73.62 | 7.86 | S-SMOTE 81.86 |
| MC-CCR | Vehicle | Original | 70.35 | 59.57 | 10.78 | S-SMOTE 71.97 |
| MC-CCR | Wine | Original | 92.87 | 80.82 | 12.05 | S-SMOTE 93.41 |
| MC-CCR | Winequality-red | Original | 46.66 | 17.80 | 28.86 | SMOM 42.56 |
| MC-CCR | Yeast | Original | 56.91 | 43.83 | 13.08 | SMOM 52.91 |
| MC-CCR | Zoo | Original | 84.29 | 55.61 | 28.68 | SMOTE-IPF 78.55 |

## 4. สิ่งที่ pilot บอกเรื่องตัว schema

1. paper ส่วนใหญ่ใน pilot ไม่มีตารางรายชุด ถ้าขยายไปทั้ง 72 เรื่องด้วย schema นี้ จะได้ข้อมูลรายชุดจากส่วนน้อยของ corpus
   ทางเลือกคือเก็บผลรายชุดจาก GitHub หรือ supplementary ของ paper ที่ชี้ไว้ (RBO, KNNOR, G-SMOTE) ซึ่งต้องตัดสินว่านับเป็น "ตีพิมพ์" หรือไม่
2. ควรเก็บ std ทุกครั้งที่พิมพ์ GOIO พิมพ์ std ไว้ แต่ schema ยังไม่ใช้
3. ต้องมีช่องบอกว่า SMOTE ในตารางเป็นแบบไหน (MC-CCR ใช้ SMOTE-all)
4. การให้ชนิดข้อมูลรายแถวควรทำตอนกรอก `data_type` ในชีต `extraction` แล้ว join กัน ไม่ใช่ให้แยกไฟล์แบบ pilot
