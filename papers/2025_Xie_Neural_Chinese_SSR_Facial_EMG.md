# Neural Chinese Silent Speech Recognition with Facial Electromyography

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊 | Speech Communication, Vol. 171 (2025), Article 103230 |
| DOI | https://doi.org/10.1016/j.specom.2025.103230 |
| 年份 | 2025（投稿 2023-09-19；修訂 2025-02-22；接受 2025-03-27；線上發表 2025-04-15） |
| 作者 | Liang Xie*, Yakun Zhang*（共同第一）, Hao Yuan, Meishan Zhang, Xingyu Zhang, Changyan Zheng, Ye Yan, Erwei Yin |
| 機構 | Defense Innovation Institute, AMS, Beijing；TAIIC, Tianjin；Peking University；HIT (Shenzhen) |
| 資助 | National Natural Science Foundation of China (62332019, 62076250) |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/第一章期刊/第三段/基於臉部肌電圖的神經網路中文無聲語音辨識.pdf` |
| 程式碼 | github.com/bluishwhite/EMG_ASR |

---

## 2. 一句話總結

首篇中文無聲語音 EMG-文本神經端對端辨識研究：建立 NBA 主題中文平行語料庫（1238 句，5.93 小時），以 CNN + Transformer 編碼器 + CTC 解碼器為基線，整合拼音生成與 session 對抗分類兩個輔助任務（AuxCEMGR），並採用頻譜相減、有聲資料補充、mixup 三種增強，在句子級中文辨識任務上達到 **38.0% 字元錯誤率（CER）**，Transformer 顯著優於 LSTM（同測試集 66.8% CER）。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 建立**首個中文無聲語音 EMG-文本平行語料庫**（1238 句，NBA 主題，667 個唯一漢字，5.93 小時無聲 + 5.80 小時有聲 EMG，5 個 session） |
| 2 | 提出 **AuxCEMGR** 端對端架構：CNN + Transformer 編碼器 + CTC 解碼器，整合拼音生成（粗→細特徵精化）和 session 分類（梯度反轉層對抗訓練，學習 session 不變特徵） |
| 3 | 設計三種針對 sEMG 特性的資料增強策略，平均降低 CER 約 **23.3 個百分點**（從 62.5% → 38.0%） |

---

## 4. 背景與動機

**問題定位：**
1. 現有 EMG 語音辨識幾乎全部針對英語，中文研究近乎空白
2. 傳統方法（GMM-HMM, DNN-HMM）依賴非端對端多模塊架構，限制了規模化發展
3. 缺乏適合神經端對端模型的中文 EMG-文本平行語料庫

**本文切入點：**
- 自建語料庫解決資料缺口
- 借鑒有聲 ASR 的 Transformer+CTC 端對端架構，直接用於 sEMG→文字轉換
- 針對中文語音特性（音節 = 拼音）設計拼音輔助任務
- 針對多 session 電極重貼問題設計對抗式 session 不變特徵學習

**與同年 Jain & Pal (2025) 的對比：**
- 本文：8 通道，中文，句子級字符辨識（CER），端對端 Transformer+CTC，軍事/學術研究導向
- Jain & Pal (2025)：8 通道，英文 22 詞，句子級詞語辨識（WER），Seq2Seq 注意力，資源受限導向

---

## 5. 資料集

**硬體設備：**

| 裝置 | 規格 |
|------|------|
| EMG | Neuracle Technology NSW308M 雙極系統，1000 Hz，8 通道，Ag/AgCl 電極 |
| 音訊（輔助）| 麥克風，44100 Hz，1 通道 |
| 參考電極 | 左鎖骨（1 個） |
| 電極組態 | 16 個差分電極貼於通道 1–8（雙極導出） |

**電極位置（8 通道，依循 Diener et al. 2015）：**

| 通道 | 位置/目標肌肉 | 備註 |
|------|-------------|------|
| ch1 | 下顎（jaw）附近 | 訊號能量最高，干擾其他通道觀察 |
| ch2 | 口輪匝肌（musculus orbicularis oris） | 在基線模型中貢獻最大的單通道 |
| ch3 | 上臉頰/眼眶下附近 | — |
| ch4 | 下顎肌和喉部表面（mandibular + throat） | 在 AuxCEMGR 中貢獻最大的單通道 |
| ch5 | 喉部附近（laryngeal region） | 無聲模式貢獻差（喉部動作細微） |
| ch6 | 喉部附近（laryngeal region） | 同 ch5；有聲/無聲模式差異顯著 |
| ch7 | 另一臉部區域 | — |
| ch8 | 另一臉部區域 | — |

**關鍵觀察（電極）：** ch5/ch6 在無聲模式貢獻最差，與有聲 ASR（ch5 近主導）形成對比；ch1-4 整體貢獻最大；6-7 對電極即可維持接近 8 對的效能。

**語料庫建構：**
- **受試者：** 1 名女性，普通話母語，無閱讀障礙
- **文本來源：** 新浪體育 NBA 賽報爬蟲（2012 年起），篩選 ≤20 詞的短句 + 常見籃球術語
- **模式：** 無聲模式（標準 EMG-文本）+ 有聲模式（輔助 EMG-音訊-文本）
- **5 個 session**，每 session 後重新黏貼電極

**資料統計：**

| 子集 | 句數 | 唯一字符數 | 無聲時長 | 有聲時長 |
|------|------|-----------|---------|---------|
| 訓練 | 1,062 | 667 | 5.13 h | 4.98 h |
| 開發 | 63 | 146 | 0.31 h | 0.31 h |
| 測試 | 113 | 297 | 0.48 h | 0.50 h |
| **總計** | **1,238** | **667** | **5.93 h** | **5.80 h** |

每句平均 10 個字符，平均每段 EMG 訊號 3.74 秒

---

## 6. 模型架構

### 前處理

```
原始 8ch sEMG (1000 Hz)
    |
    v
