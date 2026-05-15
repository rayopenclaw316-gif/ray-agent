import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np

matplotlib.rcParams['font.family'] = ['Hiragino Sans', 'DejaVu Sans']

fig, ax = plt.subplots(figsize=(26, 18))
ax.set_xlim(0, 26)
ax.set_ylim(0, 18)
ax.axis('off')
fig.patch.set_facecolor('#f0f0f0')
ax.set_facecolor('#f0f0f0')

# ── helpers ──────────────────────────────────────────────────────────────
def rect(x, y, w, h, fc='white', ec='black', lw=1.2, zorder=2, radius=0.1):
    p = mpatches.FancyBboxPatch((x, y), w, h,
        boxstyle=f'round,pad={radius}', linewidth=lw,
        edgecolor=ec, facecolor=fc, zorder=zorder)
    ax.add_patch(p)

def txt(x, y, s, fs=8, ha='center', va='center', color='black', bold=False, zorder=5):
    ax.text(x, y, s, fontsize=fs, ha=ha, va=va, color=color,
            fontweight='bold' if bold else 'normal',
            fontfamily='Hiragino Sans', zorder=zorder)

def wire(x1, y1, x2, y2, color, lw=2.2, zorder=4):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle='-', color=color, lw=lw,
                        connectionstyle='arc3,rad=0'))

def dot(x, y, color='black', r=0.10, zorder=6):
    ax.plot(x, y, 'o', markersize=r*55, color=color, zorder=zorder)

# ══════════════════════════════════════════════════════════
# BREADBOARD  (rows 1-30, cols a-j + power rails)
# origin: bb_x0, bb_y0
# ══════════════════════════════════════════════════════════
BB_X = 7.0    # breadboard left edge
BB_Y = 2.0    # breadboard bottom edge
ROW_H = 0.43  # height per row
COL_W = 0.43  # width per col
ROWS = 30
COLS = 10

# row y (bottom row = row 1)
def ry(row): return BB_Y + (row - 1) * ROW_H + ROW_H/2
# col x  (col 1=a … col 5=e | col 6=f … col 10=j)
def cx(col):
    if col <= 5:  return BB_X + (col - 1) * COL_W + COL_W/2
    else:         return BB_X + (col - 1) * COL_W + COL_W/2 + 0.4  # gap between e and f

# breadboard body
rect(BB_X - 0.5, BB_Y - 0.3, COLS * COL_W + 1.8, ROWS * ROW_H + 0.6,
     fc='#e8e8c0', ec='#888', lw=2, radius=0.2)

# row dots
for r in range(1, ROWS + 1):
    for c in range(1, COLS + 1):
        ax.plot(cx(c), ry(r), 's', markersize=4.5,
                color='#888' if c <= 5 else '#aaa', zorder=3)

# column labels (a-e, f-j)
for i, letter in enumerate(['a','b','c','d','e','f','g','h','i','j']):
    col = i + 1
    txt(cx(col), BB_Y + ROWS * ROW_H + 0.25, letter, fs=7, color='#555')

# row numbers (every 5)
for r in [1, 5, 10, 15, 20, 25, 30]:
    txt(BB_X - 0.3, ry(r), str(r), fs=6.5, ha='right', color='#666')

# power rails (left side of breadboard)
rail_x_plus = BB_X - 1.2
rail_x_minus = BB_X - 0.7
rect(rail_x_plus - 0.15, BB_Y - 0.2, 0.30, ROWS * ROW_H + 0.4,
     fc='#ffe0e0', ec='red', lw=1.5)
rect(rail_x_minus - 0.15, BB_Y - 0.2, 0.30, ROWS * ROW_H + 0.4,
     fc='#e0e0ff', ec='blue', lw=1.5)
txt(rail_x_plus,  BB_Y + ROWS * ROW_H + 0.4, '+5V', fs=7, color='red', bold=True)
txt(rail_x_minus, BB_Y + ROWS * ROW_H + 0.4, 'GND', fs=7, color='blue', bold=True)

# power rails (right side of breadboard)
rail_x_9vp = BB_X + COLS * COL_W + 0.9 + 0.35
rail_x_9vm = BB_X + COLS * COL_W + 0.9 - 0.1
rect(rail_x_9vp - 0.15, BB_Y - 0.2, 0.30, ROWS * ROW_H + 0.4,
     fc='#fff0d0', ec='darkorange', lw=1.5)
