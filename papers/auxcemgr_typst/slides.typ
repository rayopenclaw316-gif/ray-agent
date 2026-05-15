// AuxCEMGR 論文解析 — Typst + Touying 0.6.1 版
// 編譯：typst compile slides.typ slides.pdf --root /
#import "@preview/touying:0.6.1": *
#import themes.university: *

#show: university-theme.with(
  aspect-ratio: "16-9",
  config-info(
    title: [用臉部肌電圖做中文無聲語音辨識],
    subtitle: [Neural Chinese Silent Speech Recognition with Facial EMG | Xie et al., 2025],
    author: [陳睿莆　國立虎尾科技大學],
    date: [2026-05-15],
    institution: [機械與電腦輔助工程系],
  ),
)

#set text(font: ("Times New Roman", "STHeiti"), size: 17pt)
#set par(leading: 0.75em)

// 顏色
#let dark = rgb("#1F3864")
#let mid  = rgb("#2E75B6")
#let red  = rgb("#C00000")
#let orng = rgb("#C56000")
#let grn  = rgb("#006B00")

#let note(it) = text(size: 13pt, fill: gray, it)
#let hl(it)   = text(fill: mid, weight: "bold", it)
#let warn(it) = text(fill: red, weight: "bold", it)

#let figs = "/Users/rayopenclaw/ray-agent/papers/auxcemgr_figs/"
#let fig(name) = figs + name + ".png"

// ══ 封面 ══════════════════════════════════════════════════════
#title-slide()

// ══ 目錄 ══════════════════════════════════════════════════════
#slide[
  == 目錄
  #columns(2)[
    #set text(size: 16pt)
    + 研究背景與動機
    + 資料集與硬體設備
    + 訊號前處理
    + 特徵萃取（MFSC）
    + 資料增強（三種方法）
    #colbreak()
    + AuxCEMGR 模型架構
    + 訓練設定與損失函數
    + 評估指標 CER
    + 實驗結果分析
    + 結論與未來方向
    + 實驗復現快速指南
  ]
]

// ══ 一、研究背景 ══════════════════════════════════════════════
#slide[
  == 一、什麼是無聲語音介面（SSI）？
  #grid(columns: (1fr, 0.9fr), gutter: 1.5em)[
    *定義*：不發出聲音，靠感測器辨識說話意圖 → 轉成文字

    #v(0.4em)
    *應用場景*
    - 喉嚨受傷、氣管切開術後無法發聲
    - 高噪音環境（工廠、戰場）
    - 隱密通訊

    #v(0.4em)
    *為什麼難？*
    - 靜默 EMG 比有聲弱 #hl[3–5 倍]，SNR 低
    - 中文字元龐大（本研究 #hl[667 個]）
    - 每次貼電極位置不同 → #warn[Session 偏移]
  ][
    #image(fig("fig1"), width: 100%)
    #note[Fig.1 — EMG 訊號轉文字]
  ]
]

#slide[
  == 二、為什麼用臉部 sEMG？
  #grid(columns: (1fr, 0.9fr), gutter: 1.5em)[
    *sEMG（表面肌電圖）*
    - 偵測肌肉收縮時的微弱電訊號（0.1–5 mV）
    - 非侵入式、即時、可穿戴

    #v(0.4em)
    *為什麼臉部？*
    - 說話時嘴唇、下巴、臉頰、喉部肌肉都會動
    - 靜默時仍有微小收縮可被偵測

    #v(0.4em)
    *與其他技術的比較*
    #table(
      columns: (auto, 1fr),
      stroke: 0.5pt + gray,
      [喉部麥克風], [需聲帶振動，完全靜默無效],
      [EEG], [解析度低、個體差異大],
      text(fill: grn)[臉部 sEMG], text(fill: grn)[輕便、準確、可穿戴 ✓],
    )
  ][
    #image(fig("fig2"), width: 100%)
    #note[Fig.2 — 電極位置示意圖]
  ]
]

#slide[
  == 三、研究動機與挑戰
  #grid(columns: (1fr, 1fr), gutter: 1.5em)[
    *現有研究的空白*
    - 現有 sEMG 辨識大多針對英文
    - 中文 SSI 幾乎空白，#hl[本文為首篇]

    #v(0.4em)
    *中文的特殊挑戰*
    - 字元空間龐大：#hl[667 個]唯一字元
    - 聲調系統：4 個聲調 + 輕聲
    - 同音字：「ji」→ 雞、機、積…
  ][
    *Session 偏移問題（Domain Shift）*
    #block(fill: rgb("#EEF4FF"), radius: 4pt, inset: 0.8em)[
      #set text(size: 15pt)
      Session 1：電極位置 A → 分布 P₁\
      Session 2：電極位置 B → 分布 P₂\
      P₁ ≠ P₂ → 跨 Session 準確率大幅下降
    ]
    #v(0.4em)
    *本研究目標*\
    設計能克服以上挑戰的\
    #hl[第一個中文臉部 EMG SSI 系統]
  ]
]

