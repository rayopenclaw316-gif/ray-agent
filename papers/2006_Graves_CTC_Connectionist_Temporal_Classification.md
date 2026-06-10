# Connectionist Temporal Classification: Labelling Unsegmented Sequence Data with Recurrent Neural Networks

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 會議 | ICML 2006（第 23 屆國際機器學習會議，Pittsburgh, PA，2006）|
| DOI | 10.1145/1143844.1143891 |
| 年份 | 2006 |
| 作者 | Alex Graves, Santiago Fernández, Faustino Gomez, Jürgen Schmidhuber |
| 機構 | IDSIA（Istituto Dalle Molle di Studi sull'Intelligenza Artificiale），Manno-Lugano, Switzerland；TUM Munich |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/1143844.1143891.pdf` |
| **地位** | CTC 理論原創論文，被 Graves & Jaitly (2014)、Xie (2025)、Chen (2023) 等所有 CTC 相關工作引用 |

---

## 2. 一句話總結

提出 **CTC（Connectionist Temporal Classification）**：以 RNN 輸出定義標籤序列的概率分佈（含 blank 標記），透過前向後向算法邊際化所有可能對齊路徑，使模型只需序列級標注即可訓練，無需幀級對齊，在 TIMIT 音素標注任務上以 30.51% LER 優於 HMM 和 HMM-RNN 混合系統。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | **CTC 輸出表示**：RNN 輸出層加入 blank 標記（共 \|L\|+1 個輸出），以 softmax 輸出對所有標籤和 blank 的逐幀概率，定義 p(π\|x) |
| 2 | **多對一映射 B(π)**：將路徑（含 blank 和重複標籤）映射為標籤序列（去除 blank 和連續重複），p(l\|x) = Σ p(π\|x)，透過前向後向動態規劃高效計算 |
| 3 | **最大似然訓練**：CTC Loss = -log p(z\|x)，對網路輸出可微，可直接用 BPTT 訓練，無需預先分割資料或後處理輸出 |

---

## 4. 背景與動機

**問題：** 序列標注任務（語音辨識、手寫識別）中，訓練資料的輸入序列與輸出標籤序列長度不同，無先驗對齊方式。

**當時的框架與其缺陷：**

| 框架 | 缺陷 |
|------|------|
| HMM | 需要領域知識設計狀態模型；訓練是生成式而非判別式；需要馬可夫假設 |
| HMM-RNN 混合 | 繼承 HMM 缺陷；Viterbi 強制對齊仍需分割資料；未充分利用 RNN 序列建模能力 |
| Framewise RNN | 逐幀獨立分類，需要預先分割資料；無法直接輸出標籤序列 |

**CTC 的解法：** 將輸出視為所有可能路徑上的概率分佈，在訓練時只需目標標籤序列，損失函數對所有對齊路徑進行邊際化，讓 RNN 自行學習最優對齊方式。

---

## 5. 方法概述

**CTC 核心數學：**

```
輸入序列：x = (x₁,...,xT)，T 幀
輸出層：softmax，|L|+1 個單元（|L| 個標籤 + 1 個 blank）
路徑：π ∈ L'ᵀ，L' = L ∪ {blank}

路徑概率：p(π|x) = ∏ᵗ yᵗπₜ

多對一映射 B：去除 blank 和連續重複 → 標籤序列
  例：B(a-ab-) = B(-aa--abb) = aab

標籤概率：p(l|x) = Σ_{π∈B⁻¹(l)} p(π|x)

訓練損失：CTC Loss = -log p(z|x)
```

**前向後向算法：**
- 定義前向變數 αt(s) 和後向變數 βt(s)（對應修改後的標籤序列 l'，含插入的 blank）
- 動態規劃遞推，避免路徑數量指數增長
- 梯度 ∂Loss/∂yᵗk 可高效計算

**解碼方式：**
- **Best path decoding（貪婪）**：每幀取概率最高的輸出，速度快但不保證最優
- **Prefix search decoding（前綴搜索）**：類似 Beam Search，更準確但計算量較大

