# Silent Speech Recognition using Electromyography Signals

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 會議 | 2025 IEEE 6th International Symposium on the Internet of Sounds (IS2) |
| DOI | 10.1109/IS264627.2025.11284651 |
| 年份 | 2025 |
| 作者 | Darshan Jain, Amitangshu Pal |
| 機構 | Computer Science and Engineering, Indian Institute of Technology Kanpur (IIT Kanpur), India |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/第一章期刊/第三段/Silent_Speech_Recognition_using_Electromyography_Signals.pdf` |
| 備註 | 本文透過 IEEE Xplore 由國立虎尾科技大學下載（2026-06-04），即使用者所屬機構；資料集已公開於 GitHub |

---

## 2. 一句話總結

以 8 通道低密度 sEMG 搭配 Multi-DTW 樣本篩選、合成資料增強（cross-fading 拼接 + 噪音注入 + 時間彎曲）訓練注意力 Seq2Seq 模型，在 22 詞英文句子級無聲語音辨識任務上達到 9.3% WER，優於 CNN+BiLSTM+CTC 基線（16.4%），展示「合成訓練 → 真實泛化」策略的可行性。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | Multi-DTW 樣本篩選：從每詞 ≥20 個樣本中選最具代表性的 17 個，孤立詞分類從 84.4% 提升至 90.9% |
| 2 | 合成句子資料增強管線（cross-fading + 高斯噪音 + 時間彎曲 + 基線漂移），訓練集完全合成但在真實句子測試集泛化良好（34 句中 23 句完全正確） |
| 3 | 注意力 Seq2Seq（自迴歸解碼）顯著優於 CTC 基線（9.3% vs 16.4% WER），直接說明注意力機制在處理共發音和可變詞長上的優勢 |

---

## 4. 背景與動機

**問題定位：** 現有 sEMG-SSR 系統面臨四大瓶頸：
1. 固定句子模板或詞彙，擴展困難
2. 依賴手工特徵或生成式模型假設
3. CTC/HMM 難以處理可變長度輸出和共發音
4. 資料收集耗時費力（受試者疲勞 + 設備需持續監控）

**本文切入點：** 以合成資料增強解決資料不足問題；以注意力 Seq2Seq 取代 CTC，支援靈活的可變長度詞序列解碼；使用低成本 OpenBCI Cyton 8 通道硬體。

**與 Xie et al. (2025) 的對比（同年同類研究）：**
- 本文：8 通道低密度，英文 22 詞，合成訓練，Seq2Seq，資源受限導向
- Xie (2025)：多通道，中文，CNN+Transformer+CTC，字符級辨識

---

## 5. 資料集

**硬體：**
- OpenBCI Cyton Board：8 通道類比輸入，250 Hz
- 電極：金杯電極 + Ten20 導電膏
- 參考電極：左耳後
- 驅動偏置電極（bias）：右耳後（降低共模噪音）

**電極位置（8 通道）：**

| 位置 | 目標肌肉 |
|------|---------|
| 下唇下方 | 口輪匝肌（orbicularis oris） |
| 下顎下方 | 頦下區域（submental region） |
| 頸部兩側（雙側）| 胸鎖乳突肌（sternocleidomastoid） |
| 臉頰 | 顴大肌（zygomaticus major）+ 笑肌（risorius） |
| 下顎線 | 咬肌（masseter） |

**詞彙（22 個英文高頻詞，源自 TIMIT 語料庫篩選）：**
all, anyone, anything, are, back, can, come, could, did, doing, find, help, here, in, now, out, please, right, stop, that, tomorrow, you

**資料結構：**

| 子集 | 說明 | 數量 |
|------|------|------|
| 孤立詞 | 每詞 ≥20 次無聲嘴動；Multi-DTW 篩選後 17 個/詞 | 22×17=374 個 exemplar |
| 訓練 exemplars | 每詞 14 個（固定分割） | 22×14=308 個 |
| 驗證 exemplars | 每詞 3 個（固定分割） | 22×3=66 個 |
| 合成訓練句 | 運行時動態生成，每 epoch 6000 句 | 動態 |
| 真實測試句 | 34 個真實錄製句子（4-5 詞，22 詞詞彙組合）| 34 個 |

**說話模式：** 無聲嘴部動作（silent mouthing）——受試者靜坐安靜環境，無發聲嘴動詞彙；OpenBCI GUI 插入事件標記精確時間對齊

---

## 6. 模型架構

### 前處理

```
原始 8ch sEMG (250 Hz)
    |
    v
[高通濾波：0.1 Hz（實驗確認為最優，保留低頻發音資訊）]
（比較 0.1/1/10/20 Hz，0.1 Hz 在 RF 和 CNN 分類器上表現最佳）
    |
    v
[Multi-DTW 樣本篩選]
計算所有樣本間的 DTW 距離矩陣 → 選平均 DTW 距離最小的 17 個樣本/詞
（去除打噴嚏、嘴型不佳等雜訊樣本）
```

### 合成資料增強（訓練時動態生成）

```
從訓練 exemplars 中隨機選詞序列（4-7 詞）
    |
    v
[Cross-fading 拼接：50 ms 重疊淡入淡出平滑詞語邊界]
    |
    v
[隨機疊加（任意組合）：]
  (a) 高斯噪音注入（SNR 20–30 dB）
  (b) 時間彎曲：±10% 時長縮放
  (c) 基線漂移模擬（慢波形漂移）
→ 每 epoch 動態生成 6000 句合成訓練序列
```

### 提出模型（注意力 Seq2Seq）

```
8ch sEMG (250 Hz)
    ↓
【編碼器】
[Conv 1D + ReLU（2 層）]  ← 局部時空特徵提取
    ↓
