# EMG-Based Cross-Subject Silent Speech Recognition Using Conditional Domain Adversarial Network

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊 | IEEE Transactions on Cognitive and Developmental Systems, Vol. 15, No. 4, pp. 2282–2290, December 2023 |
| DOI | 10.1109/TCDS.2023.3316701 |
| 年份 | 2023（投稿 2023-02-09；修訂 2023-09-04；接受 2023-09-14；線上 2023-09-18）|
| 作者 | Yakun Zhang, Huihui Cai, Jinghan Wu, Liang Xie, Minpeng Xu, Dong Ming, Ye Yan, Erwei Yin |
| 機構 | National Innovation Institute of Defense Technology, Academy of Military Sciences, Beijing；天津大學醫學工程與轉化醫學學院；天津人工智慧創新中心 |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/EMG-Based_Cross-Subject_Silent_Speech_Recognition_Using_Conditional_Domain_Adversarial_Network.pdf` |
| **定位** | 專攻跨受試者 sEMG SSR；建立 70 人中文 sEMG 資料集（101 類）；提出 ICDAN 以遷移學習補足訓練資料不足時的跨受試者性能下滑 |

---

## 2. 一句話總結

天津大學 + 軍科院聯合組：以 **70 人、101 類普通話**的大規模中文 sEMG 資料集為基礎，發現直接使用原始時序訊號（time-series features）搭配 1D-CNN 在跨受試者任務上可達 **87.80%**，並進一步提出融合 MMD 損失的改良條件域對抗網路（ICDAN），在訓練資料僅 20 人時將跨受試者準確率從 71.42% 提升 **+14.88% → 86.32%**，是目前 EMG SSR 跨受試者方向少數同時解決大詞彙量與小樣本問題的工作。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 建立**70 人中文 sEMG 語料庫**（101 類，3–5 字日常詞語）：首個用於跨受試者研究且兼具大詞彙量與多受試者的中文 sEMG 資料集 |
| 2 | 驗證**時序特徵（time-series features）**在跨受試者情境的優越性：原始訊號攜帶更多個體不變資訊，跨受試者準確率 83.61%（vs. MFCC 63.89%、Fbank 67.03%）；以 1D-CNN 取代 VGGNet 進一步提升至 87.80% |
| 3 | 提出 **ICDAN**（CDAN + MMD 損失）：在少量訓練資料（20 人）場景下，將跨受試者準確率從 71.42% 提升至 86.32%（+14.88%），優於 DDC（76.17%）、DAN（75.47%）、DANN（76.74%）、CDAN（85.38%）|

---

## 4. 背景與動機

**問題定位：**
1. 既有 EMG-SSR 研究多為單一受試者或跨時間（cross-session）場景，跨受試者研究極為稀少
2. 早期跨受試者研究（Ratnovsky et al. 2021）僅限 3 名受試者、5 類詞語，無法反映真實應用複雜度
3. 資料收集成本高，特定族群（肢體障礙者、老人）難以取得大量樣本→需要少樣本遷移方法

**跨受試者差異的物理成因（論文實測）：**
- 皮膚條件（skin condition）
- 皮下脂肪層（fat layer）——本論文最差受試者為面部鬍渣 + 頸部厚脂肪層男性，準確率僅 30.04%
- 說話習慣（speaking style）與口音（accent）
- 電極位置偏移（electrode bias）

**為何 time-series features 優於手工特徵：**
- 手工特徵（TC-4、FC-4、MFCC）在降維過程中丟失個體間共通的分類資訊
- 原始時序訊號保留了肌肉收縮的整體啟動趨勢（activation trend），跨受試者的相似性主要體現在訊號包絡而非細節振幅

---

## 5. 資料集

**硬體設備：**

| 裝置 | 規格 |
|------|------|
| 採集方式 | 無線 EMG 設備 |
| 採樣率 | 1000 Hz |
| 每段錄製長度 | 2 秒 |

**電極配置（6 通道）：**

| 通道 | 肌肉 |
|------|------|
| 1 | 頦肌（mentalis）|
| 2 | 笑肌（risorius）|
| 3 | 上唇提肌（levator labii superioris）|
| 4 | 二腹肌前腹（anterior belly of digastric）|
| 5 | 下頜舌骨肌（mylohyoid）|
| 6 | 頸闊肌（platysma）|

**受試者：**
- 70 人（男 50、女 20），年齡 20–35（均值 27.5）
- 全部普通話母語者，自願簽署知情同意書
- 倫理核准：天津大學倫理審查委員會（TJUE-2021-138）

**語料庫：**
- 101 類（日常生活詞語 + 人機互動指令，每類 3–5 字）
- 每受試者每詞語重複 10 次（1 session × 10 次）
- 有效樣本：69,875（去除錯誤樣本後）
- 訓練集：60 受試者 × 60,026 樣本；測試集：10 受試者 × 9,849 樣本

**前處理：**
- 4 階 Butterworth 帶通濾波：10–400 Hz（去除直流偏移與低頻噪聲）
- 50 Hz + 150 Hz 陷波濾波（去除工頻干擾）

---

## 6. 方法概述

**特徵：time-series features（原始時序訊號）**

```
TS(x) = {x₁, x₂, ..., xₜ},  t = 2000（2 秒 × 1000 Hz）
輸入形狀：6 × 2000
```

**模型 1：1D-CNN（Feature Extractor）**

```
輸入：6 × 2000
  └── Conv1d (64ch) × 2 → MaxPool(1×2)
  └── Conv1d (128ch) × 2 → MaxPool(1×3)
  └── Conv1d (256ch) × 4 → MaxPool(1×3)
  └── Conv1d (512ch) × 4 → MaxPool(1×3)
  └── Flatten → FC → Softmax（101 類）