// ══ 二、資料集與硬體 ══════════════════════════════════════════
#slide[
  == 四、資料集 & 硬體設備
  #grid(columns: (1fr, 1fr), gutter: 1.5em)[
    *資料集*
    #table(
      columns: (auto, 1fr),
      stroke: 0.5pt + gray,
      [受試者], [1 名成年女性],
      [語料庫], [NBA 籃球播報語料],
      [句子數], [1,238 句],
      [總字元], [12,584 字],
      [唯一字元], text(fill: mid)[667 個],
      [Session 數], [5（不同日期）],
      [資料分割], [訓練:驗證:測試=7:1:2],
    )
  ][
    *Neuracle NSW308M*
    #table(
      columns: (auto, 1fr),
      stroke: 0.5pt + gray,
      [採樣率], [1000 Hz],
      [通道數], [8 通道],
      [電極], [Ag/AgCl],
      [訊號振幅], [0.1–5 mV],
    )
    #v(0.4em)
    *電極位置*
    - CH1–CH2：上嘴唇（口輪匝肌）
    - CH3–CH4：下巴（#hl[CH4 最重要]）
    - CH5–CH6：喉部（靜默時幾乎不動）
    - CH7–CH8：臉頰（顴大肌）
  ]
]

// ══ 三、訊號前處理 ════════════════════════════════════════════
#slide[
  == 五、訊號前處理 — Butterworth & Notch
  #grid(columns: (1fr, 1fr), gutter: 1.5em)[
    *問題：原始 EMG 充滿雜訊*
    - 工頻電磁干擾（50 Hz 及諧波）
    - 基線漂移（< 10 Hz）
    - 高頻噪訊（> 400 Hz）

    #v(0.4em)
    *Butterworth 帶通濾波（10–400 Hz）*
    ```python
    from scipy.signal import butter, filtfilt
    b, a = butter(4, [10, 400],
                  btype='band', fs=1000)
    x = filtfilt(b, a, raw_signal)
    ```

    4 階：截止斜率 -80 dB/decade，銳利不影響主頻段
  ][
    *Notch 陷波濾波（50/150/250/350 Hz）*
    ```python
    from scipy.signal import iirnotch
    for f0 in [50, 150, 250, 350]:
        b, a = iirnotch(f0, Q=30, fs=1000)
        x = filtfilt(b, a, x)
    ```
    Q=30：陷波寬度 ≈ ±0.83 Hz，精準去除工頻

    #v(0.5em)
    *前處理流程*
    #block(fill: rgb("#EEF4FF"), radius: 4pt, inset: 0.7em)[
      原始 EMG\
      → Butterworth 帶通（10–400 Hz）\
      → Notch × 4（50/150/250/350 Hz）\
      → 分段切割（依句子邊界）
    ]
  ]
]

// ══ 四、MFSC 特徵萃取 ════════════════════════════════════════
#slide[
  == 六、MFSC 特徵萃取
  #grid(columns: (1fr, 0.9fr), gutter: 1.5em)[
    *為什麼做特徵萃取？*
    - 原始：1000 pt/秒 × 8 通道，維度高且冗餘
    - MFSC：36 維/時步，有意義的壓縮表徵

    #v(0.4em)
    *計算步驟*
    + *分窗*：Hanning 窗，25 ms，移位 10 ms
    + *FFT*：時域 → 功率頻譜
    + *36 個 Mel 濾波器*：計算各頻帶能量
    + *取對數*：模仿人耳的對數感知

    *輸出*：8 通道 × T 時步 × #hl[36 維]
  ][
    #image(fig("fig3"), width: 100%)
    #note[Fig.3 — 靜默 vs 有聲 EMG 波形]

    #block(fill: rgb("#FFF3E0"), radius: 4pt, inset: 0.6em)[
      #set text(size: 14pt)
      靜默 EMG 振幅約為有聲的 #warn[1/3–1/5]\
      → SSI 比有聲辨識更難的根本原因
    ]
  ]
]

