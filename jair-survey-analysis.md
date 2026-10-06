# วิเคราะห์ลักษณะ Survey Paper ของ JAIR และจุดที่ชอบจาก 2 Survey อ้างอิง

> - **โครงการ:** 25 Years of SMOTE (SMOTE25) · **วารสารเป้าหมาย:** Journal of Artificial Intelligence Research (JAIR)
> - **จัดทำ:** 6 ตุลาคม 2569 (2026) · **แหล่งข้อมูล:** หน้านโยบายของ jair.org, บทความ survey ที่ตีพิมพ์ใน JAIR, และ PDF 2 ไฟล์ในโฟลเดอร์ Google Drive `SMOTE25/Survey/`
> - **สถานะ:** โน้ตภายใน (อยู่ใน `notes/` จึงไม่รวมใน Overleaf upload)

---

## สรุปสั้น (TL;DR)

1. **JAIR ไม่รับ survey ที่ "แค่สรุปงาน"** หน้า submission ระบุชัดว่า survey ที่ "merely summarise a selection of existing literature without providing new insights" มีโอกาสถูก reject โดยไม่ส่ง review และ survey ที่มาจากบท related work ของวิทยานิพนธ์ต้องมี "major added value" ดังนั้น SMOTE25 ต้องมี **ข้อเสนอเชิงความคิด (conceptual contribution)** ที่ชัด เช่น taxonomy ใหม่ หรือข้อค้นพบเชิงประจักษ์
2. **ต้องแยกตัวเองจาก Fernández et al. (2018) ให้ได้** เพราะเป็น survey SMOTE ฉบับครบรอบ 15 ปีที่ตีพิมพ์ใน JAIR เอง และ cover letter ของ JAIR บังคับให้ระบุ 1 ถึง 3 บทความ JAIR ที่ใกล้เคียงที่สุดพร้อมอธิบายความต่าง
3. **Survey ของ JAIR ในช่วงหลังมีแนวโน้มเป็น "survey + หลักฐานเชิงประจักษ์"** (เช่น benchmark หรือ systematic search ที่รายงานตัวเลขชัด) แต่ไม่ได้บังคับ
4. **จาก Pradipta et al. (2021):** ชอบ taxonomy 5 กลุ่มที่จำง่าย และตารางสรุปแบบ Type / Description / Advantages / Limitations / Examples ซึ่งยกมาใช้กับ `tables/variants-summary.tex` ได้ทันที
5. **จาก Hassanat et al. (2022):** ชอบการมี "จุดยืน" (thesis) ที่ชัด ตารางวิเคราะห์ว่าแต่ละวิธี "ถูกประเมินอย่างไร" (จำนวน dataset, จำนวนคลาส, classifier, metric) และการเสนอ protocol ใหม่เพื่อตรวจสอบ synthetic samples ซึ่งทำให้ survey มี insight ใหม่จริง

---

## 1. ลักษณะ Survey Paper ของ JAIR

### 1.1 นโยบายทางการที่เกี่ยวกับ survey