[4階 Butterworth 帶通濾波 10–400 Hz]
    |
    v
[Notch 濾波：50 Hz, 150 Hz, 250 Hz, 350 Hz（工頻及諧波）]
    |
    v
[MFSC 特徵提取]
Hanning 窗 + 36 Mel 濾波器 → log Mel-frequency spectral coefficients
（實作工具：Librosa + Scipy）
```

### 基線模型（Baseline：CNN + Transformer + CTC）

```
MFSC 特徵序列 S = s₁⋯sₙ
    ↓
【編碼器】
[CNN × 2層，kernel 3×3]  ← 降採樣：N → T (T < N)，局部特徵提取
    ↓
[Transformer × 6層，head=8，dim=256]  ← 長程時序依賴
→ 編碼器輸出 H = h₁⋯hₜ
    ↓
【CTC 解碼器】
[Linear → Softmax]（輸出維度 = 中文字符集大小 + blank）
→ 逐步最大概率標注 → 去除相鄰重複 → 中文字符序列
（推斷時用 beam search，beam size=5）
```

### AuxCEMGR（基線 + 2 個輔助任務）

```
同上編碼器 → H = h₁⋯hₜ
    ↓ (三路並行)
【主任務】字符級 CTC（L_CTC）
【輔助任務 1：拼音生成】
  獨立拼音 CTC 解碼器（Linear → Softmax → CTC）
  → L_pin，η₁=1.0
  效果：引導編碼器從粗到細精化特徵（粗：字符 → 細：字符+拼音）
【輔助任務 2：Session 對抗分類】
  梯度反轉層（GRL）→ Linear → Softmax → 5 個 session
  → L_ses，η₂=1.0
  效果：讓編碼器輸出 H 對 session 不敏感（電極重貼鲁棒性）

