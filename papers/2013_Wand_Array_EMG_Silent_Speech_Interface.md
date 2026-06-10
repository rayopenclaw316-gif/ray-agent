# Array-based Electromyographic Silent Speech Interface

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 會議 | BIOSIGNALS 2013（International Conference on Bio-inspired Systems and Signal Processing），pp. 89–96 |
| DOI | 10.5220/0004252400890096 |
| 年份 | 2013 |
| 作者 | Michael Wand, Christopher Schulte, Matthias Janke, Tanja Schultz |
| 機構 | Cognitive Systems Lab, Karlsruhe Institute of Technology（KIT），德國 |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/Wand array-based electromyographic silent speech interface 2013.pdf` |
| **地位** | EMG-based SSR 領域首篇引入「陣列電極」（而非單點電極）的論文，標誌從少通道向 HD-sEMG 過渡的開端 |

---

## 2. 一句話總結

**重要注意：本文任務為有聲語音（audible speech），非默語（silent speech）**，英語 108 詞彙連續辨識。以 OT Bioelettronica EMG-USB2 採集 16/35 通道電極陣列（臉頰 + 下巴），引入 **PCA 降維**解決多通道「維度詛咒」問題，再以 **ICA 信號源分離**進一步改善辨識——最佳結果 WER 10.9%（35 通道，160 訓練句，PCA+LDA）。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 首次以**電極陣列**（而非散點貼附的少量電極）採集 EMG 語音訊號，提供空間連續的肌肉活化資訊，並大幅縮短準備時間 |
| 2 | 提出 **PCA + LDA** 組合降維，解決通道數增加導致的 LDA 稀疏性問題（維度詛咒），使更寬的時域上下文堆疊成為可行 |
| 3 | 首次將 **ICA（獨立成分分析）**應用於陣列 EMG 語音訊號源分離，最高相對改善 WER 達 22.9% |

---

## 4. 電極配置（兩種設置）

| 設置 | 電極陣列 | 通道數 | 量測方式 | IED |
|------|---------|--------|---------|-----|
| **Setup A** | 臉頰 1×8 + 下巴 1×8 | 16 | Unipolar（單極）| 5 mm |
| **Setup B** | 臉頰 4×8 + 下巴 1×8 → 35 bipolar | 35 | Bipolar（相鄰差分）| 10 mm |

- 採集設備：OT Bioelettronica EMG-USB2（最多 256 通道）
- 增益：1000×；帶通：3–900 Hz；採樣率：2048 Hz
- 參考電極：頸部

**電極位置：臉頰（顴大肌、頰肌等主要發音肌群）+ 下巴（舌肌相關）**
- 注意：無頸部電極——與 Zhu (2021) 發現「頸部更重要」對比

---

## 5. 實驗設定

- 任務：**有聲連續英語語音辨識**（108 詞彙，LVCSR 子集）
- 訓練量：Set 1（~40 句）/ Set 2（160 句）
- 特徵：時域特徵 TD_n（高頻 + 低頻成分各 5 維 × 通道數）→ 上下文堆疊 → PCA（可選）→ LDA 壓至 32 維
- 模型：3-state 左到右全連續 HMM，BDPF 音素特徵，Trigram LM（perplexity 24.24）
- 評估指標：WER（詞錯率）

---

## 6. 主要結果

| 設置 | 無 PCA | PCA | PCA + ICA |
|------|--------|-----|-----------|
| A-1（16ch, 40句）| 46.3% | 40.1% | 35.7% |
| **A-2（16ch, 160句）** | 17.0% | 13.9% | **12.1%** |
| B-1（35ch, 40句）| 50.5% | 44.9% | 40.8% |
| **B-2（35ch, 160句）** | 13.4% | **10.9%** | 11.8% |

**關鍵觀察：**
- Setup B（35 通道）加 PCA 前，因維度詛咒反而比 Setup A（16 通道）**更差**（50.5% vs 46.3%）
- 加 PCA 後，35 通道才真正優於 16 通道
- 訓練資料量（160 vs 40 句）的影響比通道數更顯著

---

## 7. 限制

1. **有聲語音，非默語**：論文名稱含「Silent Speech Interface」但實際測試是 audible speech——與 sEMG-SSR 核心任務不完全一致
2. **英語，非中文**：無法直接與中文 SSR 結果比較
3. **傳統 HMM 框架**：非端對端，依賴音素強制對齊和語言模型
4. **少量受試者**：3–7 個 session，2–6 名說話者，個體差異大
5. **電極無頸部覆蓋**：Zhu (2021) 後來發現頸部比臉頰更重要，本文設計未考慮頸部

---

## 8. 與本論文的關聯

| 面向 | 關聯 |
|------|------|
| **1.2.2 電極配置（背景引用）** | 電極陣列引入 SSR 領域的先驅論文；說明從「少量散點電極」到「陣列電極」的技術演進動機 |
| **PCA 降維的必要性** | 直接示範「多通道不加降維會更差」，支持電極選擇/優化的必要性（對照 Zhu 2021 的 SFS）|
| **ICA 信號分離** | 首次在 EMG 陣列中用 ICA 分離肌肉信號源，是後續 HD-sEMG 空間分析的早期方法論 |
| **OT Bioelettronica 設備** | 使用的 EMG-USB2 是 OT Bioelettronica 商業採集系統，與 Chen/Song 2023 使用的同類系統有關聯背景 |

**在 1.2.2 中的建議引用位置：** 陣列電極方法起源的一句話背景；作為 Zhu (2021) 系統性研究的前序鋪陳。**不宜過多描述**（因為任務是 audible speech，不是 silent speech）。

---

## 9. 引用關鍵資訊

> Michael Wand, Christopher Schulte, Matthias Janke, and Tanja Schultz, "Array-based electromyographic silent speech interface," in *Proc. Int. Conf. Bio-inspired Systems and Signal Processing (BIOSIGNALS)*, 2013, pp. 89–96. DOI: 10.5220/0004252400890096

**引用重點：**
- 首次引入電極陣列（vs 傳統少量散點電極）於 EMG 語音辨識
- PCA 降維解決多通道維度詛咒
- 16 通道 → 35 通道需搭配 PCA 才有效

---

## 10. 關鍵詞

Array EMG, electrode array, ICA, PCA, dimensionality reduction, HMM, EMG speech recognition, OT Bioelettronica, silent speech interface, KIT, Schultz group
