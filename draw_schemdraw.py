import schemdraw
import schemdraw.elements as elm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

matplotlib.rcParams['font.family'] = ['Hiragino Sans', 'DejaVu Sans']

fig = plt.figure(figsize=(24, 16), facecolor='white')
ax = fig.add_subplot(111)
ax.set_facecolor('white')

with schemdraw.Drawing(canvas=ax, fontsize=9) as d:
    d.config(unit=2.8, fontsize=9)

    # ══════════════════════════════════════════════════
    #  RELAY IC BOX  (anchor 'center' at (14, 7))
    # ══════════════════════════════════════════════════
    relay = d.add(elm.Ic(
        pins=[
            elm.IcPin('COM1\n端子4',  side='left',  pin='4',  anchorname='com1'),
            elm.IcPin('COM2\n端子9',  side='left',  pin='9',  anchorname='com2'),
            elm.IcPin('Coil+\n端子16',side='left',  pin='16', anchorname='coilp'),
            elm.IcPin('Coil-\n端子1', side='left',  pin='1',  anchorname='coiln'),
            elm.IcPin('NC1\n端子6',   side='right', pin='6',  anchorname='nc1'),
            elm.IcPin('NO1\n端子8',   side='right', pin='8',  anchorname='no1'),
            elm.IcPin('NC2\n端子11',  side='right', pin='11', anchorname='nc2'),
            elm.IcPin('NO2\n端子13',  side='right', pin='13', anchorname='no2'),
        ],
        edgepadW=0.8, edgepadH=0.5,
        pinspacing=1.5,
        name='RELAY\nKS2E-M-DC5\n(DPDT 5V)',
        fontsize=10,
    ).at((14, 7)).anchor('center'))

    # ══════════════════════════════════════════════════
    #  5V and GND rails (reference lines)
    # ══════════════════════════════════════════════════
    # Get relay pin positions to align rails
    coilp_pos = relay.coilp   # Coil+ connects to 5V
    coiln_pos = relay.coiln   # Coil- connects to Q1 collector

    # 5V rail: horizontal line above circuit
    rail5v_y = coilp_pos[1]
    d.add(elm.Line().at((-1, rail5v_y)).right(3.5).color('red').linewidth(2))
    d.add(elm.Label().at((-1.3, rail5v_y)).label('+5V', loc='left').color('red'))

    # Connect 5V rail to Coil+ (端子16)
    d.add(elm.Line().at((2.5, rail5v_y)).right().to(coilp_pos).color('red'))

    # GND rail
    gnd_y = -4.5
    d.add(elm.Line().at((-1, gnd_y)).right(26).color('#444').linewidth(2))
    d.add(elm.Label().at((-1.3, gnd_y)).label('GND', loc='left').color('#444'))

    # ══════════════════════════════════════════════════
    #  Q1 : D6 → R1 → Q1 (relay coil driver)
    # ══════════════════════════════════════════════════
    # R1 starts at x=2, y=coiln_pos[1]-1
    q1_y = coiln_pos[1]

    R1 = d.add(elm.Resistor().at((2, q1_y)).right()
               .label('R1\n1kΩ', loc='top'))

    Q1 = d.add(elm.BjtNpn(circle=True).anchor('base').at(R1.end))

    # Q1 collector → up → Coil- (端子1)
    d.add(elm.Line().at(Q1.collector).up()
          .to((Q1.collector[0], coiln_pos[1])))
    d.add(elm.Line().right().to(coiln_pos))

    # Q1 emitter → down → GND
    d.add(elm.Line().at(Q1.emitter).down()
          .to((Q1.emitter[0], gnd_y)))
    d.add(elm.Dot().at((Q1.emitter[0], gnd_y)))

    # D6 label (Arduino pin)
    d.add(elm.Label().at((2, q1_y)).label('D6  →', loc='left'))

    # ══════════════════════════════════════════════════
    #  D1 flyback across relay coil
    # ══════════════════════════════════════════════════
    # Draw D1 vertically between coiln and coilp (left of relay box)
    d1_x = coiln_pos[0] - 0.6
    d.add(elm.Diode().at((d1_x, coiln_pos[1])).up()
          .to((d1_x, coilp_pos[1]))
          .label('D1', loc='right').color('navy'))
    d.add(elm.Line().at((d1_x, coiln_pos[1])).right()
          .to(coiln_pos))
    d.add(elm.Dot().at(coiln_pos))
    d.add(elm.Line().at((d1_x, coilp_pos[1])).right()
          .to(coilp_pos))
    d.add(elm.Dot().at(coilp_pos))

    # ══════════════════════════════════════════════════
    #  Q2 : D5 → R2 → Q2 (motor speed PWM)
    # ══════════════════════════════════════════════════
    com2_pos = relay.com2
    q2_y = com2_pos[1]

    R2 = d.add(elm.Resistor().at((2, q2_y)).right()
               .label('R2\n1kΩ', loc='top'))

    Q2 = d.add(elm.BjtNpn(circle=True).anchor('base').at(R2.end))

    # Q2 collector → right → COM2 (端子9)
    d.add(elm.Line().at(Q2.collector).up()
          .to((Q2.collector[0], com2_pos[1])))
    d.add(elm.Line().right().to(com2_pos))

    # Q2 emitter → down → GND
    d.add(elm.Line().at(Q2.emitter).down()
          .to((Q2.emitter[0], gnd_y)))
    d.add(elm.Dot().at((Q2.emitter[0], gnd_y)))

    d.add(elm.Label().at((2, q2_y)).label('D5(PWM)  →', loc='left'))

    # ══════════════════════════════════════════════════
    #  BUTTONS  D2 / D3 / D4
    # ══════════════════════════════════════════════════
    btn_data = [
        ('D2  →\n(正轉)', -0.5),
        ('D3  →\n(反轉)', -1.8),
        ('D4  →\n(停止)', -3.1),
    ]
    for lbl_text, btn_y in btn_data:
        d.add(elm.Label().at((2, btn_y)).label(lbl_text, loc='left'))
        btn = d.add(elm.Button().at((2, btn_y)).right())
        d.add(elm.Line().right(0.3))
        d.add(elm.Line().down().to((btn.end[0]+0.3, gnd_y)))
        d.add(elm.Dot().at((btn.end[0]+0.3, gnd_y)))

    # ══════════════════════════════════════════════════
    #  9V POWER → COM1 (端子4)
    # ══════════════════════════════════════════════════
    com1_pos = relay.com1
    # 9V source symbol (voltage source going up = positive at top)
    v9 = d.add(elm.SourceV().at((-0.5, gnd_y + 1.2)).up()
               .label('9V', loc='right').label('+', loc='top').label('−', loc='bot'))
    # 9V+ wire → COM1
    d.add(elm.Line().at(v9.end).right()
          .to((com1_pos[0], v9.end[1])))
    d.add(elm.Line().up().to(com1_pos))

    # 9V− → GND rail
    d.add(elm.Line().at(v9.start).down()
          .to((-0.5, gnd_y)))
    d.add(elm.Dot().at((-0.5, gnd_y)))

    # ══════════════════════════════════════════════════
    #  RELAY OUTPUTS → MOTOR
    #  Cross-connections:  NO1+NC2 → Motor(+)
    #                      NC1+NO2 → Motor(-)
    # ══════════════════════════════════════════════════
    nc1_pos = relay.nc1
    no1_pos = relay.no1
    nc2_pos = relay.nc2
    no2_pos = relay.no2

    motor_x = 22
    motor_plus_y  = (no1_pos[1] + nc2_pos[1]) / 2
    motor_minus_y = (nc1_pos[1] + no2_pos[1]) / 2

    # NO1 → right → junction at (motor_x-1, motor_plus_y)
    jx_p = motor_x - 1.5
    d.add(elm.Line().at(no1_pos).right().to((jx_p, no1_pos[1])))
    d.add(elm.Line().up().to((jx_p, motor_plus_y)))
    d.add(elm.Dot().at((jx_p, motor_plus_y)))

    # NC2 → right → same junction
    d.add(elm.Line().at(nc2_pos).right().to((jx_p, nc2_pos[1])))
    d.add(elm.Line().down().to((jx_p, motor_plus_y)))

    # Junction → Motor+
    d.add(elm.Line().at((jx_p, motor_plus_y)).right()
          .to((motor_x, motor_plus_y)))

    # NC1 → right → junction at (motor_x-0.8, motor_minus_y)
    jx_m = motor_x - 0.8
    d.add(elm.Line().at(nc1_pos).right().to((jx_m, nc1_pos[1])))
    d.add(elm.Line().up().to((jx_m, motor_minus_y)))
    d.add(elm.Dot().at((jx_m, motor_minus_y)))

    # NO2 → right → same junction
    d.add(elm.Line().at(no2_pos).right().to((jx_m, no2_pos[1])))
    d.add(elm.Line().down().to((jx_m, motor_minus_y)))

    # Junction → Motor-
    d.add(elm.Line().at((jx_m, motor_minus_y)).right()
          .to((motor_x, motor_minus_y)))

    # ══════════════════════════════════════════════════
    #  MOTOR  (custom circle element)
    # ══════════════════════════════════════════════════
    motor_cy = (motor_plus_y + motor_minus_y) / 2
    motor_r = 1.0
    mc = plt.Circle((motor_x + motor_r, motor_cy), motor_r,
                     fill=False, edgecolor='black', linewidth=2.0, zorder=5)
    ax.add_patch(mc)
    ax.text(motor_x + motor_r, motor_cy, 'M', ha='center', va='center',
            fontsize=16, fontweight='bold', zorder=6)
    ax.text(motor_x + motor_r, motor_cy + motor_r + 0.3, 'DC Motor',
            ha='center', va='bottom', fontsize=9)
    # Motor terminal wires (short stubs from motor circle to the junction wires)
    ax.plot([motor_x, motor_x + motor_r - motor_r*0.7],
            [motor_plus_y, motor_cy + motor_r*0.7], 'k-', lw=1.8)
    ax.plot([motor_x, motor_x + motor_r - motor_r*0.7],
            [motor_minus_y, motor_cy - motor_r*0.7], 'k-', lw=1.8)

    # D2 flyback across motor
    d2_x = motor_x + 2 * motor_r + 0.5
    d.add(elm.Diode().at((d2_x, motor_minus_y)).up()
          .to((d2_x, motor_plus_y))
          .label('D2\n1N4007', loc='right').color('navy'))
    d.add(elm.Line().at((d2_x, motor_minus_y)).left()
          .to((motor_x + 2*motor_r, motor_minus_y)))
    d.add(elm.Line().at((d2_x, motor_plus_y)).left()
          .to((motor_x + 2*motor_r, motor_plus_y)))

    # ══════════════════════════════════════════════════
    #  LABELS for cross-connections
    # ══════════════════════════════════════════════════
    ax.text(jx_p - 0.1, motor_plus_y + 0.2,
            'NO1 + NC2 → 馬達端子2(+)',
            fontsize=8, color='red', ha='right',
            fontfamily='Hiragino Sans')
    ax.text(jx_m - 0.1, motor_minus_y - 0.25,
            'NC1 + NO2 → 馬達端子1(−)',
            fontsize=8, color='#333', ha='right',
            fontfamily='Hiragino Sans')

    # ══════════════════════════════════════════════════
    #  ARDUINO BOX  (decorative, behind the pin labels)
    # ══════════════════════════════════════════════════
    # Find y range for Arduino pins
    all_pin_y = [q1_y, q2_y] + [y for _, y in btn_data]
    box_ymin = min(all_pin_y) - 0.8
    box_ymax = rail5v_y + 0.5
    ard_box = mpatches.FancyBboxPatch((-1.8, box_ymin), 3.5, box_ymax - box_ymin,
                                       boxstyle='round,pad=0.2',
                                       linewidth=2, edgecolor='#1a3a8a',
                                       facecolor='#d4e8ff', zorder=0, alpha=0.7)
    ax.add_patch(ard_box)
    ax.text(-0.05, box_ymax + 0.15, 'Arduino Uno',
            ha='center', fontsize=10, fontweight='bold', color='#1a3a8a',
            fontfamily='Hiragino Sans')

    # ══════════════════════════════════════════════════
    #  TITLE
    # ══════════════════════════════════════════════════
    ax.text(10, box_ymax + 1.0,
            'Arduino 直流馬達正反轉控制電路',
            ha='center', fontsize=14, fontweight='bold',
            fontfamily='Hiragino Sans')
    ax.text(10, box_ymax + 0.4,
            'DPDT 繼電器方向切換  +  NPN 電晶體 PWM 速度控制',
            ha='center', fontsize=10, color='#555',
            fontfamily='Hiragino Sans')

ax.autoscale()
ax.axis('off')
plt.tight_layout(pad=0.5)
plt.savefig('/Users/rayopenclaw/ray-agent/circuit_schemdraw.png',
            dpi=160, bbox_inches='tight', facecolor='white')
print("schemdraw PNG done")