// ══ 五、資料增強 ══════════════════════════════════════════════
#slide[
  == 七、三種資料增強總覽
  #table(
    columns: (1.2fr, 1.8fr, 1fr, 1.5fr),
    stroke: 0.5pt + gray,
    fill: (col, row) => if row == 0 { dark } else if calc.rem(row, 2) == 1 { rgb("#EEF4FF") } else { white },
    [#text(fill: white, weight: "bold")[方法]],
    [#text(fill: white, weight: "bold")[原理]],
    [#text(fill: white, weight: "bold")[關鍵參數]],
    [#text(fill: white, weight: "bold")[效果（CER）]],
    [① 頻譜相減], [估計背景噪訊頻譜並減去], [─], [66.5% → 53.9%],
    [② 有聲 EMG 混合], [按比例混入有聲說話 EMG], [γ = 0.8], [AuxCEMGR 降 6.5%],
    [③ Mixup], [兩樣本特徵和標籤插值混合], [α = 0.02], [額外降 1.5%],
  )

  #v(0.8em)
  #grid(columns: (1fr, 1fr), gutter: 1.5em)[
    *① 頻譜相減公式*
    $ hat(S)(f) = max(X(f) - hat(N)(f),\ 0) $
    X(f)：含噪訊頻譜，$hat(N)(f)$：背景噪訊估計
  ][
    *② 有聲混合 & ③ Mixup*
    $ x_"aug" = (1-gamma) dot x_"silent" + gamma dot x_"audible" $
    $ tilde(x) = lambda x_i + (1-lambda) x_j, quad lambda ~ "Beta"(alpha, alpha) $
  ]
]

#slide[
  == 八、資料增強詳解（Fig.6 & Fig.7）
  #grid(columns: (1fr, 0.9fr), gutter: 1.5em)[
    *② γ=0.8 為什麼最佳？*
    - γ=0：純靜默，訓練訊號仍微弱
    - #hl[γ=0.8]：甜蜜點，增強足夠且不過度
    - γ=1.0：訓練/測試分布差距最大，泛化差

    #v(0.5em)
    *③ α=0.02 的含義*
    - Beta(0.02, 0.02) 是 U 形分布
    - 大多數時候 λ ≈ 0 或 1（幾乎不混合）
    - 偶爾才真正混合兩個樣本
    - 效果：輕微擾動，提升泛化，不破壞原始樣本

    #v(0.5em)
    *三種增強的相對重要性*\
    頻譜相減 > 有聲 EMG 混合 > Mixup\
    三者相互補充，缺一效果均下降
  ][
    #image(fig("fig6"), width: 100%)
    #note[Fig.6 — γ 值對 CER 的影響]
    #v(0.3em)
    #image(fig("fig7"), width: 100%)
    #note[Fig.7 — α 值對 CER 的影響]
  ]
]

// ══ 六、模型架構 ══════════════════════════════════════════════
#slide[
  == 九、AuxCEMGR 模型架構
  #grid(columns: (1fr, 0.85fr), gutter: 1.5em)[
    *全名：Auxiliary-task Cascaded EMG Recognizer*

    *主流程（由左至右）*
    + #hl[CNN（2 層）]：提取局部肌肉動作模式（步長=2，壓縮 T→T/4）
    + #hl[Transformer（6 層，8 頭）]：捕捉全局時序依賴
    + #hl[CTC 解碼器]：輸出中文字元序列

    #v(0.4em)
    *兩個輔助任務（並行分支）*
    - #text(fill: orng)[拼音 CTC]：輔助學習音韻（η₁=1.0）
    - #text(fill: red)[GRL + Session 分類]：消除偏移（η₂=1.0）

    #v(0.4em)
    *總損失函數*
    $ L_"total" = L_"CTC"^"char" + eta_1 L_"CTC"^"pinyin" + eta_2 L_"session" $
  ][
    #image(fig("fig4"), width: 100%)
    #note[Fig.4 — 論文原始架構圖]
    #v(0.3em)
    #image(fig("chart_arch"), width: 100%)
    #note[架構示意（自製）]
  ]
]

