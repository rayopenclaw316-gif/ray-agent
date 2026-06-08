# Deep Neural Network Frontend for Continuous EMG-based Speech Recognition

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 會議 | INTERSPEECH 2016, September 8–12, San Francisco, USA, pp. 3032–3036 |
| DOI | http://dx.doi.org/10.21437/Interspeech.2016-340 |
| 年份 | 2016 |
| 作者 | Michael Wand, Jürgen Schmidhuber |
| 機構 | Istituto Dalle Molle di Studi sull'Intelligenza Artificiale (The Swiss AI Lab IDSIA), USI & SUPSI, Manno-Lugano, Switzerland |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/第一章期刊/第三段/Deep Neural Network Frontend for Continuous EMG-based Speech.pdf` |
| 備註 | Wand 從 KIT 遷移至 IDSIA 後與 Schmidhuber 合作；延伸自作者 EMBC 2014 的框架層次實驗；本文僅用有聲語音資料（無聲對齊不可用） |

---

## 2. 一句話總結

以 DNN 取代 GMM 作為 HMM 前端，在 EMG-UKA 語料庫的 session 依賴訓練條件下，對 context-independent phone 模型達到超過 32% 的相對 WER 改善（開發集），並首次示範 DNN 前端可讓簡單音素模型（phone）接近複雜 BDPF 模型的準確率，即使訓練資料僅數十句。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 首次將 DNN 前端引入連續 EMG 語音辨識，在極少量（每 session 約 3 分鐘）訓練資料下仍有效 |
| 2 | DNN + phone 模型（開發集 20.0%）接近 GMM + BDPF 模型（22.5%），大幅簡化建模範式 |
| 3 | 揭示 GMM 與 DNN 系統對 LDA 最優降維維度的差異：GMM 最優 12–22 維；DNN 最優 32–64 維 |

---

## 4. 背景與動機

**問題：** 傳統 GMM-HMM 在小資料量場景下特徵維度受限，BDPF 模型雖針對此問題設計但結構複雜。

**前驅工作：**
- Wand & Schultz (2014) 在 EMBC：首次將 ANN 用於 EMG 語音辨識的**框架級**分類，確認 ANN 能萃取判別性 EMG 特徵
- 本文將此延伸至**連續語音辨識**的完整 DNN-HMM 系統

**本文切入點：** 以 DNN 替換 GMM 發射概率，保留 HMM 後端，驗證：
1. DNN 前端是否能在 EMG 小資料場景有效訓練
2. DNN 是否能讓 phone 模型擺脫對 BDPF 的依賴

**為何只用有聲語音：** 無聲語音缺乏高品質的音素級時間對齊（alignment），有聲語音的對齊可直接由現成語音辨識系統生成。

---

## 5. 資料集

**語料庫：** EMG-UKA Corpus（英語，Broadcast News 領域）

**子集：** 僅使用「small session」有聲語音資料

| 分割 | 說話者數 | Session 數 | 平均時長/session | 總時長 |
|------|---------|-----------|----------------|--------|
| 開發集（Dev） | 4 | 12 | 3:19 | 39:47 |
| 評估集（Eval） | 7 | 49 | 3:06 | 2:31:47 |

**每 session 結構：**
- 50 句：BASE 10 句（固定，跨 session 相同，用於測試）+ SPEC 40 句（每 session 不同，用於訓練）
- 訓練為 session 依賴（session-dependent）：每 session 各自訓練一套模型

**電極設備：**
- 6 通道，ch5 不穩定移除 → 實際使用 5 通道
- 電極位置：levator anguli oris, zygomaticus major, platysma, depressor anguli oris, anterior belly of digastric, tongue
- 採樣率：600 Hz
- 聲學訊號同步錄製（用於生成音素對齊，辨識時不使用）

**詞彙：** 108 詞（測試集中出現的詞彙）

---

## 6. 模型架構

### 特徵提取（TD5）

