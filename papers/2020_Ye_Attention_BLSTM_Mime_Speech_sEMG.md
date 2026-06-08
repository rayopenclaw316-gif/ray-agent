# Attention Bidirectional LSTM Networks Based Mime Speech Recognition Using sEMG Data

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 會議 | 2020 IEEE International Conference on Systems, Man, and Cybernetics (SMC), Toronto, Canada, pp. 3162–3167 |
| 年份 | 2020 |
| 作者 | Hongyi Ye, Haohong Lin, Zijun Song, Ming Zhang, Ruifen Hu, Nan Li, Guang Li |
| 機構 | Institute of Cyber-system and Control, Zhejiang University, China；University of Cambridge, UK |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/第一章期刊/第三段/Attention_Bidirectional_LSTM_Networks_Based_Mime_Speech_Recognition_Using_sEMG_Data.pdf` |
| 備註 | 中文 4 詞無聲語音辨識，STFT+CNN 自動特徵提取 + 注意力 BLSTM 分類 |

---

## 2. 一句話總結

以 STFT 頻譜圖搭配預訓練 CNN（Inception Block）自動提取時頻特徵，再以四層雙向 LSTM 加自注意力機制分類中文四詞無聲語音，在 7 名受試者上達到 97.11% 準確率，顯著優於 CNN 與 LSTM 基線。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 首次將注意力機制引入多層 BLSTM 用於 sEMG 無聲語音辨識，達到 97.11% 準確率 |
| 2 | 以 STFT+CNN 全自動取代手工特徵（ZC、RMS 等），證明無需手工特徵工程即可達高準確率 |
| 3 | 系統回應時間 < 200ms，驗證可用於機械臂即時控制 |

---

## 4. 背景與動機

**應用場景：** 機械臂控制（指令詞彙：一/二/快/慢），需在噪音環境中可靠辨識。

**問題定位：** 傳統方法依賴手工特徵（RMS、ZC、MFCC），費時且需領域知識；深度學習可自動學習判別性特徵。

**語料設計邏輯：** 選用普通話標準發音詞彙，確保受試者發音一致性；詞彙有語義互補結構（數字：一/二；速度：快/慢）。

---

## 5. 資料集

**受試者：** 7 名（男 3 女 4），平均年齡 22 歲

**語料：** 4 個中文詞

| 編號 | 漢字 | 拼音 | 意義 |
|------|------|------|------|
| 1 | 二 | Èr | Two |
| 2 | 一 | Yī | One |
| 3 | 快 | Kuài | Fast |
| 4 | 慢 | Màn | Slow |

**數據量：** 6000 樣本，每類 1500，樣本長度 2000 ms

**採樣率：** 1000 Hz

**說話模式：** 無聲語音（mime speech，受試者不發出聲音，且盡量減少非語音肌肉動作）

**電極設備：**
- 通道數：6（10 個電極，ch 2 和 ch 5 使用雙電極差分）
- 電極：Ag/AgCl 非侵入式
- 參考電極：耳後乳突部（2 個浮地參考電極）
- 傳輸方式：WiFi 無線傳輸
- 採集設備：自製便攜設備（直徑 < 10 cm，重量 < 500 g）
- 視覺化：LabVIEW 應用程式

**電極位置（6 通道）：**

| 通道 | 目標肌肉 |
|------|---------|
| 1, 2 | 提上唇肌（levator labii superioris）、提口角肌（levator angularis） |
| 3 | 口輪匝肌、顴小肌、顴大肌、笑肌、頰肌、降口角肌的交會區 |
| 4 | 頦肌（mentalis） |
| 5 | 頸闊肌（platysma） |
| 6 | 顴大肌（zygomaticus major）、咬肌淺部（masseter superficialis） |

**訓練/測試分割：** 7:3（4200 訓練 / 1800 測試），5 次重複取平均

---

## 6. 模型架構

### 前處理

```
原始 sEMG (6ch, 1000Hz)
    |
    v
[陷波濾波器 50 Hz（去除電源頻率）]
    |
    v
[21 階 Butterworth 帶通濾波器 5–300 Hz（去除 ECG、體動噪音）]
    |
    v
[Wiener 濾波器（去除基線環境噪音，窗長 256 ms，白高斯噪音模型）]
    |
    v
[乾淨的 sEMG (6, 2000)]
```

### 特徵提取（STFT + CNN）

```
每通道：(1, 2000) 訊號
    |
    v
[STFT：窗 M=256 ms，跳距 R=192 ms → (320, 11)]
取前半（FFT 對稱性）→ (320, 6)
→ reshape 成 (299, 299, 6)
    |
    v
[預訓練 CNN（Inception Block：Conv + MaxPooling + FC）]
→ 每通道輸出 (1, 1000) 特徵向量
    |
    v
[6 通道拼接 → (6, 1000) 特徵圖/樣本]
```

### 分類器（注意力 BLSTM）

```
輸入 (6, 1000)
    |
    v
