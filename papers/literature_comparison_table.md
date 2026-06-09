# sEMG 無聲語音辨識文獻比較表

**排序：** 生理基礎 → 傳統 ML → 深度學習（DNN-HMM → CNN → RNN+Attention → Seq2Seq/Transformer）  
**評估指標：** WER = 詞語錯誤率；CER = 字元錯誤率；Acc = 分類準確率  
**更新日期：** 2026-06-09（加入 Liu et al. 2026）

---

## 一、生理基礎 / 可行性研究

| 作者（年） | 研究貢獻與目標 | 摘要（一句話） | EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數） | 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Netsell & Daniel (1974) | 量化發音時 EMG 啟動到聲音產生的機械反應時間（MRT），確立 sEMG 含語音預測資訊的生理依據 | 測量多個肌肉群的 MRT，確認 EMG 先於聲音 ~60 ms，證明臉部 sEMG 具辨識語音意圖的物理可行性 | — | 實驗室測量裝置 | — | 口唇、齶、舌等發音肌群 | 整流 + 延遲量測 | 無（測量研究，非辨識系統）| MRT ≈ 60 ms（EMG onset → 聲音產生）|
| Sugie & Tsunoda (1985) | 建立首個 sEMG 語音合成器，從口周肌肉 EMG 辨識母音並驅動語音合成 | 3 通道口周肌肉 EMG + 規則式有限自動機辨識 5 個日語母音，史上最早 sEMG-SSI 概念驗證之一 | 未明 | 自製 EMG 放大器 + 語音合成器 | 3 | 口周肌群（perioral muscles，圍繞嘴唇） | 全波整流 + 低通平滑 + 振幅特徵 | 規則式 2D 閾值判斷 → 有限自動機（非統計學習）| 5 個日語母音辨識（概念驗證，具體準確率未明）|

---

## 二、傳統機器學習方法

