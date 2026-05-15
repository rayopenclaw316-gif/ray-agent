import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

matplotlib.rcParams['font.family'] = ['Hiragino Sans', 'DejaVu Sans']

fig, ax = plt.subplots(figsize=(22, 15))
ax.set_xlim(0, 22)
ax.set_ylim(0, 15)
ax.axis('off')
fig.patch.set_facecolor('white')
ax.set_facecolor('white')

LW = 1.8

def wire(x1, y1, x2, y2, color='black', lw=LW):
    ax.plot([x1, x2], [y1, y2], color=color, lw=lw, solid_capstyle='round')

def dot(x, y, r=0.07):
    ax.plot(x, y, 'ko', markersize=r*60)

def lbl(x, y, text, ha='center', va='center', fs=8, bold=False, color='black'):
    w = 'bold' if bold else 'normal'
    ax.text(x, y, text, ha=ha, va=va, fontsize=fs, fontweight=w, color=color)

def resistor(x1, y, x2, text=''):
    wire(x1, y, x1+0.25, y)
    wire(x2-0.25, y, x2, y)
    rw = (x2-x1) - 0.5
    rect = mpatches.Rectangle((x1+0.25, y-0.15), rw, 0.30,
                                linewidth=LW, edgecolor='black', facecolor='#ffe0a0')
    ax.add_patch(rect)
    if text:
        lbl((x1+x2)/2, y+0.35, text, fs=7)

def npn_transistor(cx, cy, name=''):
    # vertical bar
    wire(cx, cy-0.55, cx, cy+0.55)
    # base lead
    wire(cx-0.8, cy, cx, cy)
    # collector lead (upper right)
    wire(cx, cy+0.35, cx+0.65, cy+0.9)
    # emitter lead (lower right) with arrowhead
    ax.annotate('', xy=(cx+0.65, cy-0.9), xytext=(cx+0.32, cy-0.45),
                arrowprops=dict(arrowstyle='->', color='black', lw=LW))
    wire(cx, cy-0.35, cx+0.32, cy-0.45)
    # circle
    c = plt.Circle((cx+0.1, cy), 0.78, fill=False, edgecolor='black', lw=LW)
    ax.add_patch(c)
    if name:
        lbl(cx-0.3, cy+1.05, name, fs=9, bold=True)
    # return (base_x, base_y), (col_x, col_y), (emit_x, emit_y)
    return (cx-0.8, cy), (cx+0.65, cy+0.9), (cx+0.65, cy-0.9)

def diode_v(x, y_bot, y_top, name=''):
    mid = (y_bot + y_top) / 2
    s = 0.22
    wire(x, y_bot, x, mid-s)
    wire(x, mid+s, x, y_top)
    tri = plt.Polygon([[x-s, mid+s],[x+s, mid+s],[x, mid-s]],
                       closed=True, facecolor='black', edgecolor='black')
    ax.add_patch(tri)
    wire(x-s, mid-s, x+s, mid-s)
    if name:
        lbl(x+0.45, mid, name, fs=7)

def diode_h(x_left, y, x_right, name=''):
    mid = (x_left + x_right) / 2
    s = 0.22
    wire(x_left, y, mid-s, y)
    wire(mid+s, y, x_right, y)
    tri = plt.Polygon([[mid-s, y-s],[mid-s, y+s],[mid+s, y]],
                       closed=True, facecolor='black', edgecolor='black')
    ax.add_patch(tri)
    wire(mid+s, y-s, mid+s, y+s)
    if name:
        lbl(mid, y+0.4, name, fs=7)

def gnd(x, y):
    wire(x, y, x, y-0.25)
    for i, w in enumerate([0.32, 0.20, 0.09]):
        yy = y-0.25-i*0.16
        wire(x-w, yy, x+w, yy)

def switch_sym(x_bus, y, x_out, label_txt, closed=True):
    """Draw switch from bus to output, closed=NC, open=NO"""
    gap = 0.35
    wire(x_bus, y, x_bus+gap, y)
    wire(x_bus+gap*2.2, y, x_out, y)
    dot(x_bus+gap, y)
    dot(x_bus+gap*2.2, y)
    if closed:
        wire(x_bus+gap, y, x_bus+gap*2.2, y)   # closed contact
    else:
        ax.plot([x_bus+gap, x_bus+gap*2.2], [y, y+0.3], 'k-', lw=LW)  # open arm
    lbl(x_out+0.6, y, label_txt, ha='left', fs=7.5)

