# sEMG 無聲語音辨識文獻比較表

**排序：** 依論文節次（1.2.1 → 1.2.4）及草稿段落排序，段落內依年代排序  
**評估指標：** WER = 詞語錯誤率；CER = 字元錯誤率；Acc = 分類準確率  
**更新日期：** 2026-06-11（按草稿段落重新分類）

---

## 一、1.2.1 節：sEMG SSR 方法演進（19 篇）

### 1.2.1 第一段：生理基礎與可行性（2 篇）

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數）| 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Netsell & Daniel (1974) | 量化發音時 EMG 啟動到聲音產生的機械反應時間（MRT），確立 sEMG 含語音預測資訊的生理依據 | 測量多個肌肉群的 MRT，確認 EMG 先於聲音 ~60 ms，證明臉部 sEMG 具辨識語音意圖的物理可行性 | — | 實驗室測量裝置 | — | 口唇、齶、舌等發音肌群 | 整流 + 延遲量測 | 無（測量研究，非辨識系統）| MRT ≈ 60 ms（EMG onset → 聲音產生）|
| Sugie & Tsunoda (1985) | 建立首個 sEMG 語音合成器，從口周肌肉 EMG 辨識母音並驅動語音合成 | 3 通道口周肌肉 EMG + 規則式有限自動機辨識 5 個日語母音，史上最早 sEMG-SSI 概念驗證之一 | 未明 | 自製 EMG 放大器 + 語音合成器 | 3 | 口周肌群（perioral muscles）| 全波整流 + 低通平滑 | 規則式 2D 閾值判斷 → 有限自動機（非統計學習）| 5 個日語母音辨識（概念驗證）|

---

### 1.2.1 第二段：傳統機器學習方法（6 篇）

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數）| 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Chan et al. (2001a) | 首次以小波特徵搭配 LDA 驗證 sEMG 語音辨識可行性 | 4 通道 sEMG 以小波多分辨率特徵 + LDA + 近鄰分類，10 個英文命令詞任務誤差 2.68%–10.36% | 未明 | 商用 EMG 放大器 | 4 | 頰部、口輪匝肌、頦肌（臉部臉頰側）| 小波分解 | LDA + 近鄰分類器 | 10 英文詞，誤差 2.68%–10.36%（session-dependent）|
| Chan et al. (2001b) | 引入 HMM 建模 EMG 時序，解決 LDA 對時間錯位敏感問題 | 4 通道 EMG 以 AR 係數為特徵，HMM 建模時間序列，奠定傳統 sEMG 語音辨識基本框架 | 未明 | 同 Chan (2001a) | 4 | 同 Chan (2001a) | AR 係數 | HMM | 10 個英文詞，準確率較 2001a 改善（具體數值未明）|
| Maier-Hein et al. (2005) | 首次量化電極重放（session-independent）問題 | 5 通道 EMG-UKA + TD5 + LDA + GMM-HMM，session-dependent 97.3% vs session-independent 76.2% | 600 Hz | EMG-UKA（KIT Schultz 組）| 5（實際 4）| levator anguli oris, zygomaticus major, platysma, depressor anguli oris, anterior belly of digastric | TD5 特徵 + LDA 降維 | GMM-HMM | session-dep 97.3%，session-indep 76.2%（英語）|
| Schultz (2010) | 擴展至 101 詞連續 sEMG 語音辨識，明確三大限制 | 5 通道 EMG-UKA，TD + GMM-HMM + BDPF，101 詞連續無聲語音，WER 31.5% | 600 Hz | EMG-UKA（KIT）| 5 | levator anguli oris, zygomaticus major, platysma, depressor anguli oris, anterior digastric | TD features + LDA | GMM-HMM + BDPF（三元語法 LM）| 101 詞連續，WER 31.5% |
| Wand et al. (2014) | 系統量化有聲/無聲/弱聲三種說話模式的 EMG 訊號差異 | 5 通道 EMG-UKA，BDPF HMM + 頻譜映射，無聲 mime 34.7% WER | 600 Hz | EMG-UKA（KIT）| 5 | levator anguli oris, zygomaticus major, platysma, depressor anguli oris, anterior digastric | TD10 特徵 + LDA + 頻譜映射 | BDPF HMM | 無聲 mime 34.7% WER；頻譜映射補償後 36.5% |
| Meltzner et al. (2018) | 傳統架構最大規模：自製 8 通道可穿戴感測器 + 2200 詞連續語音 | 8 通道（從 11 精簡）可穿戴感測器 + 傳統 ASR，2200 詞連續語音 WER 8.9% | 未明 | 自製可穿戴貼片感測器 | 8（從 11 選出）| 口輪匝肌、頰肌、喉部前方、舌骨、頦部等（臉頸部 8 位置）| 傳統 sEMG 前處理 | 多流 GMM-HMM | 2200 詞連續，WER 8.9% |

