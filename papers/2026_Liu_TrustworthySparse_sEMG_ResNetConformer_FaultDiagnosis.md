# An Expert System Framework for Trustworthy Sparse sEMG-to-Speech with Robust Decoding and In-Situ Fault Diagnosis

- **期刊**：Expert Systems With Applications 326 (2026) 132720
- **DOI**：10.1016/j.eswa.2026.132720
- **投稿／接受**：2026-01-27 投稿；2026-05-01 接受；2026-05-06 線上發表
- **作者**：Yang Liu, Yigui Feng, Chen Lv, Yi Li, Longhan Xie（通訊）
- **機構**：South China University of Technology（SCUT），廣州；National University of Defense Technology，長沙
- **PDF 路徑**：`/Users/rayopenclaw/Downloads/An expert system framework for trustworthy sparse sEMG to speech with robust decoding and in situ fault diagnosis.pdf`

---

## 1. 一句話總結

以可微分 Gumbel-Softmax 機制從 32 通道中端對端選出 16 通道最優電極配置，搭配 ResNet-Conformer + 閘控正規化（GSN）+ 雜訊注入一致性訓練（NIC）+ 波形重建虛擬感測器，實現普通話 sEMG→語音合成的高魯棒性與故障自診斷。

---

## 2. 三個主要貢獻

| # | 貢獻 | 說明 |
|---|------|------|
| 1 | 可微分稀疏電極選擇 | Gumbel-Softmax 端對端從 32 通道選出 16 通道；稀疏配置 CER（10.19%）反優於全密度（12.78%），說明高密度陣列存在顯著空間冗餘與串擾 |
| 2 | 自適應訊號強健化 | GSN（閘控融合 Instance Norm + Layer Norm）對應電極阻抗漂移；NIC（隨機通道遮蔽 + 高斯噪聲注入）模擬真實故障場景，強化模型對訊號缺失的容錯能力 |
| 3 | 虛擬感測器故障診斷 | 波形重建殘差作為即時感測器健康指標；雜訊故障（Noise2）AUC=0.850；通道脫落（Drop4）AUC=0.727 |

---

## 3. 背景與動機

**核心矛盾**：高密度電極陣列辨識精度高，但不適合日常穿戴；減少通道數又使系統對單一電極故障極度敏感。

**三個現實問題：**
1. **稀疏脆弱性**：低通道數下任一電極脫落可能導致性能崩潰
2. **振幅偏移**：電極阻抗隨時間與皮膚接觸狀態變化，造成訊號振幅不穩定
3. **黑盒無自診斷**：現有深度學習模型無法偵測輸入訊號物理完整性異常

---

## 4. 資料集

### 主資料集（普通話，自製）

| 項目 | 內容 |
|------|------|
| 語言 | 普通話（Mandarin）|
| 受試者 | 6 位健康成人，無語言/神經動作疾患 |
| 錄製 session | 每人 6 次，跨天錄製 |
| 通道數 | 32（高密度可撓式電極陣列）|
| 採樣率 | 1000 Hz，16-bit ADC（RHD2132 晶片）|
| 採集設備 | 三層疊層電子皮膚 + 無線 Wi-Fi 傳輸 |
| 電極覆蓋肌群 | 臉部：Masseter（F1/2/5/6/9/10/13）、Zygomaticus/Buccinator（F3/4/7/8/11/12）、Depressor Anguli Oris（F14/15/16）；下顎：Digastric Anterior（J5–J12）、Mylohyoid（J1–J4, J13–J16）|
| 語料規模 | 每 session 50+ 句，每句 1 次有聲 + 3 次靜音，總計 ~7,200 錄音 |
| 資料切分 | utterance 級 8:1:1（train/val/test），pooled random split（subject-dependent）|
| 說話模式 | 無聲嘴部動作（silent mouthing）；有聲配對音訊用作監督訊號 |

### 次資料集（英語，Gaddy 2020）

| 項目 | 內容 |
|------|------|
| 語言 | 英語 |
| 受試者 | 1 位，7 sessions |
| 通道數 | 8 |
| 採樣率 | 1000 Hz |
| 總錄音 | ~3,130 |
| 用途 | 魯棒性驗證（僅平行資料）|

