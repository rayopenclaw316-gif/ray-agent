# Sequence-to-Sequence Voice Reconstruction for Silent Speech in a Tonal Language

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊/arXiv | arXiv:2108.00190v3 [cs.SD]（IEEE journal 格式投稿，2022 年 6 月第 3 版）|
| DOI | arXiv:2108.00190 |
| 年份 | 2022（arXiv 原始投稿 2021-07-31，v3 更新 2022-06-01）|
| 作者 | Huiyan Li*, Haohong Lin*, You Wang, Hengyang Wang, Ming Zhang, Han Gao, Qing Ai, Zhiyuan Luo, Guang Li |
| 機構 | State Key Laboratory of Industrial Control Technology, Zhejiang University；Royal Holloway, University of London |
| 資助 | Science Foundation of Chinese Aerospace Industry (JCKY2018204B053)；SKLICT 自主課題 ICT2021A13 |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/第一章期刊/第四段/equence-to-Sequence Voice Reconstruction for Silent Speech in a Tonal Language.pdf` |
| 研究組 | 浙大 Guang Li 組（同 Wang et al. 2020 Brain Sciences、Ye et al. 2020 SMC）|

---

## 2. 一句話總結

**首篇聲調語言 sEMG-to-Voice 語音重建研究**：以 Feed-Forward Transformer Seq2Seq 框架（SSRNet）整合長度調節器（解決無聲/有聲時序不對齊）、音調素分類（toneme，含聲調的音素）和有聲 EMG 重建兩個輔助任務，搭配 Parallel WaveGAN 聲碼器，在 6 名普通話受試者任務上主觀人類評估達到平均 **CER 6.41%**，明確論證神經肌肉訊號能傳遞聲調資訊（音調素分類準確率 96.07%）。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 首次將 Seq2Seq 架構（FFT Encoder + Length Regulator + FFT Decoder）引入 sEMG-to-Voice 任務，以長度調節器解決無聲 EMG 與音訊的**時間長度不對齊**問題 |
| 2 | 引入**音調素分類（toneme classification）**輔助任務，實驗證明這是中文 sEMG-to-Voice 中最關鍵因素（去除後 CER 上升 **132.75%**）；同時論證神經肌肉訊號確實傳遞聲調資訊（96.07% 準確率）|
| 3 | 建立首個 sEMG Mandarin 資料集（6 受試者，5.79 小時，AISHELL3 語料，包含有聲+5次無聲模式）|

---

## 4. 背景與動機

**問題定位：**
1. SSD 研究主要針對英語等非聲調語言；聲調語言（普通話）研究幾乎僅限孤立詞分類
2. **聲調語言的根本困難：** 普通話有 5 個聲調，帶聲調音節（toneme）共 139 個，而英語音素僅 47 個——相同資料量下，中文包含更高維度的資訊
3. 無聲 EMG 與音訊之間缺乏時間對齊的平行資料（silent speech 比 vocal speech 更長或更短）
4. 現有 sEMG-to-Voice 方法（Gaddy & Klein 2020）在聲調語言上失敗

**與 Xie et al. (2025) 的根本差異：**

| 面向 | 本文（Li et al. 2022）| Xie et al. (2025) |
|------|---------------------|------------------|
| 輸出模態 | **語音波形（voice）**| **文字（text）** |
| 任務類型 | 回歸（語音重建）| 序列標注（字符辨識）|
| 評估方式 | 主觀人類評估 CER + 客觀 MCD/STOI | 自動 ASR 評估 CER |
| 目標 | 恢復說話者個性與情感 | 快速、準確的文字辨識 |

**本文切入點：** 受 FastSpeech（TTS）啟發，以 Seq2Seq 模型直接從 sEMG 生成 mel-spectrogram，再以 PWG 聲碼器合成音訊波形，透過長度調節器解決對齊問題，透過音調素分類強化聲調感知。

---

## 5. 資料集（sEMG Mandarin）

**硬體設備：**

| 裝置 | 規格 |
|------|------|
| EMG | 多通道 sEMG 錄製系統，標準濕性 Ag/AgCl 電極，**2000 Hz** |
| 音訊 | 頭戴麥克風，16000 Hz，1 通道 |

**電極位置（5 通道，Table I）：**

| 通道 | 位置 | 導出方式 |
|------|------|---------|
| ch1 | 鼻子**右側** 1 cm | 差分（differential）|
| ch2 | 嘴角**右側** 1 cm | 單端 |
| ch3 | 鼻子**左側** 1 cm | 單端 |
| ch4 | 下巴**左角** | 單端 |
| ch5 | 下巴後方 4 cm | 單端 |
| ref | 右耳後（推測）| 參考電極 |
| bias | 左右兩側 | 驅動偏置 |

**對應發音肌群推測：**
- ch1/ch3：鼻側（levator anguli oris 附近）
- ch2：嘴角（orbicularis oris / risorius）
- ch4：頦部（mentalis / depressor anguli oris）
- ch5：頦下（submental / digastric 前腹）

**受試者：**
- 6 名普通話母語健康年輕人（Speaker 1&3：女；2,4,5,6：男），平均年齡 25 歲
- 實驗前清潔面部，靜坐佩戴電極和麥克風

**說話模式：**
- 無聲模式：想像說話（5 次重複）→ 主要訓練資料
- 有聲模式：正常發音（1 次）→ 輔助訓練 + DTW 對齊來源

**語料來源：** AISHELL3 多說話者普通話 TTS 語料庫（音韻平衡）

**資料統計（Table II）：**

| 說話者 | 性別 | 訓練/驗/測（分鐘）| 訓練/驗/測（句）|
|--------|------|-----------------|----------------|
| Spk-1 | F | 52.59/6.68/6.49 | 680/85/85 |
| Spk-2 | M | 52.65/6.70/6.26 | 516/64/64 |
| Spk-3 | F | 56.60/7.11/6.99 | 716/89/89 |
| Spk-4 | M | 40.77/5.11/5.01 | 800/100/100 |
| Spk-5 | M | 40.49/5.06/5.09 | 600/75/75 |
| Spk-6 | M | 34.85/4.29/4.40 | 600/75/75 |
| **總計** | — | **277.95/34.95/34.25** | **3912/488/488** |

總詞彙：2260 詞，1373 字符；各人分割比例 8:1:1

---

## 6. 模型架構（SSRNet）

### 前處理

```
原始 5ch sEMG (2000 Hz)
    |
    v
