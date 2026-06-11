# Design and Implementation of a Silent Speech Recognition System Based on sEMG Signals: A Neural Network Approach

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊 | Biomedical Signal Processing and Control, vol. 92, 2024, Article 106052 |
| DOI | 10.1016/j.bspc.2024.106052 |
| 年份 | 2024（投稿 2023-05-31；修訂 2023-12-18；接受 2024-01-29；線上 2024-02-08）|
| 作者 | Bokai Huang, Yizi Shao, Hao Zhang, Peng Wang, Xianxiang Chen, Zhenfeng Li, Lidong Du, Zhen Fang, Hui Zhao, Bing Han |
| 機構 | Aerospace Information Research Institute, Chinese Academy of Sciences（AIRCAS）；中國科學院大學；中國人民解放軍總醫院（耳鼻喉頭頸外科）|
| PDF 路徑 | `/Users/rayopenclaw/Downloads/Design and implementation of a silent speech recognition.pdf` |
| **定位** | 中文 sEMG 孤立詞分類研究，設計 135 類普通話語料庫（作者自稱當時中文 SSR 最大語料庫），明確論述普通話聲調資訊在 sEMG 中丟失所造成的固有難題 |

---

## 2. 一句話總結

AIRCAS 組：8 通道臉頸部 sEMG + 時頻混合特徵（5 TD + 40 fbank，每通道 45 維）+ 速度擾動與時頻遮罩資料增強（擴增至原始量四倍）+ 多架構比較（純 GRU vs. 多種 CNN+GRU），在 12 受試者、135 類普通話孤立詞分類任務上，**純 3 層雙向 GRU 達到多受試者混合 88.01%、單受試者最高 97.19%**，優於所有 CNN+RNN 架構；論文同時明確指出普通話同音字與聲調資訊缺失是中文 sEMG-SSR 的結構性難題。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 將語音辨識中的**速度擾動（speed perturbation）與時頻遮罩（SpecAugment-style masking）**移植至 sEMG 訊號，資料擴增至 4 倍，多受試者準確率提升 +1.7%（86.33% → 88.01%）|
| 2 | 提出**時頻混合特徵**：5 維時域特徵（E_low、MAV_low、E_high、MAV_high、ZCR_high）+ 40 維 fbank，每通道 45 維，適應變長 sEMG 序列的幀級表示 |
| 3 | 系統比較純 GRU 與六種 CNN+GRU 架構，發現**純 GRU 全面優於 CNN+RNN**，論證 sEMG 特徵圖的時序依賴性強於空間特徵（CNN 的局部性與平移不變性假設不適用於 sEMG 抽象特徵圖）|

---

## 4. 背景與動機

**問題定位：**
1. 機器學習方法（SVM、LDA）依賴手工特徵，無法表示不定長序列的短時資訊
2. 現有中文 sEMG 研究（Chen 2023 的 33 類、Wu 等的 100 類）詞彙量受限，難以覆蓋日常通訊需求
3. 資料量不足是深度學習方法的主要瓶頸，語音辨識中的資料增強技術尚未驗證於 sEMG

**語料設計考量：**
- 涵蓋日常生活常用詞語，共 11 語意類別（描述、程度、身體部位、否定、問候、請求、回應、疑問、物品、方位、時間）
- 大部分類別為 1–2 字，最長 4 字
- 作者自稱（Section 3.1）設計當時已知最大中文 SSR 語料庫

---

## 5. 資料集

**硬體設備：**

| 裝置 | 規格 |
|------|------|
| ADC | ADS1298IPAGR，德州儀器，24-bit |
| 採樣率 | 1000 Hz |
| SNR | 38–50 dB（各通道），背景雜訊 2.4–4.7 μV |

**電極配置（8 通道，7 肌肉）：**

| 通道 | 肌肉 | 備注 |
|------|------|------|
| 1 | 顴小肌（zygomaticus minor）| — |
| 2 | 口輪匝肌（orbicularis oris）| — |
| 3 | 提口角肌（levator anguli oris）| — |
| 4 | 頦肌（mentalis）| — |
| 5 | 降口角肌（depressor anguli oris）| — |
| 6 | 咬肌（masseter）| — |
| 7–8 | 下頜舌骨肌（mylohyoideus）| 雙側各一，為舌肌的體表代理訊號 |

- 驅動電極：前額中央；參考電極：右耳後乳突
- **刻意迴避喉部**：默語時無喉肌活動，且避免吞嚥動作干擾

**受試者：**
- 12 人（男 7、女 5），年齡 24.3±1.2，普通話母語者
- 倫理核准：中國科學院科技倫理委員會

**語料庫：**
- 135 類詞語，每類每受試者 20 次
- 原始樣本 32,376；增強後 129,504（4 倍）
- 每位受試者分兩天採集（各分兩段），以避免肌肉疲勞

---

## 6. 方法概述

**前處理：**
1. 0.05 Hz 高通濾波（去除基線漂移）
2. 50 Hz 陷波濾波（去除工頻干擾）
3. 各通道 z-score 正規化

**特徵提取（幀長 25 ms，步長 10 ms）：**

```
每幀每通道 → 45 維特徵
  ├── 時域（5 維）
  │     ├── 低頻帶：E_low（均值能量）、MAV_low（均值絕對值）
  │     └── 高頻帶：E_high、MAV_high、ZCR_high（過零率）
  └── 頻域（40 維）
        └── 40 個 Mel filter bank（fbank）能量

8 通道 × 45 維 = 每幀 360 維
最終特徵圖形狀：[360, T]（T = ⌊(t − step) / window⌋ + 1，變長）
```

**資料增強（×4）：**