總損失：L_all = L_CTC + η₁·L_pin + η₂·L_ses
```

**訓練設定：**

| 超參數 | 值 |
|-------|-----|
| 優化器 | Adam + Noam 暖身（初始 lr=0.1，warmup=2000 步） |
| Batch size | 128 |
| CTC beam | 5 |
| η₁（拼音） | 1.0（AuxCEMGR） |
| η₂（session）| 1.0（AuxCEMGR） |
| 硬體 | 6× NVIDIA RTX 3090 + 24 核 CPU |

---

## 7. 資料增強（三種，均可自由組合）

| 方法 | 機制 | 效果（AuxCEMGR 測試集）|
|------|------|----------------------|
| 頻譜相減（Spectral Subtraction）| 對每個 EMG 計算頻譜相減降噪版本，訓練集自動翻倍 | 去除後 CER ↑ 7.8% |
| 有聲資料補充（Audible Aug）| 有聲 EMG 加入訓練，損失加權 γ（AuxCEMGR γ=0.8）| 去除後 CER ↑ 9.1% |
| Mixup | λ~Beta(α=0.02), X_new=λX1+(1-λ)X2，損失同比加權 | 去除後 CER ↑ 6.5% |
| **三種全用（Full）** | — | 基準 38.0% |
| 無任何增強 | — | 62.5%（↑ **24.5%**）|

---

## 8. 實驗結果

### 主要結果（測試集 CER，Table 5）

| 模型 | 設定 | Dev CER | Test CER |
|------|------|---------|----------|
| Baseline | Full (Final) | 37.2% | 44.5% |
| **AuxCEMGR** | **Full (Final)** | **30.7%** | **38.0%** |
| Wadkins (2019) LSTM+CTC | Full (Final) | 58.3% | 66.8% |
| AuxCEMGR | 無增強（Base） | 56.0% | 62.5% |

**AuxCEMGR vs Baseline（同 Final）：** 38.0% vs 44.5%，改善 6.5% CER  
**Transformer vs LSTM（同 Final）：** 44.5% vs 66.8%，Transformer 大幅優勝

### 電極通道分析（單通道 CER，開發集）

| 最重要單通道 | AuxCEMGR: ch4（下顎肌和喉部） |
| 基線最重要 | ch2（口輪匝肌） |
| ch1-4 | 整體貢獻最大 |
| ch5-6（喉部） | 在無聲模式下貢獻差（laryngeal motion subtle） |

### 電極對數量分析

- 8 對 > 7 對 ≈ 6 對 >> 4 對（急速下降）
- 實用場景可考慮用 6-7 對以增加穿戴舒適性

### 句子長度分析

- CER 隨句長增加，句長 ≥ 12 字時 CER 顯著上升
- AuxCEMGR (Final) 在所有句長分類中均最優

---

## 9. 論文限制

- **單一受試者**（1 名女性），跨人泛化性完全未驗證
- CTC 架構假設測試字符全部在訓練集中，無法處理 OOV（詞彙外）字符
- 語料庫為閉域（NBA 主題），無法直接應用於開放域
- 38.0% CER 仍遠高於實用要求（一般 ASR 目標 < 5%）
- 5 個 session 均來自同一受試者，session 不變性實驗較為有限
- 僅使用 MFSC 特徵，未探索原始 sEMG 或其他特徵表示

---

## 10. 與我的研究的關聯

| 面向 | Xie et al. (2025) | 我的研究方向 |
|------|------------------|-------------|
| 語言 | 普通話（漢字，NBA 主題） | 台灣注音符號 |
| 通道數 | 8 | 4 |
| 採樣率 | 1000 Hz | 待確認 |
| 說話模式 | 無聲嘴部動作（silent articulation）| 無聲語音 |
| 特徵 | MFSC（36 Mel 濾波器，Hanning 窗） | 待設計 |
| 模型 | CNN + Transformer + CTC + 兩輔助任務 | CNN + Transformer + CTC（+注音輔助任務）|
| 評估指標 | CER（字元錯誤率） | CER（預計） |
| 最佳 CER | 38.0% | 目標待定 |

**對我的啟示（直接相關）：**
1. **架構驗證：** 本文確認 CNN + Transformer + CTC 是中文 sEMG 辨識的有效基線架構，這正是你規劃的主架構，有直接文獻支撐
2. **注音輔助任務設計依據：** 本文拼音生成輔助任務對 CER 的改善最顯著（η₁>0.50 即生效），注音（Bopomofo）與拼音同為音節中介表示，你的注音輔助任務設計可直接參照此框架
3. **Session 對抗分類：** 電極重貼後訊號漂移的問題在你的研究中同樣存在，梯度反轉層的 session 分類可作為你資料增強或域適應的組件參考
4. **CER 38.0% 是中文 sEMG 的目前 SOTA：** 你的研究成果應以此為對比基準；若語言換成注音且架構類似，合理期望在相近量級
5. **MFSC（非 MFCC）：** 本文使用 log Mel 頻譜係數（MFSC）而非 MFCC（MFSC = 未做 DCT），減少了信息損失，你的特徵設計時可考慮此選擇

---

## 11. 五個核心問題

| 問題 | 答案 |
|------|------|
| 研究問題是什麼？ | 能否以神經端對端架構直接將臉部 sEMG 轉換為中文文字，突破傳統方法的特徵工程瓶頸？ |
| 方法是什麼？ | 自建 NBA 語料庫 → MFSC 特徵 → CNN+Transformer 編碼 + CTC 解碼 + 拼音生成 + session 對抗 + 三種增強 |
| 資料如何取得？ | 1 名女性受試者，1238 句，5 個 session（每次重貼電極），8 通道，1000 Hz，無聲 + 有聲雙模式 |
| 主要結果？ | AuxCEMGR Final CER 38.0%（vs 基線 44.5%，vs LSTM+CTC 66.8%） |
| 主要限制？ | 單人、閉域、OOV 問題、CER 仍高於實用門檻 |

---

## 12. 重要引用文獻

| 引用 | 內容 | 重要性 |
|------|------|--------|
| Gaddy & Klein (2020) EMNLP | 無聲語音數位發聲（英語，EMG-to-speech） | 本文起始對標研究（本文更進一步：EMG→文字而非語音） |
| Wand & Schmidhuber (2016) | DNN 前端 HMM，EMG-UKA | 本文引用的深度學習先行研究 |
| Diener et al. (2015) IJCNN | 臉部肌電直接轉換語音，DNN | 本文電極位置設定的直接來源 |
| Vaswani et al. (2017) | Transformer（Attention Is All You Need） | 本文編碼器架構 |
| Graves et al. (2006) | CTC 原始論文 | 本文解碼器 |
| Wadkins (2019) MIT 碩士論文 | LSTM+CTC，20 詞，14.8% WER（英語）| 本文主要對比基線（Transformer vs LSTM） |
| Wu et al. (2021) EMBC | Parallel-inception CNN 臉部 sEMG SSR | 本文研究組的前期工作 |