參數量：3,538,176（~33.51 MB）
```

**模型 2：ICDAN（遷移學習框架）**

```
Source Domain（有標籤，20 人）+ Target Domain（無標籤，10 人）
                │
    ┌───────────┴──────────────┐
    ▼                          ▼
[1D-CNN Feature Extractor]  [1D-CNN Feature Extractor]（共享權重）
    │ fₛ                        │ fₜ
    ├─→ [Classifier T] → 分類損失 Lᵧ（僅 source）
    ├─→ [MMD Loss] ←──────────┤  （source vs. target 分布距離）
    └─→ [CDAN Discriminator] ←┘  （對抗損失 Lᴅ，條件對齊特徵+類別聯合分布）

總損失：min_{G,T} max_D  Lᵧ + λ(ωLᴅ + λLᴹ)
```

- CDAN 對齊特徵與類別的**聯合分布**（vs. DANN 只對齊邊際分布），適合 sEMG 的多模態個體差異
- MMD 使用核 Hilbert 空間重構，測量兩域特徵分布距離
- ω = 樣本熵值（特徵學習權重）；λ = 域間比例控制參數

**訓練設定：**
- Adam optimizer；lr = 0.0001；weight decay = 0.0005；batch = 16
- Dropout(0.5) after pooling；BatchNorm in conv layers；L2 regularization in FC
- GPU：TITAN V

---

## 7. 主要結果

**特徵比較（VGGNet 骨幹，60 人訓練）：**

| 特徵 | 非跨受試者（%）| 跨受試者（%）|
|------|--------------|-------------|
| TC-4（時域組合）| 56.41 | 45.76 |
| FC-4（頻域組合）| 66.85 | 57.97 |
| MFCC | 71.02 | 63.89 |
| Fbank | 84.49 | 67.03 |
| **Time Series** | **90.12** | **83.61** |
| Time Series + 1D-CNN | **94.45** | **87.80** |

**5-fold 跨受試者交叉驗證（1D-CNN）：**

| 組別 | 跨受試者準確率（%）|
|------|-----------------|
| Group 1 | 87.80 |
| Group 2 | 79.20 |
| Group 3 | 86.45 |
| Group 4 | 81.89 |
| Group 5 | 87.36 |
| 平均 | **84.54** |

**少樣本跨受試者（20 人訓練集，10 人測試集）：**

| 方法 | 平均（%）| SD |
|------|---------|-----|
| 1D-CNN | 71.42 | 15.92 |
| DDC | 76.17 | 14.23 |
| DAN | 75.47 | 13.55 |
| DANN | 76.74 | 13.61 |
| CDAN | 85.38 | 11.83 |
| **ICDAN** | **86.32** | **11.31** |

**個體差異（20 人訓練，1D-CNN）：**
- 最高：Sub. 9 = 86.28%
- 最低：Sub. 10 = 30.04%（面部鬍渣 + 頸部厚脂肪層，訊號與他人差異過大）
- 最大差距：56.24%

---

## 8. 消融與比較分析

**為何 CDAN 優於 DANN：**
- EMG 訊號跨受試者可視為**多模態資料（multimodal）**
- DANN 只對齊邊際特徵分布，無法處理多模態遷移問題
- CDAN 對齊特徵與類別標籤的**聯合分布**，能更好捕捉 sEMG 跨個體的共通模式

**為何 ICDAN 僅略優於 CDAN（+0.94%）：**
- CDAN 已學到兩域共通特徵，MMD 附加的分布距離約束改進空間有限

---

## 9. 限制與未來工作

1. **ICDAN 仍需目標域無標籤資料**：target domain 資料需分一半作訓練集（1:1 split），距離真正的「零樣本跨受試者」仍有差距
2. **個體極端差異無解**：皮下脂肪過厚的受試者目前只能靠增加其個人樣本量解決，無法透過模型修正
3. **未來方向**：zero-shot cross-subject SSR（完全不需要目標受試者資料）

---

## 10. 與本論文的關聯

| 面向 | 關聯 |
|------|------|
| **1.2.3 跨受試者問題** | 直接量化跨受試者準確率（87.80% / 71.42%），並提出遷移學習方案，是 Huang 2024 Section 7.2「Transfer learning 是未來方向」的直接跟進 |
| **1.2.3 個體差異的物理成因** | 皮下脂肪層、鬍渣、口音等導致跨受試者性能崩潰（30%），為後續討論「為何本研究使用統一電極圖譜 + 特定族群受試者」提供依據 |
| **1.2.3 大規模中文語料庫** | 70 人、101 類，規模遠大於 Huang 2024（12 人）和 Chen/Song 2023（15/8 人），展示資料量對跨受試者性能的決定性影響 |
| **1.2.4 端對端演進** | 以 1D-CNN 直接學習原始時序訊號（無手工特徵）+ ICDAN 遷移框架，代表從分類架構走向領域自適應的演進方向 |

---

## 11. 引用關鍵資訊

> Yakun Zhang, Huihui Cai, Jinghan Wu, Liang Xie, Minpeng Xu, Dong Ming, Ye Yan, and Erwei Yin, "EMG-Based Cross-Subject Silent Speech Recognition Using Conditional Domain Adversarial Network," *IEEE Transactions on Cognitive and Developmental Systems*, vol. 15, no. 4, pp. 2282–2290, December 2023. DOI: 10.1109/TCDS.2023.3316701

**引用重點：**
- 70 人、101 類中文 sEMG 資料集
- 1D-CNN + 時序特徵：跨受試者 87.80%（60 人訓練）
- ICDAN：少樣本跨受試者 86.32%（+14.88% over baseline）
- 皮下脂肪層是跨受試者差異的關鍵物理成因
- 首次將 CDAN 成功應用於 EMG SSR 跨受試者解碼

---

## 12. 關鍵詞

Cross-subject, silent speech recognition, sEMG, domain adaptation, conditional domain adversarial network, CDAN, ICDAN, MMD, 1D-CNN, time-series features, transfer learning, Mandarin Chinese, individual variability, electrode bias
