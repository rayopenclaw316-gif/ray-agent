"""
Clean schematic for Arduino DC Motor Forward/Reverse
Simplified circuit: D6 directly drives relay coil, Q1 NPN for PWM speed.
Style: black-on-white, right-angle wires, EasyEDA-like clarity.
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
import numpy as np

matplotlib.rcParams['font.family'] = ['Hiragino Sans', 'DejaVu Sans']
matplotlib.rcParams['axes.linewidth'] = 0

fig, ax = plt.subplots(figsize=(22, 14))
ax.set_xlim(0, 22)
ax.set_ylim(0, 14)
ax.axis('off')
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

LW = 1.8   # normal wire width
LW2 = 2.5  # thick bus

def wire(x1, y1, x2, y2, lw=LW, color='black'):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, solid_capstyle='round',
            solid_joinstyle='round', zorder=3)

def dot(x, y, r=0.12, color='black'):
    c = plt.Circle((x, y), r, color=color, zorder=5)
    ax.add_patch(c)

def label(x, y, s, fs=8.5, ha='center', va='center', color='black'):
    ax.text(x, y, s, fontsize=fs, ha=ha, va=va, color=color,
            fontfamily='Hiragino Sans', zorder=6)

def box(x, y, w, h, fc='white', ec='black', lw=1.5, zorder=2):
    p = mpatches.FancyBboxPatch((x, y), w, h,
        boxstyle='square,pad=0', linewidth=lw,
        edgecolor=ec, facecolor=fc, zorder=zorder)
    ax.add_patch(p)

def resistor(x, y, length=1.2, horiz=True, lbl='', lbl_side='top'):
    """Draw a resistor symbol (rectangular body)"""
    bw, bh = (length * 0.5, 0.22) if horiz else (0.22, length * 0.5)
    bx = x - bw / 2 if horiz else x - bw / 2
    by = y - bh / 2
    if horiz:
        wire(x - length / 2, y, bx, y)
        wire(bx + bw, y, x + length / 2, y)
    else:
        wire(x, y - length / 2, x, by)
        wire(x, by + bh, x, y + length / 2)
    box(bx, by, bw, bh, fc='#fffbe6', ec='black', lw=1.2)
    off = 0.28 if lbl_side == 'top' else -0.28
    label(x, y + (off if horiz else 0), lbl, fs=8)

def diode(x1, y1, x2, y2, lbl='', lbl_off=(0.15, 0)):
    """Horizontal diode from (x1,y1) [anode] to (x2,y2) [cathode]"""
    mx = (x1 + x2) / 2
    my = (y1 + y2) / 2
    r = 0.18
    # anode wire
    wire(x1, y1, mx - r, my)
    # cathode wire
    wire(mx + r, my, x2, y2)
    # triangle (anode left, cathode right)
    tri = plt.Polygon([[mx - r, my - r], [mx - r, my + r], [mx + r, my]],
                      closed=True, fc='black', ec='black', zorder=4)
    ax.add_patch(tri)
    # cathode bar
    ax.plot([mx + r, mx + r], [my - r, my + r], 'k-', lw=1.8, zorder=5)
    label(mx + lbl_off[0], my + lbl_off[1] + 0.3, lbl, fs=8)

def npn(cx, cy, name='Q'):
    """NPN BJT symbol centered at (cx, cy)
    Returns: base_pos, collector_pos, emitter_pos"""
    r = 0.45
    # circle
    c = plt.Circle((cx, cy), r, fill=False, ec='black', lw=1.5, zorder=4)
    ax.add_patch(c)
    # base line (left)
    bx = cx - r * 0.6
    wire(cx - r, cy, bx, cy, lw=1.5)
    # vertical body bar
    ax.plot([bx, bx], [cy - 0.3, cy + 0.3], 'k-', lw=2.5, zorder=5)
    # collector (upper right)
    col_x, col_y = cx + r * 0.55, cy + r * 0.55
    wire(bx, cy + 0.2, col_x, col_y, lw=1.5)
    # emitter with arrow (lower right)
    em_x, em_y = cx + r * 0.55, cy - r * 0.55
    wire(bx, cy - 0.2, em_x, em_y, lw=1.5)
    # arrowhead on emitter (pointing outward)
    ax.annotate('', xy=(em_x, em_y),
                xytext=(em_x - 0.18, em_y + 0.18),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5))
    label(cx + 0.05, cy - r - 0.25, name, fs=8.5)
    return (cx - r, cy), (col_x, col_y), (em_x, em_y)

def switch_btn(x, y, lbl=''):
    """Pushbutton: normally open"""
    wire(x, y, x + 0.3, y)
    wire(x + 0.7, y, x + 1.0, y)
    # two vertical contacts
    ax.plot([x + 0.3, x + 0.3], [y - 0.18, y + 0.18], 'k-', lw=2)
    ax.plot([x + 0.7, x + 0.7], [y - 0.18, y + 0.18], 'k-', lw=2)
    # actuator arc
    arc = mpatches.Arc((x + 0.5, y + 0.22), 0.4, 0.28,
                        angle=0, theta1=200, theta2=340, color='black', lw=1.5)
    ax.add_patch(arc)
    label(x + 0.5, y + 0.55, lbl, fs=7.5)

def gnd_sym(x, y):
    """GND symbol"""
    wire(x, y, x, y - 0.2)
    w = 0.28
    for i, s in enumerate([1.0, 0.65, 0.3]):
        yy = y - 0.2 - i * 0.12
        ax.plot([x - w * s, x + w * s], [yy, yy], 'k-', lw=1.5)

def vcc_sym(x, y, lbl='+5V'):
    """VCC symbol (upward triangle or label)"""
    wire(x, y, x, y + 0.2)
    label(x, y + 0.38, lbl, fs=8, color='red')

# ══════════════════════════════════════════════════════════════════
# LAYOUT (all coordinates in data units)
# Left section: Arduino + buttons (x: 0.5 - 4)
# Middle-left: Q1 transistor + R1 (x: 4.5 - 7)
# Middle: Relay box (x: 8 - 13)
# Right: Motor + D2 (x: 14 - 19)
# Vertical levels:
#   +5V rail: y = 12.5
#   D6/Q1-collector bus: y = 10.5
#   Q1 base / R1: y = 9.0
#   COM2 bus: y = 7.5
#   9V+ bus: y = 6.0
#   GND rail: y = 1.0
# ══════════════════════════════════════════════════════════════════

Y_5V  = 12.5
Y_D6  = 11.0
Y_Q1B = 9.5
Y_COM2= 8.0
Y_9VP = 6.5
Y_GND = 1.0

# ──────────────────────────────────────────────────────────────────
# GND and +5V power rails (horizontal)
# ──────────────────────────────────────────────────────────────────
wire(0.8, Y_GND, 20.5, Y_GND, lw=LW2, color='#333')
label(0.3, Y_GND, 'GND', fs=9, ha='left', color='#333')

wire(0.8, Y_5V, 6.0, Y_5V, lw=LW2, color='red')
label(0.3, Y_5V, '+5V', fs=9, ha='left', color='red')

# ──────────────────────────────────────────────────────────────────
# ARDUINO box
# ──────────────────────────────────────────────────────────────────
ARD_X = 0.6; ARD_Y = 3.5; ARD_W = 2.4; ARD_H = 9.5
box(ARD_X, ARD_Y, ARD_W, ARD_H, fc='#ddeeff', ec='#1a3a8a', lw=2)
label(ARD_X + ARD_W/2, ARD_Y + ARD_H + 0.3, 'Arduino Uno', fs=11,
      color='#1a3a8a')

# Pin stubs from Arduino right edge
def ard_pin(y_level, pin_name):
    px = ARD_X + ARD_W
    ax.plot([px - 0.3, px], [y_level, y_level], 'k-', lw=1.5)
    p = mpatches.FancyBboxPatch((px - 0.55, y_level - 0.17), 0.55, 0.34,
        boxstyle='square,pad=0', lw=0.8, ec='#666', fc='#ffee88', zorder=5)
    ax.add_patch(p)
    label(px - 0.28, y_level, pin_name, fs=7.5)
    return px  # wire starts here

pins_y = {
    'D6':  Y_D6,
    'D5':  Y_Q1B,
    'D2':  5.5,
    'D3':  4.5,
    'D4':  3.8,
}
for pname, py in pins_y.items():
    ard_pin(py, pname)

# 5V pin from Arduino top
wire(ARD_X + ARD_W/2, ARD_Y + ARD_H, ARD_X + ARD_W/2, Y_5V, color='red')
dot(ARD_X + ARD_W/2, Y_5V, color='red')

# GND pin from Arduino bottom
wire(ARD_X + ARD_W/2, ARD_Y, ARD_X + ARD_W/2, Y_GND)
dot(ARD_X + ARD_W/2, Y_GND)

# ──────────────────────────────────────────────────────────────────
# BUTTONS  D2/D3/D4
# ──────────────────────────────────────────────────────────────────
btn_data = [('D2','正轉 BTN1'), ('D3','反轉 BTN2'), ('D4','停止 BTN3')]
for (pname, blbl) in btn_data:
    py = pins_y[pname]
    bx = ARD_X + ARD_W + 0.05
    switch_btn(bx, py, blbl)
    # right side → GND
    wire(bx + 1.0, py, bx + 1.5, py)
    wire(bx + 1.5, py, bx + 1.5, Y_GND)
    dot(bx + 1.5, Y_GND)

# ──────────────────────────────────────────────────────────────────
# D6 → Relay COIL+  (直驅，不經電晶體)
# ──────────────────────────────────────────────────────────────────
D6_X_OUT = ARD_X + ARD_W
COIL_P_X = 8.0   # relay left edge

# D6 wire right → relay coil+
wire(D6_X_OUT, Y_D6, COIL_P_X, Y_D6)
label(5.5, Y_D6 + 0.25, 'D6', fs=8, color='green')
# short vertical to coil+ pin on relay
wire(COIL_P_X, Y_D6, COIL_P_X, Y_D6)  # will connect into relay box pin

# ──────────────────────────────────────────────────────────────────
# D5 → R1 → Q1 (NPN for PWM speed)
# ──────────────────────────────────────────────────────────────────
R1_X = 4.2
resistor(R1_X, Y_Q1B, length=1.2, horiz=True, lbl='R1  1kΩ', lbl_side='top')
wire(D6_X_OUT, Y_Q1B, R1_X - 0.6, Y_Q1B)

Q1_CX = 5.8; Q1_CY = Y_Q1B
base_pos, col_pos, em_pos = npn(Q1_CX, Q1_CY, name='Q1\n2N2222')

# connect R1 right → Q1 base
wire(R1_X + 0.6, Y_Q1B, base_pos[0], base_pos[1])

# Q1 Emitter → GND
wire(em_pos[0], em_pos[1], em_pos[0], Y_GND)
dot(em_pos[0], Y_GND)

# Q1 Collector → up → COM2 bus
Q1_COL_X = col_pos[0]; Q1_COL_Y = col_pos[1]
COM2_Y = Y_COM2
wire(Q1_COL_X, Q1_COL_Y, Q1_COL_X, COM2_Y)
wire(Q1_COL_X, COM2_Y, COIL_P_X, COM2_Y)   # COM2 wire to relay

label(7.0, COM2_Y + 0.22, 'COM2\n端子9', fs=7.5, color='purple')

# ──────────────────────────────────────────────────────────────────
# RELAY BOX  KS2E-M-DC5  DPDT
# ──────────────────────────────────────────────────────────────────
REL_X = 8.0; REL_Y = 3.0; REL_W = 4.5; REL_H = 9.5
box(REL_X, REL_Y, REL_W, REL_H, fc='#fffbe6', ec='#996600', lw=2.5)
label(REL_X + REL_W/2, REL_Y + REL_H + 0.35, 'KS2E-M-DC5  (DPDT 5V)', fs=10,
      color='#663300')

# Left-side pins of relay (inputs)
rel_pins_left = {
    '端子16\nCOIL+': Y_D6,
    '端子1\nCOIL−': Y_D6 - 1.5,
    '端子4\nCOM1': Y_9VP,
    '端子9\nCOM2': Y_COM2,
}
for pname, py in rel_pins_left.items():
    ax.plot([REL_X - 0.3, REL_X], [py, py], 'k-', lw=1.5)
    label(REL_X - 0.55, py, pname, fs=7, ha='right')
    dot(REL_X, py)

# Right-side pins of relay (outputs → motor)
REL_RX = REL_X + REL_W
rel_pins_right = {
    '端子6\nNC1': 10.5,
    '端子8\nNO1': 9.3,
    '端子11\nNC2': 7.8,
    '端子13\nNO2': 6.6,
}
for pname, py in rel_pins_right.items():
    ax.plot([REL_RX, REL_RX + 0.3], [py, py], 'k-', lw=1.5)
    label(REL_RX + 0.55, py, pname, fs=7, ha='left')
    dot(REL_RX, py)

# Relay internal switch symbols (two SPDT switches)
def spdt(x_com, y_com, y_nc, y_no, closed_nc=True):
    """SPDT switch: COM at y_com, NC at y_nc, NO at y_no"""
    # COM contact
    ax.plot(x_com, y_com, 'ko', markersize=5, zorder=5)
    # NC contact (closed arc)
    ax.plot(x_com + 0.3, y_nc, 'ko', markersize=4, zorder=5)
    # NO contact
    ax.plot(x_com + 0.3, y_no, 'ko', markersize=4, zorder=5)
    # switch blade (to NC = normally closed)
    ax.plot([x_com, x_com + 0.3], [y_com, y_nc], 'k-', lw=1.5, zorder=4)

rel_sw_x = REL_X + 1.2
spdt(rel_sw_x, (10.5+9.3)/2 + 0.3, 10.5, 9.3)   # pole 1: COM1 side
spdt(rel_sw_x, (7.8+6.6)/2 + 0.3, 7.8, 6.6)     # pole 2: COM2 side

# Relay coil symbol (inductor) inside box
coil_cx = REL_X + REL_W / 2
coil_top = Y_D6 - 0.2
coil_bot = Y_D6 - 1.3
wire(coil_cx, coil_top, coil_cx, coil_bot)
# draw coil bumps
n_bumps = 4
bump_h = (coil_top - coil_bot) / n_bumps
for i in range(n_bumps):
    ty = coil_top - i * bump_h
    arc = mpatches.Arc((coil_cx, ty - bump_h/2), 0.22, bump_h * 0.9,
                        angle=0, theta1=180, theta2=360, color='black', lw=1.5)
    ax.add_patch(arc)
label(coil_cx + 0.35, (coil_top + coil_bot)/2, 'Relay\nCoil', fs=7.5, ha='left')

# Connect relay left pins to internal elements
# COIL+ (Y_D6) → top of coil
wire(REL_X, Y_D6, coil_cx - 0.11, Y_D6)
# COIL- (Y_D6-1.5) → bottom of coil
wire(REL_X, Y_D6 - 1.5, coil_cx - 0.11, Y_D6 - 1.3)

# COM1 → left pole 1 switch
wire(REL_X, Y_9VP, rel_sw_x, (10.5+9.3)/2 + 0.3)
# COM2 → left pole 2 switch
wire(REL_X, Y_COM2, rel_sw_x, (7.8+6.6)/2 + 0.3)

# Right side: NC1/NO1/NC2/NO2 horizontal wires inside box
for py in [10.5, 9.3, 7.8, 6.6]:
    wire(rel_sw_x + 0.3, py, REL_RX, py)

# ──────────────────────────────────────────────────────────────────
# D1 flyback across relay coil
# ──────────────────────────────────────────────────────────────────
# D1: anode at COIL- (D6-1.5), cathode at COIL+ (D6)
# Draw vertically left of relay
D1_X = REL_X - 1.0
wire(D1_X, Y_D6 - 1.5, D1_X, Y_D6)
# Triangle pointing up (cathode at top = COIL+)
mid_y = (Y_D6 + Y_D6 - 1.5) / 2
r = 0.18
tri = plt.Polygon([[D1_X - r, mid_y - r], [D1_X + r, mid_y - r],
                    [D1_X, mid_y + r]],
                  closed=True, fc='navy', ec='navy', zorder=4)
ax.add_patch(tri)
ax.plot([D1_X - r, D1_X + r], [mid_y + r, mid_y + r], color='navy', lw=1.8)
label(D1_X - 0.35, mid_y, 'D1\n1N4007', fs=7.5, ha='right', color='navy')

# Connect D1 to relay coil pins
wire(D1_X, Y_D6, REL_X, Y_D6)
dot(REL_X, Y_D6)
wire(D1_X, Y_D6 - 1.5, REL_X, Y_D6 - 1.5)
dot(REL_X, Y_D6 - 1.5)

# COIL- → GND
wire(REL_X - 0.5, Y_D6 - 1.5, REL_X - 0.5, Y_GND)
dot(REL_X - 0.5, Y_GND)
wire(D1_X, Y_D6 - 1.5, REL_X - 0.5, Y_D6 - 1.5)
dot(D1_X, Y_D6 - 1.5)

# ──────────────────────────────────────────────────────────────────
# 9V POWER  (for motor)
# ──────────────────────────────────────────────────────────────────
# 9V source symbol left side
V9_X = 0.8; V9_Y_BOT = 1.5; V9_Y_TOP = 5.5
wire(V9_X, Y_GND, V9_X, V9_Y_BOT)
# capacitor-like symbol for battery
for i, (sign, yy) in enumerate([('-', V9_Y_BOT + 0.0), ('+', V9_Y_BOT + 0.4)]):
    ax.plot([V9_X - 0.25, V9_X + 0.25], [yy, yy], 'k-',
            lw=(1.2 if sign == '-' else 2.5))
label(V9_X + 0.4, V9_Y_BOT + 0.2, '9V', fs=9, ha='left')
label(V9_X + 0.35, V9_Y_BOT + 0.45, '＋', fs=9, ha='left', color='darkorange')
label(V9_X + 0.35, V9_Y_BOT - 0.05, '−', fs=9, ha='left', color='#444')
wire(V9_X, V9_Y_BOT + 0.4, V9_X, Y_9VP)

# 9V+ horizontal rail to relay COM1
wire(V9_X, Y_9VP, REL_X, Y_9VP, color='darkorange', lw=LW)
label(4.5, Y_9VP + 0.25, '9V+', fs=8, color='darkorange')
dot(V9_X, Y_9VP, color='darkorange')

# ──────────────────────────────────────────────────────────────────
# MOTOR + D2 flyback
# ──────────────────────────────────────────────────────────────────
MTR_X = 17.0; MTR_Y = 8.0; MTR_R = 1.1
mc = plt.Circle((MTR_X, MTR_Y), MTR_R, fill=False, ec='black', lw=2.2, zorder=4)
ax.add_patch(mc)
label(MTR_X, MTR_Y, 'M', fs=18, color='black')
label(MTR_X, MTR_Y + MTR_R + 0.35, 'DC Motor', fs=9)

# Motor terminal positions
MTR_PLUS_Y  = MTR_Y + 0.55   # 端子2(+) upper
MTR_MINUS_Y = MTR_Y - 0.55   # 端子1(−) lower
MTR_LEFT_X  = MTR_X - MTR_R

wire(MTR_LEFT_X, MTR_PLUS_Y, MTR_LEFT_X - 0.3, MTR_PLUS_Y)
wire(MTR_LEFT_X, MTR_MINUS_Y, MTR_LEFT_X - 0.3, MTR_MINUS_Y)
label(MTR_LEFT_X - 0.45, MTR_PLUS_Y, '端子2\n(+)', fs=7, ha='right', color='darkorange')
label(MTR_LEFT_X - 0.45, MTR_MINUS_Y, '端子1\n(−)', fs=7, ha='right', color='#444')

# Cross-connect wires from relay right side
# NC1(10.5) → Motor端子1(−) [cross!]
# NO1(9.3)  → Motor端子2(+) [cross!]
# NC2(7.8)  → Motor端子2(+)
# NO2(6.6)  → Motor端子1(−)

JUNC_X = REL_RX + 1.5   # junction column

# Motor(+) junction at JUNC_X, MTR_PLUS_Y
wire(REL_RX + 0.3, 9.3,  JUNC_X, 9.3)           # NO1 →
wire(JUNC_X, 9.3, JUNC_X, MTR_PLUS_Y)            # up
wire(REL_RX + 0.3, 7.8,  JUNC_X + 0.5, 7.8)     # NC2 →
wire(JUNC_X + 0.5, 7.8, JUNC_X + 0.5, MTR_PLUS_Y)  # up
wire(JUNC_X, MTR_PLUS_Y, JUNC_X + 0.5, MTR_PLUS_Y)  # connect
wire(JUNC_X + 0.5, MTR_PLUS_Y, MTR_LEFT_X - 0.3, MTR_PLUS_Y)  # → Motor+
dot(JUNC_X + 0.5, MTR_PLUS_Y, color='darkorange')
label(JUNC_X + 0.25, MTR_PLUS_Y + 0.25, 'NO1+NC2', fs=7, color='darkorange')

# Motor(−) junction
wire(REL_RX + 0.3, 10.5, JUNC_X - 0.5, 10.5)    # NC1 →
wire(JUNC_X - 0.5, 10.5, JUNC_X - 0.5, MTR_MINUS_Y)  # down
wire(REL_RX + 0.3, 6.6,  JUNC_X, 6.6)            # NO2 →
wire(JUNC_X, 6.6, JUNC_X, MTR_MINUS_Y)            # up
wire(JUNC_X - 0.5, MTR_MINUS_Y, JUNC_X, MTR_MINUS_Y)  # connect
wire(JUNC_X, MTR_MINUS_Y, MTR_LEFT_X - 0.3, MTR_MINUS_Y)  # → Motor−
dot(JUNC_X - 0.5, MTR_MINUS_Y, color='#444')
label(JUNC_X - 0.25, MTR_MINUS_Y - 0.25, 'NC1+NO2', fs=7, color='#444')

# Motor right side → GND (via 9V− side)
wire(MTR_X + MTR_R, MTR_Y, MTR_X + MTR_R + 0.3, MTR_Y)
wire(MTR_X + MTR_R + 0.3, MTR_Y, MTR_X + MTR_R + 0.3, Y_GND)
dot(MTR_X + MTR_R + 0.3, Y_GND)

# D2 flyback across motor  (right side of motor)
D2_X = MTR_X + MTR_R + 0.9
wire(D2_X, MTR_MINUS_Y - 0.3, D2_X, MTR_PLUS_Y + 0.3)
mid2 = (MTR_PLUS_Y + MTR_MINUS_Y) / 2
r2 = 0.18
# diode pointing up: anode at bottom (Motor−), cathode at top (Motor+)
tri2 = plt.Polygon([[D2_X - r2, mid2 - r2], [D2_X + r2, mid2 - r2],
                     [D2_X, mid2 + r2]],
                   closed=True, fc='navy', ec='navy', zorder=4)
ax.add_patch(tri2)
ax.plot([D2_X - r2, D2_X + r2], [mid2 + r2, mid2 + r2], color='navy', lw=1.8)
label(D2_X + 0.35, mid2, 'D2\n1N4007', fs=7.5, ha='left', color='navy')
# connect D2 to motor terminals
wire(D2_X, MTR_PLUS_Y + 0.3, MTR_LEFT_X - 0.3, MTR_PLUS_Y)
dot(MTR_LEFT_X - 0.3, MTR_PLUS_Y, color='darkorange')
wire(D2_X, MTR_MINUS_Y - 0.3, MTR_LEFT_X - 0.3, MTR_MINUS_Y)
dot(MTR_LEFT_X - 0.3, MTR_MINUS_Y, color='#444')

# ──────────────────────────────────────────────────────────────────
# TITLE
# ──────────────────────────────────────────────────────────────────
ax.text(11, 13.6, 'Arduino 直流馬達正反轉控制電路', ha='center',
        fontsize=15, fontweight='bold', color='black',
        fontfamily='Hiragino Sans')
ax.text(11, 13.15, 'DPDT 繼電器換向  ＋  NPN 電晶體 PWM 速度控制  (D6直驅線圈)',
        ha='center', fontsize=9.5, color='#555',
        fontfamily='Hiragino Sans')

# ──────────────────────────────────────────────────────────────────
# COMPONENT TABLE (bottom right)
# ──────────────────────────────────────────────────────────────────
tbl = [
    ('元件', '型號/值', '接腳說明'),
    ('Q1 NPN',  '2N2222',      'B←D5/R1  C→COM2  E→GND'),
    ('R1',      '1kΩ',         'D5 → Q1 Base 限流'),
    ('繼電器',  'KS2E-M-DC5',  'COIL+←D6  COIL−←GND'),
    ('D1',      '1N4007',      '線圈反向保護'),
    ('D2',      '1N4007',      '馬達反向保護'),
    ('馬達電源','9V 電池',      '9V− 必須接 Arduino GND（共地）'),
]
tx = 12.5; ty = 3.2
box(tx - 0.2, 0.5, 8.5, ty + 0.4, fc='#f9f9f9', ec='#aaa', lw=1)
for i, row in enumerate(tbl):
    yy = ty - i * 0.43 + 0.7
    col_x = [tx, tx + 2.2, tx + 4.5]
    for j, cell in enumerate(row):
        fs = 8.5 if i == 0 else 8
        bold = (i == 0)
        ax.text(col_x[j], yy, cell, fontsize=fs, fontweight='bold' if bold else 'normal',
                va='center', fontfamily='Hiragino Sans', color='black')

plt.tight_layout(pad=0.3)
plt.savefig('/Users/rayopenclaw/ray-agent/schematic_clean.png',
            dpi=170, bbox_inches='tight', facecolor='white')
print("schematic done")
