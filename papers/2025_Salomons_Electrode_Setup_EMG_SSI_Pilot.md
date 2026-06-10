# Electrode Setup for Electromyography-Based Silent Speech Interfaces: A Pilot Study

---

## 1. 標題區塊

| 欄位 | 內容 |
|------|------|
| 期刊 | Sensors 2025, Vol. 25, Article 781 |
| DOI | 10.3390/s25030781 |
| 年份 | 2025（投稿 2024-11-15；接受 2025-01-25；發表 2025-01-28）|
| 作者 | Inge Salomons（通訊）, Eder del Blanco, Eva Navas, Inma Hernáez |
| 機構 | HiTZ Basque Center for Language Technology, University of the Basque Country（UPV/EHU），西班牙畢爾包 |
| 資助 | Agencia Estatal de Investigación（西班牙國家研究機構），ref. PID2019-108040RB-C21 |
| PDF 路徑 | `/Users/rayopenclaw/Downloads/2025 Inge Salomons.pdf` |
| **重要性** | 1.2.2 核心引用：本論文專門研究「何種雙極差分電極貼片配置對 SSI 最有效」，電極類型與本研究完全相同 |

---

## 2. 一句話總結

西班牙 UPV/EHU 為西班牙喉切除患者 SSI 建置 ReSSInt 資料庫前，以 pilot study 系統性比較**雙極同心電極 vs. 雙極單對貼片**電極類型，並從 14 個臉頸部肌肉篩選最優通道，最終確定 **8 通道、雙極單對貼片**配置，針對 8 個特定肌肉（顴大肌、笑肌、降口角肌、上唇提肌、降下唇肌、二腹肌前腹、莖突舌骨肌、咬肌），同時提供 sEMG-SSI 領域中 28 篇相關研究的電極配置總覽表。

---

## 3. 三個主要貢獻

| # | 貢獻 |
|---|------|
| 1 | **電極類型比較**：雙極單對貼片顯著優於同心電極（p < 0.001）；同心電極直徑大（40 mm），臉部小肌肉交叉串擾更嚴重 |
| 2 | **14 通道系統性篩選**：對 14 個臉頸肌肉分別做音素分類實驗，量化各肌肉的語音信息貢獻，確立最優 8 通道配置 |
| 3 | **Table 1 電極配置文獻總覽**：整理 28 篇 sEMG-SSR/SSI 研究的電極數量、類型、位置，分 4 種設計方法，是 1.2.2 電極回顧的極佳參考 |

---

## 4. 文獻中電極配置的四種設計方法（Table 1 精要）