rect(rail_x_9vm - 0.15, BB_Y - 0.2, 0.30, ROWS * ROW_H + 0.4,
     fc='#e0ffe0', ec='#006600', lw=1.5)
txt(rail_x_9vp,  BB_Y + ROWS * ROW_H + 0.4, '9V+', fs=7, color='darkorange', bold=True)
txt(rail_x_9vm,  BB_Y + ROWS * ROW_H + 0.4, '9V−', fs=7, color='#006600', bold=True)

# ══════════════════════════════════════════════════════════
# ARDUINO UNO (left block)
# ══════════════════════════════════════════════════════════
ARD_X = 0.3
rect(ARD_X, 2.5, 5.8, 14.5, fc='#2255cc', ec='#1133aa', lw=2.5, radius=0.2, zorder=2)
txt(ARD_X + 2.9, 16.7, 'Arduino Uno', fs=12, color='white', bold=True)

# pin definitions: (label, y_position, wire_color)
ard_pins = {
    '5V':  (16.0, 'red'),
    'GND': (15.3, 'blue'),
    'D2':  (13.5, '#cc8800'),
    'D3':  (12.8, '#cc6600'),
    'D4':  (12.1, '#cc4400'),
    'D5':  (10.5, 'purple'),
    'D6':  (9.8,  '#009900'),
}
pin_x_out = ARD_X + 5.8  # right edge of Arduino
for label, (y, col) in ard_pins.items():
    rect(pin_x_out - 0.3, y - 0.18, 0.7, 0.36,
         fc='#ffdd44', ec='#aa8800', lw=1, radius=0.05, zorder=5)
    txt(pin_x_out - 0.1, y, label, fs=7.5, ha='center', color='black')
    dot(pin_x_out + 0.05, y, color=col)

# ══════════════════════════════════════════════════════════
# COMPONENTS  (placed on breadboard)
# ══════════════════════════════════════════════════════════

# ── 3 Pushbuttons (rows 1-3, 5-7, 9-11) ──
btn_info = [
    (2,  'D2', '正轉 BTN1', '#cc8800'),
    (6,  'D3', '反轉 BTN2', '#cc6600'),
    (10, 'D4', '停止 BTN3', '#cc4400'),
]
for base_row, pin_label, btn_label, col in btn_info:
    # button body spans cols c(3)-h(8) across the middle gap
    rect(cx(3)-0.15, ry(base_row)-0.15, cx(8)-cx(3)+0.3, ry(base_row+2)-ry(base_row)+0.3,
         fc='#cccccc', ec='#555', lw=1.5, zorder=4)
    ax.plot(cx(3)+0.08, ry(base_row+1), 'o', markersize=10, color='#888', zorder=5)  # left pin
    ax.plot(cx(8)-0.08, ry(base_row+1), 'o', markersize=10, color='#888', zorder=5)  # right pin
    txt(cx(3)+0.5*(cx(8)-cx(3)), ry(base_row+1), btn_label, fs=7.5, color='#333')

# ── Q1 NPN transistor (rows 18-20, col d=4) ──
# E=row18, B=row19, C=row20
Q1_ROW = 18; Q1_COL = 4
rect(cx(Q1_COL)-0.22, ry(Q1_ROW)-0.15, 0.44, ry(Q1_ROW+2)-ry(Q1_ROW)+0.3,
     fc='#222', ec='#555', lw=1.5, zorder=4, radius=0.05)
txt(cx(Q1_COL), ry(Q1_ROW+1), 'Q1\nNPN', fs=7, color='white')
txt(cx(Q1_COL)+0.4, ry(Q1_ROW),   'E', fs=6.5, color='#444', ha='left')
txt(cx(Q1_COL)+0.4, ry(Q1_ROW+1), 'B', fs=6.5, color='#444', ha='left')
txt(cx(Q1_COL)+0.4, ry(Q1_ROW+2), 'C', fs=6.5, color='#444', ha='left')
dot(cx(Q1_COL), ry(Q1_ROW),   '#ff6600'); dot(cx(Q1_COL), ry(Q1_ROW+1), '#ff6600')
dot(cx(Q1_COL), ry(Q1_ROW+2), '#ff6600')

# ── R1 (1kΩ) for Q1 base (row 19, cols b-c) ──
R1_ROW = 19
rect(cx(2)-0.1, ry(R1_ROW)-0.10, cx(3)-cx(2)+0.2, 0.20,
     fc='#f5deb3', ec='#8B4513', lw=1.5, zorder=4, radius=0.05)