#slide[
  == 十、CTC 解碼器 + Beam Search
  #grid(columns: (1fr, 1fr), gutter: 1.5em)[
    *為什麼需要 CTC？*
    - EMG 序列長度（T≈100）≠ 文字長度（≈20）
    - 而且沒有字元對齊標註

    *CTC 解法：引入空白符號 ε*
    #block(fill: rgb("#EEF4FF"), radius: 4pt, inset: 0.8em)[
      #set text(size: 15pt)
      模型每步輸出：某字元 or ε\
      輸出：你-你-好-ε-ε-世-界\
      折疊：#hl[你好世界 ✓]
    ]

    *損失函數*
    $ L_"CTC" = -log P(y | x) $
    最大化正確序列所有對齊路徑的總概率
  ][
    *Beam Search（size=5）*
    #table(
      columns: (auto, 1fr, auto),
      stroke: 0.5pt + gray,
      fill: (col, row) => if row == 0 { dark } else if row == 3 { rgb("#DCEEFF") } else { white },
      [#text(fill: white)[方法]], [#text(fill: white)[說明]], [#text(fill: white)[效果]],
      [Greedy], [每步選最高概率], [快但次優],
      [Beam=1], [等同 Greedy], [同上],
      text(fill: mid, weight: "bold")[Beam=5], [同時保留 5 條路徑], text(fill: mid)[最佳平衡],
      [Beam=50], [保留 50 條], [慢，邊際遞減],
    )
    #note[比喻：5 個偵探同時出發，選最合理路線]
  ]
]

#slide[
  == 十一、兩個輔助任務詳解
  #grid(columns: (1fr, 1fr), gutter: 1.5em)[
    *① 拼音 CTC（η₁=1.0）*

    - 動機：667 個字元難學，拼音只有 63 種
    - 做法：Transformer 輸出後接拼音 CTC 分支
    - 讓模型先學「怎麼發音」再學「對應哪個字」

    #image(fig("fig5"), width: 85%)
    #note[Fig.5 — η₁/η₂ 熱力圖，最佳為 1.0/1.0]
  ][
    *② GRL + Session 分類（η₂=1.0）*

    問題：5 個 Session 特徵分布不同 → Domain Shift

    *梯度反轉層（GRL）工作原理*
    #block(fill: rgb("#EEF4FF"), radius: 4pt, inset: 0.7em)[
      #set text(size: 15pt)
      正向：資料原樣通過\
      反向：梯度乘以 *-1*（方向反轉）
    ]
    #block(fill: rgb("#FFE4E4"), radius: 4pt, inset: 0.7em)[
      #set text(size: 15pt)
      結果：CNN 被迫學到「讓 Session\
      分類器困惑」的特徵\
      → #hl[Domain Invariant 特徵]
    ]
    #note[比喻：反間諜訓練]
  ]
]

// ══ 七、訓練設定 ══════════════════════════════════════════════
#slide[
  == 十二、訓練設定
  #grid(columns: (1fr, 1fr), gutter: 1.5em)[
    *Noam 暖機學習率排程器*
    $ "lr" = d_"model"^(-0.5) dot min(t^(-0.5), t dot "warmup"^(-1.5)) $
    - $d_"model"=256$，warmup = 4000 步
    - 前 4000 步線性升高 → 之後緩慢下降

    *優化器：Adam*
    - β₁=0.9, β₂=0.98, ε=1e-9

    *評估指標：CER*
    $ "CER" = frac(S + D + I, N) $
    S 替換，D 刪除，I 插入，N 總字元數
  ][
    *超參數總覽*
    #table(
      columns: (1.5fr, 1fr),
      stroke: 0.5pt + gray,
      fill: (col, row) => if row == 0 { dark } else if calc.rem(row, 2) == 1 { rgb("#EEF4FF") } else { white },
      [#text(fill: white, weight: "bold")[參數]], [#text(fill: white, weight: "bold")[值]],
      [Batch Size], [128],
      [Dropout], [0.1],
      [Warmup Steps], [4000],
      [d_model], [256],
      [Transformer 層數], [6],
      [注意力頭數], [8],
      [η₁ / η₂], [1.0 / 1.0],
      [提前停止], [10 Epoch],
    )
  ]
]

// ══ 八、實驗結果 ══════════════════════════════════════════════
#slide[
  == 十三、主要實驗結果
  #grid(columns: (1fr, 1fr), gutter: 1.5em)[
    #table(
      columns: (1.8fr, 1fr),
      stroke: 0.5pt + gray,
      fill: (col, row) => {
        if row == 0 { dark }
        else if row == 5 { rgb("#DCEEFF") }
        else if calc.rem(row, 2) == 1 { rgb("#F5F5F5") }
        else { white }
      },
      [#text(fill: white, weight: "bold")[模型]],
      [#text(fill: white, weight: "bold")[CER]],
      [Wadkins 2019 (LSTM+CTC)], [66.8%],
      [Baseline 無增強], [66.5%],
      [Baseline 完整增強], [44.5%],
      [AuxCEMGR 無增強], [62.5%],
      text(fill: mid, weight: "bold")[AuxCEMGR 完整增強],
      text(fill: mid, weight: "bold")[38.0% ⭐],
    )
    *關鍵結論*
    - AuxCEMGR 無增強比 Baseline 差 → 模型與增強須搭配
    - #hl[模型 + 增強缺一不可]
    - 比 Wadkins 2019 改善 28.8 個百分點
  ][
    #image(fig("chart_main"), width: 100%)
    #note[主要結果橫條圖（越低越好）]
  ]
]

