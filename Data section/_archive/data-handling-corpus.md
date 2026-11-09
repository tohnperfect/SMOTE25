# ภาพรวมทั้ง corpus: แต่ละ paper เลือกและจัดการข้อมูลอย่างไร

สร้าง 16 ตุลาคม 2026 ด้วย `build/data_handling_matrix.py`
ตารางเต็ม 1 แถวต่อ paper อยู่ที่ `out/data_handling_matrix.csv` ตัวนับทั้งหมดอยู่ที่ `out/data_handling_summary.json`

**สถานะ ai_draft ทุกค่า ห้ามเอาตัวเลขในไฟล์นี้ไปใส่ manuscript**
ไฟล์นี้จัดข้อมูลให้เห็นภาพทั้งวงการ ไม่ได้สรุป insight แทน Toon

## ที่มาของค่า และระดับความเชื่อถือ

| กลุ่ม | จำนวน | ที่มา | ตรวจย้อนได้แค่ไหน |
|---|---|---|---|
| 69 เรื่อง | 69 | ข้อความในฟิลด์ `srcdet` `crit` `prep` `ev` ของ `ai-draft/papers.json` จากรอบอ่าน 6 ต.ค. | มีประโยคยกมา 1 ประโยคต่อเรื่อง (`ev`) **ไม่มีเลขหน้า** |
| 7 เรื่องที่เพิ่ม | 7 | อ่าน PDF ใหม่ 16 ต.ค. (`ai-draft/new7/*.json`) INOS, SMOTE-IPF, HDE, NROMM, GOIO, DGOT, Loyalty-SMOTE | ทุกค่ามีเลขหน้าและคำพูดยกมา 13 ถึง 24 รายการต่อเรื่อง |

**รหัส 4 ช่อง (`crit_type`, `basis`, `inherited_from`, `minority_rule`) Claude เป็นคนให้** จากการอ่านข้อความข้างบน
รหัสพร้อมคำนิยามอยู่ที่ `ai-draft/data_handling_codes.json` ข้อความต้นทางของทุกแถวอยู่ใน CSV คอลัมน์ `src_text` `crit_text` `prep_text` `quote`
ถ้าไม่เห็นด้วยกับรหัสไหน แก้ที่ไฟล์ codes แล้วรันสคริปต์ใหม่ ตัวนับทุกตัวในไฟล์นี้จะเปลี่ยนตาม

**ตัวหาร** paper ที่มีการประเมินผลบนข้อมูล 72 เรื่อง จาก corpus 76 ตัดออก 4 เรื่องที่ไม่มีการประเมินผลบนชุดข้อมูล (AdaBoost, ENN (Wilson), Survey: SMOTE Review, Tomek Links)
(แก้คำ 18 ต.ค. เดิมเขียนว่า "เชิงประจักษ์" และ "ไม่มีการทดลอง" ซึ่งไม่ตรงสำหรับ Tomek ที่มีตัวอย่าง 2 มิติ เรื่องนับ Tomek รอ Toon ตัดสิน · Section 7 ของ P ใช้ 71 เพราะนับ Hassanat 2022 เป็น survey)
แยกตามช่วงปี 1972-2009 = 14, 2010-2019 = 26, 2020-2026 = 32

---

## 1. ข้อมูลมาจากไหน

นับเป็น paper ที่ใช้แหล่งนั้นอย่างน้อยหนึ่งชุด (หนึ่ง paper นับได้หลายแหล่ง)

| แหล่ง | paper | % ของ 72 |
|---|---|---|
| UCI | 56 | 78% |
| KEEL | 32 | 44% |
| Other | 23 | 32% |
| Synthetic | 22 | 31% |
| Private | 15 | 21% |
| Image | 5 | 7% |
| Text | 2 | 3% |
| imbalanced-learn | 2 | 3% |
| UCR | 1 | 1% |
| LibSVM | 1 | 1% |
| Kaggle | 1 | 1% |

`Other` คือแหล่งที่ไม่ใช่ repository มาตรฐาน เช่น ELENA, PROMISE, HDDT collection, ชุดจาก paper ก่อนหน้า
`Private` คือข้อมูลที่ผู้เขียนเก็บเองหรือได้จากองค์กร ผู้อ่านเอามาทำซ้ำไม่ได้

---