txt((cx(2)+cx(3))/2, ry(R1_ROW)+0.25, 'R1 1kΩ', fs=6.5, color='#8B4513')
dot(cx(2), ry(R1_ROW), 'purple'); dot(cx(3), ry(R1_ROW), 'purple')

# ── D1 flyback across relay coil (row 24-25, cols c-d) ──
D1_ROW = 24
rect(cx(3)-0.10, ry(D1_ROW)-0.08, cx(4)-cx(3)+0.2, 0.16,
     fc='#ffcccc', ec='#cc0000', lw=1.5, zorder=4, radius=0.04)
txt((cx(3)+cx(4))/2, ry(D1_ROW)+0.25, 'D1', fs=6.5, color='red')
txt((cx(3)+cx(4))/2, ry(D1_ROW)-0.25, '1N4007', fs=5.5, color='#880000')
dot(cx(3), ry(D1_ROW), '#009900'); dot(cx(4), ry(D1_ROW), 'blue')

# ── D2 flyback across motor (row 27-28, col g-h) ──
D2_ROW = 27
rect(cx(7)-0.10, ry(D2_ROW)-0.08, cx(8)-cx(7)+0.2, 0.16,
     fc='#ffcccc', ec='#cc0000', lw=1.5, zorder=4, radius=0.04)
txt((cx(7)+cx(8))/2, ry(D2_ROW)+0.25, 'D2', fs=6.5, color='red')
txt((cx(7)+cx(8))/2, ry(D2_ROW)-0.25, '1N4007', fs=5.5, color='#880000')
dot(cx(7), ry(D2_ROW), 'darkorange'); dot(cx(8), ry(D2_ROW), '#006600')

# ── RELAY box (rows 21-28, cols f-j) ──
RELAY_ROWS = (21, 28); RELAY_COLS = (6, 10)
rect(cx(RELAY_COLS[0])-0.3, ry(RELAY_ROWS[0])-0.2,
     cx(RELAY_COLS[1])-cx(RELAY_COLS[0])+0.6,
     ry(RELAY_ROWS[1])-ry(RELAY_ROWS[0])+0.4,
     fc='#ffe8a0', ec='#cc6600', lw=2.5, zorder=4, radius=0.15)
txt((cx(6)+cx(10))/2, ry(28)+0.45, 'KS2E-M-DC5  (DPDT 5V)', fs=8, color='#883300', bold=True)

# relay pin dots + labels
relay_pins = {
    '端子1\n(COIL-)': (21, 6, 'green'),
    '端子16\n(COIL+)': (22, 6, 'red'),
    '端子4\n(COM1)': (23, 6, 'darkorange'),
    '端子9\n(COM2)': (24, 6, 'purple'),
    '端子6\n(NC1)': (25, 9, 'darkcyan'),
    '端子8\n(NO1)': (26, 9, 'darkcyan'),
    '端子11\n(NC2)': (27, 9, 'darkblue'),
    '端子13\n(NO2)': (28, 9, 'darkblue'),
}
for label, (row, col, col_color) in relay_pins.items():
    dot(cx(col), ry(row), col_color, r=0.12)
    txt(cx(col)+(0.5 if col<=5 else -0.5), ry(row), label,
        fs=6, ha='left' if col<=5 else 'right', color='#333')

# ── Motor (rows 25-28, right of relay) ──
MTR_X = rail_x_9vp + 0.8
MTR_Y = ry(25) + (ry(28)-ry(25))/2
mtr_r = 0.85
mc = plt.Circle((MTR_X, MTR_Y), mtr_r, fill=False, edgecolor='black', lw=2.5, zorder=5)
ax.add_patch(mc)
txt(MTR_X, MTR_Y, 'M', fs=18, bold=True)
txt(MTR_X, MTR_Y + mtr_r + 0.25, 'DC Motor', fs=8)
txt(MTR_X - mtr_r - 0.25, MTR_Y + 0.35, '端子2(+)', fs=6.5, ha='right', color='darkorange')
txt(MTR_X - mtr_r - 0.25, MTR_Y - 0.35, '端子1(−)', fs=6.5, ha='right', color='#006600')
dot(MTR_X - mtr_r, MTR_Y + 0.25, 'darkorange')
dot(MTR_X - mtr_r, MTR_Y - 0.25, '#006600')

