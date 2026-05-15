#!/usr/bin/env python3
"""
精準從 AuxCEMGR 論文 PDF 裁切每一張圖（含向量圖），
同時生成 matplotlib 補充圖表。
輸出至 /Users/rayopenclaw/ray-agent/papers/auxcemgr_figs/
"""
import fitz
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import os

PDF_PATH = '/Users/rayopenclaw/Downloads/1-s2.0-S0167639325000457-main.pdf'
FIG_DIR  = '/Users/rayopenclaw/ray-agent/papers/auxcemgr_figs'
os.makedirs(FIG_DIR, exist_ok=True)

# ── Step 1：從 PDF 精準裁切圖片 ──────────────────────────────────
# 每個圖的 caption 位置（從前面分析得到）
# 格式：key -> (page_idx, col, caption_y0, caption_y1)
# col: 'L'=左欄(x:28-292), 'R'=右欄(x:303-567), 'F'=全寬(x:28-567)
FIG_INFO = {
    'fig1':  (1,  'L', 150, 164),
    'fig2':  (2,  'R', 410, 433),
    'fig3':  (3,  'L', 250, 264),
    'fig4':  (4,  'L', 209, 239),
    'fig5':  (6,  'L', 207, 230),
    'fig6':  (6,  'L', 365, 388),
    'fig7':  (6,  'R', 165, 180),
    'fig8':  (6,  'R', 273, 287),
    'fig9':  (6,  'R', 467, 481),
    'fig10': (7,  'R', 172, 194),
    'fig11': (8,  'L', 158, 173),
    'fig12': (8,  'L', 316, 331),
}

COL_BOUNDS = {
    'L': (28, 292),
    'R': (303, 567),
    'F': (28, 567),
}

DPI = 200  # 渲染解析度

doc = fitz.open(PDF_PATH)
saved = {}

for key, (page_idx, col, cap_y0, cap_y1) in FIG_INFO.items():
    page = doc[page_idx]
    ph = page.rect.height

    x0, x1 = COL_BOUNDS[col]

    # 找圖片頂端：搜尋 caption 上方同欄最近的文字塊底部
    blocks = page.get_text("blocks")
    prev_y1 = 28  # 預設從頁頂留邊距
    for b in blocks:
        bx0, by0, bx1, by1, text, *_ = b
        if text.strip() == '':
            continue
        # 需在同欄且在 caption 上方
        mid_x = (bx0 + bx1) / 2
        in_col = (col == 'F') or (col == 'L' and mid_x < 300) or (col == 'R' and mid_x >= 300)
        if in_col and by1 < cap_y0 - 5:
            prev_y1 = max(prev_y1, by1)

    # clip rect：上方留 4pt 空白
    clip = fitz.Rect(x0 - 4, prev_y1 + 4, x1 + 4, cap_y1 + 2)
    clip = clip & page.rect  # 確保不超出頁面

    mat = fitz.Matrix(DPI / 72, DPI / 72)
    pix = page.get_pixmap(matrix=mat, clip=clip, alpha=False)

    out_path = f'{FIG_DIR}/{key}.png'
    pix.save(out_path)
    saved[key] = out_path
    print(f'  [{key}] p{page_idx+1} col={col} clip={clip} → {pix.width}×{pix.height}')

doc.close()

# ── Step 2：生成補充 matplotlib 圖表 ─────────────────────────────
import matplotlib.font_manager as fm
CHN_FONT = next(
    (f.name for f in fm.fontManager.ttflist
     if f.name in ['Heiti TC', 'PingFang TC', 'STHeiti', 'Arial Unicode MS']),
    'DejaVu Sans'
)
plt.rcParams['font.family'] = CHN_FONT
plt.rcParams['axes.unicode_minus'] = False

# ── 圖表 A：主要結果橫條圖 ───────────────────────────────────────
def chart_main_results():
    fig, ax = plt.subplots(figsize=(9, 5))
    models  = ['Wadkins 2019\n(LSTM+CTC)', 'Baseline\n(無增強)',
               'Baseline\n(完整增強)', 'AuxCEMGR\n(無增強)', 'AuxCEMGR\n(完整增強)']
    cer     = [66.8, 66.5, 44.5, 62.5, 38.0]
    colors  = ['#999999','#E07070','#F0A060','#80B0E0','#2E75B6']
    bars = ax.barh(models, cer, color=colors, edgecolor='white', height=0.55)
    for bar, val in zip(bars, cer):
        ax.text(val + 0.8, bar.get_y() + bar.get_height()/2,
                f'{val}%', va='center', fontsize=13, fontweight='bold')
    ax.set_xlabel('字元錯誤率 CER (%)', fontsize=13)
    ax.set_title('主要實驗結果比較（測試集，越低越好）', fontsize=14, fontweight='bold', pad=12)
    ax.set_xlim(0, 80)
    ax.axvline(38.0, color='#1F3864', linestyle='--', linewidth=1.5, label='最佳 38.0%')
    ax.legend(fontsize=11)
    ax.invert_yaxis()
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    plt.tight_layout()
    out = f'{FIG_DIR}/chart_main.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(); print(f'  [chart_main] {out}'); return out