| 作者（年） | 研究貢獻與目標 | 摘要（一句話） | EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數） | 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Chan et al. (2001a) | 首次以小波特徵搭配 LDA 驗證 sEMG 語音辨識可行性（4 通道，10 英文詞） | 4 通道 sEMG 以小波多分辨率特徵 + LDA + 近鄰分類，在 10 個英文命令詞任務上達到 2.68%–10.36% 誤差 | 未明 | 商用 EMG 放大器 | 4 | 頰部、口輪匝肌、頦肌附近（臉部臉頰側） | 小波分解（多分辨率特徵提取） | LDA 降維 + 近鄰分類器（speaker-dependent）| 10 英文詞，誤差 2.68%–10.36%（session-dependent）|
| Chan et al. (2001b) | 引入 HMM 建模 EMG 時序，解決 LDA 對時間錯位敏感問題 | 4 通道 EMG 以 AR 係數為特徵，HMM 建模時間序列，奠定傳統 sEMG 語音辨識的基本框架 | 未明 | 同 Chan (2001a) | 4 | 同 Chan (2001a) | AR 係數（自迴歸模型特徵，階數未明）| HMM（Hidden Markov Model，狀態數未明）| 10 個英文詞，準確率較 2001a 改善（具體數值未明）|
| Maier-Hein et al. (2005) | 首次量化電極重放（session-independent）問題，達到最高 session-independent 準確率（傳統方法） | 5 通道 EMG-UKA + TD5 + LDA + GMM-HMM，session-dependent 97.3% vs session-independent 76.2%，揭示電極重放為核心挑戰 | 600 Hz | EMG-UKA 採集系統（KIT Schultz 組）| 5（實際 4，ch5 因不穩定移除）| levator anguli oris, zygomaticus major, platysma, depressor anguli oris, anterior belly of digastric | TD5 特徵（均值、功率、過零率等）+ LDA 降維 | GMM-HMM（phone 模型，BioKIT 工具，最大似然訓練）| session-dep 97.3%，session-indep 76.2%（英語，EMG-UKA）|
| Schultz & Wand (2010) | 擴展至 101 詞連續 sEMG 語音辨識，導入 BDPF 共發音建模，明確指出三大限制（speaker dependency, electrode placement, audible/silent gap）| 5 通道 EMG-UKA，TD + GMM-HMM + BDPF 捆綁音韻特徵，101 詞連續無聲語音，WER 31.5% | 600 Hz | EMG-UKA（KIT）| 5 | levator anguli oris, zygomaticus major, platysma, depressor anguli oris, anterior digastric | TD features（時域 5 特徵/通道）+ LDA + 差分特徵 | GMM-HMM + BDPF（8 音韻特徵串流，各獨立訓練；三元語法 LM）| 101 詞連續，WER 31.5%（無聲語音）；有聲 < 10%；說話模式差異是核心問題 |
| Wand et al. (2014) | 系統量化有聲/無聲/弱聲三種說話模式的 EMG 訊號差異，頻譜映射轉換嘗試 | 5 通道 EMG-UKA，BDPF HMM + 頻譜映射，量化不同說話模式 EMG 分布差異，無聲 mime 34.7% WER | 600 Hz | EMG-UKA（KIT）| 5 | levator anguli oris, zygomaticus major, platysma, depressor anguli oris, anterior digastric | TD10 特徵（堆疊 ±10 框架）+ LDA + 頻譜映射（modes 轉換）| BDPF HMM（捆綁音韻特徵，最複雜傳統模型）| 無聲 mime 34.7% WER；頻譜映射補償後 36.5%（略差）；說話模式差異無法完全補償 |
| Meltzner et al. (2018) | 傳統架構最大規模：自製 8 通道可穿戴感測器 + 2200 詞連續語音 + 建立最大 sEMG 語料庫 | 8 通道（從 11 精簡）可穿戴感測器 + 傳統 ASR 架構，2200 詞連續語音 WER 8.9%，但指出仍需深度學習突破 | 未明（推測 1000 Hz+）| 自製可穿戴貼片感測器（Meltzner 實驗室）+ Ag/AgCl | 8（從 11 精簡選出）| 8 個臉頸部位置：口輪匝肌、頰肌、喉部前方、舌骨、頦部等 | 傳統 sEMG 前處理（帶通、整流、特徵提取）| 多流 GMM-HMM（傳統 ASR，多通道特徵融合）| 2200 詞連續，WER 8.9%；為達此結果需大規模訓練資料（傳統方法上限）|

---

## 三、深度學習方法

### 3.1 DNN-HMM 混合（深度學習轉型節點）

| 作者（年） | 研究貢獻與目標 | 摘要（一句話） | EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數） | 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Wand & Schmidhuber (2016) | 首次以 DNN 取代 GMM 作為 HMM 前端，在極少量資料下仍有效學習 EMG 判別特徵 | 5 通道 EMG-UKA，TD5 + LDA → DNN（4×200 tanh）替換 GMM，phone 模型開發集 WER 29.5%→20.0%（>32% 相對改善），簡化建模範式 | 600 Hz | EMG-UKA（IDSIA/Schmidhuber 組）| 5（ch5 移除）| levator anguli oris, zygomaticus major, platysma, depressor anguli oris, anterior digastric, tongue | TD5（均值、功率、過零率、整流均值，堆疊 ±5 框架 = 275 維）→ LDA（32 維）| DNN（4 隱藏層 × 200 neurons, tanh, SGD lr=0.005, minibatch=30）+ HMM（Viterbi）+ 三元語法 LM | 開發集：phone+DNN 20.0% WER（>32% 相對改善 vs GMM 29.5%）；評估集：26.5%（p=7×10⁻⁸）|

### 3.2 CNN 為主架構

