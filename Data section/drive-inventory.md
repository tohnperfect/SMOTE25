# สารบัญไฟล์ใน Google Drive: SMOTE25

นับแบบ **หนึ่ง paper เท่ากับหนึ่งรายการ** ถึงแม้ไฟล์เดียวกันจะวางซ้ำอยู่สองโฟลเดอร์ คอลัมน์ `หมวด` บอกว่าแต่ละเรื่องอยู่โฟลเดอร์ไหนบ้าง

ตรวจนับเมื่อ 2026-10-14 โดยไล่ทุกหน้าของทุกโฟลเดอร์แล้ว dedupe ด้วย file id

## สรุปตัวเลข

| | จำนวน |
|---|---|
| ไฟล์ทั้งหมดใน Drive | 100 |
| ไฟล์ supplementary | 12 |
| ไฟล์ที่เป็น paper (method + survey) | 88 |
| ไฟล์ที่ซ้ำข้ามโฟลเดอร์ | 12 |
| **paper ที่ต่างกันจริง** | **76** |

ไฟล์ paper ต่อโฟลเดอร์ (ยังไม่หักซ้ำ): Binary 24, Both 41, Multiclass 21, Survey 2 รวม 88

## paper ที่อยู่สองโฟลเดอร์ (12 เรื่อง นับเป็นเรื่องละ 1)

| วิธี | หมวด | ชื่อไฟล์ทั้งสองฝั่ง |
|---|---|---|
| Borderline-SMOTE | Binary + Both | `Borderline-SMOTE.pdf`<br>`Borderline-SMOTE - A New Over-Sampling Method in Imbalanced Data Sets Learning (ICIC 2005).pdf` |
| CBHSID | Multiclass + Both | `2022_CBHSID_A hybrid sampling approach for imbalanced binary and multi-class data using clustering analysis.pdf`<br>`CBHSID - A Hybrid Sampling Approach for Imbalanced Binary and Multi-Class Data Using Clustering Analysis (IEEE Access 2022).pdf` |
| DSRBF / Static-SMOTE | Multiclass + Both | `2011_DSRBF_A dynamic over-sampling procedure based on sensitivity for multi-class problems.pdf`<br>`Static-SMOTE - A Dynamic Over-Sampling Procedure Based on Sensitivity for Multi-Class Problems (Pattern Recognition 2011).pdf` |
| MC-CCR | Multiclass + Both | `2020_MC-CCR_Combined Cleaning and Resampling Algorithm for Multi-Class Imbalanced Data with Label Noise.pdf`<br>`MC-CCR - Combined Cleaning and Resampling Algorithm for Multi-Class Imbalanced Data with Label Noise (Knowledge-Based Systems 2020).pdf` |
| MC-RBO | Multiclass + Both | `2020_MC-RBO_Radial-Based Oversampling for Multiclass Imbalanced Data Classification.pdf`<br>`MC-RBO - Radial-Based Oversampling for Multiclass Imbalanced Data Classification (IEEE TNNLS 2020).pdf` |
| MDO | Multiclass + Both | `2016_MDO_To Combat Multi-Class Imbalanced Problems by Means of Over-Sampling Techniques.pdf`<br>`MDO - To Combat Multi-Class Imbalanced Problems by Means of Over-Sampling Techniques (IEEE TKDE 2016).pdf` |
| MWMOTE | Binary + Both | `MWMOTE.pdf`<br>`MWMOTE - Majority Weighted Minority Oversampling Technique for Imbalanced Data Set Learning (IEEE TKDE 2014).pdf` |
| OREM-M | Multiclass + Both | `2023_OREM-M_Oversampling With Reliably Expanding Minority Class Regions for Imbalanced Data Learning.pdf`<br>`OREM - Oversampling With Reliably Expanding Minority Class Regions for Imbalanced Data Learning (IEEE TKDE 2023).pdf` |
| SMOM | Multiclass + Both | `2017_SMOM_Synthetic minority oversampling technique for multiclass imbalance problems.pdf`<br>`SMOM - Synthetic Minority Oversampling Technique for Multiclass Imbalance Problems (Pattern Recognition 2017).pdf` |
| SMOTE | Binary + Both | `SMOTE (Original).pdf`<br>`SMOTE - Synthetic Minority Over-Sampling Technique (JAIR 2002).pdf` |
| SMOTE-ENN / SMOTE-Tomek | Binary + Both | `2004 SMOTE-ENN, SMOTE-Tomek - Batista, Prati, Monard.pdf`<br>`SMOTE-Tomek & SMOTE-ENN (Batista) - A Study of the Behavior of Several Methods for Balancing Machine Learning Training Data (SIGKDD Explorations 2004).pdf` |
| Safe-Level-SMOTE | Binary + Both | `SafeLavel.pdf`<br>`Safe-Level-SMOTE - Safe-Level-Synthetic Minority Over-Sampling Technique for Handling the Class Imbalanced Problem (PAKDD 2009).pdf` |

