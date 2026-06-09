# Decoding Silent Speech from High-Density Surface Electromyographic Data Using Transformer

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊 | Biomedical Signal Processing and Control, Vol. 80 (2023), Article 104298 |
| DOI | 10.1016/j.bspc.2022.104298 |
| 年份 | 2023（線上發表 2022 年底，Vol. 80, 2023）|
| 作者 | Rui Song, Xu Zhang（通訊）, Xi Chen, Xiang Chen, Xun Chen, Shuang Yang, Erwei Yin |
| 機構 | USTC（中國科大）School of IST；中科院計算技術研究所；解放軍軍事科學院 |
| 資助 | 未明（USTC）|
| PDF 路徑 | `/Users/rayopenclaw/Downloads/Decoding silent speech from high-density surface electromyographic data using transformer .pdf` |
| **姊妹論文** | Chen et al. (2023) IEEE TNSRE，同組同語料庫，對比 CNN-BiLSTM-CTC 方法 |

---

## 2. 一句話總結

USTC Xu Zhang 組：64 通道高密度雙側 sEMG + Hudgins TD 特徵（256-dim）→ Transformer encoder-decoder（N=4, h=4）→ 語言模型後處理，在 8 名受試者、33 中文片語任務上達到 **CER 5.14 ± 3.28%、片語準確率 96.37 ± 2.06%**，優於 LSTM decoder（12.04%）與 CNN/LSTM 分類器，驗證 Transformer 全局注意力在 sEMG 音節序列建模的優越性。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 首次將 **Transformer encoder-decoder** 架構用於 sEMG 連續中文音節序列解碼，利用多頭注意力建立所有幀對之間的長程依賴關係 |
| 2 | 提出**音節相似度語言模型（Syllable-similarity LM）**，以 2×Ns/(L(Ŷ)+L(P)) 計算解碼序列與語料庫片語的相似度並選出最佳片語 |
| 3 | 完整的參數敏感性分析：對 N（堆疊層數 2–6）× h（注意力頭數 1–6）的網格搜尋，確定最優配置 N=4, h=4 |

---

## 4. 背景與動機

**問題定位：**
1. 傳統 sEMG 分類方法忽略片語內音節間的語義關係
2. LSTM seq2seq 建模長程依賴能力有限（對比 Transformer 全局注意力）
3. 現有方法多針對孤立詞，缺乏音節級連續解碼

**本文切入點：**
- Transformer encoder 建立輸入序列全局表示（所有幀互相注意）
- Decoder 自迴歸地輸出音節序列，兼顧當前幀特徵與歷史音節決策
- 語言模型利用封閉語料庫的先驗語義知識修正輸出

**與 Chen et al. (2023)（同組）的差異：**

| 面向 | 本文（Song 2023）| Chen (2023) |
|------|-----------------|------------|
| 特徵提取 | Hudgins 4 TD 特徵 + 256-dim 向量 | CNN 空間塊（8×8 影像）|
| 解碼方式 | **Transformer encoder-decoder** | BiLSTM + CTC |
| 語言模型 | 音節相似度 | 編輯距離 |
| 受試者 | 8 名 | **15 名** |
| CER | 5.14 ± 3.28% | **3.11 ± 1.46%** |
| 片語準確率 | 96.37 ± 2.06% | **97.17 ± 1.53%** |

---

## 5. 資料集

**硬體設備：**

| 裝置 | 規格 |
|------|------|
| 電極 | 直徑 5 mm 圓形探針，monopolar（單極）量測 |
| 放大增益 | 64 dB |
| 帶通濾波 | 20–500 Hz |
| 採樣率 | 1000 Hz |
| ADC | 16-bit A/D 轉換器 |
| 導電膠 | 實驗前塗抹於所有電極 |
| 參考電極 | 雙側耳後（左右各一）|
| 接地電極 | 耳後（與參考電極不同側）|

**電極配置（64 通道，2 件 × 32 通道陣列）：**

| 陣列 | 位置 | 目標肌群 |
|------|------|---------|
| 臉部 × 2（雙側對稱）| 臉部兩側 | zygomatic major（顴大肌）, zygomatic minor（顴小肌）, risorius（笑肌）|
| 頸部 × 2（雙側對稱）| 頸部兩側 | sternocleidomastoid（胸鎖乳突肌）, anterior belly of digastric（二腹肌前腹）, platysma（頸闊肌）|

- 電極直徑：5 mm；電極間距：10–18 mm

**受試者：**
- 8 名（7 男 1 女），年齡 21–25 歲
- 全部為普通話母語者，無語言或聽力障礙
- IRB：USTC 生物醫學倫理審查委員會核准

**語料庫（與 Chen 2023 完全相同）：**
- 33 個中文片語（日常應用場景：無人機 T1–T9、工業控制 T10–T24、消防 T25–T33）
- 82 個基本音節詞彙（每漢字對應一音節）
- 每片語 20 次默讀重複；重複間隔 ≥ 3 秒
- 每受試者樣本數：33 × 20 = 660
- 訓練:驗證:測試 = 3:1:1（5-fold cross-validation）

---

## 6. 方法概述

**特徵提取：**
1. 振幅閾值法（threshold = 均值 + 3σ）偵測片語起止點
2. 每片段均分為 T=60 幀（固定，empirically determined）
3. 每幀每通道提取 Hudgins 4 時域特徵：MAV, ZC, SSC, WL
4. 64 通道 × 4 特徵 → 拼接為 **256-dim 特徵向量**；輸入序列 X = (x₁,...,x₆₀)