| 作者（年） | 研究貢獻與目標 | 摘要（一句話） | EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數） | 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Kapur et al. (2018) AlterEgo | 首個無嘴部動作（內部發聲）穿戴式 SSI，以 MFCC + 1D CNN 辨識神經肌肉細微訊號 | 7 通道 OpenBCI，MFCC + 1D CNN 三層，無嘴部動作內部發聲，10 受試者數字任務，平均 92% 準確率，延遲 0.427s | 250 Hz | OpenBCI Cyton + TPE 金鍍電極 + Ten20 膏 | 7（chi-square 從 30 點選出）| 頦部、喉部內/外側、舌骨、眶下（χ² 排名 1–7）；實際肌肉：laryngeal, hyoid, orbicularis oris, platysma, digastric, mentum | HP 1.3–50 Hz（4 階 Butterworth）+ 60 Hz notch + ICA + 整流 + 正規化 → MFCC（25ms 窗，10ms 步距）| 3× [Conv1D(400 filters, k=3, ReLU) + MaxPool] → Global MaxPool → FC(200, ReLU) → FC(n, Sigmoid)；Adam；50% Dropout | 10 受試者數字 0–9，平均 92.01%，延遲 0.427s；個人化訓練（per-user）|

### 3.3 CNN + RNN + 注意力

| 作者（年） | 研究貢獻與目標 | 摘要（一句話） | EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數） | 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Ye et al. (2020) | STFT + 注意力 BLSTM 用於中文 sEMG 分類，引入通道間注意力機制 | 4 通道，STFT 頻譜圖 + Inception CNN 特徵 + 注意力多層 BLSTM，中文 4 詞 mime speech，97.11% | 1000 Hz | 自製放大器（浙大 Guang Li 組）| 4 | 顴大肌（zygomaticus major）、笑肌（risorius）、口輪匝肌下部（orbicularis oris inferior）、頦肌（mentalis）| 帶通 + 陷波 → STFT 頻譜圖 | Inception-block CNN（局部時頻特徵）+ 多層 Attention BLSTM（long-range + 注意力）| 4 中文詞，97.11%；優於純 CNN（~92%）和 BLSTM 基線 |
| Wang et al. (2020) | 遷移學習 Xception 提取跨通道空間特徵，bLSTM 建模通道間協同機制 | 6 通道，STFT → 預訓練 Xception（6000 維）→ bLSTM，中文 10 詞想像說話，90%，首次論證多通道 sEMG 通道間協同的辨識價值 | 1000 Hz | 自製 24-bit ADC（浙大）| 6 | levator anguli oris(×2), platysma, extrinsic tongue + digastric anterior, extrinsic tongue, lateral pterygoid | Butterworth BP 0.15–300 Hz + comb notch 50 Hz + QVR（λ=100）基線漂移去除 → STFT（Hanning, 512ms, 50% overlap）→ 299×299 圖像 | Xception（ImageNet fine-tuned）/ch → 1000 特徵/ch → 6000 維拼接 → bLSTM(Bi×1024 → Bi×1024 → Bi×512) → Dense(128) → Dense(10) | bLSTM 90% > CNN 87% > MLP 85%；推論 <50ms；7 受試者中文 10 詞 |

### 3.4 Seq2Seq / Transformer 端對端