[Butterworth BP 4–400 Hz]（去除 DC 偏移和高頻）
    |
    v
[自調諧陷波濾波器：50 Hz 及諧波]（工頻干擾）
    |
    v
【特徵提取（355 維/幀）】
TD 特徵：6 特徵/通道 × 5 通道 = 30 維（跟 Jou 2006）
STFT 特徵：振幅，Hanning 窗 64ms，hop 16ms，65 維/通道 × 5 通道 = 325 維
合計：30 + 325 = 355 維/幀
```

### SSRNet 主架構（靈感來自 FastSpeech TTS）

```
sEMG 特徵 X_{1:N}（355 維序列）
    ↓
【Source Encoder（FFT）】
Linear(ReLU) + Positional Encoding
→ 6層 FFT（Multi-head Attention(head=4) + 1D Conv×2 + Add&Norm）
dim=384, hidden=1536
→ 隱層表示 h_{1:N}
    ↓ 訓練時用 GT duration；推理時用預測 duration
【Duration Predictor → Length Regulator】
DTW 對齊（sEMG_s vs sEMG_v）計算 GT duration d_{1:N}
Duration Predictor：Conv×2(filter=384, kernel=3) + Linear → d̂_{1:N}（MSE loss）
Length Regulator：按 duration 重採樣 h_{1:N} → h_{1:M}（h_{1:M} 長度 = 音訊長度）
    ↓
【Target Decoder（FFT）】
Positional Encoding + 6層 FFT，hidden=1536
→ Linear → Ŷ⁻_{1:M}
→ Postnet（5層 Conv, filter=256, size=5）→ residual → Ŷ⁺_{1:M}
（MAE loss：MAE(Ŷ⁺, Y) + MAE(Ŷ⁻, Y)）
    ↓