---

### 1.2.1 第三段：深度學習方法（7 篇）

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數）| 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Wand & Schmidhuber (2016) | 首次以 DNN 取代 GMM 作為 HMM 前端 | 5 通道 EMG-UKA，TD5 + LDA → DNN（4×200 tanh）替換 GMM，phone 模型 WER 29.5%→20.0% | 600 Hz | EMG-UKA（IDSIA）| 5 | levator anguli oris, zygomaticus major, platysma, depressor anguli oris, anterior digastric | TD5（275 維）→ LDA（32 維）| DNN（4 層 × 200 neurons, tanh）+ HMM + 三元語法 LM | 開發集：**20.0% WER**（>32% 相對改善）；評估集：26.5% |
| Kapur et al. (2018) AlterEgo | 首個無嘴部動作穿戴式 SSI，內部發聲辨識 | 7 通道 OpenBCI，MFCC + 1D CNN，無嘴部動作，10 受試者數字任務，92% 準確率 | 250 Hz | OpenBCI Cyton + TPE 金鍍電極 | 7 | 頦部、喉部內/外側、舌骨、眶下（χ² 排名 1–7）| HP + notch + ICA + 整流 → MFCC | 3× [Conv1D(400, k=3) + MaxPool] → FC(200) → FC(n)；Adam；50% Dropout | 10 受試者數字 0–9，**92.01%**，延遲 0.427s |
| Ye et al. (2020) | STFT + 注意力 BLSTM，引入通道間注意力機制（中文）| 4 通道，STFT 頻譜圖 + Inception CNN + 注意力多層 BLSTM，中文 4 詞，97.11% | 1000 Hz | 自製放大器（浙大 Guang Li 組）| 4 | 顴大肌、笑肌、口輪匝肌下部、頦肌 | 帶通 + 陷波 → STFT 頻譜圖 | Inception CNN + Attention BLSTM | 4 中文詞，**97.11%** |
| Wang et al. (2020) | 遷移學習 Xception 提取跨通道空間特徵，bLSTM 建模通道間協同 | 6 通道，STFT → 預訓練 Xception → bLSTM，中文 10 詞想像說話，90% | 1000 Hz | 自製 24-bit ADC（浙大）| 6 | levator anguli oris(×2), platysma, extrinsic tongue + digastric anterior, extrinsic tongue, lateral pterygoid | Butterworth BP + comb notch + QVR → STFT | Xception/ch → 6000 維拼接 → bLSTM(×2, 1024→512) → Dense(10) | 7 受試者中文 10 詞，**90%** |
| Gaddy & Klein (2021) | 首次將 CNN + Transformer 引入 sEMG，引入音素輔助損失（英語語音合成）| 8 通道，Conv1D 殘差塊×3 + Transformer×6（相對 PE）+ 音素輔助損失，open vocabulary WER 42.2% | 1000 Hz（→800 Hz）| 臉部電極裝置 | 8 | 臉部周圍 8 個位置 | 60 Hz 諧波帶阻 + 2 Hz HP | Conv1D 殘差塊×3 + Session 嵌入 + Transformer×6（8 頭, dim=768）+ 音素輔助頭；AdamW | **WER 42.2%**（vs 基線 68.0%）；移除音素損失 +9.5% |
| Jain & Pal (2025) | Multi-DTW 樣本篩選 + 合成資料增強，低資源 8 通道英文句子級 Seq2Seq | 8 通道 OpenBCI，Multi-DTW 篩選 + cross-fading 增強 + 注意力 Seq2Seq（CNN+BiLSTM），22 詞英文句子，WER 9.3% | 250 Hz | OpenBCI Cyton + 金杯電極 | 8 | orbicularis oris、submental、bilateral SCM、zygomaticus major + risorius、masseter | HP 0.1 Hz | CNN(×2) + BiLSTM(×2) 編碼 + Attention + 自迴歸 LSTM 解碼；合成增強 | **WER 9.3%**（vs CTC 16.4%）|
| Xie et al. (2025) AuxCEMGR | 首個中文神經端對端 sEMG→文字辨識系統，Transformer+CTC+輔助任務 | 8 通道，1238 句 NBA 中文語料，CNN + Transformer + CTC + 拼音生成 + session 對抗分類，CER 38.0% | 1000 Hz | Neuracle NSW308M 雙極系統 | 8（雙極）| ch1(jaw), ch2(orbicularis oris), ch3–8（臉頸部，依 Diener 2015）| BP 10–400 Hz + notch → MFSC（36 Mel）| CNN(×2) + Transformer(×6, 8頭, dim=256) + CTC；輔助：拼音 CTC + session GRL；增強：頻譜相減 + 有聲資料 + mixup | **CER 38.0%**（vs Baseline 44.5%）；亦引用於 1.2.1 第五段（CTC）|