def motor_circle(cx, cy):
    c = plt.Circle((cx, cy), 0.7, fill=False, edgecolor='black', lw=LW)
    ax.add_patch(c)
    lbl(cx, cy, 'M', fs=15, bold=True)
    # top pin
    wire(cx, cy+0.7, cx, cy+1.0)
    # bottom pin
    wire(cx, cy-0.7, cx, cy-1.0)

# ═══════════════════════════════════════════════════════════════
# TITLE
# ═══════════════════════════════════════════════════════════════
lbl(11, 14.6, 'Arduino 直流馬達正反轉控制電路', fs=14, bold=True)
lbl(11, 14.15, 'DPDT 繼電器方向切換 + NPN 電晶體 PWM 速度控制', fs=10, color='#444')

# ═══════════════════════════════════════════════════════════════
# POWER RAILS
# ═══════════════════════════════════════════════════════════════
# 5V rail: y=13.5
wire(2.5, 13.5, 13.8, 13.5, color='red', lw=2)
lbl(1.8, 13.65, '+5V', fs=8, color='red', bold=True)

# GND rail: y=1.3
wire(0, 1.3, 21.2, 1.3, color='#444', lw=2)
lbl(21.5, 1.3, 'GND', fs=8, color='#444', bold=True)

# ═══════════════════════════════════════════════════════════════
# ARDUINO BOX
# ═══════════════════════════════════════════════════════════════
ard_box = mpatches.FancyBboxPatch((0.2, 2.0), 2.2, 11.8,
    boxstyle='round,pad=0.1', linewidth=2,
    edgecolor='#1a3a8a', facecolor='#d0e4ff')
ax.add_patch(ard_box)
lbl(1.3, 13.55, 'Arduino', fs=9, bold=True, color='#1a3a8a')
lbl(1.3, 13.15, 'Uno', fs=9, bold=True, color='#1a3a8a')

pin_x = 2.4
pin_defs = [
    ('5V',  13.5, 'red'),
    ('D6',  11.5, 'black'),
    ('D5',   8.0, 'black'),
    ('D4',   6.8, 'black'),
    ('D3',   5.8, 'black'),
    ('D2',   4.8, 'black'),
    ('GND',  1.3, '#444'),
]
for name, py, col in pin_defs:
    lbl(pin_x-0.15, py, name, ha='right', fs=8, color=col)
    dot(pin_x, py)

# ═══════════════════════════════════════════════════════════════
# BUTTONS  (BTN1/2/3)
# ═══════════════════════════════════════════════════════════════
btn_data = [
    ('D2', 4.8, 'BTN1\n正轉', 4.5),
    ('D3', 5.8, 'BTN2\n反轉', 5.5),
    ('D4', 6.8, 'BTN3\n停止', 6.5),
]
for pin_name, pin_y, btn_label, btn_x in btn_data:
    wire(pin_x, pin_y, btn_x-0.22, pin_y)   # line to button
    # button body
    wire(btn_x-0.22, pin_y, btn_x-0.22, pin_y+0.30)   # left post
    wire(btn_x+0.22, pin_y, btn_x+0.22, pin_y+0.30)   # right post
    wire(btn_x-0.18, pin_y+0.30, btn_x+0.18, pin_y+0.30)  # bottom contact
    wire(btn_x-0.18, pin_y+0.55, btn_x+0.18, pin_y+0.55)  # top contact
    wire(btn_x, pin_y+0.55, btn_x, pin_y+0.72)             # actuator
    wire(btn_x-0.2, pin_y+0.72, btn_x+0.2, pin_y+0.72)    # button cap
    wire(btn_x+0.22, pin_y, btn_x+0.22, 1.3)   # right leg to GND
    dot(btn_x+0.22, 1.3)
    lbl(btn_x, pin_y-0.28, btn_label, fs=7)

# ═══════════════════════════════════════════════════════════════
# Q1 : D6 → R1 → Q1 → Relay Coil → 5V
#      (繼電器線圈驅動)
# ═══════════════════════════════════════════════════════════════
# D6 → R1 (horizontal)
wire(pin_x, 11.5, 3.4, 11.5)
resistor(3.4, 11.5, 5.5, 'R1  1kΩ')
wire(5.5, 11.5, 6.2, 11.5)   # to Q1 base

q1b, q1c, q1e = npn_transistor(7.0, 11.5, 'Q1')
wire(6.2, 11.5, q1b[0], q1b[1])   # base wire

# Q1 emitter → GND
wire(q1e[0], q1e[1], q1e[0], 1.3)
dot(q1e[0], 1.3)

