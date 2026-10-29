# Method section

วัสดุของ **Method section** (ส่วนที่ P รับผิดชอบ) ของ survey `25 Years of SMOTE`
เน้น paper ที่เป็น **SMOTE-family** ตามนิยามใน `SMOTE25_Method_Map_1.html` (ระดับบนสุดของ repo)

โฟลเดอร์นี้ไม่ขึ้น Overleaf โดยตรง ร่าง LaTeX จะย้ายเข้า `sections/` เมื่อทีมตกลงตำแหน่งกันแล้ว

---

## สถานะ ณ 29 ต.ค. 2026

| รายการ | ตัวเลข |
|---|---|
| Paper ใน corpus | 76 |
| SMOTE-family (Core 34, Partial 3) | 37 |
| SMOTE-family ที่ **อ่าน PDF ครบแล้ว** (28 ต.ค.) | 37 |
| Binary only / Multiclass only / Binary + Multiclass | 24 / 5 / 8 |
| ขั้นตอนของ SMOTE ที่ถูกแก้หลังอ่าน PDF | 21 จาก 36 variants |
| เรื่องที่ยังรอ P ตัดสิน | 6 (ดูด้านล่าง) |

การอ่าน PDF ทำโดย AI ภายใต้กติกาเดียวกัน (`pdf-check/coding_rules.md`) ทุกข้อความมีเลขหน้า ส่วน ตาราง
หรือสมการอ้างอิง **ยังต้องให้คนสุ่มตรวจ** ก่อนนำไปเขียนเป็นข้อสรุปใน manuscript

---

## กติกาจัดประเภทคลาส (ตัดสินโดย P)

1. **Binary only**: ทุกการทดลองที่สร้างข้อมูลเป็นปัญหา 2 คลาส รวมถึง dataset หลายคลาสที่ถูกยุบเหลือ 2 คลาส
   และการขยายไปหลายคลาสที่เขียนไว้แต่ไม่ได้ทดลอง
2. **Multiclass only**: สร้างข้อมูลโดยคงไว้ 3 คลาสขึ้นไป และไม่เคยรันกับข้อมูล 2 คลาส
3. **Binary + Multiclass**: วิธีเดียวกันรันทั้งกับข้อมูล 2 คลาส และกับข้อมูล 3 คลาสขึ้นไปที่ไม่ได้ยุบ
4. Paper ที่ใช้ข้อมูลหลายชนิด (เช่น ภาพกับตาราง) จัดประเภทแยกตามชนิดข้อมูล แล้วรวมเป็นประเภทรวม
5. **การทดลองใน supplementary นับ** (ตัดสิน 28 ต.ค.) เพราะแสดงว่าวิธีนั้นทำได้

## เรื่องที่ยังรอตัดสิน

- **GLOS**: การรันเพื่อปรับพารามิเตอร์บน Sonar (2 คลาส) นับไหม ตอนนี้ใส่ Multiclass only
- **Loyalty-SMOTE**: ใช้ข้อมูลหลายคลาสแต่เติมแค่คลาสเล็กสุด วัดผลแบบ binary ตอนนี้ใส่ Binary only
- **OREM / OREM-M**: สองรุ่นทดลองคนละแบบ, OREMBoost ทดลองทั้งคู่ ตอนนี้ใส่ Binary + Multiclass
- **NROMM**: Core หรือ Partial (จุดกลุ่ม trapped ไม่ได้สร้างด้วย interpolation)
- **CISO**: Method Map ใส่ปี 2026 แต่ key ของ Section 7 คือ `yadav2025ciso`
- **SMOM**: ไฟล์ PDF หลักใน Drive จริง ๆ คือ INOS ต้องอัปโหลดใหม่แล้วตรวจซ้ำ

---

## ไฟล์ในโฟลเดอร์

| ไฟล์ | คืออะไร |
|---|---|
| `smote-family-overview.html` | หน้า **SMOTE Family at 25** (ภาษาอังกฤษ) 4 หน้าต่าง: นิยาม, จำนวนและ Roadmap, ควรทำ oversampling ต่อไหม, ผู้อ่านได้อะไร **สร้างจาก script ห้ามแก้มือ** |
| `binary-multiclass-summary.html` | หน้าสรุปสำหรับนำเสนอ: 3 ประเภท, Timeline แบบ interactive, paper ที่ใช้ข้อมูลประเภทอื่น, ตาราง 37 วิธีพร้อมคำอธิบาย **สร้างจาก script ห้ามแก้มือ** |
| `manuscript/method-section-draft.tex` | ร่าง paper ส่วน Method (v2) มีช่องว่างให้ทีม Datasets และ Performance Metrics |
| `manuscript/generated/` | ตาราง 37 วิธีและคำอธิบายรายวิธี **สร้างจาก Method Map ห้ามแก้มือ** |
| `pdf-check/coding_rules.md` | กติกาที่ใช้อ่าน PDF ทั้ง 37 paper |
| `pdf-check/*.json` | ผลการอ่าน PDF ราย paper (ประเภท, หลักฐาน, ขั้นตอนที่เปลี่ยน, คำอธิบาย) |
| `build/` | script ที่ใช้เขียนผลลง Method Map และสร้างหน้าสรุปกับส่วนของร่าง |

## สร้างใหม่หลังแก้ Method Map (รันจากระดับบนสุดของ repo)

```bash
python "Method section/build/make_tex.py" SMOTE25_Method_Map_1.html "Method section/manuscript/generated"
python "Method section/build/make_summary2.py" SMOTE25_Method_Map_1.html "Method section/binary-multiclass-summary.html" "Method section/build/summary_template2.html"
python "Method section/build/make_overview.py" SMOTE25_Method_Map_1.html "Method section/smote-family-overview.html" "Method section/build/overview_template.html"
```

`add_class_rule.py`, `merge_pdf_check.py` และ `decide_supplement.py` เป็นบันทึกว่าแก้ Method Map อย่างไร
รันไปแล้วครั้งเดียว **ห้ามรันซ้ำ** กับไฟล์ที่แก้แล้ว