[BiLSTM（2 層）]  ← 長程依賴與全局語境
    ↓ encoder output sequence
【解碼器（自迴歸）】
[Attention Layer]  ← 對編碼器輸出加權，定位當前步的相關輸入
    ↓
[單向 LSTM + 前一預測詞 embedding + attention vector]
    ↓
[Output projection + Softmax → 22 詞詞彙]
（每步生成一個詞，以前一個預測詞作為下一步輸入）
```

### 基線模型（CTC，用於對比）

```
8ch sEMG → Conv 1D + BiLSTM → CTC Loss → WER 16.4%
```

---

## 7. 資料增強（詳見第 6 節）

本文的核心貢獻之一即為合成資料增強管線，訓練集完全由合成句子組成，測試集為真實錄製句子（domain gap 挑戰）。

---

## 8. 實驗結果

### 孤立詞分類（CNN 分類器，80/20 分割）

| 訓練資料 | 準確率 |
|---------|--------|
| 所有樣本（≥20/詞） | 84.4% |
| Multi-DTW exemplars（14/詞）| **90.9%** |

### 句子級 WER（34 真實測試句）

| 模型 | WER |
|------|-----|
| CNN+BiLSTM+CTC（基線）| 16.4% |
| **注意力 Seq2Seq（本文）** | **9.3%** |

**細節：**
- 34 句中 **23 句完全正確（WER = 0%）**
- 多數句子 WER < 20%；極少數 WER = 50%

### 常見誤辨詞對

| 混淆 | 原因 |
|------|------|
| anything ↔ anyone | 發音肌電活動幾乎相同（t-SNE cluster 相鄰） |
| "right" 替換 "that" | 臉部肌肉運動模式相似 |
| "are" 替換 "out" | 形狀接近 |

---

## 9. 論文限制

- **單一受試者測試**（論文未明確說明受試者數量，從描述推斷主要為 1 人）
- 合成訓練資料與真實句子存在 domain gap，雖已驗證泛化，但 domain shift 仍可能影響更大詞彙場景
- 22 詞固定詞彙，詞彙外（OOV）詞語無法辨識
- 採樣率僅 250 Hz，低於多數 sEMG 研究
- 每詞樣本量極少（14 個訓練 exemplar），對更複雜語音的泛化未驗證
- 無跨 session 測試

---

## 10. 與我的研究的關聯

| 面向 | Jain & Pal (2025) | 我的研究方向 |
|------|------------------|-------------|
| 語言 | 英語（22 詞） | 台灣注音符號 |
| 通道數 | 8 | 4 |
| 採樣率 | 250 Hz | 待確認 |
| 說話模式 | 無聲嘴部動作 | 無聲語音 |
| 任務 | 句子級 4-5 詞解碼（WER） | 音素/注音序列辨識 |
| 架構 | CNN+BiLSTM 編碼 + 注意力 LSTM 解碼 | CNN + Transformer + CTC |
| 最佳 WER | 9.3% | 目標待定 |

**對我的啟示：**
1. **合成資料增強是低資源 sEMG 的關鍵策略**：本文證明以合成拼接 + 增強訓練，模型仍能在真實句子上泛化，你的注音研究在初期資料不足時可採用類似策略
2. **注意力 Seq2Seq > CTC（在此場景）**：WER 從 16.4% 降至 9.3%，支持注意力機制在可變長輸出場景的優勢；但注意這是 22 詞固定詞彙，CTC 在大詞彙場景（如 Xie 2025）仍有效
3. **Multi-DTW 樣本品質控制**：你在自製資料集時同樣面臨部分錄製品質不佳的問題，Multi-DTW 篩選是一個簡單實用的品質控制方法
4. **0.1 Hz 高通截止**：本文實驗確認臉部 sEMG 低頻成分（< 1 Hz）含有辨識資訊，設計濾波時不宜用過高截止頻率

---

## 11. 五個核心問題

| 問題 | 答案 |
|------|------|
| 研究問題是什麼？ | 能否以低密度 8 通道 sEMG + 合成增強資料 + 注意力 Seq2Seq，實現資源受限的句子級 SSR？ |
| 方法是什麼？ | Multi-DTW 篩選 → cross-fading 合成句子 + 三種增強 → CNN+BiLSTM 編碼 + 注意力 LSTM 自迴歸解碼 |
| 資料如何取得？ | 1 名受試者，22 詞每詞 ≥20 次無聲嘴動，250 Hz，OpenBCI Cyton；34 個真實句子測試 |
| 主要結果？ | Seq2Seq WER 9.3%（vs CTC 基線 16.4%）；34 句中 23 句完全正確 |
| 主要限制？ | 單人、22 詞固定詞彙、低採樣率、合成訓練 domain gap |

---

## 12. 重要引用文獻

| 引用 | 內容 | 重要性 |
|------|------|--------|
| Wand et al. (2016) [ref 15] | DNN 前端 EMG 語音辨識 | 本文引用的深度學習先行研究 |
| Xie et al. (2025) [ref 16] | 中文神經網路 SSR（CNN+Transformer+CTC）| 本文同年同類研究，互補對比 |
| Meltzner et al. (2018) [ref 14] | sEMG 感測器與演算法，大規模資料 | 本文對比的「高資源」傳統方法 |
| Bahdanau et al. (2015) [ref 26] | 注意力機制原始論文（NMT） | 本文解碼器注意力設計來源 |
| Graves et al. (2006) [ref 30] | CTC 原始論文 | 本文基線模型 |
| Müller (2007) [ref 25] | DTW 方法（Multi-DTW 來源） | 本文樣本篩選方法依據 |