```
5ch sEMG (600 Hz)
    |
    v
[每通道 mean normalization]
[9-tap unweighted moving average × 2 → 低頻部分 w[n]]
高頻殘差 p[n] = x[n] - w[n]，整流 r[n] = |p[n]|
TD0 = [w̄, Pw, Pr, zp, r̄]（5 個時域特徵/通道/框架）
框架大小 27ms，移位 10ms
    |
    v
[TD5 = S(TD0, 5)：堆疊 ±5 相鄰框架 = 11 框架]
5 通道 × 5 特徵 × 11 框架 = 275 維
    |
    v
[LDA 降維 → 最優維度因系統而異（見下）]
目標類別：127 個（42 音素 × 3 子狀態 + 1 靜音）
```

**注意：** 本文使用 TD5（堆疊 ±5 框架），Wand (2014) 使用的是 TD10（堆疊 ±10 框架）；兩者在初步實驗中差異不顯著。

### GMM-HMM 基線

```
LDA 降維特徵
    |
    v
[3 狀態 left-to-right HMM，GMM 發射概率]
工具：BioKIT
    |
    v
兩種模型結構：
(A) Context-independent phone 模型：127 個模型
(B) BDPF 模型：8 個音韻特徵串流（Voiced, Consonant, Alveolar, 
    Unround, Fricative, Front, Plosive, Nasal），每串流約 100 個模型，
    每串流獨立訓練；GMM 最優 LDA 維度 22
    |
    v
三元語法語言模型（Broadcast News），困惑度 24.24，詞彙 108 詞
```

### DNN 前端（本文貢獻）

```
LDA 降維特徵（維度更高：phone 最優 32 維，BDPF 最優 64 維）
    |
    v
[4 個隱藏層，每層 200 個神經元，tanh 激活]
    |
    v
[Softmax 輸出層]
  - Phone 系統：127 個輸出
  - BDPF 系統：每串流約 100 個輸出，8 個 DNN 分別訓練
    |
    v
[DNN 輸出作為 HMM 狀態發射概率]
保留 HMM 後端（Viterbi 解碼 + 三元語法 LM）
```

**DNN 訓練設定：**
- 初始化：Gaussian，標準差 0.1（無預訓練）
- 優化：隨機梯度下降（SGD），minibatch 30，學習率 0.005
- 損失函數：Multiclass Cross Entropy
- 正則化：僅 early stopping（訓練準確率 5 個 epoch 未改善即停）
- 工具：PyLSTM（自研工具）
- 對齊來源：直接使用語料庫中聲學對齊，不重新計算

---

## 7. 資料增強

無。本文聚焦在以 DNN 替換 GMM，不使用資料增強，訓練資料即每 session 約 40 句（SPEC 子集，約 3 分鐘）。

---

## 8. 實驗結果

### 開發集 WER（Average over 12 sessions）

| 模型結構 | GMM 前端 | DNN 前端 | 相對改善 |
|---------|---------|---------|---------|
| Phone 模型（LDA 12/32）| 29.5% | **20.0%** | **>32% 相對** |
| BDPF 模型（LDA 22/64） | 22.5% | **19.5%** | **13% 相對** |

**LDA 最優維度比較：**

| 系統 | 最優 LDA 維度 | 最佳 WER |
|------|------------|---------|
| Phone + GMM | 12 | 29.5% |
| Phone + DNN | 32 | 20.0% |
| BDPF + GMM | 22 | 22.5% |
| BDPF + DNN | 64 | 19.5% |

**關鍵觀察：** DNN + Phone（20.0%）≈ GMM + BDPF（22.5%）；DNN 消除了手工設計 BDPF 複雜結構的必要性。

### 評估集 WER（Average over 49 sessions）

| 模型結構 | GMM 前端 | DNN 前端 | 統計顯著性 |
|---------|---------|---------|----------|
| Phone 模型 | 33.6% | **26.5%** | p = 7.02×10⁻⁸ ✅ |
| BDPF 模型 | 27.2% | **23.8%** | p = 1.17×10⁻² ✅ |