# Q1 collector → up → relay coil 端子1 at (13.5, 12.0)
wire(q1c[0], q1c[1], q1c[0], 13.8)
wire(q1c[0], 13.8, 13.5, 13.8)
wire(13.5, 13.8, 13.5, 13.2)   # ↓ to coil top
lbl(13.3, 13.5, '端子1', ha='right', fs=7)

# ═══════════════════════════════════════════════════════════════
# Q2 : D5 → R2 → Q2 → Relay COM2
#      (PWM 速度控制)
# ═══════════════════════════════════════════════════════════════
wire(pin_x, 8.0, 3.4, 8.0)
resistor(3.4, 8.0, 5.5, 'R2  1kΩ')
wire(5.5, 8.0, 6.2, 8.0)

q2b, q2c, q2e = npn_transistor(7.0, 8.0, 'Q2')
wire(6.2, 8.0, q2b[0], q2b[1])

# Q2 emitter → GND
wire(q2e[0], q2e[1], q2e[0], 1.3)
dot(q2e[0], 1.3)

# Q2 collector → relay COM2 (端子9) at (10.5, 10.2)
wire(q2c[0], q2c[1], q2c[0], 10.5)
wire(q2c[0], 10.5, 10.5, 10.5)
lbl(10.3, 10.7, '端子9\nCOM2', ha='right', fs=7)

# ═══════════════════════════════════════════════════════════════
# 9V POWER SUPPLY
# ═══════════════════════════════════════════════════════════════
batt = mpatches.FancyBboxPatch((0.2, 0.05), 2.0, 0.90,
    boxstyle='round,pad=0.05', linewidth=2,
    edgecolor='#555', facecolor='#222')
ax.add_patch(batt)
lbl(0.7, 0.5, '9V', fs=13, bold=True, color='orange')
lbl(1.5, 0.68, '+', fs=11, bold=True, color='red')
lbl(1.5, 0.28, '−', fs=11, bold=True, color='#aaa')

# 9V+ → right → up → relay COM1 (端子4) at x=10.5, y=6.0
wire(2.2, 0.72, 9.8, 0.72, color='darkorange', lw=LW)
wire(9.8, 0.72, 9.8, 6.0, color='darkorange', lw=LW)
wire(9.8, 6.0, 10.5, 6.0, color='darkorange', lw=LW)
lbl(10.1, 5.75, '端子4\nCOM1', ha='right', fs=7)
lbl(9.2, 3.0, '9V (+)', fs=8, color='darkorange', bold=True)

# 9V− → GND rail
wire(0.2, 0.4, 0.0, 0.4)
wire(0.0, 0.4, 0.0, 1.3)
dot(0.0, 1.3)

# ═══════════════════════════════════════════════════════════════
# RELAY BOX  KS2E-M-DC5
# ═══════════════════════════════════════════════════════════════
relay_bg = mpatches.FancyBboxPatch((10.5, 3.8), 7.2, 9.7,
    boxstyle='square,pad=0', linewidth=2.5,
    edgecolor='#cc6600', facecolor='#fff8ee')
ax.add_patch(relay_bg)
lbl(14.1, 13.3, 'RELAY  KS2E-M-DC5  (DPDT  5V)', fs=10, bold=True, color='#cc6600')

# ── Relay Coil ──
coil_rect = mpatches.FancyBboxPatch((12.5, 12.2), 2.0, 0.8,
    boxstyle='square,pad=0', linewidth=LW,
    edgecolor='black', facecolor='#ffffcc')
ax.add_patch(coil_rect)
lbl(13.5, 12.62, 'Relay Coil', fs=8.5)

# 端子16 (top of coil) → 5V rail
wire(13.5, 13.0, 13.5, 13.5)
dot(13.5, 13.5)
lbl(14.0, 13.1, '端子16', ha='left', fs=7)

# 端子1 (bottom of coil) ← Q1 collector connects here
wire(13.5, 12.2, 13.5, 11.8)   # short wire down from coil bottom
lbl(14.0, 12.1, '端子1', ha='left', fs=7)
dot(13.5, 13.8)  # junction at top (Q1 collector wire meets 5V going through)

# D1 flyback across coil (vertical, right side)
wire(14.7, 12.2, 14.7, 13.0)   # vertical wire right of coil
diode_v(14.7, 12.2, 13.0, 'D1')
wire(14.7, 13.0, 13.5, 13.0)   # top of D1 to coil top...
# Actually D1 should go from 端子1 (coil bottom) to 端子16 (coil top)
# with cathode toward 端子16 (+5V side)
# Let me just draw it as a vertical element on the right side of coil box