# ── 9V Battery ──
BAT_X = 1.5; BAT_Y = 0.4
rect(BAT_X - 0.6, BAT_Y - 0.25, 1.2, 0.5, fc='#333', ec='#666', lw=1.5, radius=0.1, zorder=4)
txt(BAT_X, BAT_Y, '9V', fs=10, color='orange', bold=True)
dot(BAT_X + 0.6, BAT_Y + 0.1, 'darkorange')
dot(BAT_X + 0.6, BAT_Y - 0.1, '#006600')
txt(BAT_X + 0.75, BAT_Y + 0.1, '+', fs=9, color='darkorange', ha='left', bold=True)
txt(BAT_X + 0.75, BAT_Y - 0.1, '−', fs=9, color='#006600', ha='left', bold=True)

# ══════════════════════════════════════════════════════════
# WIRES
# ══════════════════════════════════════════════════════════
# Helper: wire from Arduino pin to breadboard row/col
def ard_to_bb(pin_label, row, col, color):
    _, (py, _) = list(ard_pins.items())[[k for k in ard_pins].index(pin_label)]
    wire(pin_x_out + 0.05, py, cx(col), ry(row), color)

# 1. 5V → left + rail
wire(pin_x_out+0.05, ard_pins['5V'][0], rail_x_plus, ard_pins['5V'][0], 'red', lw=2.5)
wire(rail_x_plus, ard_pins['5V'][0], rail_x_plus, BB_Y + ROWS*ROW_H, 'red', lw=2.5)

# 2. GND → left − rail
wire(pin_x_out+0.05, ard_pins['GND'][0], rail_x_minus, ard_pins['GND'][0], 'blue', lw=2.5)
wire(rail_x_minus, ard_pins['GND'][0], rail_x_minus, BB_Y, 'blue', lw=2.5)

# 3. D2 → BTN1 left pin (row 2, col c=3)
ard_to_bb('D2', 2, 3, '#cc8800')
# BTN1 right pin (row 2, col h=8) → GND rail
wire(cx(8), ry(2), rail_x_minus, ry(2), 'blue')

# 4. D3 → BTN2 left pin (row 6, col c=3)
ard_to_bb('D3', 6, 3, '#cc6600')
wire(cx(8), ry(6), rail_x_minus, ry(6), 'blue')

# 5. D4 → BTN3 left pin (row 10, col c=3)
ard_to_bb('D4', 10, 3, '#cc4400')
wire(cx(8), ry(10), rail_x_minus, ry(10), 'blue')

# 6. D5 → R1 left (row 19 col b=2)
ard_to_bb('D5', 19, 2, 'purple')
# R1 right → Q1 Base (row 19 col d=4)
wire(cx(3), ry(19), cx(Q1_COL), ry(Q1_ROW+1), 'purple')

# 7. Q1 Emitter (row 18) → GND rail
wire(cx(Q1_COL), ry(Q1_ROW), rail_x_minus, ry(Q1_ROW), 'blue')

# 8. Q1 Collector (row 20) → relay 端子9/COM2 (row 24, col f=6)
wire(cx(Q1_COL), ry(Q1_ROW+2), cx(6), ry(24), 'purple', lw=2)

# 9. D6 → relay 端子16/COIL+ (row 22, col f=6)
ard_to_bb('D6', 22, 6, '#009900')

# 10. relay 端子1/COIL- (row 21, col f) → GND rail
wire(cx(6), ry(21), rail_x_minus, ry(21), 'blue')

# 11. D1 anode (col c, row 24) → relay端子1/COIL- via same GND row
wire(cx(3), ry(D1_ROW), rail_x_minus, ry(D1_ROW), 'blue')
# D1 cathode (col d, row 24) → relay端子16 (row 22, col f=6)
wire(cx(4), ry(D1_ROW), cx(6), ry(22), '#009900', lw=1.5)

# 12. 9V+ battery → right 9V+ rail
wire(BAT_X + 0.6, BAT_Y + 0.1, rail_x_9vp, BAT_Y + 0.1, 'darkorange', lw=2.5)
wire(rail_x_9vp, BAT_Y + 0.1, rail_x_9vp, BB_Y + ROWS*ROW_H, 'darkorange', lw=2.5)
# 9V- → GND shared with Arduino GND
wire(BAT_X + 0.6, BAT_Y - 0.1, rail_x_9vm, BAT_Y - 0.1, '#006600', lw=2.5)
wire(rail_x_9vm, BAT_Y - 0.1, rail_x_9vm, BB_Y + ROWS*ROW_H, '#006600', lw=2.5)
# 9V- → Arduino GND (共地！)
wire(rail_x_9vm, ry(1), rail_x_minus, ry(1), 'blue', lw=2)
dot(rail_x_minus, ry(1), 'blue')