**注意：** 評估集 phone 模型的相對改善為 (33.6-26.5)/33.6 ≈ **21.1%**，而非 32%。論文摘要引用的「>32% relative」來自開發集數據；評估集的實際相對改善為 21%，仍為顯著改善。

---

## 9. 論文限制

- Session 依賴訓練：每 session 各自訓練，無法跨 session 或跨說話者泛化
- 僅使用有聲語音（非無聲語音），因無聲語音無法自動生成可靠音素對齊
- 訓練資料極少（每 session 約 40 句）——本文視之為挑戰且已克服，但實用場景中資料量仍遠低於聲學 ASR
- 詞彙僅 108 詞，非大詞彙系統
- DNN 仍需 LDA 作為前端降維，尚非端對端特徵學習

---

## 10. 與我的研究的關聯

| 面向 | Wand & Schmidhuber (2016) | 我的研究方向 |
|------|--------------------------|-------------|
| 語言 | 英語（連續語音） | 台灣注音符號 |
| 通道數 | 5（ch5 移除） | 4 |
| 採樣率 | 600 Hz | 待確認 |
| 說話模式 | 有聲語音（訓練用） | 無聲語音 |
| 特徵 | TD5 + LDA（手工） | 待設計 |
| 模型 | DNN-HMM（phone 或 BDPF） | CNN + Transformer + CTC |
| 最佳 WER（eval） | 23.8%（BDPF + DNN） | 目標待定 |

**對我的啟示：**
1. **DNN 在小資料場景可行**：每 session 約 3 分鐘訓練資料 DNN 就能有效訓練，這對你初期收集的小規模注音語料庫是重要的可行性論據
2. **LDA 維度需重新調整**：換用 DNN 後最優 LDA 維度從 12 升至 32；如果你的系統也使用降維，要注意 DNN 和傳統模型對最優維度的需求完全不同
3. **「DNN 取代 GMM」是轉型節點**：此篇是你論文 1.2.1 第三段的起點，標誌從傳統到深度學習的關鍵轉折
4. **有聲語音問題**：本文因無聲對齊不可用而使用有聲語音訓練。你的研究若需要對齊標注，也需要考慮是否從有聲先訓練再做模式轉換

---

## 11. 五個核心問題

| 問題 | 答案 |
|------|------|
| 研究問題是什麼？ | DNN 前端能否在 EMG 語音辨識的小資料場景下有效替代 GMM，並讓簡單 phone 模型接近複雜 BDPF 模型的準確率？ |
| 方法是什麼？ | TD5 特徵 + LDA → DNN（4 隱藏層 200 神經元）→ HMM 後端（Viterbi + 三元語法 LM） |
| 資料如何取得？ | EMG-UKA Corpus，小 session 有聲語音子集，61 sessions，7 說話者，600 Hz |
| 主要結果？ | 開發集 phone 模型 WER 從 29.5% 降至 20.0%（>32% 相對改善）；評估集 BDPF 模型 23.8%（顯著） |
| 主要限制？ | Session 依賴、僅有聲語音、108 詞小詞彙、TD5+LDA 仍非端對端 |

---

## 12. 重要引用文獻

| 引用 | 內容 | 重要性 |
|------|------|--------|
| Wand & Schultz (2014) EMBC [ref 5] | ANN 用於 EMG 語音框架分類（本文前驅） | 直接前驅，確立 DNN 在 EMG 有效性 |
| Schultz & Wand (2010) Speech Comm. [ref 4] | BDPF 模型原始論文 | 本文基線模型 |
| Jou et al. (2006) Interspeech [ref 3] | 首個連續 EMG 語音辨識系統 | 本文所繼承的系統基礎 |
| Hochreiter & Schmidhuber (1997) [ref 26] | LSTM 原始論文 | 本文預告的 RNN 未來方向 |
| Wand, Janke & Schultz (2014) EMG-UKA [ref 27] | EMG-UKA 語料庫描述論文 | 本文使用的語料庫 |