# ── Relay Contacts  ──
# COM1 bus (vertical at x=11.5, y=6.0 to y=8.5)
wire(10.5, 6.0, 11.5, 6.0)     # COM1 entry
wire(11.5, 6.0, 11.5, 8.5)     # COM1 bus

# NC1 (端子6) - normally closed (solid line = closed)
wire(11.5, 6.5, 12.0, 6.5)
dot(11.5, 6.5)
wire(12.0, 6.5, 12.5, 6.5)     # closed contact
wire(12.5, 6.5, 13.0, 6.5)
dot(12.0, 6.5); dot(12.5, 6.5)
wire(13.0, 6.5, 14.0, 6.5)
lbl(13.5, 6.2, 'NC1  端子6', fs=7.5)

# NO1 (端子8) - normally open (diagonal arm)
wire(11.5, 8.5, 12.0, 8.5)
dot(11.5, 8.5)
ax.plot([12.0, 12.5], [8.5, 8.9], 'k-', lw=LW)  # open arm
wire(12.5, 8.5, 13.0, 8.5)
dot(12.0, 8.5); dot(12.5, 8.5)
wire(13.0, 8.5, 14.0, 8.5)
lbl(13.5, 8.8, 'NO1  端子8', fs=7.5)

# COM2 bus (vertical at x=11.5, y=10.5 to y=11.5)
wire(10.5, 10.5, 11.5, 10.5)   # COM2 entry
wire(11.5, 10.5, 11.5, 11.5)   # COM2 bus

# NC2 (端子11) - normally closed
wire(11.5, 10.5, 12.0, 10.5)
dot(11.5, 10.5)
wire(12.0, 10.5, 12.5, 10.5)
wire(12.5, 10.5, 13.0, 10.5)
dot(12.0, 10.5); dot(12.5, 10.5)
wire(13.0, 10.5, 14.0, 10.5)
lbl(13.5, 10.2, 'NC2  端子11', fs=7.5)

# NO2 (端子13) - normally open
wire(11.5, 11.5, 12.0, 11.5)
dot(11.5, 11.5)
ax.plot([12.0, 12.5], [11.5, 11.9], 'k-', lw=LW)
wire(12.5, 11.5, 13.0, 11.5)
dot(12.0, 11.5); dot(12.5, 11.5)
wire(13.0, 11.5, 14.0, 11.5)
lbl(13.5, 11.8, 'NO2  端子13', fs=7.5)

# Coil to 端子1 wire connecting Q1 collector path (going through relay box top)
wire(13.5, 11.8, 13.5, 10.8)
wire(13.5, 10.8, 11.3, 10.8)
wire(11.3, 10.8, 11.3, 13.5)
dot(11.3, 13.5)   # junction on 5V rail
# Wait, that doesn't make sense. Let me redo Q1 collector path.

# ═══════════════════════════════════════════════════════════════
# CROSS-CONNECTIONS  (relay outputs → motor, outside relay box)
# ═══════════════════════════════════════════════════════════════
# Motor+ node at (17.8, 9.5)  ← NO1(y=8.5) + NC2(y=10.5)
# Motor- node at (18.2, 7.5)  ← NC1(y=6.5) + NO2(y=11.5)

mx_plus  = 17.8   # x where Motor+ junction is
my_plus  = 9.5    # y where Motor+ junction is
mx_minus = 18.2   # x where Motor- junction is
my_minus = 7.5

# NO1 (14.0, 8.5) → right to (mx_plus, 8.5) → up to Motor+
wire(14.0, 8.5, mx_plus, 8.5)
wire(mx_plus, 8.5, mx_plus, my_plus)
dot(mx_plus, my_plus)
lbl(mx_plus+0.2, my_plus+0.2, '馬達端子2(+)', ha='left', fs=8, color='red', bold=True)

# NC2 (14.0, 10.5) → right to (mx_plus, 10.5) → down to Motor+
wire(14.0, 10.5, mx_plus, 10.5)
wire(mx_plus, 10.5, mx_plus, my_plus)
dot(mx_plus, 10.5)

# NC1 (14.0, 6.5) → right to (mx_minus, 6.5) → up to Motor-
wire(14.0, 6.5, mx_minus, 6.5)
wire(mx_minus, 6.5, mx_minus, my_minus)
dot(mx_minus, my_minus)
lbl(mx_minus+0.2, my_minus-0.2, '馬達端子1(−)', ha='left', fs=8, bold=True)