## 2. paper ให้เหตุผลการเลือก dataset ไหม

| crit_type | ความหมาย | paper | % |
|---|---|---|---|
| own reason | ให้เหตุผลของตัวเอง เช่น อยากให้หลากหลาย อยากทดสอบ overlap | 48 | 67% |
| cites prior work | บอกว่าเลือกตามงานก่อนหน้า | 13 | 18% |
| generic only | บอกแค่ว่า widely used / commonly used | 3 | 4% |
| not stated | ไม่บอกเลย | 8 | 11% |

**ไม่บอกหรือบอกแค่ widely used รวม 11 เรื่อง** A-SUWO, Borderline-SMOTE, DGOT, GLOS, GOIO, Loyalty-SMOTE, MBS, RSMOTE, SOS, Safe-Level-SMOTE, k-means SMOTE

**แยกตามช่วงปี** (paper ในช่วง / paper ทั้งหมดในช่วง)

| crit_type | 1972-2009 | 2010-2019 | 2020-2026 |
|---|---|---|---|
| own reason | 11 / 14 | 21 / 26 | 16 / 32 |
| cites prior work | 1 / 14 | 3 / 26 | 9 / 32 |
| generic only | 0 / 14 | 1 / 26 | 2 / 32 |
| not stated | 2 / 14 | 1 / 26 | 5 / 32 |

**เหตุผลที่ให้ เป็นเหตุผลแบบไหน** (`basis` หนึ่ง paper มีได้หลายแบบ)

| basis | ความหมาย | paper |
|---|---|---|
| diversity | ให้ขนาด IR จำนวน feature หลากหลาย | 27 |
| prior-work | ตามงานก่อนหน้า | 15 |
| difficulty | ตั้งใจให้มี overlap, noise, small disjunct หรือ IR สูง | 15 |
| method-target | ตรงกับสิ่งที่วิธีของตัวเองออกแบบมาแก้ เช่น mixed feature, high-dim | 13 |
| application | มาจากโจทย์จริงที่จูงใจงาน | 9 |
| popularity | widely used / frequently used | 9 |
| threshold rule | ตั้งเกณฑ์คัดชัดเจน เช่น IR > 1.5, IR > 10, minority อย่างน้อย 10 | 6 |
| replicability | เลือกชุดสาธารณะเพื่อให้คนอื่นทำซ้ำได้ | 2 |
| random draw | สุ่มเลือกจาก repository (CGMOS, KNNOR) | 2 |
| preregistered | ล็อกชุดข้อมูลไว้ก่อนรันผล (CISO) | 1 |

---

## 3. ยกชุด benchmark มาจากงานก่อนหน้า

19 เรื่องที่บอกไว้ในตัว paper ว่าเอารายชื่อ dataset มาจากงานอื่น
ในนั้น 10 เรื่องยกมาทั้งชุด ที่เหลือยกมาบางส่วน (ขึ้นต้นด้วย partial)

| paper | ปี | ยกมาจาก |
|---|---|---|
| SMOTE | 2002 | partial: Provost et al. (Satimage), Kubat et al. (Oil) |
| ADASYN | 2008 | partial: DataBoost-IM, Provost et al. |
| LS | 2008 | partial: SMOTE paper |
| Global-CS (journal) | 2010 | own conference version (Global-CS AAAI) |
| SPIDER2 | 2010 | partial: authors' earlier SPIDER study |
| RBBoost / Random Balance | 2015 | HDDT collection [37] and KEEL binary collection |
| SMOTE-IPF | 2015 | Napierala, Stefanowski, Wilk (noisy and borderline examples) |
| SOUP | 2019 | partial: Fernandez et al. 2013, Galar et al. 2011, Saez et al. 2016 |
| MC-CCR | 2020 | Saez et al. |
| MC-RBO | 2020 | authors' earlier study on instance-level difficulty |
| EMDO | 2021 | AMDO benchmark, reused for direct comparison |
| FW-SMOTE | 2022 | partial: Maldonado et al. (12 microarray sets) |
| KNNOR | 2022 | partial: smote-variants benchmark |
| NROMM | 2023 | multi-class: Koziarski et al. RBU (PR 2020) and MC-CCR; binary: PA, FW-SMOTE, SVDD-WSMOTE |
| GMMSampling | 2024 | SOUP paper and Lango & Stefanowski 2018 |
| MC-MBRC | 2024 | partial: synthetic generator from Vuttipittayamongkol et al. 2020 |
| GDHS | 2025 | partial: 6 defect sets from a prior CBR paper |
| MC-NCLWO | 2025 | Saez et al. |
| QC-SMOTE | 2026 | VS-SMOTE benchmark, adopted wholesale with its baseline results |