| 作者（年） | 研究貢獻與目標 | 摘要（一句話） | EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數） | 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Jain & Pal (2025) | Multi-DTW 樣本篩選 + 合成資料增強策略，低資源 8 通道 sEMG 英文句子級 Seq2Seq 辨識 | 8 通道 OpenBCI，Multi-DTW 篩選 exemplar + cross-fading 合成訓練句 + 注意力 Seq2Seq（CNN+BiLSTM 編碼 + LSTM 解碼），22 詞英文句子，WER 9.3% | 250 Hz | OpenBCI Cyton Board + 金杯電極 + Ten20 導電膏 | 8 | orbicularis oris（下唇）、submental（頦下）、bilateral SCM（頸部雙側）、zygomaticus major + risorius（臉頰）、masseter（下顎線）| HP 0.1 Hz（實驗最優，保留低頻發音資訊）；Multi-DTW 從每詞 ≥20 樣本選 17 個最具代表性 exemplar | CNN(×2, ReLU) + BiLSTM(×2) 編碼 + Attention + 自迴歸 LSTM 解碼（22 詞詞彙）；合成增強：cross-fading 50ms + 高斯噪音 SNR20–30dB + 時間彎曲 ±10% + 基線漂移 | Seq2Seq WER 9.3%（vs CTC 16.4%）；孤立詞 CNN 90.9%（vs 84.4%）；34 句中 23 句完全正確 |
| Xie et al. (2025) AuxCEMGR | 首個中文神經端對端 sEMG→文字辨識系統，建立中文 EMG-文本語料庫，Transformer+CTC+輔助任務 | 8 通道，1238 句 NBA 中文語料，CNN + Transformer 編碼 + CTC 解碼，加拼音生成 + session 對抗分類兩輔助任務，三種增強，AuxCEMGR 達 38.0% CER | 1000 Hz | Neuracle NSW308M 雙極系統 + Ag/AgCl 電極 | 8（雙極，16 差分電極）| ch1(jaw), ch2(orbicularis oris), ch3–8（臉頸部，依 Diener 2015）；ch4（下顎肌+喉部）最重要；ch5–6（喉部）在無聲模式貢獻最差 | BP 10–400 Hz（4 階 Butterworth）+ notch 50/150/250/350 Hz → MFSC（Hanning 窗，36 Mel 濾波器，Librosa 實作）| CNN(×2, k=3×3) + Transformer(×6, head=8, dim=256) + CTC；輔助：拼音 CTC(η₁=1.0) + session GRL+CE(η₂=1.0)；增強：頻譜相減 + 有聲資料(γ=0.8) + mixup(α=0.02)；Adam + Noam；batch=128 | AuxCEMGR Final: CER 38.0%（vs Baseline 44.5%，vs LSTM+CTC 66.8%）；1238 句中文 NBA；Transformer >> LSTM |

> **以下四篇為 sEMG→語音重建（Voice Reconstruction），任務為合成音訊而非辨識文字，屬同類架構的平行研究分支。**