---

### 1.2.1 第四段：中文 sEMG 語音辨識（2 篇）

> **注意：Li (2022) 任務為語音重建（sEMG→音訊），非直接辨識文字；Yang (2022) 為 EEG 聲調分類，非 sEMG。兩篇均以語言挑戰論據引用，非架構參考。**

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數）| 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Li et al. (2022) SSRNet ★語音重建 | 首個普通話聲調語言 sEMG→語音重建，量化聲調素輔助任務的不可或缺性 | 5 通道浙大設備，TD+STFT 特徵，FFT Transformer Seq2Seq + 聲調素輔助分類，主觀 CER 6.41%；移除聲調輔助 CER +132.75% | 2000 Hz | 自製（浙大 Guang Li 組）| 5 | 鼻右/左、嘴角右、下巴左角、下巴後 | Butterworth BP 4–400 Hz + 自調式陷波 | FFT Encoder(6 層, dim=384) + DTW 時長 + FFT Decoder + PWG；聲調素輔助(λ=0.5) | **CER 6.41%**（主觀）；移除聲調輔助 → CER +132.75% |
| Yang et al. (2022) ★EEG | 首次以 EEG RASM 區分有聲調/無聲調普通話，跨受試者 98.82% | 14 受試者 64 通道 EEG，RASM（左右半球 DE 比值）+ BVA 降維 + LDA，說話前差異即已存在 | 1000 Hz（→500 Hz）| SynAmps，64 Ag/AgCl | 64（★EEG，→8 最佳）| 頭皮（額、中央、頂、枕葉）| BP 0.5–180 Hz + 降採樣 + 偽差去除 | RASM + BVA(14 特徵) + LDA；6 頻段 | 跨受試者 **98.82%**；Before Speak 97.72%（說話前差異已存在）|

---

### 1.2.1 第五段：端對端與 CTC 架構（2 篇）

> **Xie et al. (2025) 亦於此段引用（CTC 應用驗證），主條目見第三段。**

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| 資料集 / 任務 | 輸入特徵 | 模型架構 | 主要結果 |
|-----------|-------------|------------|------------|---------|---------|--------|
| Graves et al. (2006) ★CTC 理論 | 提出 CTC 損失函數：blank 標記 + 多對一映射 + 前向後向算法，無需幀級對齊的端對端訓練 | BLSTM + CTC，TIMIT 音素標注，LER 30.51%（prefix search），優於 HMM 和 HMM-RNN hybrid，奠定所有後續 CTC 應用的理論基礎 | TIMIT（音素標注，61 音素）| 26 維 MFCC；10ms 幀，5ms 步進 | BLSTM（前後向各 100 LSTM cells）+ CTC 輸出層（62 類）；BPTT + online GD | **LER 30.51%**（prefix search）；vs HMM 35.21%；vs BLSTM/HMM hybrid 33.84% |
| Graves & Jaitly (2014) ★ASR | 首次在開放詞彙語音辨識上驗證 CTC 實用性，無需強制對齊即接近 DNN-HMM 基線 | 5 層深度 BLSTM + CTC，WSJ 英語 81 小時，無 LM WER 30.1%，Trigram LM 後 8.2%，接近 DNN-HMM（7.8%）| Wall Street Journal（WSJ，81 小時英語）| 頻譜圖，128 維/幀 | 5 層深度 BLSTM（500 cells/層, ~26.5M 參數）+ CTC（43 字元 + blank）；Beam Search | 無 LM：30.1%；詞典：24.0%；Trigram LM：**8.2% WER**（vs DNN-HMM 7.8%）|

