# Neural Chinese Silent Speech Recognition with Facial EMG

**期刊**：Speech Communication 171 (2025) 103230  
**DOI**：10.1016/j.specom.2025.103230  
**作者**：Liang Xie, Yakun Zhang, Hao Yuan, Meishan Zhang, Xingyu Zhang, Changyan Zheng, Ye Yan, Erwei Yin  
**機構**：Defense Innovation Institute, AMS（中國軍事科學院）/ Tianjin AI Innovation Center  
**PDF**：`~/Downloads/1-s2.0-S0167639325000457-main.pdf`

---

## 一句話總結

讓人在不發出聲音的情況下，把臉部肌電訊號 (sEMG) 直接轉換成中文文字（EMG → Text）。

---

## 三個主要貢獻

| 貢獻 | 說明 |
|------|------|
| 1. 建資料集 | 史上第一個中文無聲語音 sEMG 資料集（NBA 報導題材） |
| 2. 提出模型 AuxCEMGR | Transformer + CTC + 拼音生成 + Session 對抗分類 |
| 3. 資料增強策略 | 頻譜消減 + 有聲資料補充 + Mixup，系統性提升效能 |

---

## 背景與動機

**問題**：一般 ASR 需要聲音，某些場合無法發聲（喉癌術後、噪音環境、保密需求）。

**EMG 的優勢**：肌肉收縮訊號在不發聲時仍存在，可偵測「無聲說話」的肌肉動作。

**前人不足**：
- 幾乎只針對英文
- 多數用傳統 HMM/GMM 架構
- 唯一深度學習例外（Wadkins 2019）只有 20 個詞彙

---

## 資料集

### 電極配置

- **8 通道差分電極**貼於臉部肌肉
- **1 個參考電極**在左鎖骨
- 採樣率：**1000 Hz**（EMG）/ 44100 Hz（音訊）
- 設備：Neuracle Technology NSW308M Bipolar System

| 通道 | 對應肌肉 | 重要性 |
|------|---------|--------|
| Ch 1 | 下顎肌 (jaw) | 靜默/有聲差異不明顯 |
| Ch 2 | 口輪匝肌 (orbicularis oris) | Baseline 最重要 |
| Ch 4 | 下顎骨肌 (mandibular) | AuxCEMGR 最重要 |
| Ch 5, 6 | 靠近喉嚨 (larynx) | 靜默模式反而較弱 |

### 收集流程

1. 志願者：一位女性普通話母語者
2. 文本：NBA 報導句子，平均 10 字/句，封閉詞表 667 個唯一字元
3. 兩種模式：**靜默模式**（EMG + 文字）/ **有聲模式**（EMG + 音訊 + 文字）
4. 每句重錄 **5 次**（5 sessions），每次重新貼電極

### 資料集統計

| 集合 | 句數 | 靜默時長 | 有聲時長 |
|------|------|---------|---------|
| 訓練 | 1,062 | 5.13 h | 4.98 h |
| 驗證 | 63 | 0.31 h | 0.31 h |
| 測試 | 113 | 0.48 h | 0.50 h |
| **合計** | **1,238** | **5.93 h** | **5.80 h** |

### 訊號前處理

1. **帶通濾波器**：10–400 Hz Butterworth 4 階
2. **陷波濾波器**：50, 150, 250, 350 Hz（去除市電 50Hz 及諧波）
3. **特徵萃取**：MFSC（log Mel 頻譜係數），Hanning 窗，36 個 Mel 濾波器

---

## 模型架構

### Baseline

```
輸入 S = s₁...sₙ（MFSC 特徵序列）
  ↓
CNN × 2（kernel 3×3）→ 時序壓縮
  ↓
Transformer Encoder × 6（8 頭，256 維）→ 高階特徵 H = h₁...hₜ
  ↓
CTC Decoder（Linear + Softmax）
  ↓
輸出 Y = y₁...yₘ（中文字元序列）
```

**為什麼用 Transformer**：捕捉長距離依賴，比 RNN/LSTM 更強。  
**為什麼用 CTC**：不需要時間對齊（T >> M），小資料集易訓練。

### 輔助任務 1：拼音生成 (Pinyin Generation)

- Encoder 共享，額外接一個獨立 CTC Decoder 輸出拼音序列
- **目的**：中文同音異字問題（如「知/之/支」同為 zhī），先學拼音可細化特徵
- 損失：`拼音損失 = -log( 模型預測正確拼音的機率 )`