# 13. 9V+ → relay COM1 端子4 (row 23, col f=6)
wire(rail_x_9vp, ry(23), cx(6), ry(23), 'darkorange', lw=2)

# 14. relay NC1 (row 25, col i=9) → Motor端子1(-)
wire(cx(9), ry(25), MTR_X - mtr_r, MTR_Y - 0.25, '#006600', lw=2)
# relay NO1 (row 26, col i=9) → Motor端子2(+)
wire(cx(9), ry(26), MTR_X - mtr_r, MTR_Y + 0.25, 'darkorange', lw=2)
# relay NC2 (row 27, col i=9) → Motor端子2(+) also (cross-connect)
wire(cx(9), ry(27), MTR_X - mtr_r, MTR_Y + 0.25, 'darkorange', lw=1.8)
# relay NO2 (row 28, col i=9) → Motor端子1(-) cross-connect
wire(cx(9), ry(28), MTR_X - mtr_r, MTR_Y - 0.25, '#006600', lw=1.8)
dot(MTR_X - mtr_r, MTR_Y + 0.25, 'darkorange')
dot(MTR_X - mtr_r, MTR_Y - 0.25, '#006600')

# 16. D2 flyback across motor
wire(cx(7), ry(D2_ROW), MTR_X - mtr_r, MTR_Y + 0.25, 'darkorange', lw=1.5)
wire(cx(8), ry(D2_ROW), MTR_X - mtr_r, MTR_Y - 0.25, '#006600', lw=1.5)

# ══════════════════════════════════════════════════════════
# WIRE LEGEND (bottom)
# ══════════════════════════════════════════════════════════
leg_y = 1.5
legend_items = [
    ('5V (Arduino)', 'red'),
    ('GND (共地)', 'blue'),
    ('D5 PWM → Q1', 'purple'),
    ('D6 → 繼電器線圈', '#009900'),
    ('9V+ (馬達電源)', 'darkorange'),
    ('9V−', '#006600'),
]
for i, (lbl, col) in enumerate(legend_items):
    lx = 0.5 + i * 4.3
    ax.plot([lx, lx+0.6], [leg_y, leg_y], color=col, lw=3)
    txt(lx + 0.75, leg_y, lbl, fs=7.5, ha='left', color='#333')

# ══════════════════════════════════════════════════════════
# TITLE
# ══════════════════════════════════════════════════════════
txt(13, 17.6, 'TinkerCAD 接線圖 — Arduino 直流馬達正反轉', fs=15, bold=True, color='#1a1a6e')
txt(13, 17.15, '簡化版：1個電晶體 + 繼電器直驅 (D6→線圈)', fs=10, color='#444')

# ══════════════════════════════════════════════════════════
# STEP NUMBERS (numbered circles on wires)
# ══════════════════════════════════════════════════════════
steps = [
    (rail_x_plus - 0.3, 16.2, '1', 'red'),
    (rail_x_minus - 0.3, 15.5, '2', 'blue'),
    (6.5, ry(2), '3', '#cc8800'),
    (6.5, ry(6), '4', '#cc6600'),
    (6.5, ry(10), '5', '#cc4400'),
    (6.5, ry(19), '6', 'purple'),
    (cx(Q1_COL)-0.5, ry(Q1_ROW), '7', 'blue'),
    (cx(Q1_COL)+0.3, ry(Q1_ROW+2)+0.15, '8', 'purple'),
    (6.5, ry(22), '9', '#009900'),
    (cx(6)-0.5, ry(21)+0.15, '10', 'blue'),
    (rail_x_9vp+0.3, ry(23), '11', 'darkorange'),
]
for sx, sy, sn, sc in steps:
    c = plt.Circle((sx, sy), 0.18, color=sc, zorder=8)
    ax.add_patch(c)
    txt(sx, sy, sn, fs=7, color='white', bold=True, zorder=9)

plt.tight_layout(pad=0.2)
plt.savefig('/Users/rayopenclaw/ray-agent/breadboard.png',
            dpi=160, bbox_inches='tight', facecolor='#f0f0f0')
print("breadboard diagram done")