---

## 二、1.2.2 節：電極配置與通道數（7 篇）

### 1.2.2 第一段：電極配置決策的重要性與早期經驗性做法（2 篇）

> **跨節引用（主條目見 1.2.1 第二段）：Chan (2001a/b), Maier-Hein (2005), Schultz (2010)**

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| 採樣率 | 設備 | 通道數 | 電極類型 | 目標肌群 | 分析方法 | 主要電極發現 |
|-----------|-------------|------------|------|------|--------|---------|---------|---------|------------|
| Jou et al. (2006) | 首個連續 EMG 語音辨識；確立 KIT 標準 5 肌群配置；最早記錄 OBO（口輪匝肌）因訊號不穩排除 | CMU/KIT 組：6 通道（EMG5 OBO 因訊號不穩排除，實用 5 通道），HMM + trigram LM，108 詞連續有聲英語，WER 32.0%；EMG 比聲音早 ~50 ms（預期效應）| 600 Hz | 自製（CMU/KIT）| 6（→5 使用，EMG5 OBO 排除）| 單極（ABD+tongue, ZYG, PLT）+ 雙極（LAO, tongue）；參考：鼻/耳 | ABD+tongue, LAO, ZYG, PLT, tongue（OBO 排除）| HMM（context-independent）+ trigram LM | **OBO（口輪匝肌）因訊號不穩定排除**；確立 5 肌群標準配置；WER 32.0% |
| Wand et al. (2013) | 首篇引入電極陣列（vs 傳統散點電極）；PCA 降維解決維度詛咒；ICA 源分離 | 16/35 通道陣列，audible 英語 108 詞，PCA 前多通道反使性能劣化；PCA 後最佳 WER 10.9%；ICA 最高相對改善 22.9% | 2048 Hz | OT Bioelettronica EMG-USB2 | Setup A: 16 / Setup B: 35（bipolar 差分）| 陣列電極（1×8 + 4×8）；bipolar | 臉頰（顴大肌等發音肌群）+ 下巴（舌肌）；**無頸部電極** | PCA + LDA + ICA + HMM（audible speech）| 35 通道**不加 PCA 反比 16 通道更差**；PCA 相對改善 10–18%；ICA 相對改善最高 22.9%；最佳 WER 10.9% |

---

### 1.2.2 第二段：高密度 sEMG 量化研究（2 篇）

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| 採樣率 | 設備 | 通道數 | 電極類型 | 目標肌群 | 分析方法 | 主要電極發現 |
|-----------|-------------|------------|------|------|--------|---------|---------|---------|------------|
| Zhu et al. (2021) | 首篇以 HD-sEMG + SFS 系統性量化各電極位置對 SSR 的貢獻；英文 vs 中文差異比較 | 120 通道（臉部 40 + 頸部 80），SFS 演算法，10 最優電極 → 86%（英）/ 94%（中），頸部 >> 臉部，中文需更少電極 | 2048 Hz | REFA 120-model（TMS International，荷蘭）| 120（monopolar）→ SFS 分析 | 單極高密度電極，10 mm 直徑，15 mm 間距 | 臉部 40 通道（F_40ch）+ 頸部 80 通道（N_80ch, 5×16 陣列）；**舌骨上/下肌群為主** | LDA + SFS（循序前向選擇）+ ANOVA；4 時域特徵（MAV, WL, ZC, SSC）| **頸部 >> 臉部**；10 最優電極 ≈ 86%/94%；40 最優 ≈ 全 120 通道；中文 12 ch → 95%（英文需 24 ch）|
| Tan et al. (2023) ★補充 | 320 通道臉頸部 HD-sEMG 音素級空間活化模式分析；量化面頸部貢獻與下巴電極不可替代性 | 復旦 CIME 組：320 ch（5 陣列），14 母音 + 15 輔音（英語），RMS 熱圖可視化，面部 ≈ 頸部（p=0.682），下巴 B1 加入一致顯著提升準確率（p<0.01），SS 輔音 85.78% / 母音 79.42% | 2048 Hz | Quattrocento（OT Bioelettronica）| 320（A1/A2 臉部各 64ch + B1 下巴 65ch + A3/A4 頸部各 64ch）| 凝膠電極（5mm×2.8mm，中心距 10mm）| 臉部：顴大肌/提口角肌；頸部：頸闊肌/胸鎖乳突肌；下巴：頦肌/降下唇肌 | RMS 熱圖 + PCC 左右對稱性 + PCA + LDA（6-fold）| **面部 ≈ 頸部**（p=0.682）；下巴 B1 一致顯著提升（p<0.01）；SS 輔音 85.78% / 母音 79.42%；左右對稱 PCC > 0.9 |