### 訊號前處理

1. 4 階 Butterworth 高通濾波（5 Hz）：去除 DC 偏移與準靜態基線漂移
2. 50 Hz 陷波濾波：壓制電源線干擾
3. 每通道 Z-score 正規化：降低跨受試者解剖差異

---

## 5. 模型架構

```
32 通道 sEMG（1000 Hz）
        |
  [Gumbel-Softmax 電極選擇器]
  可學習重要性向量 π（32 維）
  溫度退火 → 選出 top-K=16 通道
  輸出：X_sel（16 通道）
        |
  [1D-ResNet 下採樣模組]
  局部暫態特徵提取 + 降採樣
        |
  [Conformer 編碼器 × L=6 層]
  每層結構：
    1/2 × FFN → MHSA → ConvModule → 1/2 × FFN → LayerNorm
  （FFN: Feed-Forward; MHSA: Multi-Head Self-Attention; ConvModule: 1D 深度可分離卷積）
  含 GSN（閘控 sEMG 正規化）取代標準 BN/IN/LN
        |
  ┌─────────────────────────────────┐
  │                                 │
  [音訊特徵解碼器]              [重建解碼器（虛擬感測器）]
  → 預測 Mel 頻譜 Ŷ             → 重建原始稀疏 sEMG X̂_sel
  → 音素分類頭 P̂                → 重建殘差 = ||X_sel - X̂_sel||_1
        |
  [HiFi-GAN 聲碼器]
  Mel 頻譜 → 16 kHz 語音
```

**GSN 公式：**
```
GSN(h) = α × IN(h) + (1-α) × LN(h)
α = Sigmoid(W_g × AvgPool(h) + b_g)    (b_g 初始化為 3.0)
```

**總損失：**
```
L_total = L_main + λ_r × L_recon + λ_c × L_consist

L_main = L_mel(DTW對齊) + λ_p × L_phone（音素交叉熵）
L_consist = ||E(X_sel) - E(T(X_sel))||_2^2    (NIC 一致性損失)
λ_p=0.5, λ_r: 1.0→0.05（epoch 150後衰減）, λ_c=0.5
```

**訓練課程：**
- Phase 1（Epoch 0–50）：僅 L_main + L_recon，無 NIC
- Phase 2（Epoch 50–300）：啟用 NIC；cosine annealing lr

---

## 6. 資料增強

| 方法 | 細節 |
|------|------|
| NIC 通道遮蔽 | 50% 機率隨機遮蔽最多 3 個通道（模擬電極脫落）|
| NIC 高斯噪聲 | 目標 SNR=15 dB（對應 sEMG 可接受信噪比下界）|
| DTW 對齊 | 無聲與有聲錄音的時間對齊（非資料增強，而是監督機制）|

---

## 7. 實驗結果

### 電極選擇方法比較（普通話資料集）

| 方法 | CER (%) ↓ | MCD (dB) ↓ |
|------|-----------|------------|
| Full-Density (32 ch) | 12.78 | 3.05 |
| Random Selection | 35.73 | 3.99 |
| LASSO | 10.01 | 2.97 |
| PCA | 17.48 | 3.17 |
| GA | 14.60 | 3.10 |
| mRMR | 28.66 | 3.78 |
| **Ours (Gumbel)** | **10.19** | **2.95** |

**反直覺關鍵發現：稀疏 16 通道優於全密度 32 通道，說明高密度陣列存在顯著空間冗餘與通道串擾。**

### 魯棒性比較（乾淨條件，16 通道）

| 模型 | 普通話 CER (%) | 英語 CER (%) |
|------|---------------|-------------|
| ResNet-Transformer (Gaddy 2021) | 19.12 | 22.74 |
| Hybrid Encoder (Ullah 2024) | 18.21 | 25.59 |
| **Ours** | **11.61** | **19.21** |

### 消融實驗（嚴重故障場景）

