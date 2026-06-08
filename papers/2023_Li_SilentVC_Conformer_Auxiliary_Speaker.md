# Silent Speech Interface With Vocal Speaker Assistance Based on Convolution-Augmented Transformer

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊 | IEEE Transactions on Instrumentation and Measurement, Vol. 72, 2023 |
| DOI | 10.1109/TIM.2023.3273660 |
| 年份 | 2023（投稿 2022-08-24；接受 2023-04-10；發表 2023-05-08）|
| 作者 | Huiyan Li, Yihao Liang, Han Gao, Li Liu, You Wang（通訊）, Daqi Chen, Zhiyuan Luo, Guang Li |
| 機構 | **浙江大學**工業控制技術國家重點實驗室；廣州大學；Royal Holloway, University of London |
| 資助 | 中央高校基本科研業務費 226-2022-00086；工業控制技術國家重點實驗室 ICT2022B02 |
| IRB | ZJU IRB CBEIS-2022 |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/第一章期刊/第四段/Silent_Speech_Interface_With_Vocal_Speaker_Assistance_Based_on_Convolution-Augmented_Transformer.pdf` |
| **重要注意** | **同一 Guang Li 研究組（Li 2022 的 follow-up）；sEMG→語音重建（非文字），跨說話者場景** |
| 論文任務 | silentVC（silent Voice Conversion）：主說話者（primary）靜音 sEMG → 輔助說話者（auxiliary）音訊 |
| 與使用者研究的關聯 | Conformer 架構（CNN+Transformer 混合）= 你規劃的架構核心；139 聲調音素輔助任務；跨說話者設計 |

---

## 2. 一句話總結

提出輔助有聲說話者架構（auxiliary vocal speaker），讓主說話者只需提供靜音 sEMG，由輔助說話者提供同文本的有聲 sEMG 與音訊作為訓練監督，以 CNN+Transformer 混合的 Conformer 編碼器實現跨說話者普通話靜音語音轉換（silentVC），ASR 客觀 CER **10.69%**，優於 LSTM（79.89%）和純 Transformer（33.24%）基線。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | **輔助有聲說話者架構（silentVC task）**：首次提出在跨說話者場景下無需主說話者自行錄製有聲語音的靜音語音轉換方案，解決了現有方法要求同一說話者同時提供有聲/無聲錄音的限制 |
| 2 | **優化 Conformer-silentVC 編碼器**：在 Conformer（CNN+Transformer）基礎上修改架構——採用序列結構取代 Macaron 結構、SeLU 取代 Swish 激活函數，提升訓練穩定性；CER 相較標準 Conformer 降低 7.92% |
| 3 | **DTW 動態時間規整靜音幀時長提取算法**：設計迭代更新的 DTW 算法（Algorithm 1），對齊不同說話者、不同說話速率的靜音/有聲 sEMG，並每 5 個 epoch 更新一次，自適應解決跨說話者語速不匹配問題 |

---

## 4. 背景與動機

**問題一（語言挑戰）：** 現有 sEMG SSI 以英語為主，普通話有 5 個聲調、大量同音詞，直接遷移困難。

**問題二（跨說話者挑戰）：** 現有普通話 sEMG 方法（Wang et al. 2020、Li et al. 2022）要求同一說話者錄製有聲+無聲配對，對喉切除等完全失聲者不可行。

**問題三（兩步驟流程的缺陷）：** sEMG → 文字 → TTS 的兩步驟流程：
- 時間消耗高（兩個推理步驟）
- 誤差傳播：text 辨識錯誤會被 TTS 放大（如 /zh/ 誤辨為 /ch/，導致聲學特徵完全錯誤）
- 失去 F0（基本頻率）與 energy（音量）資訊，說話節律無法還原

**本文解法：** 輔助說話者（不同於主說話者）提供音訊 ground truth，直接端對端 sEMG → 音訊。

---

## 5. 資料集

**sEMG 設備：**

| 項目 | 規格 |
|------|------|
| 系統 | 多通道生物電訊號採集設備（24-bit ADC, μV 解析度）|
| 電極 | 5 通道（ch1 差分電極，其餘單電極）|
| 電極位置 | 臉部與頸部，與普通話發音相關肌肉（Fig. 1）|
| 採樣率 | **2000 Hz** |
| 音訊 | 頭戴式麥克風，**16 kHz** |

**受試者：**

| 角色 | 數量 | 說明 |
|------|------|------|
| 主說話者（Primary Speaker）| 4（P1f, P2m, P3f, P4m）| 靜音模式，健康普通話母語者，25±2 歲 |
| 輔助說話者（Auxiliary Speaker）| 每位主說話者對應 2 名 | 不同性別，有聲模式，同文本 |
| 共 8 對 silentVC | 4 × 2 | |

**語料庫：**
- AISHELL3 普通話語料庫
- 1044 詞，920 字
- 主說話者：同文本靜音重複 **5 次**
- 輔助說話者：同文本有聲錄製 **1 次**（僅用於計算對齊，不參與訓練）
- 最少 32.32 分鐘 / 試驗
- 資料切分：8:1:1（train/val/test），按重複次數切分

**資料統計（Table I）：**

| 主說話者 | 靜音訓練(min) | 靜音驗證 | 靜音測試 | 靜音發聲數 | 輔助說話者 | 有聲時長(min) | 有聲發聲數 |
|----------|-------------|---------|---------|-----------|-----------|-------------|-----------|
| P1f | 40.17 | 4.93 | 5.14 | 690 | A1f, A1m | 9.45, 8.55 | 138 |
| P2m | 25.88 | 3.38 | 3.06 | 350 | A2f, A2m | 4.74, 4.52 | 70 |
| P3f | 26.16 | 3.27 | 3.32 | 510 | A3f, A3m | 5.88, 5.71 | 102 |
| P4m | 26.75 | 3.38 | 3.06 | 550 | A4f, A4m | 6.28, 6.63 | 110 |

---

## 6. 方法

### 前處理

```
原始 sEMG (5ch, 2000 Hz)
    ↓