---

### 1.2.2 第三段：高密度電極的高性能與實用限制（2 篇）

> **Salomons et al. (2025) 亦於此段引用（陣列電極串擾問題），主條目見第四段。**

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數）| 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Chen et al. (2023) CBiL-CTC | 64 通道 HD-sEMG 空時端對端辨識：CNN 空間塊 + BiLSTM + CTC + LM，首批中文 sEMG 音節級序列解碼 | USTC Xu Zhang 組：64ch HD-sEMG → 8×8 影像，CNN+BiLSTM-CTC，15 受試者 33 中文片語，CER 3.11% | 1000 Hz | 自製多通道採集（USTC Xu Zhang 組）| 64（4 件陣列，雙側）| 臉部（buccinator, masseter, orbicularis oris）×2 + 喉頸（cervical, digastric）×2；排列為 8×8 影像 | BP 20–500 Hz + 64 dB → MAV+3 TD-PSD/通道/幀 → 8×8×4；幀長 200 ms | CBiL-CTC = CNN(×2,BN,Dropout) + BiLSTM(3層) + CTC；Nadam lr=0.01；LM = 編輯距離 | **CER 3.11 ± 1.46%**，PCA 97.17%；去除 CNN → CER 4.76% (+53%)；15 受試者 |
| Song et al. (2023) | 64 通道 HD-sEMG + Transformer encoder-decoder + 音節相似度語言模型 | USTC Xu Zhang 組（同 Chen 2023 語料）：Hudgins TD 256-dim → Transformer enc-dec（N=4, h=4）→ LM，8 受試者，CER 5.14% | 1000 Hz | 自製（USTC，同 Chen 2023）| 64（2 件 × 32，雙側）| 臉部（ZYG, risorius）×2 + 頸部（SCM, digastric, platysma）×2 | BP 20–500 Hz → Hudgins 4 TD × 64 = 256-dim；T=60 幀固定 | Transformer enc-dec（N=4, h=4, dmodel=256, dff=1024）+ Beam Search + 音節相似度 LM | **CER 5.14 ± 3.28%**，PCA 96.37%；LSTM decoder CER 12.04%（Transformer 相對改善 57%）|

---

### 1.2.2 第四段：雙極差分電極的位置選擇原則與本研究定位（2 篇）

> **Jou et al. (2006) OBO 不穩定最早記錄，見第一段。**

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| 採樣率 | 設備 | 通道數 | 電極類型 | 目標肌群 | 分析方法 | 主要電極發現 |
|-----------|-------------|------------|------|------|--------|---------|---------|---------|------------|
| Salomons et al. (2025) | 首篇系統性 pilot study 比較電極類型（同心 vs 單對貼片）並從 14 肌肉篩選最優 8 通道配置 | 14 個臉頸肌肉逐一評估音素分類貢獻，雙極單對貼片顯著優於同心電極（p < 0.001），最終 8 通道，音素準確率 48.42% | 2048 Hz | OT Bioelettronica Quattrocento | 14（Session 2）→ 10（Session 3）→ **8（最終）**（bipolar 單對）| **雙極單對貼片**（直徑 24mm）vs 同心電極（40mm）| 臉部 5：ZYG, DAO, RIS, LLS, DLI + 頸部 3：ABD, SLH, MAS；OBO（口輪匝肌）因附著問題排除 | GMM / Bagging DT / NN；逐通道音素分類；5-fold | 單對 > 同心（p < 0.001）；8 通道音素準確率 **48.42%**；OBO 附著不穩；FRT（額肌）近似基線（負對照）|
| Liu et al. (2026) | Gumbel-Softmax 可微分電極選擇（32→16 ch）+ ResNet-Conformer，普通話 sEMG→語音 | 32 通道可撓式陣列，Gumbel-Softmax 選 16 通道（CER 10.19%），乾淨 11.61%，故障場景 35.36% | 1000 Hz | 自製三層電子皮膚 + Wi-Fi（SCUT Longhan Xie 組）| 32→16（Gumbel 選出）| 臉部 Masseter/Zygomaticus/DAO、下顎 Digastric/Mylohyoid；最重要：嘴角+頦下 | Butterworth HP 5 Hz + 陷波 + Z-score | Gumbel-Softmax 選擇器 + 1D-ResNet + Conformer×6 + GSN + Mel 解碼 + HiFi-GAN | 稀疏 16 ch **CER 10.19%**（vs 全密度 12.78%）|

