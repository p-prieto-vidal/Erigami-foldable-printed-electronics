import serial
import serial.tools.list_ports
import matplotlib
matplotlib.rcParams.update({
    'font.family':    'sans-serif',
    'font.sans-serif': ['Helvetica Neue', 'Helvetica', 'Arial', 'sans-serif'],
    'font.monospace':  ['Menlo', 'SF Mono', 'Courier New', 'monospace'],
})
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button, TextBox, RadioButtons
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from collections import deque
import numpy as np
import time
import os
import sys

# ─── Design tokens ────────────────────────────────────────
BG      = '#0E0E0E'
PANEL   = '#141412'
INPUTBG = '#1C1C1E'
GRAPHBG = '#0A0A0A'
BORDER  = '#2A2825'
IBORDER = '#3A3A3C'
TEXT    = '#E8E4DC'
TEXT2   = '#6B6760'
TEXT3   = '#38342F'
GREEN   = '#2E6B45'
PURPLE  = '#534AB7'
AMBER   = '#C9811F'
RED     = '#A32D2D'
GRID    = '#1A1A18'
BEIGE3D = '#F5F0E8'


def _btn(ax, label, fc=PANEL, hc='#1C1C1A', lc=TEXT, fs=9):
    b = Button(ax, label, color=fc, hovercolor=hc)
    b.label.set_color(lc)
    b.label.set_fontsize(fs)
    b.label.set_fontfamily('sans-serif')
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER); sp.set_linewidth(0.5)
    return b


def _field(ax, initial=''):
    tb = TextBox(ax, '', initial=initial, color=INPUTBG, hovercolor='#222220')
    tb.text_disp.set_color(TEXT)
    tb.text_disp.set_fontfamily('monospace')
    tb.text_disp.set_fontsize(10)
    for sp in ax.spines.values():
        sp.set_edgecolor(IBORDER); sp.set_linewidth(0.5)
    return tb


# ── Output folder ──────────────────────────────────────────
OUTPUT_DIR = os.path.expanduser('~/Desktop/DEMODAY/OUTPUT')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Auto-detect Arduino port ───────────────────────────────
_ARDUINO_KEYWORDS = ('arduino', 'usbmodem', 'usbserial', 'ch340', 'cp210', 'ftdi', 'wch')

def detect_arduino_port():
    candidates = [
        p.device for p in serial.tools.list_ports.comports()
        if any(kw in (p.description or '').lower() or
               kw in (p.manufacturer or '').lower() or
               kw in p.device.lower()
               for kw in _ARDUINO_KEYWORDS)
    ]
    return candidates[0] if candidates else None

# ── Global state ───────────────────────────────────────────
_FOLD_TYPES = ('Single Crease', 'Accordion', 'Water Bomb', 'Kirigami', 'Miura Ori')

config = {
    'PORT':      detect_arduino_port() or '',
    'R_REF':     330.0,
    'R0':        None,
    'name':      '',
    'fold_type': _FOLD_TYPES[0],
    'ser':       None,
    'r0_auto':   False,
}

def reset_measurement():
    global datos, tiempos, grabando, t_inicio, ciclo_actual
    global marcas_ciclo, eventos_abierto, ultimo_estado_abierto
    datos                 = deque(maxlen=600)
    tiempos               = deque(maxlen=600)
    grabando              = False
    t_inicio              = None
    ciclo_actual          = 0
    marcas_ciclo          = []
    eventos_abierto       = []
    ultimo_estado_abierto = False

reset_measurement()
ani_ref = [None]