# NO2 (14.0, 11.5) → right to (mx_minus, 11.5) → down to Motor-
wire(14.0, 11.5, mx_minus, 11.5)
wire(mx_minus, 11.5, mx_minus, my_minus)
dot(mx_minus, 11.5)

# Wire from Motor+ and Motor- nodes to actual motor terminals
wire(mx_plus,  my_plus,  mx_plus,  11.0)  # extend up
wire(mx_plus,  11.0,     20.2, 11.0)      # right to motor+
wire(mx_minus, my_minus, mx_minus, 5.0)   # extend down
wire(mx_minus, 5.0,      20.2, 5.0)       # right to motor-

# ═══════════════════════════════════════════════════════════════
# DC MOTOR
# ═══════════════════════════════════════════════════════════════
motor_circle(20.9, 8.0)
lbl(20.9, 9.1, 'DC Motor', fs=9)

# Motor top terminal (端子2+) at (20.9, 8.7)
wire(20.2, 11.0, 20.9, 11.0)
wire(20.9, 11.0, 20.9, 8.7)
lbl(21.5, 11.0, '端子2\n(+)', ha='left', fs=7, color='red')

# Motor bottom terminal (端子1−) at (20.9, 7.3)
wire(20.2, 5.0, 20.9, 5.0)
wire(20.9, 5.0, 20.9, 7.3)
lbl(21.5, 5.0, '端子1\n(−)', ha='left', fs=7)

# D2 flyback across motor
diode_v(21.5, 7.3, 8.7, 'D2\n1N4007')
wire(21.5, 7.3, 20.9, 7.3)
dot(20.9, 7.3)
wire(21.5, 8.7, 20.9, 8.7)
dot(20.9, 8.7)

# ═══════════════════════════════════════════════════════════════
# FIX Q1 COLLECTOR PATH (needs clean route to relay coil 端子1)
# ═══════════════════════════════════════════════════════════════
# Earlier I drew q1c → up to y=13.8 → right to x=13.5 → down to coil 端子1 at y=12.2
# But relay box top is at y=13.5 and coil is inside at y=12.2-13.0
# The wire at y=13.8 goes ABOVE the relay box top which is fine.
# Let's just make sure the wire visually goes to the bottom of coil rect (端子1 at 13.5, 12.2)
wire(13.5, 13.8, 13.5, 13.0)   # from above relay box down to coil top (端子16)
# Oh wait, I need to rethink.
# 端子16 = coil TOP = connected to 5V (+5V comes IN from the top)
# 端子1 = coil BOTTOM = connected to Q1 collector (current flows OUT through transistor to GND)
#
# Q1 collector should go to 端子1 (coil BOTTOM)
# 5V rail should connect to 端子16 (coil TOP)
#
# My coil box is at y=12.2 to 13.0:
# - 端子16 at y=13.0 (top) → connected to 5V rail at y=13.5 via short wire
# - 端子1  at y=12.2 (bottom) → Q1 collector comes up from below
#
# Q1 collector was drawn going to y=13.8 which is ABOVE the 5V rail. Let me fix this.
# The Q1 collector path should go: (q1c_x, q1c_y) → up → right → (13.5, 12.2)

# ═══════════════════════════════════════════════════════════════
# LEGEND BOX
# ═══════════════════════════════════════════════════════════════
leg = mpatches.FancyBboxPatch((0.2, 2.0), 2.5, 3.5,
    boxstyle='square,pad=0.1', linewidth=1,
    edgecolor='#888', facecolor='#f5f5f5')

# Actually let me place legend bottom-left below Arduino
# Since Arduino box goes y=2.0 to y=13.8, put legend to right of 9V
leg2 = mpatches.FancyBboxPatch((3.0, 0.0), 6.2, 1.1,
    boxstyle='round,pad=0.05', linewidth=1,
    edgecolor='#888', facecolor='#f8f8f8')
ax.add_patch(leg2)
lbl(6.1, 0.82, '元件清單', fs=9, bold=True)
items = [
    'Q1, Q2: NPN 2N2222 / BC547',
    'R1, R2: 1kΩ    D1, D2: 1N4007',
    'Relay: KS2E-M-DC5 (DC 5V DPDT)',
    '電源: 9V (馬達路徑) / USB 5V (Arduino)',
]
for i, it in enumerate(items):
    lbl(3.2, 0.60-i*0.18, it, ha='left', fs=7.5)

plt.tight_layout(pad=0.3)
plt.savefig('/Users/rayopenclaw/ray-agent/circuit.png', dpi=160,
            bbox_inches='tight', facecolor='white')
print("Done")