| 模型 | Drop4 CER | Noise2 CER | Drift2 CER |
|------|-----------|------------|------------|
| M0（無 GSN/NIC/重建）| 76.07% | 63.71% | 24.90% |
| M1（+GSN）| 58.77% | 61.82% | 24.71% |
| M2（+GSN+NIC）| **33.75%** | 57.09% | **20.26%** |
| M3（+GSN+NIC+重建）| 35.36% | **52.66%** | 21.32% |

NIC 是最大單項貢獻（Drop4: 58.77%→33.75%）；重建損失在 Noise2 最有效。

### 跨受試者泛化（LOSO）

| 模型 | 受試者依賴 CER | 跨受試者 CER | ΔCER |
|------|-------------|------------|------|
| ResNet-Transformer | 19.12% | 60.03% | +40.91% |
| Ours | **11.61%** | **47.83%** | **+36.22%** |

跨受試者性能急劇下降——解剖差異、阻抗變化、發音習慣是三大瓶頸。

---

## 8. 論文限制

- **受試者依賴性強**：subject-dependent CER 11.61% vs cross-subject 47.83%，差距 36%
- **自製封閉資料集**：6 位受試者，多樣性有限
- **未測試自由移動**：所有實驗在靜止條件下進行，運動偽差未明確驗證
- **sEMG→語音合成**（非文字辨識）：CER 透過 Whisper ASR 間接計算，非直接文字輸出
- **可撓式電極陣列成本高**：三層疊層電子皮膚設計，難以推廣至低成本穿戴裝置

---

## 9. 與我的研究的關聯

| 面向 | 關聯說明 |
|------|---------|
| **電極選擇（1.2.2）** | 最直接相關：Gumbel-Softmax 找出的重要通道集中於嘴角（orbicularis oris）+ 頦下（digastric），與 Xie 2025 一致；「16 通道優於 32 通道」支撐使用少數精選電極的設計選擇 |
| **通道數決策（1.2.2）** | 稀疏化反而提升性能的發現，為論文中採用 4–8 通道的決策提供依據：多通道不一定更好，關鍵在於位置選擇 |
| 架構（1.2.4）| ResNet-Conformer 是 Gaddy 2021 + Conformer（Li 2023）的整合延伸，可在 1.2.4 一句話提及此演進 |
| 普通話 sEMG 資料 | 主資料集為普通話，與研究語言相近，但任務為語音合成而非注音辨識 |
| 跨受試者問題 | LOSO 結果（+36% CER）量化了受試者依賴性的嚴峻程度，可用於說明自製資料集的挑戰 |

---

## 10. 五個核心問題

1. **問題**：為什麼 16 通道比 32 通道更好？
   → 高密度陣列中鄰近電極訊號高度相關，冗餘與串擾引入額外雜訊；稀疏選擇消除冗餘，模型獲得更乾淨的輸入

2. **方法**：Gumbel-Softmax 如何實現可微分離散選擇？
   → 以溫度參數 τ 控制 Softmax 的「尖銳度」；τ→0 趨近於離散 one-hot；訓練時退火以強制選出 top-K 通道

3. **資料**：為什麼採用 pooled random split 而非 LOSO？
   → 論文主要評估電極選擇與魯棒性機制，pooled split 消除跨受試者分布偏移的干擾變數；LOSO 作為補充評估

4. **結果**：GSN 與 NIC 的貢獻如何分工？
   → GSN 主要對抗振幅偏移（Drop4: 76→59%）；NIC 對抗通道脫落（Drop4: 59→34%）；兩者互補

5. **限制**：跨受試者性能崩潰的根本原因？
   → 解剖個體差異（相同電極位置採集到不同肌肉訊號）+ 皮膚阻抗差異 + 發音習慣差異

---

## 11. 重要引用文獻

| 文獻 | 重要性 |
|------|--------|
| Gaddy & Klein (2021) ACL | 本篇直接建立於其 ResNet-Transformer 架構之上 |
| Gulati et al. (2020) Conformer | Conformer 原始論文，本篇以此取代 Transformer |
| Li et al. (2023) silentVC | 同樣使用 Conformer 的 sEMG 系統，同時期相關工作 |
| Zhu et al. (2024) | 同組先前的電極佈局優化研究，本篇可撓式電極陣列設計來源 |
| Kong et al. (2020) HiFi-GAN | 語音合成聲碼器 |