| ประเด็น | สิ่งที่ JAIR ระบุ | ที่มา |
|---|---|---|
| นิยาม survey | "Survey articles are tutorials or literature reviews that contribute an analysis or perspective that advance our understanding of the subject matter and make it accessible to a broad community of researchers or practitioners." | [About][about] |
| บรรณาธิการ | มี **Surveys Editor** แยกเฉพาะ (Min-Yen Kan ณ วันที่ตรวจ) | [About][about] |
| มาตรฐานการ review | survey ผ่านกระบวนการ review เข้มเท่ากับ research article และถูกวัดด้วยมาตรฐานเดียวกันด้าน significance, relevance, technical และ expository quality | [Survey papers list][surveylist] |
| เกณฑ์ desk reject ที่เกี่ยวข้อง | (1) "Surveys that merely summarise a selection of existing literature without providing new insights or conceptual contributions" (2) งานที่ "insufficiently grounded in the state of the art ... (lack of suitable, recent references)" | [Submissions][subm] |
| survey จากวิทยานิพนธ์ | survey ที่มาจากบท related work ของ thesis โดยไม่มี "major added value, by means of novel and insightful organisation of a research area within AI" ถือว่าไม่เหมาะ | [Transparent Publishing][tp] |
| Cover letter (บังคับ, ไม่เกิน 150 คำต่อข้อ) | (1) งานนี้สำคัญต่อนักวิจัย AI อย่างไร (2) ระบุ 1 ถึง 3 บทความใน JAIR ที่ใกล้เคียงที่สุดและอธิบายความต่าง (3) ส่วนใดเคยตีพิมพ์หรืออยู่ระหว่าง review ที่อื่นหรือไม่ | [Submissions][subm] |
| Reproducibility checklist | **บังคับทุก submission** (ต่อท้าย template) ไม่กรอกมีโอกาส desk reject; checklist มีส่วน general สำหรับทุกบทความ และส่วนเงื่อนไข (theory / computational experiments / datasets) ที่ตอบ "no" ได้ถ้าไม่เกี่ยว แต่ต้องชัดว่าทำไมไม่เกี่ยว | [Submissions][subm], [Gundersen et al. 2024][repro] |
| Structured abstract | Background / Objectives / Methods / Results / Conclusions เป็นแบบที่ **แนะนำ (encouraged)** ไม่ใช่บังคับ | [Gundersen et al. 2024][repro] |
| Template | JAIR Author Kit (บน ACM `acmart`) บังคับตั้งแต่ Vol. 83 (repo นี้ใช้อยู่แล้ว) | [Formatting][fmt] |
| ความยาว | **ไม่พบการกำหนดจำนวนหน้าหรือคำ**; ไฟล์แนะนำไม่เกิน 15 MB; รูปต้องอ่านเข้าใจได้แม้พิมพ์ขาวดำ | [Submissions][subm] |
| ระยะเวลา review | ประมาณ 8 ถึง 12 สัปดาห์ต่อรอบ, ไม่เกิน 2 รอบ; ไม่มี "major revision" แต่จะ "reject with encouragement to resubmit" แทน | [Submissions][subm], [About][about], [Transparent Publishing][tp] |
| สถิติที่ JAIR เปิดเผย | ตัวอย่าง submission ที่รับเมื่อ 1 ก.ค. 2025: โอกาส accept รวม 10.6% (56.3% ถ้าไม่นับที่ถูก summary reject), เวลาถึง accept โดยคาด 41.7 สัปดาห์ (เป็นตัวเลขรวมทุกประเภท ไม่เฉพาะ survey) | [Transparent Publishing][tp] |
| Open access | Diamond OA ไม่มีค่าธรรมเนียม; บทความตั้งแต่ 1 พ.ค. 2023 เป็น CC BY | [About][about], [FAQ][faq] |
| Special track ที่น่าสนใจ | **AI and Society** track รับงานเรื่องผลกระทบของ AI ต่อสังคมและ "AI focused on social good" ซึ่งตรงกับแกน "How did it benefit society?" ของเรา (พิจารณาเป็นทางเลือก) | [AI and Society track][aisoc] |

**ข้อสังเกตสำคัญสำหรับทีม:** ผู้เขียนหลักของ SMOTE25 เป็นนักศึกษา ป.โท จึงเสี่ยงถูกมองว่าเป็น "survey from thesis chapter" ถ้าเนื้อหาออกมาเป็นการเล่าเรียงงาน ต้องออกแบบ contribution เชิงโครงสร้าง (taxonomy, framework, evidence synthesis) ตั้งแต่ต้น ไม่ใช่เติมทีหลัง

### 1.2 ตัวอย่าง survey ที่ตีพิมพ์ใน JAIR