**Transformer encoder-decoder 架構：**

```
輸入：X = 60 × 256 特徵序列
    │ + 位置編碼（Positional Encoding）
    ▼
[Encoder，N=4 個相同模塊]
  每模塊：
    Multi-Head Self-Attention（h=4 頭）
    → Add & LayerNorm
    Position-wise FFN（dff=1024）
    → Add & LayerNorm
    dmodel=256
    │
    ▼
[Decoder，N=4 個相同模塊]
  每模塊：
    Masked Multi-Head Self-Attention（h=4）
    → Add & LayerNorm
    Multi-Head Cross-Attention（Encoder 輸出）
    → Add & LayerNorm
    Position-wise FFN（dff=1024）
    → Add & LayerNorm
    │
    ▼
[Linear + Softmax → 82 音節概率]
    │ Beam Search（beam size=2）
    ▼
決策序列 Ŷ = (ŷ₁,...,ŷM)
    │
    ▼
[語言模型 Syllable-similarity LM]
  similarity = 2×Ns / (L(Ŷ) + L(P))
  選語料庫中相似度最高片語 → 最終輸出 P̂
```

**訓練設定：**
- 損失函數：Cross-Entropy
- 優化器：Adam；初始 lr = 6×10⁻⁵；每 30 epochs × 0.1
- Batch size = 12；Dropout = 0.1
- 框架：PyTorch（Python 3.6.1）；GPU：RTX 3080Ti（雲端伺服器）
- Epochs = 100

---

## 7. 主要結果

**CER（音節解碼）：**

| 方法 | CER (%) |
|------|---------|
| LSTM decoder | 12.04 ± 5.82 |
| **Transformer decoder（本文）** | **5.14 ± 3.28** |

（統計顯著 p < 0.05）

**片語準確率（PCA）：**

| 方法 | PCA (%) |
|------|---------|
| CNN 分類器 | 88.89 ± 7.93 |
| LSTM 分類器 | 91.44 ± 4.09 |
| LSTM decoder | 87.05 ± 5.79 |
| Transformer decoder | 92.39 ± 4.17 |
| LSTM decoder + LM | 88.89 ± 5.23 |
| **Transformer decoder + LM（本文完整）** | **96.37 ± 2.06** |

（統計顯著優於所有其他方法 p < 0.05）

**參數敏感性（以 S1 為例）：**
- 最優配置 N=4, h=4（所有受試者一致）
- 單頭注意力（h=1）穩定劣於多頭（h≥2）
- dmodel = 256（固定，與特徵維度一致）

---

## 8. 消融實驗

| 消融項目 | 影響 |
|---------|------|
| Transformer decoder → LSTM decoder | CER 5.14% → 12.04%（+134%相對上升）|
| 移除語言模型（Transformer decoder 直接輸出）| PCA 92.39% → 96.37%（LM 貢獻 +3.98%）|

關鍵結論：Transformer 全局注意力顯著優於 LSTM 序列建模（CER 相對改善 57%）；語言模型對片語準確率貢獻不可忽視。

---

## 9. 限制與未來工作

1. **封閉詞彙限制**：33 片語 / 82 音節，無法直接擴展至開放詞彙場景
2. **小數據集**：8 受試者 × 660 樣本；Transformer 在資料量更大時可能有更大優勢
3. **無聲調辨識設計**：中文聲調資訊未明確建模（對比 Li 2022 的聲調素輔助任務）
4. 未來方向：擴大語料庫、跨說話者泛化、結合聲調輔助任務

---

## 10. 與本論文的關聯

| 面向 | 關聯 |
|------|------|
| **1.2.2 電極配置** | 64 通道雙側 HD sEMG（2×32）；臉部+頸部多肌群聯合配置；說明高密度電極在音節解碼中的應用 |
| **1.2.3 中文 SSR** | 首批中文 sEMG 音節級序列解碼論文；USTC 33 片語語料庫建立的封閉詞彙基準；橋接孤立詞分類與開放詞彙辨識之間的空白 |
| **1.2.4 端對端演進** | Transformer encoder-decoder 在 sEMG 中文連續解碼的首次應用；對比 Chen (2023) CTC 方法（同語料庫，不同架構）|
| **架構參考** | 純 Transformer encoder-decoder（無 CTC）用於 sEMG，與 Xie (2025) Transformer+CTC 形成對比 |

---

## 11. 引用關鍵資訊

> Rui Song, Xu Zhang, Xi Chen, Xiang Chen, Xun Chen, Shuang Yang, and Erwei Yin, "Decoding silent speech from high-density surface electromyographic data using transformer," *Biomedical Signal Processing and Control*, vol. 80, p. 104298, 2023. DOI: 10.1016/j.bspc.2022.104298

**引用重點：**
- 中文 sEMG 音節級序列解碼，Transformer encoder-decoder + 語言模型
- 64 通道 HD 電極，USTC 33 片語語料庫
- CER 5.14%；對比 Chen (2023) CTC 架構的 3.11%

---

## 12. 關鍵詞

Silent speech recognition, high-density sEMG, transformer encoder-decoder, syllable-level decoding, Chinese, language model, electrode array, sequence-to-sequence