| 作者（年） | 研究貢獻與目標 | 摘要（一句話） | EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數） | 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Gaddy & Klein (2021) | 首次將 CNN + Transformer 引入 sEMG 語音合成，並引入音素輔助損失，open vocabulary WER 68%→42.2% | 3 殘差 Conv1D 塊取代手工特徵 + 6 層 Transformer（相對位置編碼）+ 音素輔助損失（λ=0.1），英語 open vocabulary，WER 42.2%（自動）/ 32.3%（人工）| 1000 Hz（→800 Hz）| Gaddy & Klein (2020) 臉部電極裝置 | 8 | 臉部周圍 8 電極 | 60 Hz 諧波帶阻 + 2 Hz HP（DC 漂移）+ 重採樣 ×0.1 振幅縮放 | Conv1D 殘差塊×3（800→100 Hz, dim=768）+ Session 嵌入（32→768 維）+ Transformer×6（8 頭, dim=768, FF=3072, 相對 PE）→ 26 MFCC → WaveNet；音素輔助頭（訓練後丟棄）；DTW 對齊；AdamW | **WER 42.2%**（vs 基線 68.0%）；消融：移除音素損失 +9.5%（最大貢獻）；Transformer→LSTM +3.8%；手工特徵 +3.0% |
| Li et al. (2022) SSRNet | 首個普通話聲調語言 sEMG→語音重建系統，以聲調素輔助任務解決聲調辨識，DTW 時長對齊 | 5 通道浙大自製設備，Butterworth BP + 自調陷波，TD+STFT 特徵，Feed-Forward Transformer Seq2Seq + Length Regulator + PWG 聲碼器，聲調素輔助分類，主觀 CER 6.41% | 2000 Hz | 自製多通道生物電訊號採集器（浙大 Guang Li 組）| 5 | ch1(鼻右 1cm 差分), ch2(嘴角右 1cm), ch3(鼻左 1cm), ch4(下巴左角), ch5(下巴後 4cm) | Butterworth BP 4–400 Hz + 自調式陷波（50 Hz 及諧波）→ TD+STFT 特徵（355 維/幀）| SSRNet = FFT Encoder(6 層, dim=384) + DTW Duration Extractor + Length Regulator + FFT Decoder(6 層) + PWG 聲碼器；輔助：聲調素分類(λ=0.5) + 有聲 EMG 重建(λ=0.5)；音素詞彙 139 | 主觀 CER 6.41%（vs 39.76% 基線）；聲調素分類 96.07%；**移除聲調輔助任務 → CER +132.75%**（消融最大影響）|
| Li et al. (2023) silentVC | 輔助有聲說話者跨說話者架構 + Conformer（CNN+Transformer 混合）編碼器，首次在跨說話者場景下實現普通話 sEMG→語音轉換 | 5 通道，4 主說話者（靜音）× 2 輔助說話者（有聲），Conformer 編碼器 + Length Regulator + Transformer 解碼器，三任務損失（mel+音素+時長），ASR CER 10.69% | 2000 Hz | 自製多通道生物電訊號採集器（浙大 Guang Li 組，同 Li 2022）| 5（ch1 差分，其餘單電極；臉部與頸部）| 臉部與頸部，與普通話發音肌群相關（Fig.1，同浙大設定）| RC 濾波（DC + 5 kHz LP）+ Butterworth BP 4–400 Hz + 自適應梳狀濾波（50 Hz 諧波）→ TD+STFT 特徵（355 維/幀）| MFT = Conformer-silentVC 編碼器(6 塊, 序列結構, SeLU, 相對位置編碼) + Length Regulator（DTW 迭代更新，每 5 epoch）+ Transformer 解碼器(6 塊) + Post-Net + PWG；三任務：L_mel(λ=1.0) + L_dur(λ=1.0) + L_ph(λ=0.5, 音素 139)；ESPnet | ASR CER 10.69%±5.79%；人工 CER 5.31%；MOS 3.95；**去除 Conv 模組 → CER +20.91%**；直接 sEMG→音訊優於兩步驟 sEMG→音素→TTS（+31.22%）|
| Liu et al. (2026) | Gumbel-Softmax 可微分電極選擇（32→16 ch）+ ResNet-Conformer + GSN 閘控正規化 + NIC 雜訊注入訓練 + 波形重建虛擬感測器，普通話 sEMG→語音合成高魯棒性系統 | 32 通道可撓式電極陣列，Gumbel-Softmax 端對端選出 16 通道（稀疏 CER 10.19% 優於全密度 12.78%）；乾淨條件 CER 11.61%；Drop4 故障場景 CER 35.36% vs 基線 73.54%；故障診斷 AUC 0.727–0.850 | 1000 Hz | 自製三層疊層電子皮膚 + RHD2132 晶片 + Wi-Fi 無線傳輸（SCUT Longhan Xie 組）| 32 原始（Gumbel 選出 16）| 臉部：Masseter, Zygomaticus/Buccinator, Depressor Anguli Oris（F1–F16）；下顎：Digastric Anterior, Mylohyoid（J1–J16）；最重要：嘴角（modiolus）+ 頦下（submental）| Butterworth HP 4 階 5 Hz + 50 Hz 陷波 + 每通道 Z-score 正規化 | Gumbel-Softmax 選擇器（π 向量，溫度退火）→ 1D-ResNet 下採樣 → Conformer×6（8 頭, dim=512, dropout=0.2）+ GSN（α·IN+(1-α)·LN）→ Mel 解碼 + 音素頭 + 重建解碼 → HiFi-GAN；L_mel(DTW)+λ_p·L_ph(0.5)+λ_r·L_recon(1→0.05)+λ_c·L_consist(0.5) | **稀疏 16 ch CER 10.19%**（vs 全密度 32 ch 12.78%）；乾淨 11.61%；Drop4 35.36%；LOSO 跨受試者 47.83%（受試者依賴性強）|