| บทความ | ที่ตีพิมพ์ | ความยาวโดยประมาณ | ลักษณะเด่นที่สังเกตได้ |
|---|---|---|---|
| Fernández, García, Herrera, Chawla. *SMOTE for Learning from Imbalanced Data: Progress and Challenges, Marking the 15-year Anniversary* ([link][fern2018]) | JAIR 61, 863-905 (2018) | 43 หน้า | **คู่เทียบหลักของเรา** (ในระบบ JAIR จัดอยู่หมวด "Articles" และไม่อยู่ในรายการ Survey papers) ไม่มี search protocol ไม่มีการทดลองใหม่; มี pseudo-code, ตารางจัดกลุ่ม extension (ระบุว่ามี "more than 85 extensions"), บท variations สำหรับ paradigm อื่น (streaming, semi-supervised, multi-class/label/instance, regression) และบท challenges (small disjuncts, overlap, dataset shift, dimensionality, real-time, Big Data) |
| Gao, Liu, Li. *Data Augmentation for Time-Series Classification: An Extensive Empirical Study and Comprehensive Survey* ([link][tsc]) | JAIR 83 (2025) | ~46 หน้า | **ต้นแบบที่ใกล้เคียงเรามากที่สุด**: structured abstract ครบ 5 หัวข้อ, มีบท Survey Methodology (Google Scholar, arXiv, snowballing), taxonomy, ทดลองเทียบเกือบ 20 วิธีบน 15 UCR datasets, มีบท Limitations and Threats to Validity |
| Kirstein, Wahle, Gipp, Ruas. *CADS: A Systematic Literature Review on the Challenges of Abstractive Dialogue Summarization* ([link][cads]) | JAIR 82, 313-365 (2025) | 53 หน้า | systematic review รายงานตัวเลขชัด (1262 papers คัดกรองเหลือที่ใช้), taxonomy เป็น 6 challenges, มีบท datasets และ evaluation แยก, บทสุดท้ายพูดถึงข้อจำกัดของหลักฐานและของกระบวนการ review |
| Mehrotra et al. *Understanding AI Trustworthiness: A Scoping Review of AIES & FAccT Articles* ([link][trust]) | JAIR 85 (2026) | ~24 หน้า | structured abstract, research questions RQ1 ถึง RQ4, **PRISMA flow diagram**, รายงาน inter-coder agreement |
| Kage et al. *A Review of Pseudo-Labeling for Computer Vision* ([link][pseudo]) | JAIR 85 (2026) | ~32 หน้า | มีบท Preliminaries (notation) และ **นิยามรวม (unifying definition)** เป็น contribution, family-tree figure, บท Open Directions |
| Serra-Perelló, Ortiz. *Incremental Learning Methodologies for Addressing Catastrophic Forgetting: Analysis and Experimental Evaluation* ([link][incr]) | JAIR 83 (2025) | ~36 หน้า | taxonomy 9 กลุ่ม + การทดลองเปรียบเทียบขนาดใหญ่ |
| Uma et al. *Learning from Disagreement: A Survey* ([link][disagree]) | JAIR 72, 1385-1470 (2021) | 86 หน้า | taxonomy table + experimental comparison บน 6 datasets |
| Thuremella, Kunze. *Prediction of Social Dynamic Agents and Long-Tailed Learning Challenges: A Survey* ([link][longtail]) | JAIR 77, 1697-1772 (2023) | 76 หน้า | มี subsection Methodology / Inclusion Criteria / Related Surveys ในบทนำ, task taxonomy figure |

> หมายเหตุ: จำนวนหน้าดูจาก running header; รูปแบบเก่า (เลขหน้าต่อเนื่องทั้งเล่ม จนถึงราว Vol. 82) กับรูปแบบใหม่ ACM (Vol. 83 ขึ้นไป, เลข article) **เทียบกันตรงๆ ไม่ได้** เพราะ layout ใหม่แน่นกว่า JAIR มีรายการ survey รวมไว้ที่ [Survey papers list][surveylist]

### 1.3 ลักษณะร่วมของ survey ใน JAIR (สังเคราะห์)

1. **Contribution เชิงการจัดระเบียบความรู้เป็นแกนหลัก.** เกือบทุกฉบับมี taxonomy หรือ framework ที่เป็นของตัวเอง (6 challenges ใน CADS, unifying definition ใน pseudo-labeling, 9 families ใน incremental learning) การเรียงรายวิธีแบบแคตตาล็อกถูกห้ามโดยนโยบาย
2. **Review methodology เป็นทางเลือก แต่กำลังเป็นกระแส.** survey แนว systematic (CADS, Text Generation, Scoping review, Data Augmentation) รายงานฐานข้อมูล, query, จำนวนที่คัดกรอง, เกณฑ์ และบางฉบับมี PRISMA ส่วน survey แนว method (SMOTE 2018, pseudo-labeling) ไม่มี ทั้งสองแบบได้รับการตีพิมพ์
3. **Survey สาย ML มักมีส่วนเชิงประจักษ์.** Data Augmentation, Incremental Learning, Learning from Disagreement และ Decision-Focused Learning ล้วนจับคู่ review กับ benchmark
4. **อ่านง่ายสำหรับผู้อ่าน AI ทั่วไป.** น้ำเสียงแบบ tutorial (มีชื่อเช่น "A Field Guide for the Uninitiated", "A Practical Guide") มี background และ notation ที่ self-contained
5. **มีบท limitations และ future directions แยกชัด.** หลายฉบับมีทั้ง "Limitations / Threats to Validity" ของตัว survey เอง และ "Open problems" ของสาขา
6. **ความยาว:** รูปแบบเก่าราว 43 ถึง 135 หน้า (ส่วนใหญ่ 70 ขึ้นไป) รูปแบบใหม่ราว 24 ถึง 49 หน้า; อ้างอิงมักหลักร้อยรายการ (ค่าประมาณ)
7. **Structured abstract** พบในฉบับ 2025 ถึง 2026 บางส่วน (repo เราใช้แบบนี้อยู่แล้ว ซึ่งดี)