ทั้ง 12 คู่ยืนยันว่าเป็นเอกสารเดียวกัน จากขนาดไฟล์ที่เท่ากันหรือต่างกันไม่กี่ไบต์ และจากเนื้อหาที่อ่านแล้วตรงกัน

## รายการทั้งหมด 76 เรื่อง

| # | วิธี | ปี | venue | หมวด | สถานะระเบียน |
|---|---|---|---|---|---|
| 1 | ENN (Wilson) | 1972 | IEEE TSMC | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 2 | Tomek Links | 1976 | IEEE TSMC | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 3 | AdaBoost | 1997 | JCSS | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 4 | OSS | 1997 | ICML | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 5 | SHRINK | 1998 | Machine Learning | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 6 | SMOTE | 2002 | JAIR | Binary + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 7 | SMOTEBoost | 2003 | PKDD | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 8 | SMOTE-ENN / SMOTE-Tomek | 2004 | SIGKDD Explorations | Binary + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 9 | Borderline-SMOTE | 2005 | ICIC | Binary + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 10 | Cluster-SMOTE | 2006 | IEEE GrC | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 11 | Global-CS (AAAI) | 2006 | AAAI | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 12 | COG-OS | 2007 | KDD | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 13 | ADASYN | 2008 | IEEE IJCNN | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 14 | LS | 2008 | IEEE ICDM | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 15 | ClusterCentroids | 2009 | Expert Systems with Applications | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 16 | EasyEnsemble / BalanceCascade | 2009 | IEEE TSMC-B | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 17 | Safe-Level-SMOTE | 2009 | PAKDD | Binary + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 18 | Global-CS (journal) | 2010 | Computational Intelligence | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 19 | RAMOBoost | 2010 | IEEE TNN | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 20 | RUSBoost | 2010 | IEEE TSMC-A | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 21 | SPIDER2 | 2010 | RSCTC | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 22 | DSRBF / Static-SMOTE | 2011 | Pattern Recognition | Multiclass + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 23 | INOS | 2013 | IEEE TKDE | Both | **ยังไม่สกัด** |
| 24 | OVO-SMOTE | 2013 | Knowledge-Based Systems | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 25 | MWMOTE | 2014 | IEEE TKDE | Binary + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 26 | RACOG / wRACOG | 2015 | IEEE TKDE | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 27 | RBBoost / Random Balance | 2015 | Knowledge-Based Systems | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 28 | SCUT | 2015 | KDIR | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 29 | SMOTE-IPF | 2015 | Information Sciences | Both | **ยังไม่สกัด** |
| 30 | SplitBal | 2015 | Pattern Recognition | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 31 | A-SUWO | 2016 | Expert Systems with Applications | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 32 | CGMOS | 2016 | ACM CIKM | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 33 | MDO | 2016 | IEEE TKDE | Multiclass + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 34 | SMOM | 2017 | Pattern Recognition | Multiclass + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 35 | AMDO | 2018 | IEEE TKDE | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 36 | k-means SMOTE | 2018 | Information Sciences | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 37 | OBU | 2018 | IDEAL | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 38 | ROS (Buda) | 2018 | Neural Networks | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 39 | CTGAN / TVAE | 2019 | NeurIPS | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 40 | G-SMOTE | 2019 | Information Sciences | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 41 | GAMO | 2019 | ICCV | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 42 | RBO | 2019 | Neurocomputing | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 43 | SOUP | 2019 | AMCS | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 44 | AB-SMOTE | 2020 | IJMLC | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 45 | DLexiBoost | 2020 | IEEE TKDE | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 46 | MBS | 2020 | IEEE TKDE | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 47 | MC-CCR | 2020 | Knowledge-Based Systems | Multiclass + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 48 | MC-RBO | 2020 | IEEE TNNLS | Multiclass + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 49 | NBU | 2020 | Information Sciences | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 50 | SPE | 2020 | IEEE ICDE | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 51 | EMDO | 2021 | Sensors | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 52 | HDE | 2021 | Information Sciences | Both | **ยังไม่สกัด** |
| 53 | RSMOTE | 2021 | Information Sciences | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 54 | Survey: SMOTE Review | 2021 | IEEE conference | Survey | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 55 | CBHSID | 2022 | IEEE Access | Multiclass + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 56 | FW-SMOTE | 2022 | Pattern Recognition | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 57 | GDO | 2022 | IEEE TKDE | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 58 | KNNOR | 2022 | Applied Soft Computing | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 59 | SHSampler | 2022 | IEEE conference | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 60 | SOS | 2022 | KDD | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 61 | Survey: Stop Oversampling | 2022 | Preprint (Elsevier) | Survey | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 62 | SVDD-WSMOTE | 2022 | Information Sciences | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 63 | GLOS | 2023 | IJMLC | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 64 | NROMM | 2023 | Pattern Recognition | Both | **ยังไม่สกัด** |
| 65 | OREM-M | 2023 | IEEE TKDE | Multiclass + Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 66 | GMMSampling | 2024 | Machine Learning | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 67 | MC-MBRC | 2024 | Expert Systems with Applications | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 68 | MKC-SMOTE | 2024 | IEEE Access | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 69 | CISO | 2025 | arXiv preprint | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 70 | GDHS | 2025 | Neurocomputing | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 71 | GOIO | 2025 | IEEE TKDE | Both | **ยังไม่สกัด** |
| 72 | MC-NCLWO | 2025 | IEEE Access | Multiclass | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 73 | MLOS | 2025 | Expert Systems with Applications | Both | มีระเบียนรอบแรก (ยังไม่ตรวจ) |
| 74 | DGOT | 2026 | IEEE TKDE | Both | **ยังไม่สกัด** |
| 75 | Loyalty-SMOTE | 2026 | Neural Networks | Both | **ยังไม่สกัด** |
| 76 | QC-SMOTE | 2026 | Preprint (Elsevier) | Binary | มีระเบียนรอบแรก (ยังไม่ตรวจ) |