---

## 6. 實驗設定

| 項目 | 內容 |
|------|------|
| 任務 | TIMIT 英語語料庫音素標注（61 音素）|
| 輸入特徵 | 26 維 MFCC（12 係數 + log energy + 一階差分），10ms 幀，5ms 步進 |
| RNN 架構 | BLSTM（前後向各 100 個 LSTM cell，帶 peepholes 和 forget gates）|
| 輸出層 | 62 個 softmax 單元（61 音素 + blank）|
| 總參數量 | 114,662 |
| 訓練 | BPTT + online gradient descent，lr = 10⁻⁴，momentum = 0.9；Gaussian 噪聲 σ=0.6 |
| 基線 | Context-independent HMM、Context-dependent HMM、BLSTM/HMM hybrid |

---

## 7. 主要結果

| 系統 | LER (%) |
|------|---------|
| Context-independent HMM | 38.85 |
| Context-dependent HMM | 35.21 |
| BLSTM/HMM hybrid | 33.84 ± 0.06 |
| Weighted error BLSTM/HMM | 31.57 ± 0.06 |
| **CTC（best path）** | 31.47 ± 0.21 |
| **CTC（prefix search）** | **30.51 ± 0.19** |

CTC (prefix search) 顯著優於 HMM 和 HMM-RNN 混合（p < 0.01），且不需要標籤加權（HMM 需要 weighted error 才能達到 31.57%）。

---

## 8. 關鍵特性（與 HMM 的根本差異）

| 特性 | CTC | HMM |
|------|-----|-----|
| 分割資料需求 | **不需要**（訓練時自動學習對齊）| 需要強制對齊 |
| 領域知識 | **最小化**（不需要發音詞典、狀態模型設計）| 需要大量 |
| 訓練目標 | **判別式**（最大化正確標籤序列概率）| 生成式 |
| 標籤間依賴 | 條件獨立假設（每幀輸出獨立）| Markov 鏈假設 |
| 後處理 | **不需要**（B(π) 直接得到序列）| 需要 |

---

## 9. 限制

1. **條件獨立假設**：假設各幀輸出條件獨立（given 網路內部狀態），不顯式建模標籤間依賴（Transformer 或語言模型可補充）
2. **解碼近似**：best path decoding 不保證最優；prefix search 在某些情況下失效
3. **單調對齊**：只適用於輸入輸出保持時間順序的任務（語音辨識天然滿足，但複雜 NLP 任務不適合）

---

## 10. 與本論文的關聯

| 面向 | 關聯 |
|------|------|
| **1.2.1 第五段（CTC 架構）** | CTC 理論源頭：blank 標記概念、前向後向算法、無需幀級對齊的端對端訓練，是整節的理論基礎 |
| **草稿已引用** | 「Graves et al.（2006）提出的 CTC 損失函數...透過引入 blank 標記，在所有可能路徑上進行邊際化...使模型只需序列層級標注」|
| **延伸應用** | Graves & Jaitly (2014) 將 CTC 應用於開放詞彙語音辨識；Chen (2023) 和 Xie (2025) 將 CTC 用於中文 sEMG 序列解碼 |

---

## 11. 引用關鍵資訊

> Alex Graves, Santiago Fernández, Faustino Gomez, and Jürgen Schmidhuber, "Connectionist Temporal Classification: Labelling Unsegmented Sequence Data with Recurrent Neural Networks," in *Proc. 23rd Int. Conf. Mach. Learn. (ICML)*, Pittsburgh, PA, 2006, pp. 369–376. DOI: 10.1145/1143844.1143891

**引用重點：**
- CTC 理論：blank 標記 + 多對一映射 + 前向後向算法
- 無需幀級對齊，只需序列層級標注
- TIMIT 音素標注 LER 30.51%（優於 HMM）

---

## 12. 關鍵詞

Connectionist Temporal Classification, CTC, RNN, BLSTM, sequence labelling, blank token, forward-backward algorithm, no forced alignment, TIMIT, speech recognition
