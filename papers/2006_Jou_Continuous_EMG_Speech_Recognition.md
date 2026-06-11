# Towards Continuous Speech Recognition Using Surface Electromyography

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 會議 | Interspeech 2006（第九屆國際語音語言處理會議，ICSLP），Pittsburgh, PA，pp. 573–576 |
| DOI | — |
| 年份 | 2006 |
| 作者 | Szu-Chen Jou, Tanja Schultz, Matthias Walliczek, Florian Kraft, Alex Waibel |
| 機構 | International Center for Advanced Communication Technologies，CMU（美）& Universität Karlsruhe（德）|
| PDF 路徑 | `/Users/rayopenclaw/Downloads/Towards Continuous Speech Recognition Using Surface Electromyography.pdf` |
| **地位** | KIT EMG 語音辨識系列論文的關鍵節點：確立 TD 時域特徵（f₂）作為 EMG 語音辨識的標準特徵，被 Wand (2013)、Salomons (2025) 等後續論文直接沿用 |

---

## 2. 一句話總結

**注意：任務為有聲連續英語語音辨識（audible speech），非默語。**  
CMU/KIT 組以 5 通道 sEMG 建立首個音素模型連續辨識系統，提出 TD 時域特徵（f₂ = [w̄, Pw, Pr, z, r̄]）搭配 50 ms 預期效應建模，在 108 詞受限詞彙任務上將 WER 從 86.8%（頻譜特徵）降至 **32.0%**（TD 特徵 E4）。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | 建立**連續 EMG 語音辨識系統**：以有聲語音強制對齊標注 bootstrap 音素聲學模型，搭配 trigram 語言模型解碼，突破前人孤立詞分類的限制 |
| 2 | 提出 **TD 時域特徵集（f₂）**：從 EMG 訊號分解低頻（w[n]）與高頻（p[n]）成分，提取 5 個特徵（均值、功率、高頻功率、過零率、高頻均值），比頻譜特徵更穩健，成為後來研究的標準特徵 |
| 3 | 量化建模 **EMG 預期效應（anticipatory effect）**：EMG 比聲音早約 50 ms 啟動，通過對 EMG 信號加入延遲（delay）對齊標注，改善聲學模型訓練 |

---

## 4. 電極配置（與論文引用相關）

| 通道 | 肌肉 | 量測方式 |
|------|------|---------|
| EMG1 | 二腹肌前腹（anterior belly of digastric）+ 舌肌 | 單極（參考：鼻子）|
| EMG2 | 提口角肌（levator anguli oris）| **雙極**（2 cm IED）|
| EMG3 | 顴大肌（zygomaticus major）| 單極（參考：耳朵）|
| EMG4 | 頸闊肌（platysma）| 單極（參考：耳朵）|
| EMG5 | 口輪匝肌（orbicularis oris）| 單極（參考：耳朵）|
| EMG6 | 舌肌（tongue）| **雙極** |

**最終實驗使用通道：1, 2, 3, 4, 6（共 5 通道）**  
**EMG5（口輪匝肌）因訊號不穩定排除** ← 與 Salomons (2025) 的發現一致

採樣率：600 Hz；帶通：1–300 Hz；無 50 Hz 陷波（以保留有用信息）

---

## 5. TD 時域特徵（後續論文的技術基礎）

```
EMG 訊號 x[n]
    │
    ├── 低頻成分 w[n]：9 點雙重滑動平均
    │       特徵：w̄（均值），Pw（功率）
    │
    └── 高頻成分 p[n] = x[n] - w[n]，整流 r[n] = |p[n]|
            特徵：Pr（高頻功率），z（過零率），r̄（高頻均值）

f₂ = [w̄, Pw, Pr, z, r̄]  ← 5 維基礎 TD 特徵

E4 = S(f₂, 5)  ← 堆疊 ±5 幀上下文（共 11 幀），最終最佳特徵
```

→ 此 f₂ 特徵被 Wand (2013)、Salomons (2025) 直接沿用（TD0 = [w̄, r̄, Pw, Pr, z]，順序略異）

**上下文堆疊（stacking）+ 50 ms 延遲** 是關鍵改進——WER 86.8% → 32.0%

---

## 6. 實驗設定

| 項目 | 內容 |
|------|------|
| 說話模式 | **有聲語音（audible speech）**，非默語 |
| 說話者 | 1 名男性，單一會話（避免電極重放問題）|
| 訓練集 | 38 音韻平衡句子 × 10 輪 = 380 句（45.9 分鐘）|
| 測試集 | 12 新聞文章句子 × 10 輪 = 120 句（10.6 分鐘）|
| 解碼詞彙 | 108 詞（限制於測試集用詞）|
| 聲學模型 | Context-independent HMM（訓練資料少，未做上下文相關）|
| 語言模型 | Trigram Broadcast News LM |
| 對齊工具 | Janus Recognition Toolkit（JRTk）+ BN ASR 強制對齊 |

---

## 7. 主要結果

| 特徵類型 | WER (%) |
|---------|---------|
| 頻譜特徵 S0 | 86.8 |
| 頻譜 + delta SS | ~75 |
| EMG 特徵 E0 （僅 w̄, Pw）| ~65 |
| EMG 特徵 E1 （+ Pr, z）| ~55 |
| EMG 特徵 E2 （+ r̄）| ~50 |
| **EMG 特徵 E4（S(f₂, 5)，大上下文）** | **32.0** |

（所有結果均為 50 ms 延遲條件下）

---

## 8. 限制

1. **有聲語音**：非無聲/默語，與 SSI 應用場景有差距
2. **單說話者 / 單會話**：人為避免電極重放問題，泛化性未驗證
3. **Context-independent 聲學模型**：詞彙量受限，context-dependent 模型仍是未來工作
4. **受限詞彙**（108 詞）：無法直接應用於 LVCSR

---

## 9. 與本論文的關聯

| 面向 | 關聯 |
|------|------|
| **1.2.1（傳統方法節點）** | 首個以音素模型做連續 EMG 語音辨識；確立 TD 特徵為標準特徵，後續所有 KIT 組論文（Schultz 2010、Wand 2014、Wand 2013）及 Salomons (2025) 均沿用此特徵設計 |
| **1.2.2（電極配置）** | 建立「KIT 標準 5 肌群」配置（LAO, ZYG, PLT, ABD, tongue）；OBO（口輪匝肌）在此論文中即以訊號不穩定排除，與 Salomons (2025) 的發現相互印證 |
| **OBO 不穩定的早期依據** | 本文明確記錄 EMG5（口輪匝肌）信號不穩定而排除，是 Salomons (2025) 排除 OBO 的歷史先例 |

---

## 10. 引用關鍵資訊

> Szu-Chen Jou, Tanja Schultz, Matthias Walliczek, Florian Kraft, and Alex Waibel, "Towards Continuous Speech Recognition Using Surface Electromyography," in *Proc. Interspeech 2006*, Pittsburgh, PA, 2006, pp. 573–576.

**引用重點：**
- 連續 EMG 語音辨識系統；108 詞，WER 32.0%
- TD 時域特徵（f₂）的原始定義
- OBO（口輪匝肌）因訊號不穩定排除
- 50 ms EMG 預期效應建模

---

## 11. 關鍵詞

Surface electromyography, continuous speech recognition, time-domain features, TD features, anticipatory effect, HMM, audible speech, KIT, Schultz group, electrode placement, orbicularis oris instability