# ════════════════════════════════════════════════════════
#  SCREEN 1 — CONFIGURATION
# ════════════════════════════════════════════════════════
def screen_config():
    reset_measurement()

    fig_cfg = plt.figure(figsize=(9, 8.0), facecolor=BG)
    fig_cfg.canvas.manager.set_window_title('Setup — Resistance Monitor')

    # Header
    fig_cfg.text(0.5, 0.945, 'RESISTANCE MONITOR', ha='center',
                 color=TEXT, fontsize=17, fontweight='light')
    fig_cfg.text(0.5, 0.906, 'Ailarian Sea Silver Ink  ·  Voltera V-One  ·  TU/e',
                 ha='center', color=TEXT2, fontsize=9)

    ax_sep = fig_cfg.add_axes([0.08, 0.882, 0.84, 0.001])
    ax_sep.set_facecolor(BORDER); ax_sep.axis('off')

    # ── Circuit ───────────────────────────────────────────
    fig_cfg.text(0.10, 0.850, 'C I R C U I T', color=TEXT2, fontsize=7.5, alpha=0.7)

    fig_cfg.text(0.10, 0.798, 'Reference Resistor (Ω)', color=TEXT2, fontsize=10)
    ax_rref = fig_cfg.add_axes([0.42, 0.764, 0.48, 0.046])
    tb_rref = _field(ax_rref, initial=str(config['R_REF']))

    ax_sep2 = fig_cfg.add_axes([0.08, 0.724, 0.84, 0.001])
    ax_sep2.set_facecolor(BORDER); ax_sep2.axis('off')

    # ── Sample ────────────────────────────────────────────
    fig_cfg.text(0.10, 0.604, 'S A M P L E', color=TEXT2, fontsize=7.5, alpha=0.7)

    # Fold type — two columns
    _3D_TYPES  = ('Single Crease', 'Miura Ori')
    _RES_TYPES = ('Accordion', 'Water Bomb', 'Kirigami')
    _ft        = config['fold_type']
    _in_3d     = _ft in _3D_TYPES
    _active_3d  = list(_3D_TYPES).index(_ft)  if _in_3d     else 0
    _active_res = list(_RES_TYPES).index(_ft) if not _in_3d else 0

    # Left column — 3D
    fig_cfg.text(0.10, 0.572, '3D Live Folding', color=GREEN, fontsize=8.5)
    ax_left = fig_cfg.add_axes([0.10, 0.440, 0.37, 0.118])
    ax_left.set_facecolor(PANEL)
    for sp in ax_left.spines.values():
        sp.set_edgecolor(BORDER); sp.set_linewidth(0.5)
    radio_left = RadioButtons(ax_left, _3D_TYPES, active=_active_3d, activecolor=GREEN)
    for lbl in radio_left.labels:
        lbl.set_color(TEXT); lbl.set_fontsize(10)
    fig_cfg.text(0.10, 0.424, 'includes real-time 3D model',
                 color=GREEN, fontsize=7.5, style='italic', alpha=0.55)

    # Right column — resistance only
    fig_cfg.text(0.53, 0.572, 'Resistance Only', color=TEXT2, fontsize=8.5)
    ax_right = fig_cfg.add_axes([0.53, 0.426, 0.37, 0.132])
    ax_right.set_facecolor(PANEL)
    for sp in ax_right.spines.values():
        sp.set_edgecolor(BORDER); sp.set_linewidth(0.5)
    radio_right = RadioButtons(ax_right, _RES_TYPES, active=_active_res, activecolor=PURPLE)
    for lbl in radio_right.labels:
        lbl.set_color(TEXT); lbl.set_fontsize(10)
    fig_cfg.text(0.53, 0.410, 'full-width graph',
                 color=TEXT2, fontsize=7.5, style='italic', alpha=0.55)

    def _deselect_all(radio_widget):
        try:
            bg = radio_widget.ax.get_facecolor()
            for c in radio_widget.circles:
                c.set_facecolor(bg)
        except AttributeError:
            pass
        radio_widget.ax.figure.canvas.draw_idle()

    if _in_3d:
        _deselect_all(radio_right)
    else:
        _deselect_all(radio_left)

    def _on_left_type(label):
        config['fold_type'] = label
        _deselect_all(radio_right)

    def _on_right_type(label):
        config['fold_type'] = label
        _deselect_all(radio_left)

    radio_left.on_clicked(_on_left_type)
    radio_right.on_clicked(_on_right_type)

    # R0
    fig_cfg.text(0.10, 0.382, 'Flat-paper Resistance R₀ (Ω)', color=TEXT2, fontsize=10)
    ax_r0 = fig_cfg.add_axes([0.42, 0.348, 0.30, 0.046])
    tb_r0 = _field(ax_r0, initial=str(config['R0']) if config['R0'] else '')
    ax_bmr0 = fig_cfg.add_axes([0.74, 0.348, 0.14, 0.046])
    btn_mr0 = _btn(ax_bmr0, 'AUTO 5 s', fc='#0E1E0E', hc='#142014', lc=GREEN, fs=8.5)
    fig_cfg.text(0.10, 0.328, 'enter manually  or  connect paper flat and press AUTO 5 s',
                 color=TEXT3, fontsize=7.5, style='italic')

    # Sample name
    fig_cfg.text(0.10, 0.268, 'Sample Name', color=TEXT2, fontsize=10)
    ax_name = fig_cfg.add_axes([0.42, 0.234, 0.48, 0.046])
    tb_name = _field(ax_name, initial=config['name'])

    # Status + connect button
    txt_status = fig_cfg.text(0.5, 0.172, '', ha='center', color=RED, fontsize=9)

    ax_btn = fig_cfg.add_axes([0.08, 0.058, 0.84, 0.082])
    btn_start = _btn(ax_btn, 'CONNECT  &  START', fc='#0E1E0E', hc='#142014',
                     lc=GREEN, fs=13)
    for sp in ax_btn.spines.values():
        sp.set_edgecolor(GREEN); sp.set_linewidth(0.8)

    # Callbacks
    def ensure_connected():
        try:
            config['R_REF'] = float(tb_rref.text.strip())
        except:
            txt_status.set_text('R_REF must be a number (e.g. 330)')
            txt_status.set_color(RED)
            fig_cfg.canvas.draw()
            return False
        if config['ser'] and config['ser'].is_open:
            return True
        port = detect_arduino_port()
        if port is None:
            txt_status.set_text('Arduino not found — check USB connection')
            txt_status.set_color(RED)
            fig_cfg.canvas.draw()
            return False
        config['PORT'] = port
        txt_status.set_text('Connecting to Arduino…')
        txt_status.set_color(AMBER)
        fig_cfg.canvas.draw(); plt.pause(0.1)
        try:
            config['ser'] = serial.Serial(config['PORT'], 9600, timeout=1)
            time.sleep(2)
            txt_status.set_text('Arduino connected')
            txt_status.set_color(GREEN)
            fig_cfg.canvas.draw()
            return True
        except Exception as e:
            txt_status.set_text(f'Connection failed: {e}')
            txt_status.set_color(RED)
            fig_cfg.canvas.draw()
            return False

    def on_measure_r0(event):
        if not ensure_connected():
            return
        ser_tmp  = config['ser']
        readings = []
        DURATION = 5.0
        t_start  = time.time()
        while time.time() - t_start < DURATION:
            remaining = DURATION - (time.time() - t_start)
            txt_status.set_text(
                f'Measuring R₀ — keep paper flat  ·  {remaining:.1f} s remaining')
            txt_status.set_color(AMBER)
            fig_cfg.canvas.draw(); plt.pause(0.05)
            try:
                raw = ser_tmp.readline().decode('utf-8').strip()
                if 'R_muestra' in raw:
                    r = float(raw.split('R_muestra:')[1].replace('ohm', '').strip())
                    if r < 9000:
                        readings.append(r)
            except:
                pass
        if not readings:
            txt_status.set_text('No valid readings — check paper connections')
            txt_status.set_color(RED)
            fig_cfg.canvas.draw()
            return
        r_min  = min(readings)
        r_mean = sum(readings) / len(readings)
        r_max  = max(readings)
        r_std  = (sum((x - r_mean)**2 for x in readings) / len(readings)) ** 0.5
        config['R0']      = r_min
        config['r0_auto'] = True
        tb_r0.set_val(f'{r_min:.2f}')
        txt_status.set_text(
            f'R₀ = {r_min:.2f} Ω  (min)   mean {r_mean:.2f}   '
            f'max {r_max:.2f}   σ {r_std:.2f}   n = {len(readings)}')
        txt_status.set_color(GREEN)
        fig_cfg.canvas.draw()

    btn_mr0.on_clicked(on_measure_r0)

    def on_start(event):
        config['name'] = tb_name.text.strip() or 'Sample'
        if not ensure_connected():
            return
        ser_tmp  = config['ser']
        readings = []
        DURATION = 5.0
        t_start  = time.time()
        while time.time() - t_start < DURATION:
            remaining = DURATION - (time.time() - t_start)
            txt_status.set_text(
                f'Measuring R₀ — keep paper flat  ·  {remaining:.1f} s remaining')
            txt_status.set_color(AMBER)
            fig_cfg.canvas.draw(); plt.pause(0.05)
            try:
                raw = ser_tmp.readline().decode('utf-8').strip()
                if 'R_muestra' in raw:
                    r = float(raw.split('R_muestra:')[1].replace('ohm', '').strip())
                    if r < 9000:
                        readings.append(r)
            except:
                pass
        if not readings:
            txt_status.set_text('No valid readings — check paper connections')
            txt_status.set_color(RED)
            fig_cfg.canvas.draw()
            return
        config['R0']      = min(readings)
        config['r0_auto'] = True
        txt_status.set_text(f'R₀ = {config["R0"]:.2f} Ω  ·  opening graph…')
        txt_status.set_color(GREEN)
        fig_cfg.canvas.draw(); plt.pause(0.3)
        plt.close(fig_cfg)
        screen_graph()

    btn_start.on_clicked(on_start)
    plt.show()