---

## 三、1.2.3 節：中文語音辨識與音韻輔助任務（2 篇）

### 1.2.3 第一段：大詞彙中文 sEMG 辨識的現況與聲調缺失問題（1 篇）

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數）| 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Huang et al. (2024) | 135 類普通話孤立詞 sEMG 資料庫（當時最大）；明確論述普通話聲調資訊在 sEMG 中的結構性缺失；速度擾動 + 時頻遮罩增強移植自語音辨識 | AIRCAS 組：8 通道臉頸部 sEMG，135 類普通話孤立詞，純 3 層雙向 GRU 多受試者 88.01%；速度擾動 + 時頻遮罩 +1.68%；跨受試者 47.22%；「腳」最低 59.57%（同音字混淆） | 1000 Hz | ADS1298IPAGR（TI, 24-bit）| 8 | 顴小肌、口輪匝肌、提口角肌、頦肌、降口角肌、咬肌、下頜舌骨肌（雙側×2）；無喉部 | HP 0.05 Hz + 50 Hz 陷波 + z-score 正規化 | 時頻混合特徵（5 TD + 40 fbank，每通道 45 維）→ 純 GRU（3 層雙向）+ Max Pool over time + MLP；速度擾動（×0.9/×1.1）+ 時頻遮罩（F=T=40）| **GRU 88.01%**（multi-subject, 5-fold）；單受試者最高 97.19%；跨受試者 47.22%；跨 session 78.67%（-17%）；「腳」最低 59.57% |

---

### 1.2.3 第二段：跨受試者泛化——規模效應與域自適應（1 篇）

| 作者（年） | 研究貢獻與目標 | 摘要（一句話）| EMG 採樣率 | 設備 | 通道數 | 電極位置 | 訊號前處理 | 模型（含參數）| 主要結果 |
|-----------|-------------|------------|-----------|------|--------|---------|----------|-------------|--------|
| Zhang et al. (2023) | 70 人 101 類中文 sEMG 最大語料庫；1D-CNN 跨受試者 87.80%；ICDAN（CDAN+MMD）少樣本遷移學習；揭示皮下脂肪層為跨受試者差異主要物理成因 | 天津大學+軍科院組：70 人 101 類普通話，1D-CNN + 原始時序訊號跨受試者 87.80%（60 人訓練）；ICDAN 少樣本跨受試者 86.32%（+14.88%，20 人訓練）；最差受試者 30.04%（皮下脂肪厚）| 1000 Hz | 無線 EMG 設備 | 6 | 頦肌、笑肌、上唇提肌、二腹肌前腹、下頜舌骨肌、頸闊肌 | 帶通 4 階 Butterworth 10–400 Hz + 50/150 Hz 陷波 | 原始時序訊號（6×2000 直接輸入）→ 1D-CNN（Conv1d 64/128/256/512ch + MaxPool × 4 + FC, ~3.5M 參數）；ICDAN = 共享 Feature Extractor + Classifier + CDAN 對抗 Discriminator + MMD 損失 | 跨受試者（60 人）：**87.80%**；ICDAN 少樣本（20 人）：**86.32%**（+14.88% vs baseline 71.42%）；最差受試者 30.04%；最大個體差距 56 pt |

---

## 四、1.2.4 節：端對端模型演進（待補）

---

## 五、待規劃（草稿段落尚未確定）

| 論文 | 目前狀態 | 預計節次 |
|------|---------|---------|
| Li et al. (2023) silentVC | 完成 .md；Conformer 架構；普通話 sEMG→語音合成；跨說話者 | 暫定 1.2.3 或 1.2.4 |

---

## 六、快速比較索引