---

## 四、端對端語音辨識背景研究（ASR，非 sEMG）

> **以下研究為一般語音辨識（音訊→文字），非 sEMG，用於提供 CTC 端對端框架的方法論背景。**

| 作者（年） | 研究貢獻與目標 | 摘要（一句話） | 資料集 | 輸入特徵 | 模型架構 | 主要結果 |
|-----------|-------------|------------|--------|---------|---------|--------|
| Graves & Jaitly (2014) ICML | 首次在開放詞彙語音辨識上驗證 CTC 實用性，無需強制對齊、無需音素詞典即可直接輸出字元序列 | 深度雙向 LSTM + CTC，Wall Street Journal 英語語料，無語言模型 WER 30.1%，加 trigram LM 後 8.2%，接近 DNN-HMM 基線（7.8%） | Wall Street Journal (WSJ)，81 小時英語 | 頻譜圖，128 維/幀（matplotlib specgram）| 5 層深度雙向 LSTM（500 cells/層，~26.5M 參數）+ CTC 輸出層（43 字元 + blank）；Beam Search 解碼（可整合詞典 / n-gram LM）| 無 LM：30.1% WER；詞典：24.0%；Trigram LM：**8.2% WER**（vs DNN-HMM 基線 7.8%）；組合 6.7% |

---

## 五、聲調語言 EEG-BCI 研究（輔助論述）

> **以下研究訊號模態為 EEG（腦電圖），非 sEMG，用於提供聲調語言神經生理學背景。**

| 作者（年） | 研究貢獻與目標 | 摘要（一句話） | EEG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 特徵 / 模型 | 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|------------|--------|
| Yang et al. (2022) | 首次以 EEG RASM 不對稱特徵區分有聲調/無聲調普通話，提出 BVA 跨受試者特徵選擇，98.82% 跨受試者準確率 | 14 受試者，64 通道 EEG，RASM（左右半球 DE 比值）+ BVA 降維（14 特徵）+ LDA，BRCSpeech 普通話語料，有聲調 vs 無聲調二元分類 | 1000 Hz（降採樣 500 Hz）| SynAmps (Compumedics)，64 Ag/AgCl 電極，國際 10-20 系統 | 64（精簡後 8 通道最佳：F7/F8, C5/C6, P5/P6, O1/O2）| 頭皮電極（額葉、中央、頂葉、枕葉）；最關鍵：**(C5, C6) All-band**（對應說話感覺運動皮層）| BP 0.5–180 Hz + 降採樣 500 Hz + EEGLAB 偽差去除；基線校正：前 1 秒 BS 功率相減 | RASM（左右對稱電極對 DE 之比，162 維）→ BVA 降維（14 特徵）→ LDA；6 頻段；BS / Before Speak / Speak 三時段 | 跨受試者 RASM+LDA Speak：**98.82%**（SD=0.66）；單受試者：**99.40%**；8 通道：94.44%；High Gamma（60–170 Hz）最佳頻段；Before Speak 97.72%（說話前差異已存在）|

---

## 六、快速比較索引

### 5.1 採樣率

| 採樣率 | 論文 |
|--------|------|
| 未明 / 低（1970–1990s）| Netsell (1974), Sugie (1985), Chan (2001a/b) |
| 600 Hz | Maier-Hein (2005), Schultz (2010), Wand (2014), Wand & Schmidhuber (2016) |
| 250 Hz | Kapur (2018), Jain (2025) |
| 1000 Hz（→800 Hz）| Gaddy (2021) |
| 1000 Hz | Wang (2020), Ye (2020), Xie (2025), Yang (2022)★EEG, Liu (2026) |
| 2000 Hz | Li (2022), Li (2023) |
| 未明（高）| Meltzner (2018) |