## ไฟล์ supplementary 12 ไฟล์

ไม่นับเป็น paper แยก ผูกกับ paper หลักดังนี้

| paper หลัก | ไฟล์ |
|---|---|
| CTGAN / TVAE | `CTGAN-TVAE - Supplementary (NeurIPS 2019).pdf` |
| DLexiBoost | `DLexiBoost - Supplementary (IEEE TKDE 2020).pdf` |
| FW-SMOTE | `FW-SMOTE - Supplementary (Pattern Recognition 2022).pdf` |
| GAMO | `GAMO - Supplementary (ICCV 2019).pdf` |
| NROMM | `NROMM - Supplementary (Pattern Recognition 2023).pdf` |
| OREM-M | `OREM - Supplementary 54pp (IEEE TKDE 2023).pdf` |
| RBBoost / Random Balance | `RBBoost - Supplementary (Knowledge-Based Systems 2015).pdf` |
| ROS (Buda) | `ROS (Buda) - Supplementary 1 Appendix A Reshuffled Splits (Neural Networks 2018).pdf` |
| ROS (Buda) | `ROS (Buda) - Supplementary 2 Appendix B Convergence Plots (Neural Networks 2018).pdf` |
| ROS (Buda) | `ROS (Buda) - Supplementary 3 Appendix C Confusion Matrices (Neural Networks 2018).pdf` |
| ROS (Buda) | `ROS (Buda) - Supplementary 4 Appendix C.2 Confusion Matrices CIFAR-10 (Neural Networks 2018).pdf` |
| SMOM | `SMOM - Supplementary (Pattern Recognition 2017).pdf` |

OREM supplementary ยาว 54 หน้า และ ROS (Buda) มี supplementary ถึง 4 ไฟล์ ทั้งสองชุดมีตารางผลรายชุดข้อมูลที่อาจจำเป็นตอนกรอกคอลัมน์ outcome

## 7 เรื่องที่เพิ่งพบว่าขาดไป

รอบแรกไล่ไฟล์ด้วย Drive connector แล้ว pagination ข้ามไฟล์ไปเงียบ ๆ จึงได้มาแค่ 69 เรื่อง ทั้ง 7 เรื่องนี้อยู่ในโฟลเดอร์ Both และถูกเพิ่มเข้าชีต `papers` แล้ว โดยเว้นทุกช่องให้กรอกจาก PDF เอง

| วิธี | ปี | venue |
|---|---|---|
| INOS | 2013 | IEEE TKDE |
| SMOTE-IPF | 2015 | Information Sciences |
| HDE | 2021 | Information Sciences |
| NROMM | 2023 | Pattern Recognition |
| GOIO | 2025 | IEEE TKDE |
| DGOT | 2026 | IEEE TKDE |
| Loyalty-SMOTE | 2026 | Neural Networks |

สามเรื่องเป็นงานปี 2025 ถึง 2026 และสองเรื่องเป็นสาย generative หรือ diffusion ซึ่งเป็นช่วงเวลาที่ survey ของ Fernández et al. 2018 ไม่ครอบคลุม จึงเป็นส่วนที่ใช้แยกตัวเองจากงานนั้นได้