**ข้อจำกัด** นับเฉพาะกรณีที่ paper *บอกเอง* ส่วน A-SUWO ที่รายชื่อทับกับ MWMOTE หนักมากแต่ไม่ได้อ้าง ไม่นับ
การหาการส่งต่อที่ไม่ได้ประกาศต้องเทียบรายชื่อ dataset ข้ามคู่ paper (D7 ใน `section-outline.md`)

---

## 4. ดัดแปลงข้อมูลอย่างไร

`origin` หนึ่ง paper มีได้หลายแบบ

| origin | ความหมาย | paper | % |
|---|---|---|---|
| Natural | ใช้ตามที่แจกมาอย่างน้อยบางชุด | 69 | 96% |
| Binarised | ทำ multiclass ให้เป็นสองคลาส | 37 | 51% |
| Generated | สร้างข้อมูลสังเคราะห์เอง | 20 | 28% |
| Undersampled | ตัด minority ออกเพื่อดัน IR | 8 | 11% |
| Noise-injected | ใส่ noise ใน label หรือ feature | 7 | 10% |
| Class-merged | รวมคลาส | 6 | 8% |
| Induced profile | สร้างความไม่สมดุลจากชุดที่สมดุล (ภาพ) | 3 | 4% |
| Class-resized | ปรับขนาดคลาส | 2 | 3% |

**paper ที่ดัดแปลงอย่างน้อยหนึ่งแบบ 51 จาก 72 เรื่อง**
ตัวเลขนี้ **ขึ้นกับ decisions-pending เรื่องที่ 2** เพราะนับไฟล์ KEEL 2 คลาสเป็น Binarised ด้วย
7 เรื่องที่ Binarised มาจาก KEEL เป็นผู้ binarize ให้ (RBBoost / Random Balance, SplitBal, RBO, KNNOR, NROMM, MLOS, QC-SMOTE)
ถ้านับไฟล์ KEEL เป็น Original จะเหลือ 46 เรื่อง

**แยกตามช่วงปี** (paper ในช่วง / paper ทั้งหมดในช่วง)

| origin | 1972-2009 | 2010-2019 | 2020-2026 |
|---|---|---|---|
| Binarised | 10 / 14 | 14 / 26 | 13 / 32 |
| Generated | 4 / 14 | 8 / 26 | 8 / 32 |
| Undersampled | 3 / 14 | 2 / 26 | 3 / 32 |
| Noise-injected | 1 / 14 | 2 / 26 | 4 / 32 |
| Class-merged | 0 / 14 | 3 / 26 | 3 / 32 |

---

## 5. บอกไหมว่าคลาสไหนเป็น minority

| minority_rule | ความหมาย | ทุก paper | ในกลุ่มที่ Binarised (37) |
|---|---|---|---|
| explicit target listed | ระบุคลาสเป้าหมายรายชุด ในเนื้อความหรือตาราง | 20 | 15 |
| smallest class vs rest | ตั้งกติกาเดียวทุกชุด คลาสเล็กสุดเป็น minority | 7 | 7 |
| repository-defined | ใช้ไฟล์ KEEL ที่ชื่อบอกการแบ่งไว้แล้ว | 9 | 7 |
| mean-size or IR threshold | (multiclass) คลาสเล็กกว่าค่าเฉลี่ยหรือ IR_i เกินเกณฑ์ | 6 | 0 |
| induced by authors | ผู้เขียนกำหนดเองตอนสร้างความไม่สมดุล | 2 | 0 |
| not defined | (multiclass) ไม่นิยาม minority ใช้การกระจายคลาสดิบ | 8 | 0 |
| not stated | binarize หรือดัดแปลงแล้วไม่บอกว่าคลาสไหน | 15 | 8 |
| n.a. | ข้อมูลสองคลาสโดยกำเนิดทั้งหมด | 5 | 0 |

**binarize แล้วไม่บอกกติกา 8 เรื่อง** A-SUWO, COG-OS, G-SMOTE, INOS, MBS, OBU, RACOG / wRACOG, RSMOTE