[BLSTM Layer 1 → (6, 1000)]
    |
    v
[Self-Attention Layer]  ← 結構 1（效果較佳）
    |
    v
[BLSTM Layer 2 → (6, 20)]
[BLSTM Layer 3 → (6, 20)]
[BLSTM Layer 4 → (6, 20)]
    |
    v
[Dense + Activation → 4 類]
損失函數：Multi-category Focal Loss（FAIR 2017）
```

**自注意力機制：**
```
hi → MLP → qti
βti = softmax(qti^T × qa)  ← 注意力權重
ho_t = Σ βti × hi
```

---

## 7. 資料增強

無明確資料增強。每類 1500 個樣本屬於自採資料，類別均衡。Focal Loss 設計本身用於處理難易樣本不均衡問題，但類別分布是平衡的。

---

## 8. 實驗結果

### 各分類器比較（4 詞，7 受試者）

| 分類器 | 準確率（均值 ± 標準差） | F1 score |
|--------|---------------------|---------|
| LSTM | 0.8989 ± 0.0206 | 0.8984 |
| BLSTM | 0.9634 ± 0.0028 | 0.9630 |
| Random Forest | 0.9097 ± 0.0035 | 0.9106 |
| CNN | 0.9022 ± 0.0042 | 0.9024 |
| **Att-BLSTM（本文）** | **0.9711 ± 0.0030** | **0.9706** |

### 各詞 F1 分數（Att-BLSTM）

- 範圍：0.96–0.98
- 最易混淆詞對：「二（Er）」 vs 「快（Kuai）」

### 即時性能

- 系統回應時間：< 200 ms（含採集、傳輸、處理、辨識）

---

## 9. 論文限制

- 詞彙量極少（4 詞），不具大詞彙實用性
- 受試者只有 7 名，跨人泛化性未驗證
- 說話者內（within-subject）測試，無跨 session 測試
- 未報告跨受試者（speaker-independent）結果
- 4 詞任務本身較簡單（先驗機率 25%），97% 準確率仍需大詞彙驗證
- CNN 為預訓練固定參數，非端對端聯合訓練

---

## 10. 與我的研究的關聯

| 面向 | Ye (2020) | 我的研究方向 |
|------|-----------|-------------|
| 語言 | 中文（普通話，4 詞） | 台灣注音符號 |
| 通道數 | 6 | 4 |
| 採樣率 | 1000 Hz | 待確認 |
| 說話模式 | 無聲語音 | 無聲語音 |
| 特徵 | STFT + CNN（自動） | 待設計（可考慮類似） |
| 模型 | BLSTM + Self-Attention | CNN + Transformer + CTC |
| 任務 | 4 詞孤立詞分類 | 注音字符序列辨識 |
| 最佳準確率 | 97.11% | 目標待定 |

**對我的啟示：**
1. **STFT + CNN 自動特徵提取可行**：這篇確認了在中文無聲語音任務中，STFT 頻譜圖配合 CNN 可替代手工特徵，你的系統可以考慮類似的輸入表示
2. **雙向 LSTM 優於單向**：BLSTM（96.34%）比 LSTM（89.89%）高出約 7%，說明未來時間資訊對 EMG 語音辨識有顯著幫助
3. **Focal Loss 適合類別不均衡場景**：如果你的注音資料集在不同注音符號間有頻率差異（某些注音較少），可考慮使用 Focal Loss
4. **電極選擇**：本文加入頦肌（mentalis）和咬肌，與先前文獻的選擇略有不同，反映中文與英語發音肌群使用差異

---

## 11. 五個核心問題

| 問題 | 答案 |
|------|------|
| 研究問題是什麼？ | 能否用 STFT+CNN 自動特徵提取 + 注意力 BLSTM 實現高準確率中文無聲語音辨識？ |
| 方法是什麼？ | STFT 頻譜圖 → 預訓練 CNN → 4 層注意力 BLSTM，Focal Loss |
| 資料如何取得？ | 自採，7 名受試者，4 個中文控制詞，6000 樣本，1000 Hz |
| 主要結果？ | Att-BLSTM 97.11%，系統回應時間 < 200ms |
| 主要限制？ | 4 詞小詞彙，7 名受試者，無跨人/跨 session 測試 |

---

## 12. 重要引用文獻

| 引用 | 內容 | 重要性 |
|------|------|--------|
| Wand et al. (2014) [本文 ref 16] | 電極位置設計來源 | 本文沿用其通道配置 |
| Hochreiter & Schmidhuber (1997) [ref 21] | LSTM 原始論文 | BLSTM 理論基礎 |
| Lin et al. ICCV 2017 [ref 25] | Focal Loss | 本文損失函數來源 |
| Chollet CVPR 2017 [ref 20] | Xception（深度可分離卷積） | CNN 特徵提取架構來源 |