#slide[
  == 十四、電極通道 & 句子長度分析
  #grid(columns: (1fr, 0.9fr), gutter: 1.5em)[
    *電極通道重要性（Fig.8）*
    #table(
      columns: (auto, auto, 1fr),
      stroke: 0.5pt + gray,
      fill: (col, row) => if row == 0 { dark } else if row == 1 or row == 2 { rgb("#DCEEFF") } else { white },
      [#text(fill: white)[通道]], [#text(fill: white)[位置]], [#text(fill: white)[重要性]],
      text(fill: mid, weight: "bold")[CH4], [下巴右], [⭐⭐⭐⭐⭐ 最重要],
      text(fill: mid)[CH3], [下巴左], [⭐⭐⭐⭐],
      [CH1,CH2], [上嘴唇], [⭐⭐⭐],
      [CH7,CH8], [臉頰], [⭐⭐],
      text(fill: gray)[CH5,CH6], [喉部], text(fill: gray)[⭐ 最不重要],
    )
    *句子長度 vs CER（Fig.10）*
    - 短句 CER 低，長句 CER 大幅上升
    - 改善方向：加入語言模型（LM）輔助解碼
  ][
    #image(fig("fig8"), width: 100%)
    #note[Fig.8 — 各通道單獨 CER]
    #v(0.3em)
    #image(fig("fig10"), width: 100%)
    #note[Fig.10 — 句子長度 vs CER]
  ]
]

// ══ 十、結論與復現 ════════════════════════════════════════════
#slide[
  == 十五、結論
  #grid(columns: (1fr, 1fr), gutter: 1.5em)[
    *主要貢獻*
    - 第一個中文臉部 sEMG 無聲語音辨識系統
    - 最佳測試集 CER = #hl[38.0%]
    - 三種增強 + 兩個輔助任務，各自都有貢獻

    *研究限制*
    - 只有 1 名受試者（跨人泛化未知）
    - NBA 特定語料庫
    - CER 38% 實用化仍有距離
  ][
    *未來研究方向*
    + 多受試者跨人辨識
    + 加入語言模型解碼
    + 擴充語料庫（方言、日常）
    + 硬體微型化（可穿戴式）
    + 多模態融合（sEMG + 視訊）
    + 即時推論（Online）
  ]
]

#slide[
  == 十六、實驗復現快速指南
  #grid(columns: (1fr, 1fr), gutter: 1em)[
    ```python
    # 環境安裝
    pip install torch librosa scipy numpy jiwer

    # Step 1：訊號前處理
    from scipy.signal import butter, filtfilt, iirnotch
    b, a = butter(4, [10,400], btype='band', fs=1000)
    x = filtfilt(b, a, raw)
    for f0 in [50,150,250,350]:
        b, a = iirnotch(f0, Q=30, fs=1000)
        x = filtfilt(b, a, x)

    # Step 2：MFSC
    mfsc = librosa.feature.melspectrogram(
        y=x, sr=1000, n_mels=36, hop_length=10)
    ```
  ][
    ```python
    # Step 3：模型建立
    class AuxCEMGR(nn.Module):
      def __init__(self):
        super().__init__()
        self.cnn = nn.Sequential(
          nn.Conv2d(8, 256, 3, stride=2),
          nn.Conv2d(256, 256, 3, stride=2))
        enc = nn.TransformerEncoderLayer(
          d_model=256, nhead=8, dropout=0.1)
        self.enc = nn.TransformerEncoder(enc, 6)
        self.ctc     = nn.Linear(256, 668)
        self.pinyin  = nn.Linear(256, 64)
        self.session = nn.Linear(256, 5)

    # Step 4：訓練
    # Adam + Noam(warmup=4000) + Batch=128
    # L = L_ctc + 1.0*L_py + 1.0*L_sess(GRL)
    # Beam Search(size=5) → 評估 CER
    ```
  ]
]
