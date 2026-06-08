# Silent Speech Decoding Using Spectrogram Features Based on Neuromuscular Activities

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊 | Brain Sciences, 2020, Vol. 10, Article 442 |
| DOI | doi:10.3390/brainsci10070442 |
| 年份 | 2020（投稿 2020-05-13，接受 2020-07-08，發表 2020-07-11） |
| 作者 | You Wang, Ming Zhang, RuMeng Wu, Han Gao, Meng Yang, Zhiyuan Luo, Guang Li |
| 機構 | 浙江大學（State Key Laboratory of Industrial Control Technology）；中國礦業大學；倫敦大學皇家哈洛威學院 |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/第一章期刊/第三段/Silent Speech Decoding Using Spectrogram Features.pdf` |
| 備註 | 與 Ye et al. (2020 SMC) 同一研究組（浙大 Guang Li 實驗室）；本文強調通道間協同特徵，Ye (2020) 強調注意力機制 |

---

## 2. 一句話總結

以 STFT 頻譜圖搭配預訓練 Xception 遷移學習提取多通道 sEMG 的跨通道空間特徵，再以雙向 LSTM 解碼，在 7 名受試者的中文 10 詞無聲語音任務上達到 90% 準確率，首次系統性論證多通道 sEMG 通道間協同資訊的辨識價值。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 首次明確提出以頻譜圖作為「通道交互（channel-interactive）」表示，以 Xception 遷移學習挖掘多通道 sEMG 的跨通道空間關聯 |
| 2 | 比較 MLP/CNN/bLSTM 三種解碼器，bLSTM 以 90% 準確率最佳，推論時間 < 50 ms |
| 3 | 揭示無聲語音中多肌肉的「協同機制（synergic mechanism）」，支持未來研究擴展至詞組或句子層級 |

---

## 4. 背景與動機

**問題定位：**
既有研究多採用「逐通道（channel-wise）」特徵提取，忽略多通道之間的相關性。語音由多塊肌肉協同運作產生，無聲語音中同樣存在肌肉間的協同機制。

**技術切入點：**
- 把多通道 sEMG 各自轉換為頻譜圖 → 視為一組圖像（「固定尺寸視頻」的概念）
- 以 Xception（ImageNet 預訓練圖像分類器）提取每張頻譜圖的空間特徵
- 以 bLSTM 在通道維度上建模跨通道時序依賴

**與同組 Ye (2020 SMC) 的對比：**
- 本文特色：Xception 遷移學習 + 跨通道空間特徵 + bLSTM
- Ye (2020)：STFT + Inception Block CNN + 注意力 BLSTM（同樣是浙大，但側重注意力機制）

---

## 5. 資料集

**受試者：**
- 7 名學生（男 4 女 3），年齡 20–25 歲（平均 22 歲）
- 通過浙江大學倫理委員會審批（ZJUEHAPC2019-CSEA01），遵循赫爾辛基宣言

**說話模式：** 想像說話（imagine speaking）—— 受試者看到螢幕上的詞彙後，在腦中/神經肌肉層面模擬發音，無聲無明顯嘴部動作

**詞彙（10 個中文詞，用於機器人/設備控制）：**

| 標籤 | 漢字 | 英文含義 |
|------|------|---------|
| 0 | 噪 | null（背景/靜音類別） |
| 1 | 1# | No. 1 |
| 2 | 2# | No. 2 |
| 3 | 前 | forward |
| 4 | 后 | backward |
| 5 | 左 | left |
| 6 | 右 | right |
| 7 | 快 | accelerate |
| 8 | 慢 | decelerate |
| 9 | 停 | stop |

**樣本數：** 共 69,296 有效樣本，各類 6510–7964（類別略不均衡）；樣本長度約 2000 ms

**電極設備：**
- 通道數：6（ch2、ch5 雙極導出，其餘單極）
- 採樣率：1000 Hz，24-bit ADC，帶寬 ~5 kHz
- 前端：DC 濾波 + 5 kHz 低通（RC 濾波器）
- 參考電極：耳後乳突部（2 個）
- 電極阻抗：< 5 kΩ

**電極位置（6 通道）：**

| 通道 | 導出方式 | 目標肌肉 |
|------|---------|---------|
| ch 1 | 單極 | 提口角肌（levator anguli oris） |
| ch 2 | 雙極 | 提口角肌（levator anguli oris） |
| ch 3 | 單極 | 頸闊肌（platysma） |
| ch 4 | 單極 | 外舌肌（extrinsic tongue）+ 二腹肌前腹（digastric anterior belly） |
| ch 5 | 雙極 | 外舌肌（extrinsic tongue） |
| ch 6 | 單極 | 翼外肌（lateral pterygoid） |

---

## 6. 模型架構

### 前處理

```
原始 6ch sEMG (1000 Hz)
    |
    v