| 技術 | 操作 | 目的 |
|------|------|------|
| 速度擾動（Speed Perturbation）| 原始訊號速度 ×0.9 / ×1.1 → 各生成 1 份 | 模擬跨受試者與跨 session 語速差異 |
| 時頻遮罩（TF Masking）| 特徵圖隨機遮罩部分頻率通道與時間步（F=40, T=40）| 提升對局部遮蔽的魯棒性 |

**模型架構（GRU 最佳）：**

```
輸入：[360, T] 特徵圖（可選 CNN 塊提取空間特徵）
    │
    ▼
[3 層雙向 GRU]
    │ 輸出：所有時間步的隱藏狀態
    ▼
[Max Pooling over time] → 固定長度向量
    │
    ▼
[MLP + Softmax] → 135 類概率
```

**訓練設定：**
- 優化器：Adam + warm-up LR schedule
- LR：1e-5 → 5e-4（前 3 epoch 線性增加）→ 1e-4（epoch 3–8 cosine 衰減）
- Batch：32；Epoch：30
- PyTorch；GPU：NVIDIA RTX 3090

---

## 7. 主要結果

**多受試者混合分類（Multi-subject Mixed, 5-fold CV）：**

| 模型 | 準確率（%）|
|------|-----------|
| **GRU（純）** | **88.01** |
| Multi-Scaled CNN+GRU | 81.53 |
| CNN+GRU | 80.20 |
| Inception+GRU | 79.85 |
| ParallelNet+GRU | 79.58 |
| ResNet+GRU | 79.35 |
| Xception+GRU | 78.70 |

**單受試者分類（Single Subject, 5-fold CV）：**

| 模型 | 平均（%）| Top-1（%）|
|------|---------|----------|
| **GRU（純）** | **87.93** | **97.19** |
| ResNet+GRU | 83.95 | 93.37 |
| CNN+GRU | 82.30 | 93.33 |

**資料增強消融（12 受試者，GRU）：**

| 設定 | 準確率（%）|
|------|-----------|
| 無增強 | 86.33 |
| 時頻遮罩 only | 87.43（+1.10）|
| 速度擾動 only | 87.32（+0.99）|
| 兩者併用 | **88.01（+1.68）** |

**跨受試者（Cross-subject）：47.22%**（以 7 人訓練、1 人驗證，準確率大幅下滑）

**跨 session（Cross-session）：95.70% → 78.67%**（同一受試者、相隔 4 天，下降 17%）

---

## 8. 類別層級分析

- 含 3 字以上的 22 類：全部 ≥85%，其中 20 類 ≥90%
- 單字類別普遍較低（59–75%），準確率最低為「腳」（jiao3）：59.57%
  - 29.79% 誤辨為「腰」（yao1）或「熱」（re4）——發音動作極相似
- **結論：音節數越少，發音動作越相似，越難區分**

---

## 9. 限制與未來工作

1. **跨受試者與跨 session 泛化性不足**：實際應用仍受限，遷移學習（transfer learning）被列為未來方向
2. **孤立詞離散辨識**：每個 utterance 視為整體類別，無法輸出語料庫外的詞語；連續辨識（逐詞/逐音節輸出）是下一步目標
3. **普通話固有難題**（Section 7.3，核心論述）：
   - 大量同音字 → sEMG 訊號極相似難以區分
   - 聲調語言 → sEMG 無法攜帶聲調資訊 → 進一步增加同音字混淆
   - 作者建議：語料設計應以多字詞為主，避免大量單字類別

---

## 10. 與本論文的關聯

| 面向 | 關聯 |
|------|------|
| **1.2.3 中文 sEMG 分類** | 8 通道、135 類普通話孤立詞分類，展示中文 sEMG-SSR 的可行性與挑戰規模 |
| **1.2.3 短詞辨識困難** | 1–2 字類別準確率僅 59–75%，連結到「注音輔助任務有助於區分發音相似的短字詞」的動機 |
| **1.2.3 聲調缺失問題** | Section 7.3 明確論述：sEMG 訊號無法保留聲調資訊，導致普通話同音字大量混淆——此問題是本論文設計注音輔助任務的核心動機之一 |
| **1.2.3 資料增強** | 速度擾動 + 時頻遮罩直接移植自語音辨識，可作為本研究增強 sEMG 資料的參考方案 |
| **1.2.2 電極配置** | 7 肌群 8 通道設計，刻意迴避喉部，與本論文臉頸部貼片設計相近；下頜舌骨肌（mylohyoideus）雙側量測提供舌肌代理訊號的依據 |
| **跨受試者問題** | 跨受試者準確率 47.22%，跨 session 下降 17%，量化了 sEMG 個體差異的嚴重程度，支持後續討論泛化性的必要性 |

---

## 11. 引用關鍵資訊

> Bokai Huang, Yizi Shao, Hao Zhang, Peng Wang, Xianxiang Chen, Zhenfeng Li, Lidong Du, Zhen Fang, Hui Zhao, and Bing Han, "Design and implementation of a silent speech recognition system based on sEMG signals: A neural network approach," *Biomedical Signal Processing and Control*, vol. 92, p. 106052, 2024. DOI: 10.1016/j.bspc.2024.106052

**引用重點：**
- 135 類普通話孤立詞分類，8 通道，12 受試者
- 純 GRU 優於 CNN+RNN（88.01%，多受試者）
- 速度擾動 + 時頻遮罩資料增強（+1.7%）
- 普通話聲調資訊在 sEMG 中丟失，加劇同音字混淆（Section 7.3）
- 跨受試者 47.22%；跨 session -17%

---

## 12. 關鍵詞

Silent speech recognition, sEMG, Mandarin Chinese, GRU, CNN+RNN, data augmentation, speed perturbation, time-frequency masking, fbank features, cross-subject, tonal language, homophones, electrode placement, mylohyoideus, AIRCAS
