# difficulty/ — วัดลักษณะความยากของ dataset ที่ตรวจสอบได้จริง (28 ต.ค. 2026)

สถานะ: Claude ทำ, Toon ยังไม่ทบทวน · วัดแล้ว + จัดกลุ่มชั่วคราว (`group.py`) · ไม่เกี่ยวกับ win/loss (พักไว้)

## คำตัดสินของ Toon ที่ใช้
- overlap รวมเข้ากับ noise
- วัดเฉพาะ dataset ที่ตรวจสอบได้จริง ที่เหลือเว้นไว้
- entry ที่ paper ไม่พิมพ์ขนาด แต่ชื่อตรงกับไฟล์ KEEL นับว่าตรวจได้ (Claude ไม่นับ entry ที่เป็น modified เพราะผู้เขียนดัดแปลงไฟล์แล้ว จึงไม่ใช่ไฟล์นั้น)
- ไฟล์ multiclass วัดทุกคลาสแบบ one-vs-rest

## นิยาม "ตรวจสอบได้จริง" (ระดับ entry = 1 dataset ใน 1 paper)
1. หาไฟล์สาธารณะได้จากชื่อ (normalise: ตัวเล็ก ตัดอักขระที่ไม่ใช่ a-z0-9, ALIAS ใน `catalog.py`)
2. จำนวน instance ที่พิมพ์ตรงกับไฟล์พอดี (feature ต่างได้ ±1) หรือไม่พิมพ์ขนาดแต่ชื่อตรงกับไฟล์ KEEL และไม่ใช่ modified
3. ถ้าพิมพ์ขนาด minority ต้องตรงกับไฟล์ หรือ (ไฟล์ multiclass) เท่ากับผลรวมของคลาสชุดเดียวแบบไม่กำกวม

## แหล่งไฟล์ (เว็บ KEEL / UCI / OpenML เข้าไม่ได้จากทั้ง cloud และเครื่อง)
- KEEL imbalanced 100 ชุด: `keel-ds==0.2.5` และ `imbalanced-databases==0.1.1` (PyPI) ขนาดตรงกันทั้ง 100 ชุด
- KEEL ทั่วไป 43 ชุด: `keel-ds` raw (ไม่มี header, คอลัมน์สุดท้ายคือคลาส, ชนิด attribute อนุมานจากค่า)
- อื่น ๆ: PMLB (ไฟล์ LFS จาก media.githubusercontent.com; nominal ถูก label-encode แล้ว)
- เป็น mirror ไม่ใช่ไฟล์ทางการ ควรเทียบกับไฟล์จาก KEEL/UCI โดยตรงก่อนใช้ใน manuscript

## ผลการตรวจ
| สถานะ | entry |
|---|---:|
| V-binary_file | 425 |
| V-keel_name_only | 80 |
| V-multiclass_asis | 89 |
| V-binarized_rule_unique | 20 |
| **ตรวจได้** | **614** (59 paper, 189 ชื่อ, 125 ไฟล์) |
| U-no_public_file | 646 |
| U-size_mismatch | 182 |
| U-synthetic | 119 |
| U-no_printed_size (modified 28, original 28 ที่ไม่ใช่ KEEL, not stated 1) | 57 |
| U-task_not_reconstructible | 25 |
| V?-binarized_rule_ambiguous | 8 |
| U-minority_mismatch | 2 |
| **เว้นไว้** | **1,039** |

## การวัด (`measure.py` → `difficulty_measures.csv`, 263 task: binary 102, OvR 152 จาก 23 ไฟล์, binarize 9)
ค่าตั้งต้นที่ Claude เลือก (ยังไม่ได้ทบทวน): k = 5, Euclidean บน numeric ที่ min-max แล้ว + one-hot nominal, แถวที่มีค่าหายถูกตัด (รอบนี้ไม่มี), เก็บแถวซ้ำไว้

| ปัจจัย | คอลัมน์ | นิยาม |
|---|---|---|
| Noise (รวม overlap) | `borderline`, `outlier`, `noise_index` = borderline + outlier, `kDN_min` | สัดส่วน minority ตาม Napierala & Stefanowski (เพื่อนบ้าน minority 2–3 / 0 จาก 5); kDN = ค่าเฉลี่ยสัดส่วนเพื่อนบ้านต่างคลาส |
| Small disjuncts | `rare`, `n_subconcepts`, `subconcepts_ge2`, `largest_subconcept_share`, `singletons` | rare = เพื่อนบ้าน minority 1 จาก 5; sub-concept = connected component ของ minority ที่เชื่อมผ่าน kNN ที่เป็น minority |
| Small sample / rarity | `N`, `n_min`, `n_features_raw`, `n_min_per_feature` | |
| Imbalance | `IR` = n_maj / n_min คำนวณจากไฟล์ด้วยนิยามเดียว | |
| อื่น ๆ | `safe`, `min_share_ge_half` | 6 task ใน OvR มีคลาส "minority" ≥ 50% (IR < 1) |

ตรวจสอบเบื้องต้น: yeast4 N 1,484 n_min 51 IR 28.1, glass2 17 / 11.59, abalone19 32 / 129.4 ตรงกับค่าที่ KEEL ประกาศ

## ไฟล์
- `catalog.py` → `file_catalog.csv` · `match.py` · `verify.py` → `verifiability_entries.csv` (1,653 แถว คอลัมน์ `verif`)
- `verified_files.csv` 125 ไฟล์ที่ตรวจได้ · `measure.py` → `difficulty_measures.csv` (263 task)
- รันใน cloud scratchpad ต้องมีไฟล์ mirror ใน `src/` ยังไม่ได้ย้ายเข้า `build/`