### 1.4 ความหมายต่อ SMOTE25

- **Cover letter ข้อ 2 แทบเขียนได้แล้ว:** บทความ JAIR ที่ใกล้ที่สุดคือ Chawla et al. (2002) และ Fernández et al. (2018) ต้องอธิบายว่าเรา (ก) ครอบคลุมช่วง 2018 ถึง 2026 ที่ 2018 ไม่มี (deep generative, LLM-era tabular synthesis ฯลฯ) (ข) มีแกน **ผลต่อสังคม/การนำไปใช้จริง** ที่ 2018 ไม่ได้วิเคราะห์ (ค) มีมุมมองเชิงวิพากษ์และหลักฐาน (เช่น ข้อโต้แย้งของ Hassanat et al.) และ (ง) แยก binary กับ multiclass อย่างเป็นระบบ
- **ต้องมี "new insight" ที่จับต้องได้** อย่างน้อยหนึ่งอย่าง: taxonomy แบบหลายมิติ, evidence map ของการประเมินผล, หรือ benchmark/validation ขนาดเล็ก
- **เลือกแนว systematic** (บท methodology ที่วางไว้แล้วใน `sections/03-methodology.tex`) จะช่วยตอบเกณฑ์ "grounded in state of the art" และทำให้ตัวเลขใน Results ของ structured abstract มีความหมาย
- **Reproducibility checklist:** ถ้าไม่มีการทดลอง ตอบส่วน general และตอบ "no" ในส่วนเงื่อนไขพร้อมเหตุผล ถ้ามี benchmark ต้องกรอกส่วน experiments/datasets ครบ (seeds, code, data license, statistical tests)

---

## 2. Survey 1: Pradipta et al. (2021)

