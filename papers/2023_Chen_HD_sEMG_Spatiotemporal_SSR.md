# Decoding Silent Speech Based on High-Density Surface Electromyogram Using Spatiotemporal Neural Network

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊 | IEEE Transactions on Neural Systems and Rehabilitation Engineering, Vol. 31, 2023, pp. 2069–2078 |
| DOI | 10.1109/TNSRE.2023.3266299 |
| 年份 | 2023（投稿 2022-08-30；接受 2023-03-01；發表 2023-04-11；線上 2023-04-26）|
| 作者 | Xi Chen, Xu Zhang（通訊）, Xiang Chen, Xun Chen |
| 機構 | School of Information Science and Technology, USTC（中國科學技術大學），Hefei, Anhui 230027 |
| 資助 | National Natural Science Foundation of China (62271464) |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/Decoding_Silent_Speech_Based_on_High-Density_Surface_Electromyogram_Using_Spatiotemporal_Neural_Network (1).pdf` |
| **姊妹論文** | Song et al. (2023)，同組同語料庫，對比 Transformer encoder-decoder 方法 |

---

## 2. 一句話總結

USTC Xu Zhang 組：64 通道高密度 sEMG + CNN 空間塊（8×8 影像）+ BiLSTM 時序塊 + CTC 解碼器（CBiL-CTC），搭配編輯距離語言模型，在 15 名受試者、33 中文片語任務上達到 **CER 3.11 ± 1.46%、片語準確率 97.17 ± 1.53%**，優於純 BiLSTM（4.76%）與孤立詞分類方法，證明空間特徵對中文 sEMG 音節級解碼的關鍵作用。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 提出**空時端對端神經網路（CBiL-CTC）**：CNN 提取 HD-sEMG 空間特徵（臉部肌群位置分布）+ BiLSTM 提取時序語義 + CTC 解碼，無需幀級手動對齊 |
| 2 | 以 4 件 64 通道電極陣列（雙側臉部 + 喉頸部）實現**多部位聯合高密度電極配置**，電極信號重排為 8×8 影像以利空間 CNN 處理 |
| 3 | 消融實驗明確顯示 **CNN 空間塊的貢獻**：去除 CNN（BiL-CTC）CER 上升至 4.76%（+1.65%），語言模型對片語準確率的提升優於純解碼改善 |

---

## 4. 背景與動機

**問題定位：**
1. 傳統分類方法（SVM、LDA、CNN、BiLSTM 分類器）將整段片語當作單一模式，忽略音節間的語法與語境關係
2. HMM 型連續語音辨識需要大量幀級對齊訓練資料，技術門檻高
3. HD-sEMG 的空間資訊（肌群位置分布）尚未被 sEMG-SSR 充分利用

**本文切入點：**
- CTC 消除對齊需求，直接訓練序列到序列映射
- CNN 將 64 通道排列成 8×8 影像，提取臉頸肌群的空間活化模式
- BiLSTM 捕捉音節序列的時間語境關係

**與 Song et al. (2023)（同組）的差異：**

| 面向 | 本文（Chen 2023）| Song (2023) |
|------|-----------------|------------|
| 特徵提取 | CNN 空間塊（影像化 HD-sEMG）| Hudgins TD 特徵（256-dim 向量）|
| 解碼方式 | BiLSTM + CTC | Transformer encoder-decoder |
| 語言模型 | 編輯距離 LM | 音節相似度 LM |
| 受試者 | **15 名** | 8 名 |
| CER | **3.11 ± 1.46%** | 5.14 ± 3.28% |
| 片語準確率 | **97.17 ± 1.53%** | 96.37 ± 2.06% |

---

## 5. 資料集

**硬體設備：**

| 裝置 | 規格 |
|------|------|
| 採集系統 | 自製多通道生物電訊號採集設備 |
| 放大增益 | 64 dB（2 級放大）|
| 帶通濾波 | 20–500 Hz |
| 採樣率 | 1000 Hz |
| ADC | 16-bit A/D 轉換器 |
| 電極材料 | 直徑 5 mm 圓形探針，單極量測（monopolar）|
| 參考電極 | 耳後 uricularis posterior（雙側各一，分別作參考與接地）|

**電極配置（64 通道，4 件陣列）：**

| 陣列 | 位置 | 目標肌群 |
|------|------|---------|
| 臉部×2（雙側）| 面頰對稱貼放 | buccinator（頰肌）, masseter（咬肌）, orbicularis oris（口輪匝肌）|
| 喉頸部×2（雙側）| 喉頸部對稱貼放 | cervical muscle（頸肌）, anterior belly of digastric（二腹肌前腹）|

- 喉頸部電極間距：18 mm
- 臉部電極間距：水平 18 mm，垂直 10 mm
- 信號處理後重排為 **8×8 影像**（每像素對應 1 通道）

**受試者：**
- 15 名，年齡 21–27 歲（均值 24.53 ± 1.45）
- 全部為普通話母語者，無語言障礙
- IRB：USTC 倫理委員會核准

**語料庫（與 Song 2023 完全相同）：**
- 33 個中文片語（日常應用場景：無人機控制 T1–T9、工業控制 T10–T24、消防通訊 T25–T33）
- 82 個基本音節，加空白符號（blank, "_"）= 83 類
- 每片語 20 次默讀重複；重複間隔 4 秒
- 每受試者樣本數：33 × 20 = 660

---

## 6. 方法概述

**特徵提取：**
1. 振幅閾值法（threshold = 均值 + 3σ）偵測發音起止點，切出片語片段
2. 分幀：frame length = 200 ms，frame increment = 180 ms（敏感性分析後最優）
3. 每幀每通道提取 4 特徵：MAV（均值絕對值）+ 3 TD-PSD（時域功率頻譜描述子）
4. 64 通道 × 4 特徵 → 排列為 **8×8×4 特徵圖**（等效 T × 8 × 8 × 4）

**CBiL-CTC 架構：**

```
輸入：T × 8×8×4 特徵圖
    │
    ▼