### 輔助任務 2：Session 分類（對抗訓練）

```
Encoder 輸出 H
  ↓
梯度反轉層 GRL（梯度乘以 -1）
  ↓
Session 分類器
```

- **目的**：強迫 Encoder 學不出「是第幾次錄製」→ H 變成 session-invariant
- **概念**：Domain Adversarial Training（可延伸至跨人泛化）
- 損失：`Session 損失 = log( 模型預測正確 session 編號的機率 )`

### 總訓練目標

```
總損失 = 文字辨識損失
       + 權重1 × 拼音生成損失
       + 權重2 × Session 分類損失
```

最佳超參數：**權重1 = 權重2 = 1.0**

---

## 資料增強（三種方法）

| 方法 | 做法 | Test CER 改善 |
|------|------|--------------|
| 頻譜消減 (Spectral Subtraction) | 去噪版本加入訓練，資料量 ×2 | ~7–10% |
| 有聲資料補充 (Audible Data) | 有聲 EMG 打折加入（權重 γ=0.8） | ~5–9% |
| Mixup | 兩筆資料加權混合（α=0.02） | ~5–7% |

---

## 實驗結果

### 主要結果

| 模型 | 設定 | Dev CER | Test CER |
|------|------|---------|---------|
| Baseline | 無增強 | 63.8% | 66.5% |
| Baseline | 完整增強 | 37.2% | 44.5% |
| **AuxCEMGR** | **完整增強** | **30.7%** | **38.0%** |
| Wadkins LSTM | 完整增強 | 58.3% | 66.8% |

### 關鍵發現

1. **拼音輔助任務最有效**：拼音損失權重 > 0.5 時，CER 低於 Baseline（無論 Session 損失權重為何）
2. **三種增強缺一不可**：單獨移除任一方法均導致明顯下降
3. **Transformer >> LSTM**：LSTM 甚至無法從有聲資料中獲益
4. **Ch 4 最重要**（下顎骨肌），Ch 5, 6（喉嚨）在靜默模式反而最弱
5. **電極數量**：6–7 個電極效果接近 8 個，可提升穿戴舒適度

### 分析結果

- **句子長度**：≥12 字時 CER 明顯上升
- **Session 穩定性**：AuxCEMGR (Final) 跨 session 最穩定
- **有聲/靜默切換**：加入有聲訓練資料後，模型辨識有聲 EMG 效果大幅提升

---

## 論文限制（自承）

| 限制 | 說明 |
|------|------|
| 單一受試者 | 無法跨人泛化（subject-dependent） |
| CTC 封閉詞表 | 無法處理 OOV（詞表外字元） |
| 封閉領域 | 只有 NBA 題材，不能做開放領域 |
| CER 仍高 | 38% 尚不達實用標準 |

---

## 與我的研究的關聯

| 面向 | 論文做法 | 我的研究可延伸之處 |
|------|---------|-----------------|
| 跨人泛化 | 只有一人 | Session 分類的對抗訓練 → 延伸為跨人對抗訓練 |
| 資料集 | 自建中文 NBA | 使用 CSL-EMG 資料集 |
| 解碼 | CTC | 可考慮加入語言模型 beam search |
| 電極 | 8 通道 | 探討最少需要幾個電極 |

---

## 五個核心問題（讀論文的基本檢驗）

1. **他們解決了什麼問題？** 中文無聲語音 sEMG → 文字的端到端辨識
2. **方法核心是什麼？** Transformer + CTC + 拼音輔助 + Session 對抗訓練
3. **資料怎麼收集與處理？** 自建資料集，8 通道 1000Hz，MFSC 特徵
4. **結果如何？** 最佳 38.0% CER，顯著優於 LSTM baseline
5. **限制在哪？** 單人、封閉詞表、封閉領域

---

## 重要引用文獻

- Gaddy & Klein (2020)：EMG 無聲語音數位化（英文先驅）
- Vaswani et al. (2017)：Attention is All You Need（Transformer）
- Graves et al. (2006)：CTC 原始論文
- Ganin & Lempitsky (2015)：梯度反轉層 (GRL)，Domain Adversarial Training
- Zhang et al. (2018)：Mixup 原始論文