【Vocoder：Parallel WaveGAN（PWG）】
輸入：Ŷ⁺_{1:M}（mel-spectrogram）
WaveNet Generator（30層 dilated residual conv）+ Discriminator（10層）
GAN 訓練（generator 1e6 步 → jointly 4e6 步）
→ 最終音訊波形
```

### 聯合優化（輔助任務，僅訓練時使用）

```
h_{1:M}（解碼器前）
    ↓
【輔助任務 1：音調素分類（Toneme Classification）】
使用 MFA（Montreal Forced Aligner）預先提取對齊音調素序列 tm_{1:M}
Linear → Softmax → CE loss（λ_tm=0.5）
音調素集合（139 個）= 音素（onset/nucleus/coda）+ 聲調標注（在 nucleus 上）
e.g., /teng2/ 分解為 /t e2 ng/（聲調標注在韻核 e2 上）
    |
【輔助任務 2：有聲 EMG 重建（Vocal sEMG Reconstruction）】
Linear → MSE loss（λ_recons=0.5），重建 sEMGv 穩定訓練

總損失 L = MAE(Ŷ⁺,Y) + MAE(Ŷ⁻,Y) + MSE(d̂,d) + 0.5·CE(tm̂,tm) + 0.5·MSE(x̂,x)
```

**訓練設定：**

| 超參數 | 值 |
|-------|-----|
| attention dim | 384 |
| heads | 4 |
| encoder/decoder FFT 層 | 6 |
| hidden units | 1536 |
| batch size | 8 utterances |
| dropout | 0.1（enc/dec）/ 0.5（postnet）|
| 優化器 | Adam + Noam（d_model=384, step_w=4000）|
| λ_align | 10，λ_tm=0.5，λ_recons=0.5 |
| 實作框架 | ESPnet + Parallel WaveGAN |

---

## 7. 聲調語言的挑戰（本論文核心論述）

普通話中文與英語的根本差異：

| 面向 | 英語 | 普通話 |
|------|------|--------|
| 音素/音調素數量 | ~47 音素 | ~139 音調素（toneme）|
| 聲調作用 | 非辨義 | 辨義（一個聲調差即改變詞義，如 bā/bá/bǎ/bà/ba）|
| 神經肌肉複雜度 | 較低 | 較高（額外需要 F0 控制肌肉）|

**關鍵實驗結論：**
- 神經肌肉訊號確實傳遞了聲調資訊：**音調素分類準確率 96.07%**
- 移除音調素分類：CER 上升 **132.75%**（最大消融影響）
- 去除聲調資訊（僅音素分類）：CER 上升 6.51%
- 第五聲（輕聲）在無聲模式下最難表達

---

## 8. 實驗結果

### 主觀評估（10 名普通話母語者人工轉錄）

| 模型 | 平均 CER | 最佳 | 最差 |
|------|---------|------|------|
| Baseline（Gaddy&Klein 2020）| 39.76% | 17.72%（Spk-2）| 63.05%（Spk-6）|
| **SSRNet（本文）** | **6.41%** | **1.19%**（Spk-2）| **20.67%**（Spk-5）|

自然度評分（0–100）：SSRNet 64–95 vs 基線 39–51

### 客觀評估（MASR 自動辨識評估）

| 模型 | 平均 CER |
|------|---------|
| Baseline | 46.62% |
| **SSRNet** | **21.99%（±4.99%）** |
| Ground-truth 音訊 | 11.30%（系統上限參考）|

### 音質評估

| 模型 | MCD（越低越好）| STOI（越高越好）|
|------|-------------|--------------|
| Baseline | 高（~4–4.5 dB）| 低（~0.3）|
| **SSRNet** | **低（~1–2 dB）**| **高（~0.7–0.9）**|

### 消融實驗（Table VI，以平均 CER 變化量報告）

| 去除項目 | ΔCER |
|---------|------|
| 完整模型（SSRNet）| 0 |
| 去除有聲 EMG 重建 | +9.38% |
| **去除音調素分類** | **+132.75%**（最大影響）|
| 音調素分類放解碼器後 | +1.89% |
| 音調素改用音素（無聲調）| +6.51% |
| λ_align=0（不用 DTW 對齊）| +81.18% |

---

## 9. 論文限制

- **單一女性 + 5 男性受試者**（6 人），跨人泛化未驗證
- sEMG-to-Voice 任務（語音重建），**不是** sEMG-to-Text（文字辨識）
- 客觀 CER（21.99%）與主觀 CER（6.41%）差距大，反映 MASR 系統對重建語音的評估偏差
- 受試者 Spk-4/Spk-5 表現較差：Spk-4 因 ground-truth 本身 ASR 準確率低；Spk-5 因電極阻抗高導致 SNR 差
- 實時性尚未達到（PWG 推理需要時間）
- 閉合語料（AISHELL3），開放域泛化未驗證

---

## 10. 與我的研究的關聯

| 面向 | Li et al. (2022) | 我的研究方向 |
|------|-----------------|-------------|
| 語言 | 普通話（5 聲調）| 台灣注音符號（4 聲調+輕聲）|
| 通道數 | 5 | 4 |
| 採樣率 | 2000 Hz | 待確認 |
| 任務 | sEMG-to-Voice（語音重建）| sEMG-to-Text（文字辨識）|
| 輔助任務 | 音調素分類（含聲調）| 注音生成（與拼音類似，含聲調）|
| 核心架構 | FFT Transformer Seq2Seq + PWG | CNN + Transformer + CTC |

**對我的啟示（直接相關）：**

1. **聲調資訊在 sEMG 中確實存在且可被捕捉：** 96.07% 音調素分類準確率說明神經肌肉訊號能攜帶聲調資訊，對台灣注音（同樣有聲調）的研究是重要的可行性依據
2. **聲調輔助任務設計的強力論據：** 去除音調素分類導致 CER 上升 132.75%，遠超其他消融結果，說明在注音研究中加入聲調/注音輔助任務是必要的，而非可選的
3. **第四段內容支撐：** 本文對普通話聲調語言困難的量化（139 音調素 vs 47 音素）直接支持你的論文第四段對「中文比英文難」的論述
4. **電極位置差異：** 本文 5 通道電極集中在鼻側、嘴角、頦部（水平分布），與多數研究的臉部+頸部混合配置不同，4 通道系統可參考此精簡方案

---

## 11. 五個核心問題

| 問題 | 答案 |
|------|------|
| 研究問題是什麼？ | 能否以 Seq2Seq 模型從普通話無聲 EMG 重建音訊，解決聲調語言的高維度和時間對齊挑戰？ |
| 方法是什麼？ | 5ch sEMG → TD+STFT 特徵 → FFT Encoder + Length Regulator + FFT Decoder → mel-spec → PWG → 音訊波形；輔助：音調素分類 + 有聲 EMG 重建 |
| 資料如何取得？ | 6 名普通話受試者，AISHELL3 語料，5.79 小時無聲 EMG，2000 Hz；有聲+無聲×5 平行錄製 |
| 主要結果？ | 主觀 CER 6.41%（基線 39.76%）；音調素分類準確率 96.07% |
| 主要限制？ | 語音重建非文字辨識，6 人，客觀/主觀 CER 差距大，實時性未達 |

---

## 12. 重要引用文獻

| 引用 | 內容 | 重要性 |
|------|------|--------|
| Wang et al. (2020) [2] Brain Sciences | sEMG 頻譜圖 + Xception + bLSTM，中文 10 詞（同研究組）| 本文同組前驅研究，資料集和硬體相同 |
| Gaddy & Klein (2020) [17] EMNLP | Digital voicing of silent speech（英語 EMG-to-Voice，WER 68%）| 本文基線模型 |
| FastSpeech [33] / FastSpeech 2 [34] | TTS Seq2Seq 模型（Length Regulator 來源）| 本文架構直接借鑒 TTS 領域 |
| Parallel WaveGAN [39] | 聲碼器 | 本文語音合成後端 |
| MFA [44] | Montreal Forced Aligner，音調素對齊工具 | 音調素分類輔助任務的標注來源 |
| Schultz et al. (2017) [3] IEEE/ACM | Biosignal-based spoken communication survey | 本文 SSD 分類框架（biosignal-to-text vs voice）|