| 方法 | 說明 | 代表論文 |
|------|------|---------|
| **1. 針對特定肌肉** | 選定臉頸部特定肌肉，將電極對準肌纖維方向貼附 | Chan (2001, 2002), Maier-Hein (2005), Jou (2006), Schultz/Wand (2010), Ye/Wang (2020)（本論文採此方法）|
| **2. 針對解剖區域** | 不指定特定肌肉，按面部或頸部位置區分 | Meltzner 系列（2008–2018），Gaddy (2020–2022）|
| **3. 高密度電極** | 大量電極覆蓋廣泛區域，含陣列電極或密集單點電極 | Wand (2013)，Zhu (2019–2021） |
| **4. HD 引導稀疏選擇** | 先用高密度找最優位置，再用少量電極實現 | Deng et al. (2023) IEEE TIM |

**本論文立場：** 方法 1（特定肌肉）最適合臉部 SSI——臉部肌肉細長且密集，陣列電極形狀固定難適應肌肉運動，容易產生串擾；針對特定肌肉的縱向貼附可最大化信噪比。

---

## 5. 實驗設定

**硬體：**
- 放大器：OT Bioelettronica Quattrocento（2048 Hz 採樣）
- 電極類型：雙極同心電極（直徑 40mm）vs. 雙極單對貼片（直徑 24mm）
- 語料：西班牙語（250 個音韻平衡句子 Sharvard Corpus；105 個 CV 組合）
- 受試者：1 名健康男性母語西班牙語說話者（3 個 session）

**Session 設計：**

| Session | 目的 | 通道數 |
|---------|------|--------|
| Session 1 | 比較同心 vs. 單對電極（5 個相同肌肉）| 5 |
| Session 2 | 14 個不同肌肉各自貢獻評估 | 14 |
| Session 3 | 篩選後 10 通道驗證（含前額 FRT 作為負對照）| 10 |

**特徵提取：** 時域特徵 TD₀ = [mean(w), mean(r), power(w), power(r), ZC]，幀長 25 ms，步進 5 ms，上下文堆疊 k=15（共 31 幀）→ LDA 降維

**分類器：** GMM、Bagging DT、前饋 NN，5-fold 交叉驗證，評估：音素幀準確率

---

## 6. 最終電極配置（8 通道）

| 肌肉（英文縮寫）| 中文名稱 | 解剖位置 | 語音功能 |
|-----------------|---------|---------|---------|
| ZYG（Zygomaticus major）| 顴大肌 | 臉頰 | 微笑、上唇橫向拉伸 |
| DAO（Depressor anguli oris）| 降口角肌 | 口角下方 | 下拉口角 |
| RIS（Risorius）| 笑肌 | 臉頰外側 | 橫向拉伸口角 |
| LLS（Levator labii superioris）| 上唇提肌 | 上唇上方 | 提升上唇 |
| DLI（Depressor labii inferioris）| 降下唇肌 | 下唇下方 | 下拉下唇 |
| ABD（Anterior belly of digastric）| 二腹肌前腹 | 下顎下方（頸）| 舌骨舌相關、舌頭動作 |
| SLH（Stylohyoid）| 莖突舌骨肌 | 頸部 | 舌骨上提、吞嚥/發音 |
| MAS（Masseter）| 咬肌 | 下顎（臉頰側）| 下顎閉合 |

**臉部 5 個 + 頸部 3 個；位置不對稱（因臉部空間有限）**

**被排除的肌肉及原因：**
- OBO（口輪匝肌）：電極難以附著（嘴唇運動＋汗水），信號不穩定
- SCM（胸鎖乳突肌）：分類表現低
- STR（胸骨甲狀肌）：分類表現低
- PLT（頸闊肌）：肌肉為大片薄膜，位置難以精確定位
- SBO（肩舌骨上腹）：針對喉切除患者的氣孔位置不適用
- PBD（二腹肌後腹）：與 SLH 位置重疊且表現相似，保留一個即可
- LAO（提口角肌）：肌肉太短，改用更長的 LLS 替代

---

## 7. 主要結果

**電極類型比較（Session 1）：**
- 雙極單對貼片 > 雙極同心電極（所有 3 種分類器，p < 0.001）
- 原因：同心電極直徑（40 mm）比單對（24 mm）大，臉部小肌肉間串擾更嚴重

**各通道音素分類準確率（Session 2，14 通道）：**
- 最低（被排除）：SLH、PBD、OBO、DLI、STR、SCM
- DLI 在第一輪表現佳但後續下降（附著不穩）→ 保留至 Session 3 再驗証

**Session 3 驗証：**
- FRT（前額）準確率接近基線（baseline = 永遠預測最常見類別）→ 確認其他通道確實帶有語音信息
- 使用 Session 3 全部通道（除 FRT）最高 NN 音素準確率：**48.42%**

---

## 8. 限制

1. **單一受試者**：3 個 session 均來自同一名說話者，個體差異未能評估
2. **非默語**：實驗使用有聲語音（研究的目標是喉切除患者的 silent speech，但 pilot 資料是有聲）
3. **電極不對稱**：臉部空間不足，兩側肌肉各配置不同，未能驗證對稱配置的差異
4. **通道組合分析缺失**：每次只評估單一通道，未分析通道組合的協同效果

---

## 9. 與本論文的關聯

| 面向 | 關聯 |
|------|------|
| **1.2.2 電極配置（核心引用）** | 本論文最直接的電極配置依據：雙極差分貼片（完全相同電極類型）+ 系統性肌肉篩選 + 同類設備（OT Bioelettronica）|
| **支持「針對特定肌肉」方法** | 明確論證陣列電極在臉部 SSI 有串擾問題；支持本論文選用雙極單對貼片針對特定肌肉的設計決策 |
| **Table 1 文獻整合** | 提供 28 篇相關研究的電極配置總覽，可直接引用作為 1.2.2 的文獻脈絡梳理依據 |
| **肌肉選擇建議** | 本論文所使用的 4 通道位置（ZYG、OBO/DAO、MEN/ABD、前腹二腹肌）與 Salomons (2025) 最終 8 通道中的前 4 個高度重疊 |
| **OBO 的警示** | 口輪匝肌（本論文原配置之一）在 Salomons (2025) 中因嘴唇運動造成附著問題而被排除——提醒注意此位置的信號穩定性 |

---

## 10. 引用關鍵資訊

> Inge Salomons, Eder del Blanco, Eva Navas, and Inma Hernáez, "Electrode Setup for Electromyography-Based Silent Speech Interfaces: A Pilot Study," *Sensors*, vol. 25, no. 3, p. 781, 2025. DOI: 10.3390/s25030781

**引用重點：**
- 雙極單對貼片優於同心電極（臉部 SSI）
- 8 通道針對特定肌肉是比陣列電極更適合臉部的設計
- 最優肌肉：ZYG、DAO、RIS、LLS、DLI（臉部）+ ABD、SLH、MAS（頸部）

---

## 11. 關鍵詞

Electrode setup, bipolar EMG, facial muscles, neck muscles, silent speech interface, laryngectomy, Spanish, phone classification, electrode type comparison, muscle selection, pilot study