**บรรณานุกรม:** G. A. Pradipta, R. Wardoyo, A. Musdholifah, I. N. H. Sanjaya, M. Ismail. "SMOTE for Handling Imbalanced Data Problem: A Review." *2021 Sixth International Conference on Informatics and Computing (ICIC)*, IEEE. DOI: [10.1109/ICIC54025.2021.9632912](https://doi.org/10.1109/ICIC54025.2021.9632912)  
**ขนาด:** 8 หน้า (conference, 2 คอลัมน์), อ้างอิง 60 รายการ

**โครงสร้าง:** I. Introduction · II. Classification for Imbalanced Dataset (3 แนวทาง: algorithm-level, data-level, cost-sensitive; นิยาม IR; ปัจจัยความยากของข้อมูล) · III. SMOTE (นิยามเชิงรูปนัย + สมการ interpolation) · IV. Progress Extension of SMOTE (A. Clustering, B. Metaheuristic, C. Initial Selection, D. Filtering, E. Dimensionality Changes + Table I) · V. Conclusion and Challenges in Future Work

### จุดที่ชอบ (ควรนำมาใช้)

1. **Taxonomy 5 กลุ่มที่เรียบง่ายและจำง่าย** (Clustering / Metaheuristic / Initial Selection / Filtering / Dimensionality Changes) ถ้ามองให้ลึกกว่าที่ผู้เขียนเขียน กลุ่มเหล่านี้แทบจะเรียงตาม **ขั้นตอนของ pipeline ที่ SMOTE ถูกดัดแปลง**: ตั้งค่า parameter (metaheuristic) → เลือก seed (initial selection) → กำหนดบริเวณ/ปริภูมิที่สร้าง (clustering, dimensionality) → กรองหลังสร้าง (filtering) แนวคิด "pipeline stage" นี้นำมาเป็นแกนหนึ่งของ taxonomy ใน `sections/04-taxonomy.tex` ได้ดี
2. **Table I: Summary of SMOTE-Based Extension** มีคอลัมน์ *Type · Short Description · Advantages · Limitations · Example Studies* อ่านจบในตารางเดียวและเห็น trade-off ของแต่ละกลุ่มทันที แนะนำให้ขยาย `tables/variants-summary.tex` (ตอนนี้มีแค่ Method / Year / Category / Key Idea) เป็นสองตาราง: ระดับ **กลุ่ม** (แบบ Table I) และระดับ **วิธี**
3. **ผูก "ปัญหาของข้อมูล" เข้ากับ "เหตุผลที่เกิด variant"**: Section II อธิบาย noise, small disjuncts, overlapping พร้อม Fig. 1 (ภาพ 2D ของแต่ละปัญหา) แล้ว Section IV อธิบายว่าแต่ละกลุ่มแก้ข้อจำกัดใดของ SMOTE เดิม (สร้างตัวอย่างในเขต majority, ต้องเลือก k, สร้าง noise) เป็นโครง problem → remedy ที่ทำให้ผู้อ่านเข้าใจว่า "ทำไม" ไม่ใช่แค่ "อะไร"
4. **นิยามเชิงรูปนัยสั้นและครบ**: สมการ IR และสมการ interpolation ของ SMOTE ในหน้าเดียว เหมาะเป็นแบบของ `sections/02-background.tex` (ให้ notation ที่ใช้ต่อทั้งบทความ)
5. **ปิดท้ายด้วย intrinsic data characteristics เป็นทิศทางอนาคต** และยกตัวอย่างข้อมูลการแพทย์ ซึ่งเชื่อมกับแกน "ประโยชน์ต่อสังคม" ของเราได้

### จุดที่ควรระวัง (ไม่ควรเลียนแบบเมื่อส่ง JAIR)

- **ไม่มี review methodology** ไม่บอกว่าค้นอย่างไร คัดเลือกอย่างไร ครอบคลุมช่วงปีใด
- **เชิงพรรณนา ไม่ใช่เชิงวิพากษ์:** เล่าว่าแต่ละวิธีทำอะไร แต่ไม่เปรียบเทียบผลหรือสังเคราะห์ข้อค้นพบข้ามงาน
- **หมวดหมู่ทับซ้อนโดยไม่ประกาศ:** เช่น MWMOTE [26] และ HPM [29] อยู่ทั้งแถว Clustering ([23]-[29]) และแถว Initial Selection ใน Table I ส่วน DBSMOTE [30] ถูกอธิบายใน Section A (Clustering) แต่ในตารางอยู่แถว Initial Selection บทเรียน: ถ้าวิธีหนึ่งอยู่ได้หลายกลุ่ม ให้ใช้ **faceted taxonomy** (หลายแกน) และประกาศให้ชัด
- **สัญญาใน abstract ไม่ครบ:** abstract บอกว่าจะ review "performance evaluation in imbalanced data" แต่ไม่มีหัวข้อนี้ในเนื้อหา
- **ขอบเขตแคบ:** ไม่มี multiclass, ไม่มี deep generative, ไม่มีบทการประยุกต์ (แม้บทนำจะยกตัวอย่างโดเมน)

---

## 3. Survey 2: Hassanat et al. (2022)

**บรรณานุกรม:** A. B. Hassanat, A. S. Tarawneh, G. A. Altarawneh, A. Almuhaimeed. "Stop Oversampling for Class Imbalance Learning: A Critical Review." arXiv:[2202.03579](https://arxiv.org/abs/2202.03579) v2, 8 มิ.ย. 2022 (ระบุ "Preprint submitted to Elsevier")  
**ขนาด:** 19 หน้า, อ้างอิง 190 รายการ · **สถานะ:** ยังไม่พบฉบับที่ผ่าน peer review ในวารสาร (ค้น ณ 6 ต.ค. 2026; ควรตรวจซ้ำก่อนอ้าง)

**โครงสร้าง:** 1. Introduction (ประกาศ "counterclaim") · 2. Literature review of oversampling methods (Fig. 1 แนวโน้มจำนวนบทความ; Table 1 สรุป 72 วิธี) · 3. Method and Data (ระบบ validation แบบซ่อน majority + Hassanat distance + สมการ error) · 4. Datasets (Yeast4, Yeast5, Yeast6) · 5. Experiments and Results (ซ่อน 10/25/50%, ทำซ้ำ 5 ครั้ง, box plot, ranking, visualization, ทดสอบเพิ่มบน Vehicle3) · 6. Conclusion

### จุดที่ชอบ (ควรนำมาใช้)

1. **มีจุดยืน (thesis) ที่ชัดตั้งแต่หน้าแรก:** "Oversampling in its current forms and methodologies is a misleading approach that should be avoided..." ทำให้ทั้งบทความมีทิศทาง ตรงกับที่ JAIR ต้องการ "analysis or perspective" สำหรับ SMOTE25 ไม่จำเป็นต้องสุดโต่งแบบนี้ แต่ควรมี **ข้อสรุปหลัก 2 ถึง 3 ข้อ** ที่ประกาศในบทนำและพิสูจน์ในเนื้อหา
2. **Table 1 วิเคราะห์ "วิธีถูกประเมินอย่างไร" ไม่ใช่แค่ "วิธีทำอะไร":** สำหรับ 72 วิธี บันทึก จำนวน dataset, จำนวนคลาส, classifier ที่ใช้, metric ที่ใช้ ทำให้เห็นข้อค้นพบระดับสาขา เช่น เกือบทั้งหมดทดสอบแค่ binary (นับจากข้อความที่สกัดได้ราว 63 จาก 72 วิธี) และทุกวิธีพิสูจน์ความดีผ่าน accuracy ของ classifier เท่านั้น **นี่คือ schema ที่ควรใช้ทำ extraction sheet ใน `notes/`** และเป็นวัตถุดิบของ `sections/07-empirical-comparisons.tex`
3. **ใช้ bibliometrics เปิดเรื่อง:** Fig. 1 แสดงจำนวนบทความที่มีคำว่า SMOTE/oversampling รายปี (ข้อมูลจาก Google Scholar) สำหรับ survey ครบรอบ 25 ปี ภาพ timeline/ปริมาณงานคือ figure ที่ควรมี (ตรงกับ `figures/timeline` ที่วางแผนไว้) แต่ควรใช้ฐานข้อมูลที่ทำซ้ำได้ (Scopus/WoS/OpenAlex) และระบุ query กับวันที่ค้น
4. **เพิ่มหลักฐานใหม่แทนการเล่า:** เสนอ protocol "ซ่อน majority บางส่วน แล้วดูว่า synthetic sample ไปตกใกล้ majority ที่ซ่อนไว้หรือไม่" แล้วรันกับกว่า 70 วิธี ทำให้ review นี้มี insight ที่หาจากที่อื่นไม่ได้ เป็นตัวอย่างของ "new insights" ตามเกณฑ์ JAIR
5. **พูดถึงความเสี่ยงในการใช้งานจริง:** ชี้ว่า synthetic data อาจทำให้ระบบล้มเหลวในงานสำคัญ (การแพทย์, ความปลอดภัย, ยานยนต์ไร้คนขับ) และเตือนว่าวิธีเหล่านี้อยู่ใน library ยอดนิยมอย่าง imbalanced-learn แกน "How did it benefit society?" ของเราควรมี **ด้านความเสี่ยง** คู่กับด้านประโยชน์ เพื่อความสมดุลและน่าเชื่อถือ
6. **ข้อเสนอเชิงปฏิบัติ:** ถ้าจำเป็นต้อง oversample ให้ validate ก่อน และพิจารณา ensemble (เช่น EasyEnsemble) เป็นทางเลือก บทสรุปของ SMOTE25 ควรมี practitioner guidance แบบนี้เช่นกัน

### จุดที่ควรระวัง (อ่านอย่างวิพากษ์)

- **หลักฐานบางเกินข้อสรุป:** ใช้ 3 datasets ตระกูล Yeast (10 attributes, binary) + Vehicle3 อีกหนึ่ง แต่สรุปว่า oversampling "should be avoided in real-world applications"
- **ตัววัด "ผิด" มีข้อถกเถียง:** synthetic sample ที่ "ใกล้ majority" (ตาม Hassanat distance ซึ่งเป็น metric ของผู้เขียนเอง) ไม่ได้แปลว่าป้ายผิดเสมอ โดยเฉพาะในบริเวณ overlap ที่ป้ายจริงกำกวมอยู่แล้ว SMOTE25 ควรอภิปรายจุดนี้และค้นงานที่ทดสอบซ้ำหรือโต้แย้ง (**TODO: ค้นงานที่อ้างถึงและตอบโต้บทความนี้**)
- **Literature review ตื้น:** อธิบายจริงราว 10 วิธี ที่เหลืออ้างเป็นก้อน "[91, 92, ..., 119]" (citation dumping) ซึ่ง JAIR ไม่ยอมรับ
- **คุณภาพการเขียน:** เลขตารางในเนื้อหาไม่ตรงกับตาราง (อ้าง "Table 2" แต่ผลอยู่ใน Table 3), roadmap ในบทนำไม่ตรงกับหัวข้อจริง, พิมพ์ "mythology" แทน "methodology"
- **ยังเป็น preprint** ต้องระบุสถานะให้ชัดเมื่ออ้างอิง

---

## 4. ข้อเสนอการนำไปใช้กับ SMOTE25

| องค์ประกอบ | แรงบันดาลใจจาก | สิ่งที่จะทำใน SMOTE25 | ไฟล์ใน repo |
|---|---|---|---|
| ข้อสรุปหลัก 2 ถึง 3 ข้อในบทนำ | Hassanat (thesis ชัด) | ประกาศ research questions + key findings ตั้งแต่ Introduction | `sections/01-introduction.tex` |
| ส่วนต่างจาก JAIR 2018 | นโยบาย JAIR (cover letter ข้อ 2) | ย่อหน้า "Relation to previous surveys" + ตารางเทียบขอบเขตกับ Fernández 2018 และ survey อื่น | `sections/01-introduction.tex` |
| Review methodology + PRISMA | CADS, Scoping review, Data Augmentation (JAIR) | ระบุฐานข้อมูล, query, ช่วงปี, เกณฑ์, ตัวเลขคัดกรอง, flow diagram | `sections/03-methodology.tex`, `figures/prisma-flow` |
| Data difficulty factors | Pradipta (Fig. 1, Section II) | ภาพ overlap / noise / small disjuncts + notation ของ SMOTE | `sections/02-background.tex` |
| Faceted taxonomy | Pradipta (5 กลุ่ม) + บทเรียนเรื่องหมวดทับซ้อน | แกน (1) pipeline stage (2) กลไก (3) problem setting binary/multiclass; วิธีหนึ่งอยู่ได้หลาย facet อย่างเป็นทางการ | `sections/04-taxonomy.tex`, `figures/taxonomy` |
| ตารางสรุประดับกลุ่ม | Pradipta (Table I) | คอลัมน์ Category / Idea / Advantages / Limitations / Representative works | `tables/variants-summary.tex` |
| Evidence map ของการประเมินผล | Hassanat (Table 1) | สกัด #datasets, #classes, classifier, metric, statistical test, code availability ของทุกวิธี แล้วสรุปเป็นข้อค้นพบระดับสาขา | `notes/` (extraction sheet), `sections/07-empirical-comparisons.tex` |
| Timeline / bibliometrics | Hassanat (Fig. 1) | จำนวนงานต่อปี 2002 ถึง 2026 จากฐานข้อมูลที่ทำซ้ำได้ + milestones | `figures/timeline` |
| ประโยชน์ และ ความเสี่ยง | Hassanat (real-world harm) | แยกหัวข้อ benefit ตามโดเมน และ risk / failure mode | `sections/06-applications.tex`, `sections/08-challenges.tex` |
| ส่วนเชิงประจักษ์ (ทางเลือก) | Data Augmentation for TSC (JAIR), Hassanat | benchmark หรือ validation ขนาดเล็กที่ทำซ้ำได้ ขยายสิ่งที่ Hassanat ทำให้ครอบคลุม multiclass และ datasets มากขึ้น (ถ้าทำ ต้องกรอก checklist ส่วน experiments) | `sections/07-empirical-comparisons.tex`, Appendix A |
| Practitioner guidance | Hassanat (recommendations) | ตาราง/กล่อง "ควรใช้วิธีใดเมื่อไร" ในบทสรุป | `sections/09-conclusion.tex` |

### Extraction sheet ที่เสนอ (สำหรับทุกบทความใน Binary / Multiclass / Both)

| คอลัมน์ | ตัวอย่างค่า |
|---|---|
| ID, ชื่อวิธี, ปี, venue, DOI | M1, SMOTE, 2002, JAIR, 10.1613/jair.953 |
| Problem setting | binary / multiclass / both |
| Pipeline stage ที่ดัดแปลง | parameter / seed selection / generation space / post-filtering / hybrid |
| กลไกหลัก | interpolation, clustering, density, kernel, GAN/VAE/diffusion, ... |
| ข้อจำกัดของ SMOTE ที่อ้างว่าแก้ | overlap, noise, small disjuncts, high-dim, choice of k |
| #datasets, แหล่ง (KEEL/UCI/อื่นๆ), IR range | 6, UCI, 1.8 ถึง 42 |
| Classifiers, metrics | C4.5, NB; AUC, F1, G-mean |
| Statistical test | Friedman + Holm / ไม่มี |
| Code available | ใช่ (ลิงก์) / ไม่ |
| Application domain และผลต่อสังคมที่รายงาน | การแพทย์: ... |

---

## 5. Checklist ก่อนส่ง JAIR (เฉพาะประเด็น survey)

- [ ] ระบุ **conceptual contribution** ได้ในประโยคเดียว (ถ้าตอบไม่ได้ ยังไม่พร้อมส่ง)
- [ ] มีย่อหน้าเทียบกับ Fernández et al. (2018) และ survey อื่น พร้อมตารางเทียบขอบเขต
- [ ] Review methodology ครบ: ฐานข้อมูล, query, วันที่ค้น, เกณฑ์ include/exclude, ตัวเลขแต่ละขั้น, PRISMA flow
- [ ] Taxonomy ประกาศแกนชัด และจัดการกรณีวิธีอยู่หลายกลุ่ม
- [ ] อ้างงานล่าสุด (2024 ถึง 2026) เพียงพอ ไม่มี citation dumping
- [ ] มีบท limitations ของตัว survey เอง (threats to validity)
- [ ] Structured abstract มีตัวเลขจริงใน Results
- [ ] รูปอ่านได้เมื่อพิมพ์ขาวดำ, ทุกรูปมี `\Description{}`
- [ ] Reproducibility checklist (Appendix A) กรอกครบ พร้อมเหตุผลในข้อที่ตอบ "no"
- [ ] Cover letter ตอบ 3 คำถาม (ไม่เกิน 150 คำต่อข้อ)

---

## 6. สิ่งที่ยังไม่ได้ยืนยัน

- จำนวน reviewer ต่อบทความ และ JAIR ใช้ double-blind หรือไม่ (ไม่พบในหน้าที่อ่าน)
- จำนวนหน้าของตัวอย่าง survey เป็นค่าประมาณจาก running header; จำนวนอ้างอิงใน survey ของ JAIR เป็นค่าประมาณ
- สถิติ acceptance เป็นตัวเลขที่ JAIR แสดง ณ ต.ค. 2026 อาจเปลี่ยน
- ชื่อ Surveys Editor ตรวจจากหน้า About ณ วันที่จัดทำ
- สถานะการตีพิมพ์ของ Hassanat et al. (ยังพบเฉพาะ arXiv)

---

## แหล่งอ้างอิง

**นโยบาย JAIR**
- [About JAIR][about] · [Submissions][subm] · [Transparent Publishing][tp] · [FAQ][faq] · [Formatting / Author Kit][fmt] · [Survey papers list][surveylist] · [AI and Society track][aisoc]
- Gundersen, Helmert, Hoos. "Improving Reproducibility in AI Research: Four Mechanisms Adopted by JAIR." JAIR 81 (2024) 1019-1041. [link][repro]

**Survey ที่ใช้เป็นตัวอย่าง**
- [Fernández et al. 2018][fern2018] · [Gao et al. 2025][tsc] · [Kirstein et al. 2025][cads] · [Mehrotra et al. 2026][trust] · [Kage et al. 2026][pseudo] · [Serra-Perelló & Ortiz 2025][incr] · [Uma et al. 2021][disagree] · [Thuremella & Kunze 2023][longtail]

**2 survey ในโฟลเดอร์ `SMOTE25/Survey/`**
- Pradipta et al. 2021: [Drive][drive-pradipta] · DOI [10.1109/ICIC54025.2021.9632912](https://doi.org/10.1109/ICIC54025.2021.9632912)
- Hassanat et al. 2022: [Drive][drive-hassanat] · [arXiv:2202.03579](https://arxiv.org/abs/2202.03579)

[about]: https://jair.org/index.php/jair/about
[subm]: https://www.jair.org/index.php/jair/about/submissions
[tp]: https://jair.org/index.php/jair/transparent-publishing
[faq]: https://www.jair.org/index.php/jair/faq
[fmt]: https://www.jair.org/index.php/jair/formatting
[surveylist]: https://www.jair.org/index.php/jair/surveypapers
[aisoc]: https://jair.org/index.php/jair/SpecialTrack-AIandSociety
[repro]: https://jair.org/index.php/jair/article/view/16905
[fern2018]: https://jair.org/index.php/jair/article/view/11192
[tsc]: https://www.jair.org/index.php/jair/article/view/17084
[cads]: https://www.jair.org/index.php/jair/article/view/16674
[trust]: https://www.jair.org/index.php/jair/article/view/20729
[pseudo]: https://www.jair.org/index.php/jair/article/view/19656
[incr]: https://www.jair.org/index.php/jair/article/view/18405
[disagree]: https://www.jair.org/index.php/jair/article/view/12752
[longtail]: https://www.jair.org/index.php/jair/article/view/14749
[drive-pradipta]: https://drive.google.com/file/d/13fFnaGVW1Ap9s1r8139AwjNjAmVOlUv1/view
[drive-hassanat]: https://drive.google.com/file/d/1JBCOQ5HpJrHPs0L3CAIIegHcK0ecJY4c/view