### 6.1 論文段落對照

| 節次 / 段落 | 論文 | 跨節引用 |
|------------|------|---------|
| **1.2.1 第一段** | Netsell (1974), Sugie (1985) | — |
| **1.2.1 第二段** | Chan (2001a/b), Maier-Hein (2005), Schultz (2010), Wand (2014), Meltzner (2018) | 跨引至 1.2.2 第一段 |
| **1.2.1 第三段** | Wand & Schmidhuber (2016), Kapur (2018), Ye (2020), Wang (2020), Gaddy (2021), Jain (2025), Xie (2025) | Xie 亦引於第五段 |
| **1.2.1 第四段** | Li (2022) ★重建, Yang (2022) ★EEG | — |
| **1.2.1 第五段** | Graves (2006) ★CTC, Graves & Jaitly (2014) ★ASR | Xie (2025) 跨引自第三段 |
| **1.2.2 第一段** | Jou (2006), Wand (2013) | 跨引：Chan (2001a/b), Maier-Hein (2005), Schultz (2010) → 見 1.2.1 第二段 |
| **1.2.2 第二段** | Zhu (2021) | — |
| **1.2.2 第三段** | Chen (2023), Song (2023) | Salomons (2025) 跨引自第四段 |
| **1.2.2 第二段** | Zhu (2021), Tan (2023) ★補充 | — |
| **1.2.2 第四段** | Salomons (2025), Liu (2026) | Jou (2006) OBO 跨引自第一段 |
| **1.2.3 第一段** | Huang (2024) | 跨引：Li (2022) 聲調輔助任務 → 見 1.2.1 第四段 |
| **1.2.3 第二段** | Zhang (2023) | 跨引：Huang (2024) 47.22% |
| **待規劃** | Li (2023) silentVC | 暫定 1.2.4 |

### 6.2 採樣率

| 採樣率 | 論文 |
|--------|------|
| 未明 / 低（1970–1990s）| Netsell (1974), Sugie (1985), Chan (2001a/b) |
| 600 Hz | Maier-Hein (2005), Jou (2006), Schultz (2010), Wand (2014), Wand & Schmidhuber (2016) |
| 250 Hz | Kapur (2018), Jain (2025) |
| 1000 Hz（→800 Hz）| Gaddy (2021) |
| 1000 Hz | Ye (2020), Wang (2020), Xie (2025), Liu (2026), Chen (2023), Song (2023), Yang (2022) ★EEG, Huang (2024), Zhang (2023) |
| 2000 Hz | Li (2022), Li (2023) |
| 2048 Hz | Wand (2013), Zhu (2021), Salomons (2025), Tan (2023) |
| 未明（高）| Meltzner (2018) |

### 6.3 通道數（sEMG）

| 通道數 | 論文 |
|--------|------|
| 3 | Sugie (1985) |
| 4 | Chan (2001a/b), Ye (2020) |
| 5 | Maier-Hein (2005), Jou (2006)（6 ch，EMG5 OBO 排除後實用 5）, Schultz (2010), Wand (2014), Wand & Schmidhuber (2016), Li (2022), Li (2023) |
| 6 | Wang (2020), Zhang (2023) |
| 7 | Kapur (2018) |
| 8 | Meltzner (2018), Jain (2025), Xie (2025), Gaddy (2021), Huang (2024), **Salomons (2025)（最終配置）** |
| 14→8 | Salomons (2025)（pilot, 14 測試 → 8 最終）|
| 320（HD sEMG）| Tan (2023) |
| 16（陣列）| Wand (2013) Setup A |
| 16（從 32 選出）| Liu (2026) |
| 35（陣列）| Wand (2013) Setup B |
| 64（HD sEMG）| Chen (2023), Song (2023) |
| 120（HD sEMG）| Zhu (2021) |
| 64 ★EEG | Yang (2022) |

### 6.4 說話模式

| 模式 | 論文 |
|------|------|
| 有聲語音（audible）| Jou (2006)（有聲，注意！）；Wand (2013)（任務為有聲語音，注意！）；Li (2022/2023)（配對訓練用）|
| mime speech（無聲嘴部動作）| Maier-Hein (2005), Schultz (2010), Wand (2014), Meltzner (2018), Ye (2020), Jain (2025), Xie (2025), Li (2022/2023) 主說話者, Chen (2023), Song (2023), Zhu (2021), Salomons (2025), Huang (2024), Zhang (2023), Tan (2023) |
| 內部發聲（無嘴部動作）| Kapur (2018) |
| 想像說話（無任何動作）| Wang (2020) |
| 有聲/無聲調語音 ★EEG | Yang (2022) |

