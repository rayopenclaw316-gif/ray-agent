# Extracting Spatial Muscle Activation Patterns in Facial and Neck Muscles for Silent Speech Recognition Using High-Density sEMG

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊 | IEEE Transactions on Instrumentation and Measurement, Vol. 72, 2023, Article 4006313 |
| DOI | 10.1109/TIM.2023.3277930 |
| 年份 | 2023（投稿 2022-12-29；修訂 2023-04-10；接受 2023-04-25；線上 2023-05-22）|
| 作者 | Xin Tan, Xinyu Jiang, Zhanhui Lin, Xiangyu Liu, Chenyun Dai, Wei Chen |
| 機構 | Center for Intelligent Medical Electronics, School of Information Science and Technology, Fudan University, Shanghai |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/Extracting_Spatial_Muscle_Activation_Patterns_in_Facial_and_Neck_Muscles_for_Silent_Speech_Recognition_Using_High-Density_sEMG.pdf` |
| **定位** | 首篇以 320 通道 HD-sEMG 系統性量化音素級臉頸部肌肉空間活化模式（RMS 熱圖），比較有聲與無聲說話模式的差異，並提供電極配置設計的空間分佈依據 |

---

## 2. 一句話總結

復旦大學 Fudan CIME 組：以 **320 通道臉頸部 HD-sEMG** 對 10 名受試者進行 14 個母音與 15 個輔音（英語）的有聲/無聲說話模式比較，透過 RMS 熱圖量化發現臉頸部活化高度對稱（相關係數 > 0.9）、臉部集中於顴大肌/提口角肌、頸部集中於頸闊肌/胸鎖乳突肌；在 SS 模式下以全陣列 PCA+LDA 達到輔音 **85.78%**、母音 **79.42%** 的音素分類準確率，且明確指出下巴電極（頦肌，B1）對分類準確率有不可替代的貢獻。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 首次以 320 通道覆蓋臉部（顴/頰/下巴）與頸部（頸闊肌/胸鎖乳突肌）的 HD-sEMG，完整可視化音素級 SAMGs 空間活化模式（RMS 熱圖），提供電極設計的生理依據 |
| 2 | 量化臉頸部肌肉的左右對稱性（面部 PCC = 0.86–0.99，頸部 PCC = 0.57–0.93），顯示 SS 模式下頸部對稱性顯著低於 AS 模式（無聲帶振動）；此差異支持以單側覆蓋減少電極冗餘 |
| 3 | 以電極組合消融實驗量化各肌群對分類準確率的貢獻：加入下巴電極（B1）一致顯著提升準確率（p < 0.01），面部 ≈ 頸部貢獻（無顯著差異，p = 0.682） |

---

## 4. 背景與動機

**問題定位：**
1. 大多數早期 sEMG-SSR 研究依靠先驗知識經驗性決定電極位置，缺乏量化分析
2. 有聲（AS）vs. 無聲（SS）說話模式下 sEMG 信號差異尚未充分研究
3. 現有 SSR 研究聚焦詞彙分類，音素級辨識尚缺乏系統性探索

**電極設計的核心困難：**
- 說話涉及臉頸部數十條肌肉協作，不同音素的活化模式重疊
- 傳統少通道電極無法可視化空間分佈，導致次優電極選擇
- SS 模式下 sEMG 振幅普遍小於 AS（缺乏聽覺回饋 → 說話力量較弱）

---

## 5. 資料集

**硬體設備：**

| 裝置 | 規格 |
|------|------|
| 採集系統 | Quattrocento（OT Bioelettronica），16-bit ADC，採樣率 2048 Hz，增益 150 |
| 電極類型 | 凝膠電極，橢圓形（5 mm × 2.8 mm），中心距 10 mm（A1–A4）；2.5 mm 中心距（B1） |

**電極配置（320 通道，5 陣列）：**

| 陣列 | 位置 | 目標肌群 |
|------|------|---------|
| A1（8×8, 64ch）| 左臉 | 顴大肌（zygomaticus）、頰肌（buccinators）、提口角肌（levator anguli oris）|
| A2（8×8, 64ch）| 右臉 | 同 A1（對稱）|
| B1（5×13, 65ch）| 下巴/頦部 | 頦肌（mentalis）、降下唇肌（depressor labii inferioris）|
| A3（8×8, 64ch）| 左頸 | 頸闊肌（platysma）、胸鎖乳突肌、環甲肌、甲狀舌骨肌 |
| A4（8×8, 64ch）| 右頸 | 同 A3（對稱）|

- 參考電極：左右耳後乳突
- 阻抗：< 5 kΩ（全通道）

**受試者：**
- 10 人（男 9、女 1），年齡 21–35（均值 25.1±3.8）
- 第二母語英語使用者，無語言或聽力障礙
- 倫理核准：復旦大學（BE2035）

**任務：**
- 14 個英語母音 + 15 個英語輔音（IPA 音素）
- 各音素重複 2 組（block）× 3 次 = 6 次試驗
- 每次試驗：1 秒說話 + 1 秒休息；組間休息 5 秒
- AS session 與 SS session 各一，電極不重新貼附

---

## 6. 方法概述

**前處理：**
- 10 Hz 高通 + 500 Hz 低通（Butterworth，零相位，各方向 8 階）
- 50 Hz 及諧波陷波濾波
- 每次試驗去除前 0.25 s 反應期，保留後 0.75 s 穩定段

**特徵提取（4 種時域特徵）：**
- RMS（均方根）：量化肌肉活化強度，用於熱圖可視化
- WL（波形長度）：訊號複雜度
- ZC（過零率）：時域變化
- SSC（斜率符號變化）：頻率相關資訊
- 每通道 4 特徵 → 1280 維特徵向量（320 ch × 4）

**空間活化分析：**
- RMS 熱圖（2D）：8×8（A1–A4）和 5×13（B1）
- 質心座標計算（式 5–6）
- 左右對稱性：Pearson 相關係數（PCC，式 7）
- 肌群相似度：歸一化相似度計算（式 8）

**分類：**
- PCA 降維（保留 Ns−1 維）+ LDA 分類
- 6-fold 交叉驗證（各音素 6 次試驗）
- 各電極組合分別測試（全陣列 / 不同子集）

---

## 7. 主要結果

**音素分類準確率（SS 模式，LDA，10 受試者均值）：**

| 電極組合 | SS 母音（%）| SS 輔音（%）|
|---------|------------|------------|
| 全陣列（All） | 79.42±10.11 | 85.78±6.54 |
| A1+A2+A3+A4（無下巴）| 71.43±14.24 | 82.87±7.15 |
| A1+A2+B1 | 69.49±10.94 | 76.30±12.34 |
| A3+A4+B1 | 72.26±10.55 | 79.30±8.26 |
| A1+A3+B1 | 75.85±12.87 | 80.41±7.42 |
| A2+A4+B1 | 71.43±10.51 | 79.54±9.47 |
| B1（下巴單獨）| 49.55±13.37 | 48.54±11.16 |

**關鍵統計結論：**
- B1（下巴/頦肌）顯著提升各組準確率（p < 0.01）
- 面部 A1+A2 ≈ 頸部 A3+A4（p = 0.682，無顯著差異）
- SS 模式輔音 > 母音（p < 0.001）；AS 模式無此差異

**左右對稱性（PCC）：**
- 臉部 X 方向：PCC = 0.86（p < 10⁻⁶）
- 頸部 Y 方向：PCC = 0.72（p < 10⁻⁶）
- 整體：all tasks > 82% similarity，最高達 99%

**AS vs SS 對稱性差異：**
- 臉部：AS ≈ SS（p = 0.085–0.099，無顯著差異）
- **頸部：AS > SS**（p < 10⁻⁵）；推測因 AS 模式有聲帶振動帶動頸肌協調，SS 模式頸肌僅捕捉微弱的喉部活動

---

## 8. 消融與比較分析

**電極組合加入 B1（下巴）的效果：**
- A1+A2+B1 > A1+A2（p = 0.011）
- A3+A4+B1 > A3+A4（p = 0.003）
- A1+A3+B1 > A1+A3（p = 0.001）
- A2+A4+B1 > A2+A4（p = 0.004）

→ 頦肌/降下唇肌區域攜帶不可被臉頰或頸部替代的辨識資訊

**SS 模式輔音 > 母音的原因（論文推論）：**
- 輔音發音時氣流較強，肌肉收縮更強烈 → 訊號振幅更高 → 辨識更容易
- 母音發音時各發音器官維持相對平衡張力 → 肌電模式差異較小

---

## 9. 限制與未來工作

1. **任務為英語音素，10 受試者**：分類準確率有待在更大語料庫和更多受試者上驗證
2. **PCA+LDA 分類器**：準確率未充分發揮 HD-sEMG 的全部資訊，深度學習分類器有望大幅提升
3. **320 通道系統不實用**：準備時間長、凝膠電極難以固定於臉部動態表面，需轉換為精簡實用系統
4. **應加入失語症患者**：目前僅健康受試者，臨床應用需要患者資料驗證

---

## 10. 與本論文的關聯

| 面向 | 關聯 |
|------|------|
| **1.2.2 電極空間分佈依據** | 提供音素級臉頸部肌肉活化的空間可視化（熱圖），量化確認臉部活化集中於顴大肌/提口角肌、頸部集中於頸闊肌/胸鎖乳突肌——為電極位置選擇提供生理解剖根據，補充 Zhu 2021 的電極篩選演算法 |
| **1.2.2 下巴電極的重要性** | 頦肌（B1）加入一致顯著提升分類準確率（p < 0.01）；本研究設計涵蓋頦肌在內的電極配置有此文獻支撐 |
| **1.2.2 面頸部貢獻的量化** | 面部 ≈ 頸部貢獻（p = 0.682），與 Zhu 2021 的頸部優先結論形成有趣對比，可能因任務（英語音素 vs. 中文數字）和特徵設計不同 |
| **1.2.2 SS vs AS 的電極設計差異** | SS 模式下頸部對稱性顯著下降，提示無聲語音場景的電極設計應重新評估頸部陣列的最適位置 |

---

## 11. 引用關鍵資訊

> Xin Tan, Xinyu Jiang, Zhanhui Lin, Xiangyu Liu, Chenyun Dai, and Wei Chen, "Extracting Spatial Muscle Activation Patterns in Facial and Neck Muscles for Silent Speech Recognition Using High-Density sEMG," *IEEE Transactions on Instrumentation and Measurement*, vol. 72, pp. 1–13, 2023. DOI: 10.1109/TIM.2023.3277930

**引用重點：**
- 320 通道臉頸部 HD-sEMG 音素級活化熱圖
- 臉部活化：顴大肌/提口角肌；頸部活化：頸闊肌/胸鎖乳突肌
- 下巴電極（頦肌）對分類準確率有不可替代的貢獻
- SS 模式：輔音 85.78% > 母音 79.42%；面部 ≈ 頸部貢獻
- SS 模式頸部左右對稱性顯著低於 AS（因無聲帶振動）

---

## 12. 關鍵詞

HD-sEMG, high-density sEMG, silent speech recognition, phoneme-level, spatial activation pattern, RMS heat map, electrode design, facial muscles, neck muscles, SAMG, zygomaticus, platysma, mentalis, PCA, LDA, audible vs. silent speech, electrode configuration, Fudan University