---

## 6. มิติที่มีเฉพาะ 7 เรื่องที่อ่านใหม่

69 เรื่องเดิมไม่ได้เก็บมิติเหล่านี้แยกเป็นช่อง บางเรื่องมีปนอยู่ในข้อความ `prep` แต่ไม่ครบ
**ห้ามตีความว่า paper ไม่ได้บอก** แค่รอบสกัด 6 ต.ค. ไม่ได้เก็บ

| paper | split | resample ใน fold | missing | nominal | normalise | คอลัมน์ตารางคุณลักษณะ | นิยาม IR | รูปแบบพิมพ์ IR | เปิดเผยข้อมูล | ประกาศการดัดแปลงที่ |
|---|---|---|---|---|---|---|---|---|---|---|
| DGOT | Stratified 5-fold cross-validation, repeated with ten random… | yes, stated | not stated in paper | not stated in paper | not stated in paper | N, features, classes, IR, other | IR = Nmaj/Nmin, where Nmaj and Nmin are the number of majori… | single ratio | repository named only | table only |
| GOIO | stratified 5-fold cross-validation, repeated with ten random… | yes, stated | not stated in paper | not stated in paper | not stated in paper | N, features, IR, other | IR = Nmaj / Nmin, where Nmaj and Nmin represent the number o… | single ratio | repository named only | data/experimental section |
| HDE | 5-fold stratified cross validation repeated 10 times (5 x 10… | yes, stated | not stated in paper | not stated in paper | not stated in paper | N, features, IR, other | the ratio of majority instances to minority instances | single ratio | link given (https://github.com/smallcube/HD-Ensemble) | data/experimental section |
| INOS | Training and test data divided randomly, with all available … | yes, stated | not stated in paper | not stated in paper | Each feature is min-max scaled to [-1, 1] using the training… |  | IM-ratio = number of negative samples divided by number of p… | not printed | link given (http://sites.google.com/site/sstarcao/) | data/experimental section |
| Loyalty-SMOTE | single 7:3 train/test split (no repetitions or CV stated) | not stated in paper | not stated in paper | not stated in paper | not stated in paper | N, features, classes, IR | IR = N_majority / N_minority, where N_majority and N_minorit… | single ratio | repository named only | not declared |
| NROMM | Inconsistent in supplement: '2 fold cross-validation repeate… | yes, stated | not stated in paper | Kept as categorical; handled by the method itself: entropy d… | not stated in paper | N, features, classes, class_distribution, IR, other | The imbalance ratio (IR) is computed by dividing the number … | single ratio | repository named only | elsewhere (binary D1-D10 identities and class splits appear … |
| SMOTE-IPF | 5 runs of stratified 5-fold cross-validation, results averag… | yes, stated | not stated in paper | Kept, not encoded: SMOTE finds neighbours over numerical and… | not stated in paper | N, features, n_minority, n_majority, IR, other | IR = N- / N+, 'the relation between the majority class and m… | single ratio | link given (http://sci2s.ugr.es/noisebor-imbalanced; KEEL ht… | data/experimental section |

ถ้าจะนับมิติเหล่านี้ทั้ง corpus ต้องอ่าน 69 เรื่องเฉพาะส่วน experimental setup อีกรอบ
ไม่ใช่อ่านใหม่ทั้งเล่ม เพราะรู้แล้วว่าจะหาอะไร

---

## 7. ถ้าจะตรวจ เริ่มที่ไหนคุ้มที่สุด

ค่าที่บอกว่า "ไม่มี" (not stated) ตรวจถูกที่สุด เพราะค้นคำใน PDF ได้ทั้งเล่ม และเป็นค่าที่ผิดได้ง่ายที่สุด
ถ้ารอบสกัดอ่านข้ามไป จะกลายเป็นการกล่าวหาว่า paper ไม่บอกทั้งที่บอก

1. 11 เรื่องที่ `crit_type` เป็น not stated / generic only
2. 8 เรื่องที่ binarize โดยไม่บอกกติกา
3. 19 เรื่องที่ยกชุด benchmark มา ต้องการเลขหน้าของประโยคที่อ้าง

รายชื่อซ้ำกันบางส่วน รวมแล้ว 35 เรื่อง