[空間塊 Spatial Block]
  Conv2D（32 filters）→ BN → Dropout(0.2)
  Conv2D（16 filters）→ BN → Dropout(0.2)
    │
    ▼ Flatten → T × 256
[時序塊 Temporal Block]
  BiLSTM（256/256/128 neurons, 3 層）→ BN → Dropout
    │
    ▼ T × 83（音節概率）
[CTC 解碼器]
  訓練：CTC Loss = -log P(L|X)
  推理：Beam Search / Greedy Search
    │
    ▼
[語言模型 LM]
  編輯距離計算 vs 語料庫所有片語 → 取最小距離片語為最終輸出
```

**訓練設定：**
- 優化器：Nadam；lr = 0.01；500 epochs；full batch
- 框架：Keras（Python 3.6）；GPU：NVIDIA RTX 3060

---

## 7. 主要結果

| 方法 | CER (%) | 片語準確率（PCA, %）|
|------|---------|-------------------|
| SVM | — | 87.98 ± 5.26 |
| RF | — | 84.54 ± 2.17 |
| LDA | — | 88.38 ± 4.49 |
| LR | — | 85.76 ± 5.13 |
| CNN 分類 | — | 91.72 ± 4.63 |
| BiLSTM 分類 | — | 93.23 ± 2.99 |
| BiL-CTC-LM（無空間塊）| 4.76 ± 1.94 | 96.06 ± 1.52 |
| **CBiL-CTC-LM（本文）** | **3.11 ± 1.46** | **97.17 ± 1.53** |

- 5-fold cross-validation；訓練:驗證:測試 = 60:20:20
- 統計顯著性 p < 0.05（ANOVA + Bonferroni）
- CBiL-CTC 顯著優於 BiL-CTC（p = 0.026）；兩者加 LM 後無顯著差異（p = 0.841）→ LM 能補償架構差距

---

## 8. 消融實驗

| 消融項目 | 影響 |
|---------|------|
| 移除 CNN 空間塊（BiL-CTC）| CER 3.11% → 4.76%（+1.65%，相對 +53%）|
| 移除語言模型 | PCA 從 97.17% → ~95.66%（BiL-CTC 從 96.06% → ~94%）|

關鍵結論：CTC 的幀條件獨立假設不利於連續語音語境建模，但 LM 能有效補償；CNN 空間特徵在解碼層面有顯著優勢，LM 後兩者差距縮小。

---

## 9. 限制與未來工作

1. CTC 假設幀間條件獨立，不利於語境語義建模（對比 Transformer 有注意力機制）
2. 語料庫規模小（封閉 33 片語），CNN 空間特徵的優勢受限——更大語料可能放大差距
3. 未來方向：注意力機制整合入 CTC 輸出後處理（Self-attention over CTC output）

---

## 10. 與本論文的關聯

| 面向 | 關聯 |
|------|------|
| **1.2.2 電極配置** | 64 通道 HD 雙側電極陣列；空間排列成 8×8 影像作 CNN 輸入；臉部+喉頸部多位置聯合的典型設計 |
| **1.2.3 中文 SSR** | 首批以音節級**序列解碼**（非分類）處理中文 sEMG 的論文；USTC 組建立的 33 片語/82 音節語料庫基準 |
| **1.2.4 端對端演進** | CNN-BiLSTM-CTC 空時端對端架構；對比 Song (2023) 的 Transformer 方法，代表 CTC 方向的代表作 |
| **橋樑論文** | 填補 Wang/Ye (2020) 孤立詞分類 → Xie (2025) 開放詞彙句子辨識之間的「封閉詞彙序列解碼」缺口 |

---

## 11. 引用關鍵資訊

> Xi Chen, Xu Zhang, Xiang Chen, and Xun Chen, "Decoding Silent Speech Based on High-Density Surface Electromyogram Using Spatiotemporal Neural Network," *IEEE Transactions on Neural Systems and Rehabilitation Engineering*, vol. 31, pp. 2069–2078, 2023. DOI: 10.1109/TNSRE.2023.3266299

**引用重點：**
- 中文 sEMG 音節級序列解碼（非孤立詞分類）
- 64 通道 HD 電極雙側配置
- CNN 空間特徵 + CTC 端對端
- CER 3.11%（封閉 33 片語）

---

## 12. 關鍵詞

Silent speech recognition, high-density sEMG, spatiotemporal neural network, CTC, syllable-level decoding, Chinese, language model, electrode array