### 6.5 最佳辨識結果對比

| 論文 | 語言 | 任務類型 | 任務規模 | 最佳結果 |
|------|------|---------|---------|---------|
| Maier-Hein (2005) | 英語 | sEMG→文字 | 孤立詞 | 97.3% Acc（session-dep）/ 76.2%（session-indep）|
| Jou et al. (2006) | 英語 | sEMG→文字（有聲）| 108 詞連續 | WER 32.0%（TD f₂ + E4）|
| Schultz (2010) | 英語 | sEMG→文字 | 101 詞連續 | 31.5% WER |
| Meltzner (2018) | 英語 | sEMG→文字 | 2200 詞連續 | 8.9% WER |
| Wand & Schmidhuber (2016) | 英語 | sEMG→文字 | 108 詞連續 | 20.0% WER（開發集）|
| Kapur (2018) | 英語 | sEMG→文字 | 10 數字 | 92.01% Acc |
| Ye (2020) | 中文 | sEMG→文字 | 4 詞孤立 | 97.11% Acc |
| Wang (2020) | 中文 | sEMG→文字 | 10 詞孤立 | 90% Acc |
| Gaddy & Klein (2021) | 英語 | sEMG→語音（重建）| open vocabulary（19 hr）| 42.2% WER（自動）/ 32.3%（人工）|
| Jain & Pal (2025) | 英語 | sEMG→文字 | 22 詞句子 | 9.3% WER |
| Xie et al. (2025) | 中文 | sEMG→文字 | 1238 句連續 | 38.0% CER |
| Wand (2013) | 英語 | sEMG→文字（有聲）| 108 詞連續 | 10.9% WER（35ch + PCA + LDA）|
| Zhu et al. (2021) | 英/中文 | sEMG→10 數字分類 | 10 類（英/中）| 86%（英）/ **94%（中）**（10 最優電極）|
| Salomons et al. (2025) | 西班牙語 | 音素分類（電極比較）| 29 音素類別 | 48.42%（8 通道 NN，Session 3）|
| Chen et al. (2023) | 中文 | sEMG→文字 | 33 片語（封閉）| **3.11 ± 1.46% CER** |
| Song et al. (2023) | 中文 | sEMG→文字 | 33 片語（封閉）| 5.14 ± 3.28% CER |
| Li et al. (2022) | 普通話 | sEMG→語音（重建）| 句子（AISHELL3）| 6.41% CER（主觀）|
| Li et al. (2023) | 普通話 | sEMG→語音（跨說話者）| 句子（AISHELL3）| 10.69% CER（ASR）/ 5.31%（人工）|
| Liu et al. (2026) | 普通話 | sEMG→語音（重建）| 句子（自製 6 受試者）| **10.19% CER**（稀疏 16 ch）|
| Graves et al. (2006) ★CTC | 英語 | 音訊→音素（非 sEMG）| TIMIT（音素標注）| 30.51% LER（prefix search）|
| Graves & Jaitly (2014) ★ASR | 英語 | 音訊→文字（非 sEMG）| open vocabulary（WSJ 81 hr）| 8.2% WER（trigram LM）|
| Yang et al. (2022) ★EEG | 普通話 | EEG→聲調分類 | 有聲調 vs 無聲調（二元）| 98.82% Acc（跨受試者）|
| Huang et al. (2024) | 普通話 | sEMG→文字 | 135 類孤立詞（12 受試者）| **88.01% Acc**（multi-subject）/ 97.19%（single-subject）/ 47.22%（跨受試者）|
| Zhang et al. (2023) | 普通話 | sEMG→文字（跨受試者）| 101 類孤立詞（70 受試者）| 跨受試者 **87.80%**（1D-CNN, 60 人訓練）；ICDAN 少樣本 **86.32%**（20 人訓練）|
| Tan et al. (2023) ★音素分析 | 英語 | sEMG→音素分類（電極配置研究）| 14 母音 + 15 輔音（音素級）| SS 輔音 **85.78%** / 母音 79.42%（PCA+LDA，全 320 ch）|