## อัปเดต 28 ต.ค. (รอบ 2): ดึงไฟล์ที่ไม่ใช่ KEEL + density + จัดกลุ่ม
- `V-name_only_other` 29 entry (9 paper): paper ไม่พิมพ์ขนาด ชื่อตรงกับไฟล์ที่ไม่ใช่ KEEL
  แหล่ง: PMLB 12 ไฟล์ 26 entry (adult, balance_scale, dermatology, ecoli, lymphography, new_thyroid, page_blocks, pendigits, shuttle, spect, wine_quality_red, yeast);
  ไฟล์ UCI ต้นฉบับที่มากับ imbalanced-databases 2 ไฟล์ 3 entry (glass, hepatitis)
  ไม่นับ modified 9 entry (เหตุผลเดียวกับ KEEL 19 entry) · ตรวจได้รวม **643 entry 61 paper**
- `version_risk` ขนาดไฟล์ไม่ใช่ขนาดที่ corpus พิมพ์บ่อยที่สุด: ecoli (PMLB 327 vs 336), yeast (1479 vs 1484), dermatology (366 vs 358 KEEL), shuttle (58000 vs หลายเวอร์ชัน), adult (48842 vs 32562), spect (267 vs 268), balance_scale (ไม่มีขนาดใน corpus เลย) = 31 task
- hepatitis ไฟล์ UCI มีค่าหายจนแถวถูกตัด 75 จาก 155 (เหลือ 80)
- **density / มิติ** (คอลัมน์ใหม่): `T2_points_per_dim` = N / มิติหลัง encode, `T4_pca95_share` = สัดส่วนมิติ PCA ที่อธิบาย 95%, `min_knn_dist` `maj_knn_dist` = ระยะเฉลี่ยถึงเพื่อนบ้านคลาสเดียวกัน 5 ตัว, `min_sparsity_ratio` = min/maj (> 1 แปลว่า minority กระจายห่างกว่า)
- measures รอบนี้ 291 task (binary 104, OvR 178, binarize 9)

## การจัดกลุ่มชั่วคราว (`group.py` → `difficulty_groups.csv`, ปรับ 28 ต.ค. รอบ 3)
- **คำตัดสินของ Toon** ยุบ overlap เป็น noise: ประเภทมี 3 แบบ safe / noise (= borderline + outlier) / rare (small disjuncts)
- กติกา: safe ถ้า safe ≥ 0.5 ไม่งั้นเลือกค่าที่มากกว่าระหว่าง noise กับ rare · small sample: minority ต่อ feature < 5 · ตัด 7 task ที่ "minority" ≥ 50%
- ผล 284 task: safe 184, noise 97, rare 3 · small sample 84 · เฉพาะ binary+binarize 113 task: safe 59, noise 52, rare 2 · small sample 57
- `version_note` (32 task รวม 1 task ที่ถูกตัดเพราะ minority ≥ 50%): **คำตัดสินของ Toon** เก็บไว้ทั้งหมด ใช้โครงสร้างของไฟล์ตามชื่อที่ paper ยกมา และจดว่า paper บอกแค่ชื่อ ไม่บอกขนาดหรือสัดส่วนคลาส
- `verifiability_entries.csv` คอลัมน์ `note_structure` ระบุ entry ที่ paper บอกแค่ชื่อ (109 entry: KEEL 80 + อื่น 29)

## ความไวต่อเกณฑ์ (`group_sensitivity.csv`)
- safe 0.4 / 0.5 / 0.6 × small sample 3 / 5 / 10 เทียบกับ 0.5 / 5
- ประเภทเปลี่ยน ≤ 5.6% ของ task (safe 168–197) · small sample เปลี่ยนมาก: 53 / 84 / 149 task ที่เกณฑ์ 3 / 5 / 10

## อัปเดต 28 ต.ค. (รอบ 4): rare ตาม Napierala §5.2.1 + เกณฑ์ที่มีอ้างอิง
- ใช้ `measure.py` (แก้แล้ว) → `difficulty_measures.csv` แล้ว `group_cited.py` → `difficulty_groups_cited.csv` → `profile_final.py`, `fig_noise.py`
- **ล้าสมัย**: `group.py`, `difficulty_groups.csv`, `group_sensitivity.csv`, `verified_tasks.csv`
- mirror: `fetch_mirrors.sh` · ตรวจกับตาราง KEEL ทางการ: `keel_official_check.csv` · bib: `difficulty_refs.bib`
- **คำตัดสินของ Toon 28 ต.ค.** ไม่นับ modified ที่ไม่พิมพ์ขนาด (28 entry) เพราะไม่รู้ลักษณะ/สัดส่วนของข้อมูลที่ใช้จริง (แนวทาง ก)

## อัปเดต 28 ต.ค. (รอบ 5): HVDM + ภาพสำหรับ Atlas
- `measure.py` ใช้ HVDM (Wilson & Martinez 1997) สำหรับเพื่อนบ้านทุกตัว · ค่าเดิมแบบ Euclidean: `difficulty_measures_euclidean.csv`
- `projection.py` → `projections.json` (ต้องมี src/ จาก `fetch_mirrors.sh`) · ลำดับ rebuild: measure.py → group_cited.py → profile_final.py → fig_noise.py / structure_check.py / category_options.py / dimension_profile.py → projection.py → ../build/make_atlas.py