# ════════════════════════════════════════════════════════
#  SCREEN 2 — LIVE GRAPH + 3D FOLD MODEL
# ════════════════════════════════════════════════════════
def screen_graph():
    global grabando, t_inicio, ciclo_actual, marcas_ciclo
    global eventos_abierto, ultimo_estado_abierto

    reset_measurement()

    ser       = config['ser']
    R_REF     = config['R_REF']
    R0        = config['R0']
    name      = config['name']
    fold_type = config.get('fold_type', '')
    HAS_3D    = fold_type in ('Single Crease', 'Miura Ori')

    fig = plt.figure(figsize=(20, 7) if HAS_3D else (14, 7), facecolor=BG)
    fig.canvas.manager.set_window_title(f'Live — {name}  [{fold_type}]')

    # ── Resistance graph ──────────────────────────────────
    ax = fig.add_axes([0.04, 0.18, 0.43, 0.72] if HAS_3D else [0.06, 0.18, 0.90, 0.72])
    ax.set_facecolor(GRAPHBG)
    ax.set_title(f'{name}  —  {fold_type}', color=TEXT2, fontsize=9,
                 pad=10, fontweight='normal')
    ax.set_ylabel('Ω', color=TEXT2, fontsize=11)
    ax.set_xlabel('Time (s)', color=TEXT2, fontsize=9)
    ax.tick_params(colors=TEXT2, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color(BORDER); spine.set_linewidth(0.5)
    ax.grid(True, color=GRID, linewidth=0.4, alpha=0.8)

    linea, = ax.plot([], [], color=GREEN, linewidth=1.5, zorder=3)

    # Fixed R0 — purple dashed
    if R0:
        ax.axhline(y=R0, color=PURPLE, linewidth=0.8, linestyle='--', alpha=0.6, zorder=2)
        label_r0 = (' R₀ initial = {:.2f}  [auto]' if config.get('r0_auto')
                    else ' R₀ initial = {:.2f}').format(R0)
        ax.text(0.01, R0, label_r0, color=PURPLE, fontsize=7.5, va='bottom',
                transform=ax.get_yaxis_transform())

    # Rolling R0 — amber dashed, y updated each frame
    _rr0_init  = R0 if R0 else 200.0
    line_rr0, = ax.plot([0, 1], [_rr0_init, _rr0_init], color=AMBER,
                        linewidth=0.8, linestyle='--', alpha=0.65, zorder=2,
                        transform=ax.get_yaxis_transform())
    txt_r0_roll = ax.text(0.01, _rr0_init, f' R₀ cycle min = {_rr0_init:.1f}',
                          color=AMBER, fontsize=7.5, va='top',
                          transform=ax.get_yaxis_transform())

    _n_perm_lines = len(ax.lines)

    # Overlaid text — Apple Health style
    txt_r = ax.text(0.03, 0.96, '', transform=ax.transAxes,
                    color=TEXT, fontsize=22, fontweight='bold',
                    fontfamily='monospace', va='top')
    ax.text(0.03, 0.84, 'dR / R₀', transform=ax.transAxes,
            color=TEXT3, fontsize=7.5, va='baseline')
    txt_dr_total = ax.text(0.03, 0.80, '', transform=ax.transAxes,
                           color='#8888E8', fontsize=10.5, fontfamily='monospace')
    txt_dr_cycle = ax.text(0.03, 0.72, '', transform=ax.transAxes,
                           color=AMBER, fontsize=10.5, fontfamily='monospace')
    ax.text(0.03, 0.64, f'R_REF = {R_REF:.0f} Ω', transform=ax.transAxes,
            color=TEXT3, fontsize=8, fontfamily='monospace')

    # Status badge (right side) — iOS pill style via bbox
    txt_est = ax.text(0.98, 0.96, '', transform=ax.transAxes,
                      color=GREEN, fontsize=8.5, ha='right', va='top',
                      bbox=dict(boxstyle='round,pad=0.4',
                                fc=(0.18, 0.42, 0.27, 0.12),
                                ec=GREEN, lw=0.5))
    txt_ciclo = ax.text(0.98, 0.84, '', transform=ax.transAxes,
                        color=PURPLE, fontsize=10, ha='right', fontfamily='monospace')
    txt_gaps  = ax.text(0.98, 0.74, '', transform=ax.transAxes,
                        color=RED, fontsize=8.5, ha='right')

    open_spans = []
    open_start = [None]

    # Rolling R0 state
    rolling_R0             = [R0 if R0 else None]
    rolling_r0_win         = deque()   # resistance samples in current 3 s epoch
    rolling_r0_epoch_start = [None]    # wall-clock time the current epoch began
    rolling_r0_hist        = deque(maxlen=600)
    cycle_R_max            = [R0 if R0 else None]  # max R since last baseline update
    r_window_10s           = deque()   # (wall_time, resistance) — last 10 s
    smoothed_fold_pct      = [0.5]     # exponentially smoothed fold %

    # ── 3D panel ─────────────────────────────────────────
    if HAS_3D:
        ax3d = fig.add_axes([0.52, 0.06, 0.46, 0.88], projection='3d')
        azimuth = [30]
        INK     = GREEN

        def _style_3d():
            ax3d.set_facecolor('#090909')
            ax3d.xaxis.pane.fill = False
            ax3d.yaxis.pane.fill = False
            ax3d.zaxis.pane.fill = False
            ax3d.xaxis.pane.set_edgecolor(BORDER)
            ax3d.yaxis.pane.set_edgecolor(BORDER)
            ax3d.zaxis.pane.set_edgecolor(BORDER)
            ax3d.tick_params(colors=TEXT3, labelsize=6)
            ax3d.set_xlabel(''); ax3d.set_ylabel(''); ax3d.set_zlabel('')
            ax3d.set_title(fold_type, color=TEXT2, fontsize=9,
                           pad=4, fontweight='normal')

        def _floor_grid(xlim, ylim):
            for gx in np.linspace(xlim[0], xlim[1], 7):
                ax3d.plot3D([gx, gx], [ylim[0], ylim[1]], [0, 0],
                            color=GRID, linewidth=0.35, alpha=0.7, zorder=1)
            for gy in np.linspace(ylim[0], ylim[1], 5):
                ax3d.plot3D([xlim[0], xlim[1]], [gy, gy], [0, 0],
                            color=GRID, linewidth=0.35, alpha=0.7, zorder=1)

        def _draw_single_crease(fold_pct, window_min, window_max):
            angle_deg = 180.0 - fold_pct * 170.0
            half      = np.radians(angle_deg / 2.0)
            w, h      = 1.2, 1.5
            lx = -w * np.sin(half);  lz = w * np.cos(half)
            rx =  w * np.sin(half)

            left_v  = np.array([[0,0,0],[0,h,0],[lx,h,lz],[lx,0,lz]])
            right_v = np.array([[0,0,0],[0,h,0],[rx,h,lz],[rx,0,lz]])
            pc = Poly3DCollection([left_v, right_v], alpha=0.82, zorder=2)
            pc.set_facecolor([BEIGE3D, BEIGE3D])
            pc.set_edgecolor('#B0A898'); pc.set_linewidth(0.4)
            ax3d.add_collection3d(pc)

            mid = h / 2
            ax3d.plot3D([0,lx],[mid,mid],[0,lz], color=INK, linewidth=2.2, zorder=3)
            ax3d.plot3D([0,rx],[mid,mid],[0,lz], color=INK, linewidth=2.2, zorder=3)

            ax3d.set_xlim(-w*1.15, w*1.15)
            ax3d.set_ylim(-0.2, h+0.2)
            ax3d.set_zlim(-0.05, w+0.1)
            _floor_grid((-w*1.15, w*1.15), (-0.2, h+0.2))
            _win = (f'Window  {window_min:.0f} — {window_max:.0f} Ω'
                    if window_min is not None else '— waiting for data —')
            ax3d.text2D(0.5, 0.08, _win,
                        transform=ax3d.transAxes, ha='center', color=TEXT3, fontsize=8)
            ax3d.text2D(0.5, 0.02, f'Fold angle  {angle_deg:.0f}°',
                        transform=ax3d.transAxes, ha='center', color=TEXT2, fontsize=10)

        def _draw_miura_ori(fold_pct, window_min, window_max):
            compression = 1.0 - fold_pct * 0.7
            ROWS, COLS  = 2, 3
            a, b        = 0.8, 0.6
            fold_z_max  = 0.55
            fold_z      = (1.0 - compression) / 0.7 * fold_z_max

            verts = np.zeros((ROWS+1, COLS+1, 3))
            for i in range(ROWS+1):
                for j in range(COLS+1):
                    verts[i,j,0] = j * a * compression
                    verts[i,j,1] = i * b
                    verts[i,j,2] = fold_z * ((i+j) % 2)

            faces = [
                [verts[i,j], verts[i,j+1], verts[i+1,j+1], verts[i+1,j]]
                for i in range(ROWS) for j in range(COLS)
            ]
            pc = Poly3DCollection(faces, alpha=0.82, zorder=2)
            pc.set_facecolor(BEIGE3D)
            pc.set_edgecolor('#B0A898'); pc.set_linewidth(0.6)
            ax3d.add_collection3d(pc)

            ax3d.set_xlim(-0.1, COLS*a+0.1)
            ax3d.set_ylim(-0.1, ROWS*b+0.1)
            ax3d.set_zlim(-0.05, fold_z_max+0.1)
            _floor_grid((-0.1, COLS*a+0.1), (-0.1, ROWS*b+0.1))
            _win = (f'Window  {window_min:.0f} — {window_max:.0f} Ω'
                    if window_min is not None else '— waiting for data —')
            ax3d.text2D(0.5, 0.08, _win,
                        transform=ax3d.transAxes, ha='center', color=TEXT3, fontsize=8)
            ax3d.text2D(0.5, 0.02, f'Compression  {compression*100:.0f}%',
                        transform=ax3d.transAxes, ha='center', color=TEXT2, fontsize=10)

        def refresh_3d(r_val):
            now = time.time()
            r_window_10s.append((now, r_val))
            while r_window_10s and now - r_window_10s[0][0] > 10.0:
                r_window_10s.popleft()

            vals = [v for _, v in r_window_10s]
            window_min = min(vals)
            window_max = max(vals)
            if window_max == window_min:
                raw_fold_pct = 0.5
            else:
                raw_fold_pct = min(max((r_val - window_min) / (window_max - window_min), 0.0), 1.0)

            smoothed_fold_pct[0] = smoothed_fold_pct[0] * 0.75 + raw_fold_pct * 0.25
            spct = smoothed_fold_pct[0]

            ax3d.cla()
            _style_3d()
            if fold_type == 'Miura Ori':
                _draw_miura_ori(spct, window_min, window_max)
            else:
                _draw_single_crease(1.0 - spct, window_min, window_max)
            ax3d.view_init(elev=22, azim=azimuth[0])
            azimuth[0] = (azimuth[0] + 1) % 360

        def draw_neutral_3d():
            ax3d.cla()
            _style_3d()
            if fold_type == 'Miura Ori':
                _draw_miura_ori(0.0, None, None)
            else:
                _draw_single_crease(0.0, None, None)
            ax3d.view_init(elev=22, azim=azimuth[0])

        draw_neutral_3d()

    else:
        def refresh_3d(r_val):
            pass
        def draw_neutral_3d():
            pass

    # ── Buttons ───────────────────────────────────────────
    if HAS_3D:
        ax_bg = fig.add_axes([0.04, 0.03, 0.07, 0.09])
        ax_bc = fig.add_axes([0.12, 0.03, 0.09, 0.09])
        ax_bl = fig.add_axes([0.22, 0.03, 0.07, 0.09])
        ax_bs = fig.add_axes([0.30, 0.03, 0.08, 0.09])
        ax_bm = fig.add_axes([0.39, 0.03, 0.09, 0.09])
        _fs = 8
    else:
        ax_bg = fig.add_axes([0.06, 0.03, 0.12, 0.09])
        ax_bc = fig.add_axes([0.20, 0.03, 0.14, 0.09])
        ax_bl = fig.add_axes([0.36, 0.03, 0.12, 0.09])
        ax_bs = fig.add_axes([0.50, 0.03, 0.13, 0.09])
        ax_bm = fig.add_axes([0.65, 0.03, 0.22, 0.09])
        _fs = 9

    btn_grab  = _btn(ax_bg, 'START',       fc='#0E1E0E', hc='#142014', lc=GREEN,  fs=_fs)
    btn_cycle = _btn(ax_bc, 'MARK CYCLE',  fc=PANEL,     hc='#1A1A28', lc=PURPLE, fs=_fs)
    btn_clear = _btn(ax_bl, 'CLEAR',       fc=PANEL,     hc='#1C1C1A', lc=TEXT2,  fs=_fs)
    btn_save  = _btn(ax_bs, 'SAVE CSV',    fc='#1A1005', hc='#221808', lc=AMBER,  fs=_fs)
    btn_menu  = _btn(ax_bm, 'NEW SAMPLE',  fc=PANEL,     hc='#1C1C1A', lc=TEXT2,  fs=_fs)

    def toggle_record(event):
        global grabando, t_inicio
        grabando = not grabando
        if grabando:
            if t_inicio is None:
                t_inicio = time.time()
            btn_grab.label.set_text('STOP')
            btn_grab.label.set_color(RED)
            ax_bg.set_facecolor('#1E0A0A')
        else:
            btn_grab.label.set_text('START')
            btn_grab.label.set_color(GREEN)
            ax_bg.set_facecolor('#0E1E0E')

    def mark_cycle(event):
        global ciclo_actual
        if not grabando or not datos:
            return
        ciclo_actual += 1
        x = tiempos[-1]; r = datos[-1]
        marcas_ciclo.append((x, r))
        ax.axvline(x=x, color=PURPLE, linewidth=0.6, linestyle=':', alpha=0.5)
        ax.text(x, ax.get_ylim()[1] * 0.95, f' {ciclo_actual}',
                color=PURPLE, fontsize=7.5, va='top')
        txt_ciclo.set_text(f'Cycle {ciclo_actual}')
        print(f"  Cycle {ciclo_actual} — t={x:.1f}s  R={r:.1f} Ω")

    def clear_data(event):
        global ciclo_actual, marcas_ciclo, t_inicio
        global eventos_abierto, ultimo_estado_abierto
        datos.clear(); tiempos.clear()
        ciclo_actual = 0; marcas_ciclo = []
        t_inicio = None; eventos_abierto = []
        ultimo_estado_abierto = False; open_start[0] = None
        rolling_R0[0] = R0 if R0 else None
        rolling_r0_win.clear(); rolling_r0_hist.clear()
        rolling_r0_epoch_start[0] = None
        cycle_R_max[0] = R0 if R0 else None
        rr0_reset = rolling_R0[0] if rolling_R0[0] else _rr0_init
        line_rr0.set_ydata([rr0_reset, rr0_reset])
        txt_r0_roll.set_y(rr0_reset)
        txt_r0_roll.set_text(f' R₀ cycle min = {rr0_reset:.1f}')
        linea.set_data([], [])
        r_window_10s.clear()
        smoothed_fold_pct[0] = 0.5
        for t in [txt_r, txt_dr_total, txt_dr_cycle, txt_ciclo, txt_gaps]:
            t.set_text('')
        txt_est.set_text('')
        draw_neutral_3d()
        for sp in open_spans:
            try: sp.remove()
            except: pass
        open_spans.clear()
        while len(ax.lines) > _n_perm_lines:
            ax.lines[-1].remove()

    def save_csv(event):
        ts    = time.strftime('%Y%m%d_%H%M%S')
        fname = os.path.join(OUTPUT_DIR, f'{name}_{ts}.csv')
        def is_open(t):
            return any(ta <= t <= tb for ta, tb in eventos_abierto)
        with open(fname, 'w') as f:
            f.write(f'# Sample: {name}\n')
            f.write(f'# Origami type: {fold_type}\n')
            f.write(f'# R_REF circuit: {R_REF} ohm\n')
            f.write(f'# R0 flat paper: {R0:.4f} ohm\n' if R0 else '# R0: not defined\n')
            f.write(f'# R0 method: 5s auto-measurement (minimum)\n' if config.get('r0_auto') else '# R0 method: manual entry\n')
            f.write(f'# Open-circuit threshold: dynamic (5x max measured, min 5x R0)\n')
            f.write(f'# Open-circuit events: {len(eventos_abierto)}\n')
            for i, (ta, tb) in enumerate(eventos_abierto):
                f.write(f'#   gap {i+1}: {ta:.2f}s - {tb:.2f}s  ({tb-ta:.2f}s)\n')
            f.write('time_s,resistance_ohm,rolling_R0,dR_R0_total,dR_R0_cycle,open_circuit\n')
            for t, r, rr0 in zip(tiempos, datos, rolling_r0_hist):
                dr_total = f'{(r - R0)  / R0:.4f}'  if R0  else 'n/a'
                dr_cycle = f'{(r - rr0) / rr0:.4f}' if rr0 else 'n/a'
                rr0_str  = f'{rr0:.2f}'              if rr0 else 'n/a'
                oc       = '1' if is_open(t) else '0'
                f.write(f'{t:.3f},{r:.2f},{rr0_str},{dr_total},{dr_cycle},{oc}\n')
        ax.set_title(f'{name}  —  saved', color=GREEN, fontsize=9)
        print(f"  Saved: {fname}")

    def go_to_menu(event):
        if ani_ref[0] is not None:
            ani_ref[0].event_source.stop()
        plt.close(fig)
        screen_config()

    btn_grab.on_clicked(toggle_record)
    btn_cycle.on_clicked(mark_cycle)
    btn_clear.on_clicked(clear_data)
    btn_save.on_clicked(save_csv)
    btn_menu.on_clicked(go_to_menu)

    def status_badge(dr_abs):
        if dr_abs < 0.3:
            return 'EXCELLENT',  GREEN,  (0.180, 0.420, 0.271, 0.13)
        if dr_abs < 0.7:
            return 'ACCEPTABLE', AMBER,  (0.788, 0.506, 0.122, 0.13)
        if dr_abs < 1.0:
            return 'MARGINAL',   '#E08020', (0.878, 0.502, 0.125, 0.13)
        return     'FAIL',       RED,    (0.639, 0.176, 0.176, 0.13)

    def update(frame):
        global grabando, ultimo_estado_abierto, eventos_abierto
        try:
            raw = ser.readline().decode('utf-8').strip()
            if not raw or 'R_muestra' not in raw:
                return linea, txt_r, txt_dr_total, txt_dr_cycle, txt_est, txt_ciclo, txt_gaps

            r     = float(raw.split('R_muestra:')[1].replace('ohm', '').strip())
            ahora = time.time() - t_inicio if t_inicio else 0

            r_base    = R0 if R0 else 200.0
            r_max_val = max(datos) if datos else r_base
            umbral_oc = max(r_base, r_max_val) * 5.0
            circuito_abierto = (r > umbral_oc)

            if not grabando:
                txt_est.set_text('PAUSED')
                txt_est.set_color(TEXT2)
                txt_est.set_bbox(dict(boxstyle='round,pad=0.4',
                                      fc=(0.10, 0.10, 0.10, 0.6), ec=TEXT2, lw=0.5))
                return linea, txt_r, txt_dr_total, txt_dr_cycle, txt_est, txt_ciclo, txt_gaps

            if circuito_abierto and not ultimo_estado_abierto:
                open_start[0] = ahora
                ultimo_estado_abierto = True
                txt_est.set_text('OPEN CIRCUIT')
                txt_est.set_color(RED)
                txt_est.set_bbox(dict(boxstyle='round,pad=0.4',
                                      fc=(0.639, 0.176, 0.176, 0.13), ec=RED, lw=0.5))
                print(f"  Open circuit at t={ahora:.1f}s")

            elif not circuito_abierto and ultimo_estado_abierto:
                t_end   = ahora
                t_start = open_start[0] if open_start[0] else ahora
                eventos_abierto.append((t_start, t_end))
                span = ax.axvspan(t_start, t_end, color=RED, alpha=0.08, zorder=1)
                mid  = (t_start + t_end) / 2
                ax.text(mid, ax.get_ylim()[1] * 0.88,
                        f'OPEN\n{t_end - t_start:.1f}s',
                        color=RED, fontsize=7, ha='center', va='top',
                        bbox=dict(boxstyle='round,pad=0.25',
                                  fc=(0.639, 0.176, 0.176, 0.12),
                                  ec=RED, lw=0.5))
                open_spans.append(span)
                open_start[0] = None
                ultimo_estado_abierto = False
                txt_gaps.set_text(f'Open-circuit events: {len(eventos_abierto)}')
                print(f"  Restored at t={t_end:.1f}s  (gap: {t_end - t_start:.1f}s)")

            if circuito_abierto:
                return linea, txt_r, txt_dr_total, txt_dr_cycle, txt_est, txt_ciclo, txt_gaps

            t = ahora
            datos.append(r); tiempos.append(t)

            # 3-second epoch minimum — update rolling_R0 only if epoch min < current
            if rolling_r0_epoch_start[0] is None:
                rolling_r0_epoch_start[0] = t
            rolling_r0_win.append(r)
            if t - rolling_r0_epoch_start[0] >= 3.0:
                epoch_min = min(rolling_r0_win)
                if rolling_R0[0] is None or epoch_min < rolling_R0[0]:
                    rolling_R0[0] = epoch_min
                    cycle_R_max[0] = r   # reset cycle range at every new baseline
                    line_rr0.set_ydata([epoch_min, epoch_min])
                    txt_r0_roll.set_y(epoch_min)
                    txt_r0_roll.set_text(f' R₀ cycle min = {epoch_min:.1f}')
                rolling_r0_win.clear()
                rolling_r0_epoch_start[0] = t
            rr0 = rolling_R0[0] if rolling_R0[0] is not None else r
            rolling_r0_hist.append(rr0)
            if cycle_R_max[0] is None or r > cycle_R_max[0]:
                cycle_R_max[0] = r

            xs = list(tiempos); ys = list(datos)
            linea.set_data(xs, ys)
            ax.set_xlim(max(0, t - 60), t + 2)
            ax.set_ylim(0, max(ys) * 1.25 if ys else 10)
            txt_r.set_text(f'{r:.1f} Ω')

            refresh_3d(r)

            if R0:
                dr_total = (r - R0) / R0
                s_t = '+' if dr_total >= 0 else ''
                txt_dr_total.set_text(
                    f'total   {s_t}{dr_total:.4f}   ({s_t}{r - R0:.1f} Ω)')
                dr_cycle = (r - rr0) / rr0
                s_c = '+' if dr_cycle >= 0 else ''
                txt_dr_cycle.set_text(
                    f'cycle   {s_c}{dr_cycle:.4f}   ({s_c}{r - rr0:.1f} Ω)')
                label, fg, bg = status_badge(abs(dr_total))
                txt_est.set_text(label)
                txt_est.set_color(fg)
                txt_est.set_bbox(dict(boxstyle='round,pad=0.4', fc=bg, ec=fg, lw=0.5))
            else:
                dr_cycle = (r - rr0) / rr0 if rr0 else 0.0
                s_c = '+' if dr_cycle >= 0 else ''
                txt_dr_cycle.set_text(f'cycle   {s_c}{dr_cycle:.4f}')
                txt_est.set_text('RECORDING')
                txt_est.set_color(GREEN)
                txt_est.set_bbox(dict(boxstyle='round,pad=0.4',
                                      fc=(0.18, 0.42, 0.27, 0.12), ec=GREEN, lw=0.5))

            if eventos_abierto:
                txt_gaps.set_text(f'Open-circuit events: {len(eventos_abierto)}')

        except Exception:
            pass
        return linea, txt_r, txt_dr_total, txt_dr_cycle, txt_est, txt_ciclo, txt_gaps

    ani_ref[0] = animation.FuncAnimation(
        fig, update, interval=300, blit=False, cache_frame_data=False)
    plt.show()
    try: ser.close()
    except: pass


# ── Launch ────────────────────────────────────────────────
screen_config()