[8th order Butterworth BP 0.15–300 Hz]
（去除 DC 偏移與高頻雜訊）
    |
    v
[Comb notch filter：50 Hz 及其諧波]
（去除工頻干擾）
    |
    v
[QVR（Quadratic Variation Reduction）基線漂移去除]
z = [I − (I + λDᵀD)⁻¹] × z̃，λ=100
```

### 特徵提取（STFT → Xception 遷移學習）

```
每通道 sEMG
    |
    v
[STFT → 頻譜圖 = |STFT(x)|²]
參數：Hanning 窗，窗長 512 ms，採樣率 1000 Hz，重疊 50%，FFT 長度 64
→ 時間-頻率二維圖像
    |
    v
[縮放至 299×299]
    |
    v
[預訓練 Xception（ImageNet，深度可分離卷積+殘差連接）]
每通道輸出：1000 維特徵向量
    |
    v
[6 通道拼接 → 6×1000 特徵矩陣/樣本]
```

**Xception 遷移策略：** Fine-tuning（以較小學習率訓練所有權重，並更新部分偏置）

### 三種解碼器比較

**MLP（Multi-Layer Perceptron）：**
```
Input 6×1000 → Dense(512,ReLU) → Dense(512,ReLU) → Dense(256,ReLU)
→ Dense(256,ReLU) → Dense(10) → Softmax
Dropout: 0.2，Optimizer: Adam，準確率: 0.85
```

**CNN：**
```
Input 6×1000 → Conv1(1×3 filter, 64 maps) → Conv2(1×5 filter, 64 maps)
→ BatchNorm → MaxPool(1×2) → Flatten(192000) → Dense(128) → Dense(10) → Softmax
Dropout: 0.5，Optimizer: Adadelta，準確率: 0.87
```

**bLSTM（最佳）：**
```
Input 6×1000
→ BiLSTM_1(6×1024) → BiLSTM_2(6×1024) → BiLSTM_3(6×512)
→ Dense(128) → Dense(10) → Softmax
Dropout: 0.2，Optimizer: RMSprop，準確率: 0.90
```

**共同超參數：**
- 初始學習率：1×10⁻³
- 學習率衰減：ReduceLROnPlateau（factor=0.2，patience=20，min_lr=0.5×10⁻⁶）
- Early stopping：patience=80
- Batch size：32，Activation：ReLU，Loss：Cross Entropy
- 框架：Keras + TensorFlow，平台：Intel i5-7400 @ 3 GHz

---

## 7. 資料增強

無傳統資料增強。訓練/驗證/測試分割為 7:2:1 隨機分割。

---

## 8. 實驗結果

### 三種解碼器比較（測試集）

| 解碼器 | 測試準確率 | 訓練時間 | 推論時間（單樣本）|
|--------|----------|---------|----------------|
| MLP | 0.85 | ~8 h | < 50 ms |
| CNN | 0.87 | ~6 h（最快）| < 50 ms |
| **bLSTM** | **0.90** | ~10 h（最慢）| < 50 ms |

### 混淆矩陣觀察（bLSTM）

| 觀察 | 細節 |
|------|------|
| 最高準確率 | 類別 0（噪/null）和 8（慢/decelerate）最高 |
| 最低準確率 | 類別 1、5、6（1#、左、右）相對較低 |
| 最難區分 | 類別 4（后）vs 類別 6（右）——三個解碼器均有此混淆，推測發音肌電活動相似 |

---

## 9. 論文限制

- 孤立詞分類，未擴展至詞組或句子
- 7 名受試者，樣本量偏少
- 類別略不均衡（6510–7964 樣本/類），雖在可接受範圍
- 說話模式為「想像說話（imagine speaking）」，神經肌肉活動信號弱（< 1 mV），比傳統 sEMG 雜訊比更具挑戰性
- Xception 為逐通道提取（per-channel），跨通道空間關聯是在 bLSTM 通道序列建模中體現，而非 Xception 直接提取
- 未測試說話者獨立（speaker-independent）場景
- 翼外肌（lateral pterygoid）電極位置不易定位（位於口腔深部附近），重複性有挑戰

---

## 10. 與我的研究的關聯

| 面向 | Wang et al. (2020) | 我的研究方向 |
|------|-------------------|-------------|
| 語言 | 普通話（10 詞） | 台灣注音符號 |
| 通道數 | 6 | 4 |
| 採樣率 | 1000 Hz | 待確認 |
| 說話模式 | 想像說話（無嘴部動作）| 無聲語音 |
| 特徵 | STFT 頻譜圖 + Xception | 待設計 |
| 模型 | Xception + bLSTM | CNN + Transformer + CTC |
| 最佳準確率 | 90% | 目標待定 |

**對我的啟示：**
1. **遷移學習可行**：ImageNet 預訓練的視覺模型用於 sEMG 頻譜圖有效，你的系統也可考慮類似遷移學習方案（如以預訓練 CNN 提取 STFT 特徵）
2. **翼外肌（lateral pterygoid）通道**：本文選用此通道，與多數先前研究的「5 條臉部肌肉」組合有差異，反映中文無聲語音對口腔深部肌肉的依賴
3. **「想像說話」vs「無聲嘴部動作」**：本文最弱的訊號來源（< 1 mV，無嘴部動作），與 Ye (2020) 的「mime speech」（有微嘴部動作）不同。若你的受試者需要無任何動作，本文是更接近的參照
4. **通道間協同**：本文的核心訊息對你的論文有直接意義——你的 4 通道系統設計時應明確說明通道組合如何捕捉協同機制，而非只看單通道性能

---

## 11. 五個核心問題

| 問題 | 答案 |
|------|------|
| 研究問題是什麼？ | 多通道 sEMG 的通道間協同資訊能否透過頻譜圖 + 遷移學習有效提取，用於無聲語音辨識？ |
| 方法是什麼？ | 6ch sEMG → STFT 頻譜圖 → 預訓練 Xception（6000 維特徵）→ bLSTM 解碼 |
| 資料如何取得？ | 7 名受試者，10 個中文詞，69,296 有效樣本，1000 Hz，想像說話條件 |
| 主要結果？ | bLSTM 90% > CNN 87% > MLP 85%；推論 < 50 ms |
| 主要限制？ | 孤立詞、7 人、無跨人測試、想像說話訊號弱 |

---

## 12. 重要引用文獻

| 引用 | 內容 | 重要性 |
|------|------|--------|
| Kapur et al. (2018) [ref 6] | AlterEgo，MFCC+1D CNN，92% | 本文定位的主要先行研究之一 |
| Wand et al. (2014) [ref 9] | BDPF HMM，34.7% WER | 本文對比的傳統方法基準 |
| Chollet (2017) [ref 26] | Xception 原始論文 | 本文遷移學習骨幹網路 |
| Schultz & Wand (2010) [ref 8] | Modeling coarticulation in EMG-based speech recognition | 本文的 sEMG 電極位置參考 |
| Fasano & Villani (2014) [ref 37] | QVR 基線漂移去除方法 | 本文前處理 QVR 方法來源 |