# ── 圖表 B：資料增強消融 ─────────────────────────────────────────
def chart_augmentation():
    fig, ax = plt.subplots(figsize=(8, 4.5))
    x = np.arange(4)
    w = 0.35
    baseline = [66.5, 53.9, 49.6, 44.5]
    auxcemgr = [62.5, 45.8, 44.5, 38.0]
    labels   = ['無增強', '頻譜相減\n移除', 'Mixup\n移除', '完整增強']
    b1 = ax.bar(x - w/2, baseline, w, label='Baseline', color='#F0A060', edgecolor='white')
    b2 = ax.bar(x + w/2, auxcemgr, w, label='AuxCEMGR', color='#2E75B6', edgecolor='white')
    for bar in list(b1)+list(b2):
        h = bar.get_height()
        ax.text(bar.get_x()+bar.get_width()/2, h+0.5, f'{h}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylabel('CER (%)'); ax.set_ylim(0, 80)
    ax.set_title('資料增強消融實驗（三種增強各自移除的影響）', fontsize=13, fontweight='bold', pad=10)
    ax.legend(fontsize=11)
    ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
    plt.tight_layout()
    out = f'{FIG_DIR}/chart_aug.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(); print(f'  [chart_aug] {out}'); return out

# ── 圖表 C：CER 評估指標說明 ──────────────────────────────────────
def chart_cer_example():
    fig, ax = plt.subplots(figsize=(8, 3.5))
    ax.axis('off')
    data = [
        ['操作', '說明', '範例'],
        ['Substitution (S)', '錯誤替換', '「好」→「號」'],
        ['Deletion (D)',      '漏字',     '「你好世界」→「你世界」'],
        ['Insertion (I)',     '多字',     '「你好」→「你啊好」'],
    ]
    tbl = ax.table(cellText=data[1:], colLabels=data[0],
                   cellLoc='center', loc='center',
                   colWidths=[0.35, 0.25, 0.4])
    tbl.auto_set_font_size(False); tbl.set_fontsize(12)
    tbl.scale(1, 2.5)
    for (r, c), cell in tbl.get_celld().items():
        if r == 0:
            cell.set_facecolor('#1F3864'); cell.set_text_props(color='white', fontweight='bold')
        else:
            cell.set_facecolor('#EEF4FF' if r % 2 == 1 else 'white')
    ax.set_title('CER = (S + D + I) / N，計算方式說明', fontsize=13, fontweight='bold', pad=20)
    plt.tight_layout()
    out = f'{FIG_DIR}/chart_cer.png'
    plt.savefig(out, dpi=150, bbox_inches='tight')
    plt.close(); print(f'  [chart_cer] {out}'); return out

# ── 圖表 D：模型架構示意圖 ────────────────────────────────────────
def chart_architecture():
    fig, ax = plt.subplots(figsize=(10, 5.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 6); ax.axis('off')

    def box(cx, cy, w, h, text, fc, tc='white', fs=10):
        rect = mpatches.FancyBboxPatch((cx-w/2, cy-h/2), w, h,
            boxstyle='round,pad=0.08', facecolor=fc, edgecolor='white', linewidth=1.5)
        ax.add_patch(rect)
        ax.text(cx, cy, text, ha='center', va='center', fontsize=fs,
                color=tc, fontweight='bold', multialignment='center')

    def arrow(x1,y1,x2,y2):
        ax.annotate('', xy=(x2,y2), xytext=(x1,y1),
                    arrowprops=dict(arrowstyle='->', color='#555', lw=1.8))

    box(0.9, 3.0, 1.5, 1.0, '臉部\nsEMG\n(8 通道)', '#666666', fs=9)
    arrow(1.65, 3.0, 2.1, 3.0)
    box(2.7,  3.0, 1.1, 1.0, 'CNN\n(2層)', '#2E75B6', fs=10)
    arrow(3.25, 3.0, 3.7, 3.0)
    box(4.5,  3.0, 1.5, 1.0, 'Transformer\n編碼器\n(6層)', '#1F3864', fs=9)
    arrow(5.25, 3.0, 5.7, 3.0)
    box(6.4,  3.0, 1.2, 1.0, 'CTC\n解碼器', '#2E75B6', fs=10)
    arrow(7.0, 3.0, 7.45, 3.0)
    box(8.2,  3.0, 1.4, 1.0, '中文\n字元序列', '#006B00', fs=9)

    ax.annotate('', xy=(6.4, 4.7), xytext=(4.5, 3.5),
                arrowprops=dict(arrowstyle='->', color='#C56000', lw=1.5))
    box(6.4, 5.1, 1.5, 0.8, '拼音 CTC\n（輔助任務1）', '#C56000', fs=9)
    ax.text(7.35, 5.1, '→ 拼音序列', va='center', fontsize=9, color='#C56000')

    ax.annotate('', xy=(6.4, 1.3), xytext=(4.5, 2.5),
                arrowprops=dict(arrowstyle='->', color='#C00000', lw=1.5))
    box(6.4, 0.9, 1.8, 0.8, 'GRL + Session 分類\n（輔助任務2）', '#C00000', fs=8.5)
    ax.text(7.45, 0.9, '→ 消除 Session 偏移', va='center', fontsize=9, color='#C00000')

    ax.text(0.1, 5.7, 'AuxCEMGR 模型架構示意圖', fontsize=13, fontweight='bold', color='#1F3864')
    plt.tight_layout(pad=0.3)
    out = f'{FIG_DIR}/chart_arch.png'
    plt.savefig(out, dpi=150, bbox_inches='tight', facecolor='white')
    plt.close(); print(f'  [chart_arch] {out}'); return out

print('\n=== 生成補充圖表 ===')
saved['chart_main'] = chart_main_results()
saved['chart_aug']  = chart_augmentation()
saved['chart_cer']  = chart_cer_example()
saved['chart_arch'] = chart_architecture()

print(f'\n=== 完成，共 {len(saved)} 個圖檔 ===')
for k, v in saved.items():
    print(f'  {k}: {os.path.basename(v)}')