### 5.2 通道數（sEMG）

| 通道數 | 論文 |
|--------|------|
| 3 | Sugie (1985) |
| 4 | Chan (2001a/b), Ye (2020) |
| 5 | Maier-Hein (2005), Schultz (2010), Wand (2014), Wand & Schmidhuber (2016), Li (2022), Li (2023) |
| 6 | Wang (2020) |
| 7 | Kapur (2018) |
| 8 | Meltzner (2018), Jain (2025), Xie (2025), Gaddy (2021) |
| 16（從 32 選出）| Liu (2026) |
| 32 原始 | Liu (2026) |
| 64★EEG | Yang (2022) |

### 5.3 說話模式

| 模式 | 論文 |
|------|------|
| 有聲語音（audible）| Wand & Schmidhuber (2016)（訓練用）；Li (2022)（配對訓練用）；Li (2023) 輔助說話者 |
| mime speech（無聲嘴部動作）| Maier-Hein (2005), Schultz (2010), Wand (2014), Meltzner (2018), Ye (2020), Jain (2025), Xie (2025), Li (2022/2023) 主說話者 |
| 內部發聲（無嘴部動作）| Kapur (2018) |
| 想像說話（無任何動作）| Wang (2020) |
| 有聲 / 無聲調語音★EEG | Yang (2022) |

### 5.4 最佳辨識結果對比

| 論文 | 語言 | 任務類型 | 任務規模 | 最佳結果 |
|------|------|---------|---------|---------|
| Maier-Hein (2005) | 英語 | sEMG→文字 | 孤立詞 | 97.3% Acc（session-dep）/ 76.2%（session-indep）|
| Schultz (2010) | 英語 | sEMG→文字 | 101 詞連續 | 31.5% WER |
| Meltzner (2018) | 英語 | sEMG→文字 | 2200 詞連續 | 8.9% WER |
| Wand & Schmidhuber (2016) | 英語 | sEMG→文字 | 108 詞連續 | 20.0% WER（開發集）|
| Kapur (2018) | 英語 | sEMG→文字 | 10 數字 | 92.01% Acc |
| Ye (2020) | 中文 | sEMG→文字 | 4 詞孤立 | 97.11% Acc |
| Wang (2020) | 中文 | sEMG→文字 | 10 詞孤立 | 90% Acc |
| Jain & Pal (2025) | 英語 | sEMG→文字 | 22 詞句子 | 9.3% WER |
| Xie et al. (2025) | 中文 | sEMG→文字 | 1238 句連續 | 38.0% CER |
| Li et al. (2022) | 普通話 | sEMG→語音 | 句子（AISHELL3）| 6.41% CER（主觀）|
| Li et al. (2023) | 普通話 | sEMG→語音（跨說話者）| 句子（AISHELL3）| 10.69% CER（ASR）/ 5.31%（人工）|
| Gaddy & Klein (2021) | 英語 | sEMG→語音 | open vocabulary（19 hr）| 42.2% WER（自動）/ 32.3%（人工）|
| Graves & Jaitly (2014) ★ASR | 英語 | 音訊→文字（非 sEMG）| open vocabulary（WSJ 81 hr）| 8.2% WER（trigram LM）|
| Liu et al. (2026) | 普通話 | sEMG→語音 | 句子（自製 6 受試者）| **10.19% CER**（稀疏 16 ch）/ 11.61%（乾淨條件）|
| Yang et al. (2022) ★EEG | 普通話 | EEG→聲調分類 | 有聲調 vs 無聲調（二元）| 98.82% Acc（跨受試者）|