[RC 濾波：DC 濾波 + 5 kHz 低通（移除 DC 偏移與高頻干擾）]
    ↓
[8 階 Butterworth 帶通 4–400 Hz（去除基線漂移與高頻）]
    ↓
[自適應梳狀濾波（adaptive comb filter）去除 50 Hz 電源干擾]
```

### 特徵提取

**sEMG 特徵（355 維/幀）：**
- 窗長 128 點（Hanning），hop 32 點
- 時域特徵（TD × 6 維）+ STFT 振幅
- 6 TD 特徵：參照 Jou et al. [47]（MAV, ZC, SSC, WL, AR, RMS 等）

**音訊特徵（80 維/幀）：**
- 80 維 mel 頻譜圖，80-7600 Hz
- 窗長 1024 點，hop 256 點

### 模型架構：MFT（Multi-task Feature Transformation）

```
靜音 sEMG 特徵 I_{1:T'} (T'幀, 355維)
    ↓
[Linear + ReLU]
    ↓
[6× Conformer-silentVC 塊] ← 編碼器
    ↓
H_{1:T'} 隱藏表示
    ↓
[Length Regulator（DTW 時長對齊，T'→T）]
    ↓
H_{1:T} 對齊後隱藏表示
    ↓
[6× Transformer-silentVC 塊] ← 解碼器
    ↓
[Post-Net（5層卷積 + 殘差）]
    ↓
O_{1:T} 預測 Mel 頻譜圖（80維）
    ↓
[Parallel WaveGAN 聲碼器（預訓練）]
    ↓
合成音訊
```

**Conformer-silentVC 塊（Fig. 4b）：**
```
x → MHA（多頭注意力）→ + → Conv Module → + → FFN → LayerNorm → y
         ↑—skip—↑            ↑—skip—↑     ↑—skip—↑
```
- 相對位置編碼（Transformer-XL 風格，比正弦位置編碼更適應不同輸入長度）
- **序列結構**（非 Macaron）：MHA → Conv → FFN，避免 Macaron 雙半步 FFN 訓練不穩定

**Convolution Module（Fig. 4c）：**
```
LayerNorm → 1D Pointwise Conv + GLU → 1D Depthwise Conv → BN → SeLU → 1D Pointwise Conv → Dropout
```
- 激活函數：**SeLU**（自我正規化，避免梯度消失/爆炸，優於 Swish/ReLU/Hardtanh）
- GLU 用於門控選擇性局部特徵

**輔助任務（多任務學習）：**

| 任務 | 監督訊號來源 | 損失函數 | 權重 |
|------|------------|---------|------|
| 特徵轉換（主任務）| 輔助說話者 mel 頻譜圖 | MAE（L_mel）| λ_mel = 1.0 |
| 靜音幀時長預測 | DTW 對齊的靜音幀時長 | MSE（L_dur）| λ_dur = 1.0 |
| 音素（聲調）預測 | Montreal Forced Alignment | CrossEntropy（L_ph）| λ_ph = 0.5 |

**音素詞彙大小：139（含有聲調的普通話母音與子音，即聲調素）**

**總損失：** L = λ_mel × L_mel + λ_dur × L_dur + λ_ph × L_ph

### DTW 靜音幀時長提取（Algorithm 1）

核心思路：用輔助說話者的有聲 sEMG A_{1:T} 和主說話者的靜音 sEMG I_{1:T'} 做 DTW 對齊，取得每個靜音幀對應多少個音訊幀的時長資訊，每 5 個 epoch 用預測 mel 頻譜圖更新 DTW cost function，自適應迭代校正。

---

## 7. 訓練設定

| 參數 | 值 |
|------|---|
| Toolkit | ESPnet（開源）|
| Batch size | 8 |
| Epochs | 160 |
| Optimizer | Adam（β1=0.9, β2=0.98, ε=1e-9）|
| Learning rate | Warm-up 4000 steps → 峰值 1/(4000×d_model)^0.5 → 逆平方根衰減 |
| 注意力維度 d_model | 384 |
| Conv kernel | 7；FFT kernel | 3；FFT hidden | 1536 |
| Dropout | 0.1 |
| Post-net | 5 層 × 256 通道，kernel 5，dropout 0.5 |
| PWG 聲碼器 | 說話者無關預訓練，條件為所有輔助說話者音訊 |

---

## 8. 實驗結果

### 客觀評估（ASR CER，Table III, Fig. 5）

- Ground truth mel → PWG 上界：CER **1.74%**
- 本文方法：CER **10.69% ± 5.79%**
  - 最佳：P2m → 5.83%；最差：P4m → 19.53%（阻抗較高導致 SNR 較低）

| 指標 | Mean | Std |
|------|------|-----|
| MCD (dB) | 3.36 | 0.39 |
| log F0-RMSE | 0.21 | 0.019 |
| STOI | 0.85 | 0.046 |

### 主觀評估（26 名母語聽眾，Table IV）

| 指標 | Mean | Std |
|------|------|-----|
| 聽眾辨識 CER | 5.31% | 3.06% |
| MOS（1–5）| 3.95 | 0.16 |

人工評估 CER（5.31%）優於 ASR CER（10.69%），因為普通話同音詞多，人類可利用語境推斷。

### 與其他方法比較（Table V, VI）

| 方法 | ASR CER | 人工 CER | MOS |
|------|---------|---------|-----|
| LSTM-based [Gaddy 2020] | 79.89±16.99 | 83.71±25.67 | 1.50±0.32 |
| Transformer-based [Gaddy 2021] | 33.24±19.48 | 33.44±21.33 | 3.07±0.56 |
| **本文（Proposed）** | **10.69±5.79** | **5.31±3.06** | **3.95±0.16** |

---

## 9. 消融實驗（Table VII）

| 組合 | CER | 備注 |
|------|-----|------|
| **本文完整架構** | **10.69±5.79** | Conv + 序列結構 + SeLU |
| 去除 Conv Module | 31.60±6.38 | **CER +20.91%**；局部特徵最重要 |
| 使用 Macaron 結構 | 14.80±5.50 | CER +4.11%；兩個半步 FFN 不穩定 |
| SeLU → Hardtanh | 14.10±5.19 | |
| SeLU → ReLU | 14.81±7.69 | |
| SeLU → Swish | 14.81±7.69 | |
| 原始 Conformer [42] | 18.61±6.33 | CER +7.92% |

**關鍵消融結論：**
1. 卷積模組是最重要的組件（去除後 CER 增加 20.91%）——局部時序特徵對 sEMG 理解至關重要
2. SeLU 自我正規化激活最適合此任務
3. Macaron 雙半步 FFN 對 silentVC 不穩定，序列結構更優

### sEMG→音素→TTS vs 直接 sEMG→音訊（Section IV.E）

| 方法 | ASR CER | MCD | STOI |
|------|---------|-----|------|
| 直接 sEMG→audio（本文）| 10.69% | 3.36 | 0.85 |
| sEMG→phoneme→TTS | +31.22%（CER 增加）| +3.42 MCD | -0.45 |

直接轉換優於兩步驟流程的原因：
- 避免音素誤辨誤差傳播（/zh/ 誤辨為 /ch/ 直接導致音訊失真）
- 直接保留 F0 輪廓與能量（節律資訊）
- 計算效率更高

---

## 10. 與 Li et al. (2022) 的比較

| 面向 | Li 2022（SSRNet）| Li 2023（silentVC/本文）|
|------|----------------|----------------------|
| 研究組 | 浙大 Guang Li | 浙大 Guang Li（同組）|
| 任務 | sEMG→音訊（單說話者）| sEMG→音訊（跨說話者）|
| 架構 | FFT Encoder + 長度調節 + FFT Decoder | Conformer Encoder + 長度調節 + Transformer Decoder |
| 編碼器 | Feed-Forward Transformer（純注意力）| **Conformer（CNN+Transformer 混合）** |
| 輔助任務 | 聲調素分類（λ=0.5）+ 有聲 EMG 重建 | 幀音素預測（λ=0.5）+ 幀時長預測 |
| 最佳 CER | 6.41%（主觀，單說話者）| 10.69%（ASR，跨說話者），5.31%（人工）|
| 說話者設定 | 單說話者：自行提供有聲/無聲配對 | 跨說話者：輔助說話者提供有聲配對 |
| 聲調素詞彙 | 139 | 139 |
| 語料庫 | AISHELL3, 6 說話者 | AISHELL3, 4+2×4 說話者 |

---

## 11. 與我的研究的關聯

| 面向 | Li 2023（本文）| 我的研究方向 |
|------|--------------|-------------|
| 架構類型 | **Conformer（CNN+Transformer）** | **CNN + Transformer（相同方向）** |
| 語言 | 普通話，139 聲調素 | 台灣注音符號，聲調 |
| 任務 | sEMG → 音訊（語音重建）| sEMG → 注音（語音辨識）|
| 輔助任務 | 音素預測（L_ph）+ 時長預測（L_dur）| 注音/聲調輔助任務 |
| 跨說話者 | 是（auxiliary speaker）| 未定 |

**對我的啟示：**

1. **Conformer = CNN + Transformer 優於純 Transformer：** 本文消融實驗明確量化——去除卷積模組 CER 上升 20.91%，說明 sEMG 的局部時序特徵（小窗口內的肌肉活化模式）比長程全局特徵更關鍵，這直接支撐在設計架構時保留 CNN 前端的決策

2. **SeLU 激活的優越性：** 對 sEMG 特徵轉換任務，SeLU 的自我正規化特性比 Swish/ReLU 更穩定，可考慮在卷積模組中採用

3. **139 聲調素音素詞彙大小的實際驗證：** 與 Li 2022 一致，本文也採用 139 作為普通話聲調音素詞彙，這說明 Mandarin 聲調語音系統的最小完備表示確實需要這個規模

4. **直接端對端優於兩步驟：** sEMG-to-audio 比 sEMG-to-text-to-speech 好 31.22% CER，說明引入音素/注音輔助任務的正確方式是作為**輔助損失**而非作為**中間步驟**，這與你規劃的 CTC+輔助任務架構方向一致

5. **DTW 在跨說話者時長對齊中的必要性：** 不同說話者的語速不匹配必須透過顯式的時長對齊解決，這對未來錄製多說話者資料集也是重要的前處理設計考量

---

## 12. 五個核心問題

| 問題 | 答案 |
|------|------|
| 研究問題是什麼？ | 在跨說話者場景中，如何讓靜音說話者無需自行錄製有聲語音就能實現 sEMG→音訊轉換？ |
| 方法是什麼？ | 輔助說話者提供有聲 sEMG+音訊作為 ground truth；Conformer 編碼器（CNN+Transformer）+ DTW 時長對齊 + 音素輔助任務 |
| 資料如何取得？ | 4 主說話者（靜音×5 重複）+ 每人 2 輔助說話者（有聲×1），AISHELL3，浙大 IRB |
| 主要結果？ | ASR CER 10.69%，人工 CER 5.31%，MOS 3.95；卷積模組最關鍵（去除後 +20.91%）|
| 主要限制？ | 需要輔助說話者配合錄製（不適合即時應用）；先天失聲者肌肉運動模式與正常人不同；電極位置個體差異導致跨受試者差異大 |
