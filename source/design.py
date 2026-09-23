"""Wrapshap visual system — generates mm-accurate HTML pages for every deliverable.

All geometry is in millimetres. Print pages are trim + 3 mm bleed on every side.
Logo slots are empty <div class="logo-slot"> elements; the original vector logo
from the supplied envelope artwork is placed into them afterwards (post.py), so the
brand mark is never redrawn.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'fonts'))
LOGO_RATIO = 219.12 / 79.92          # width / height of the original wordmark
BLEED = 3.0


def lerp_hex(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return '#' + ''.join('%02X' % round(x + (y - x) * t) for x, y in zip(a, b))


# ---- tokens: screen colour + print spec (CMYK %) --------------------------
# post.py swaps every solid use of these RGB values for the exact CMYK spec.
TOKENS = {
    'Wrap Black': ('#0B0B0C', (60, 40, 40, 100)),   # rich black for large solids
    'Ink Text':   ('#111111', (0, 0, 0, 100)),      # small dark type: black only
    'Graphite':   ('#17171A', (70, 60, 55, 85)),
    'Amber':      ('#ECBF30', (10, 18, 90, 0)),     # logo gradient top
    'Orange':     ('#F39200', (0, 50, 100, 0)),     # logo gradient bottom
    'Signal':     ('#F0A616', (5, 36, 96, 0)),      # accent type (amber/orange midpoint)
    'Paper':      ('#F4F2EE', (2, 2, 4, 0)),
    'White':      ('#FFFFFF', (0, 0, 0, 0)),
    'Smoke':      ('#8C8C8C', (0, 0, 0, 55)),       # secondary type on black
    'Label':      ('#A6A6A6', (0, 0, 0, 42)),       # mono labels on black
    'Tick':       ('#5A5A5A', (0, 0, 0, 75)),       # hairline ticks on black
    'Card Text':  ('#555555', (0, 0, 0, 78)),
    'Card Muted': ('#999999', (0, 0, 0, 45)),
    'Card Rule':  ('#C8C8C8', (0, 0, 0, 25)),
}
C = {k: v[0] for k, v in TOKENS.items()}
INK, AMBER, ORANGE, SIGNAL, WHITE = C['Wrap Black'], C['Amber'], C['Orange'], C['Signal'], C['White']


def css_base(w, h):
    faces = []
    for wt in (300, 400, 500, 600, 700, 800):
        faces.append(f"@font-face{{font-family:'Geist';font-weight:{wt};src:url('file://{FONTS}/Geist-{wt}.ttf')}}")
    for wt in (400, 500, 600):
        faces.append(f"@font-face{{font-family:'Geist Mono';font-weight:{wt};src:url('file://{FONTS}/GeistMono-{wt}.ttf')}}")
    return '\n'.join(faces) + f"""
@page {{ size: {w}mm {h}mm; margin: 0 }}
* {{ box-sizing: border-box; margin: 0; padding: 0 }}
html, body {{ width: {w}mm; height: {h}mm; overflow: hidden }}
body {{ position: relative; -webkit-print-color-adjust: exact; print-color-adjust: exact;
       font-family: 'Geist', sans-serif; font-kerning: normal; text-rendering: geometricPrecision; }}
.abs {{ position: absolute }}
.mono {{ font-family: 'Geist Mono', monospace; font-weight: 500; text-transform: uppercase; letter-spacing: .16em; }}
.logo-slot {{ position: absolute }}
svg {{ display: block }}
svg.layer {{ position: absolute; left: 0; top: 0 }}
"""


# ---- the Wrap Halo --------------------------------------------------------
def halo(cx, cy, logo_w, n, step, stroke, pad=None, growth=0.0, a0=0.95, a1=0.04,
         c0=AMBER, c1=ORANGE, radius_k=0.46, fade=None, taper=None, gid='r', blend_bg=None):
    """Concentric offset outlines of a rounded 'device' shape hugging the wordmark.

    Each ring is a true offset of the one inside it (corner radius grows with the
    offset), colour runs amber -> orange and opacity fades outward.
    growth : spacing widens ring by ring for a ripple rhythm.
    fade   : (y0, y1, k) -> below y0 the rings dim to k x their opacity by y1.
    taper  : (w_inner, w_outer) -> stroke width runs inner -> outer instead of opacity
    blend_bg: garment colour -> the fade is baked into solid ink (no transparency on fabric)
             (used for garment printing, where solid ink beats transparency).
    """
    logo_h = logo_w / LOGO_RATIO
    pad = pad if pad is not None else logo_h * 0.34
    w0, h0 = logo_w + pad * 2.2, logo_h + pad * 2
    r0 = h0 * radius_k
    defs, out, off = [], [], 0.0
    for k in range(n):
        t = k / max(1, n - 1)
        w, h, r = w0 + 2 * off, h0 + 2 * off, r0 + off
        op = a0 + (a1 - a0) * (t ** 0.75)
        col = lerp_hex(c0, c1, min(1, t * 1.6))
        sw = stroke if not taper else taper[0] + (taper[1] - taper[0]) * t
        if fade:
            y0, y1, kf = fade
            defs.append(f'<linearGradient id="{gid}{k}" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y1}">'
                        f'<stop offset="0" stop-color="{col}" stop-opacity="{op:.3f}"/>'
                        f'<stop offset="1" stop-color="{col}" stop-opacity="{op * kf:.3f}"/></linearGradient>')
            paint = f'stroke="url(#{gid}{k})"'
        else:
            paint = f'stroke="{col}" stroke-opacity="{op:.3f}"' if not taper else f'stroke="{col}"'
            if blend_bg:
                paint = f'stroke="{lerp_hex(blend_bg, col, op)}"'
        out.append(f'<rect x="{cx - w / 2:.3f}" y="{cy - h / 2:.3f}" width="{w:.3f}" height="{h:.3f}" '
                   f'rx="{r:.3f}" fill="none" {paint} stroke-width="{sw:.3f}"/>')
        off += step * (1 + growth * k)
    return (f'<defs>{"".join(defs)}</defs>' if defs else '') + '\n'.join(out)


def halo_extent(logo_w, n, step, growth, pad=None):
    logo_h = logo_w / LOGO_RATIO
    pad = pad if pad is not None else logo_h * 0.34
    off = sum(step * (1 + growth * k) for k in range(n - 1))
    return logo_w + pad * 2.2 + 2 * off, logo_h + pad * 2 + 2 * off


def glow(cx, cy, rx, ry, color=ORANGE, opacity=0.2, gid='g'):
    return (f'<defs><radialGradient id="{gid}" cx="50%" cy="50%" r="50%">'
            f'<stop offset="0" stop-color="{color}" stop-opacity="{opacity}"/>'
            f'<stop offset=".55" stop-color="{color}" stop-opacity="{opacity * 0.35:.3f}"/>'
            f'<stop offset="1" stop-color="{color}" stop-opacity="0"/></radialGradient></defs>'
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#{gid})"/>')


def ticks(x0, y0, x1, y1, L, stroke, color=None):
    """Precision corner ticks framing a rectangle."""
    color = color or C['Tick']
    s = []
    for x, y, dx, dy in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
        s.append(f'<path d="M{x + dx * L:.3f} {y:.3f} H{x:.3f} V{y + dy * L:.3f}" fill="none" '
                 f'stroke="{color}" stroke-width="{stroke}" stroke-linecap="square"/>')
    return '\n'.join(s)


def page(w, h, bg, svg, html, extra_css=''):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>{css_base(w, h)}
body {{ background: {bg}; }}
{extra_css}
</style></head><body>
<svg class="layer" width="{w}mm" height="{h}mm" viewBox="0 0 {w} {h}" xmlns="http://www.w3.org/2000/svg">
{svg}
</svg>
{html}
</body></html>"""


def logo_slot(cx, cy, w, sid='logo'):
    h = w / LOGO_RATIO
    return f'<div class="logo-slot" id="{sid}" style="left:{cx - w / 2}mm;top:{cy - h / 2}mm;width:{w}mm;height:{h}mm"></div>'


CORNER_COPY = ('Stay wrapped', 'Stay protected', 'Invisible protection', 'Made for your device')


def corner_labels(x0, y0, x1, y1, size_pt, labels=CORNER_COPY, color=None):
    color = color or C['Label']
    tl, tr, bl, br = labels
    st = f"font-size:{size_pt}pt;color:{color};line-height:1"
    return f"""
<div class="abs mono" style="left:{x0}mm;top:{y0}mm;{st}">{tl}</div>
<div class="abs mono" style="right:calc(100% - {x1}mm);top:{y0}mm;text-align:right;{st}">{tr}</div>
<div class="abs mono" style="left:{x0}mm;bottom:calc(100% - {y1}mm);{st}">{bl}</div>
<div class="abs mono" style="right:calc(100% - {x1}mm);bottom:calc(100% - {y1}mm);text-align:right;{st}">{br}</div>"""


def framed(W, H, u):
    """The system frame: ticks + four corner labels, scaled to the short side `u`."""
    b = BLEED
    tm, lm = u * 0.034, u * 0.055               # tick inset, label inset (from trim)
    stroke = round(max(0.25, u * 0.0011), 3)
    svg = ticks(b + tm, b + tm, W - b - tm, H - b - tm, u * 0.02, stroke)
    size = round(max(6.4, u * 0.0155 * 2.8346), 2)
    html = corner_labels(b + lm, b + lm, W - b - lm, H - b - lm, size)
    return svg, html


# ---- ENVELOPE (163 x 205 mm) ----------------------------------------------
ENV = (163, 205)


def envelope_front():
    tw, th = ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, cy, lw = W / 2, b + 66, 88
    svg = glow(cx, cy, 70, 46, gid='gf') + halo(cx, cy, lw, n=24, step=3.1, stroke=0.3, growth=0.035,
                                               fade=(b + 80, b + 120, 0.2), gid='rf')
    m = 14
    card_top, card_h, cw = b + 152, 39, tw - 2 * m
    rule = f"position:absolute;left:21mm;right:6mm;border-bottom:.28mm solid {C['Card Rule']}"
    lab = f"position:absolute;left:6mm;font-size:7.6pt;color:{C['Card Text']};line-height:1"
    html = logo_slot(cx, cy, lw) + f"""
<div class="abs" style="left:{b}mm;width:{tw}mm;top:{b + 106}mm;text-align:center">
  <div style="font-weight:600;font-size:23pt;line-height:1.04;letter-spacing:-.025em;color:{WHITE}">Stay wrapped.</div>
  <div style="font-weight:600;font-size:23pt;line-height:1.04;letter-spacing:-.025em;color:{SIGNAL}">Stay protected.</div>
  <div style="margin-top:4.2mm;font-weight:400;font-size:8.6pt;letter-spacing:.005em;color:{C['Smoke']}">Invisible protection. Made for your device.</div>
</div>
<div class="abs" style="left:{b + m}mm;top:{card_top}mm;width:{cw}mm;height:{card_h}mm;background:{C['Paper']};border-radius:3.2mm">
  <div class="mono" style="position:absolute;left:6mm;top:5.6mm;font-size:6.4pt;line-height:1;color:{C['Ink Text']};display:flex;align-items:center;gap:2.2mm">
    <svg width="2.1mm" height="2.1mm" viewBox="0 0 21 21"><rect width="21" height="21" rx="5" fill="{ORANGE}"/></svg>This device belongs to</div>
  <div class="mono" style="position:absolute;right:6mm;top:5.9mm;font-size:5.6pt;line-height:1;color:{C['Card Muted']};letter-spacing:.14em">Wrapshap</div>
  <div style="{lab};top:17.2mm">Name</div><div style="{rule};top:19.6mm"></div>
  <div style="{lab};top:29.2mm">Number</div><div style="{rule};top:31.6mm"></div>
</div>"""
    return W, H, page(W, H, INK, svg, html)


def envelope_back():
    tw, th = ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    cx, cy, lw = W / 2, H / 2, 92
    svg = glow(cx, cy, 78, 52, gid='gb') + halo(cx, cy, lw, n=30, step=3.1, stroke=0.3, growth=0.03, a1=0.035)
    fsvg, fhtml = framed(W, H, tw)
    return W, H, page(W, H, INK, svg + fsvg, logo_slot(cx, cy, lw) + fhtml)


# ---- MAT PADS -------------------------------------------------------------
def matpad(tw, th):
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    u = min(tw, th)                                   # layout unit = short side
    cx, cy = W / 2, H / 2
    wide = tw / th > 1.2
    lw = u * (0.46 if not wide else 0.60)
    step = u * 0.019
    n = int(math.hypot(tw, th) / 2 / (step * 1.35)) + 2
    stroke = round(max(0.3, u * 0.0013), 3)
    svg = glow(cx, cy, lw * 0.85, lw * 0.55, opacity=0.18, gid='gm')
    svg += halo(cx, cy, lw, n=n, step=step, stroke=stroke, growth=0.03 if not wide else 0.025, a1=0.035)
    fsvg, fhtml = framed(W, H, u)
    return W, H, page(W, H, INK, svg + fsvg, logo_slot(cx, cy, lw) + fhtml)


# ---- DESIGN SYSTEM SHEET (A3 landscape) -----------------------------------
def system_sheet():
    W, H = 420, 297
    m = 16
    g = C['Graphite']
    lab = f"font-size:6.4pt;color:{C['Label']};line-height:1"
    svg = []
    # hero panel with clipped halo
    hx, hy, hw, hh = m, 34, 226, 150
    hcx, hcy, hlw = hx + hw / 2, hy + hh / 2 - 2, 104
    svg.append(f'<defs><clipPath id="hc"><rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="4"/></clipPath></defs>'
               f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="4" fill="{INK}"/>'
               f'<g clip-path="url(#hc)">{glow(hcx, hcy, 84, 54, gid="gs")}'
               f'{halo(hcx, hcy, hlw, n=22, step=3.6, stroke=0.3, growth=0.03, a1=0.05, gid="hs")}</g>')
    svg.append(ticks(hx + 5, hy + 5, hx + hw - 5, hy + hh - 5, 4, 0.25))
    svg.append(f'<line x1="{m}" y1="25" x2="{W - m}" y2="25" stroke="{C["Tick"]}" stroke-width=".25"/>')
    # bottom rule cards
    cy0, ch = 196, 81
    cw = (W - 2 * m - 2 * 8) / 3
    for i in range(3):
        x = m + i * (cw + 8)
        svg.append(f'<rect x="{x}" y="{cy0}" width="{cw}" height="{ch}" rx="3.5" fill="{g}"/>')
    # card 1 diagram: halo construction
    dx, dy = m + 12, cy0 + 16
    dcx, dcy = dx + 32, dy + 26
    for k in range(6):
        off = k * 3.2 * (1 + 0.05 * k)
        w, h = 34 + 2 * off, 14 + 2 * off
        col = lerp_hex(AMBER, ORANGE, min(1, k / 5 * 1.6))
        svg.append(f'<rect x="{dcx - w / 2:.2f}" y="{dcy - h / 2:.2f}" width="{w:.2f}" height="{h:.2f}" rx="{6.5 + off:.2f}" '
                   f'fill="none" stroke="{col}" stroke-opacity="{0.95 - k * 0.16:.2f}" stroke-width=".35"/>')
    svg.append(f'<rect x="{dcx - 17}" y="{dcy - 7}" width="34" height="14" rx="6.5" fill="{AMBER}" fill-opacity=".14"/>')
    # card 2 diagram: frame
    fx, fy = m + cw + 8 + 12, cy0 + 12
    svg.append(ticks(fx, fy, fx + 64, fy + 44, 3, 0.3, C['Label']))
    # card 3: clear-space diagram around the logo slot
    lx0 = m + 2 * (cw + 8) + 12
    llw = 50
    lh = llw / LOGO_RATIO
    cs = lh / 3
    svg.append(f'<rect x="{lx0 + cs}" y="{cy0 + 14 + cs}" width="{llw}" height="{lh}" fill="none" stroke="{C["Tick"]}" stroke-width=".25" stroke-dasharray="1 1"/>'
               f'<rect x="{lx0}" y="{cy0 + 14}" width="{llw + 2 * cs}" height="{lh + 2 * cs}" fill="none" stroke="{ORANGE}" stroke-width=".3"/>')

    sw = []
    names = ['Wrap Black', 'Graphite', 'Amber', 'Orange', 'Signal', 'Paper']
    for i, nme in enumerate(names):
        hexv, cmyk = TOKENS[nme]
        col, row = i % 3, i // 3
        x, y = 256 + col * 50, 40 + row * 50
        border = f"border:.25mm solid {C['Tick']};" if nme in ('Wrap Black',) else ''
        sw.append(f"""<div class="abs" style="left:{x}mm;top:{y}mm;width:46mm">
  <div style="height:28mm;border-radius:2.4mm;background:{hexv};{border}"></div>
  <div style="margin-top:2.6mm;font-size:8pt;font-weight:600;color:{WHITE};line-height:1">{nme}</div>
  <div class="mono" style="margin-top:1.8mm;font-size:5.6pt;letter-spacing:.08em;color:{C['Label']};line-height:1.45">{hexv}<br>CMYK {'/'.join(str(v) for v in cmyk)}</div>
</div>""")
    cards = [
        ('02 — Halo', 'Offset rings around the wordmark. Each ring is a true offset: spacing ≈ 3.5% of logo width, widening ~3% per ring. 0.3 mm stroke (heavier on large formats), amber → orange, opacity 95% → 4%.'),
        ('03 — Frame', 'Precision corner ticks and four Geist Mono labels frame every layout: Stay wrapped · Stay protected · Invisible protection · Made for your device.'),
        ('04 — Logo', 'Always the original wordmark artwork, never redrawn or recoloured. Clear space = ⅓ logo height on every side. Minimum width 25 mm print / 120 px screen.'),
    ]
    ctext = []
    for i, (t, body) in enumerate(cards):
        x = m + i * (cw + 8) + 12
        ctext.append(f"""<div class="abs" style="left:{x + 76 if i < 2 else x}mm;top:{cy0 + (14 if i < 2 else 53)}mm;width:{cw - 88 if i < 2 else cw - 24}mm">
  <div class="mono" style="font-size:6.4pt;color:{SIGNAL};line-height:1">{t}</div>
  <div style="margin-top:3mm;font-size:8.2pt;line-height:1.42;color:{C['Label']}">{body}</div></div>""")
    frame_demo = (f'<div class="abs mono" style="left:{fx + 4}mm;top:{fy + 4}mm;font-size:4.6pt;color:{C["Label"]}">Stay wrapped</div>'
                  f'<div class="abs mono" style="left:{fx + 64 - 40}mm;width:36mm;text-align:right;top:{fy + 4}mm;font-size:4.6pt;color:{C["Label"]}">Stay protected</div>'
                  f'<div class="abs mono" style="left:{fx + 4}mm;top:{fy + 44 - 6.2}mm;font-size:4.6pt;color:{C["Label"]}">Invisible protection</div>'
                  f'<div class="abs mono" style="left:{fx + 64 - 40}mm;width:36mm;text-align:right;top:{fy + 44 - 6.2}mm;font-size:4.6pt;color:{C["Label"]}">Made for your device</div>')
    html = logo_slot(hcx, hcy, hlw, 'logo') + logo_slot(lx0 + cs + llw / 2, cy0 + 14 + cs + lh / 2, llw, 'logo2') + f"""
<div class="abs mono" style="left:{m}mm;top:16mm;{lab}">Wrapshap&nbsp;&nbsp;/&nbsp;&nbsp;Visual system</div>
<div class="abs mono" style="right:{m}mm;top:16mm;{lab}">v1.0&nbsp;&nbsp;—&nbsp;&nbsp;2026</div>
<div class="abs mono" style="left:{m + 10}mm;top:{hy + hh - 12}mm;font-size:6pt;color:{C['Label']};line-height:1">01 — Wrap Halo lockup</div>
<div class="abs mono" style="left:256mm;top:34mm;{lab};color:{SIGNAL}">Colour</div>
{''.join(sw)}
<div class="abs mono" style="left:256mm;top:146mm;{lab};color:{SIGNAL}">Type</div>
<div class="abs" style="left:256mm;top:152mm;width:148mm">
  <div style="font-weight:600;font-size:25pt;letter-spacing:-.025em;line-height:1;color:{WHITE}">Stay wrapped. <span style="color:{SIGNAL}">Stay protected.</span></div>
  <div style="display:flex;gap:10mm;margin-top:4.2mm">
    <div style="font-size:7.4pt;line-height:1.4;color:{C['Label']}"><b style="color:{WHITE};font-weight:600">Geist</b> — display 600, −2.5% tracking<br>body 400, 8–10 pt</div>
    <div style="font-size:7.4pt;line-height:1.4;color:{C['Label']}"><b style="color:{WHITE};font-weight:600">Geist Mono</b> — labels 500<br>all caps, +16% tracking</div>
  </div>
</div>
{''.join(ctext)}
{frame_demo}"""
    return W, H, page(W, H, INK, '\n'.join(svg), html)


def build():
    os.makedirs(os.path.join(HERE, 'html'), exist_ok=True)
    jobs = []

    def add(name, spec, trim=None, cmyk=True):
        W, H, doc = spec
        p = os.path.join(HERE, 'html', name + '.html')
        open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=trim, cmyk=cmyk))

    add('envelope-front', envelope_front(), ENV)
    add('envelope-back', envelope_back(), ENV)
    for tw, th in ((250, 250), (350, 350), (400, 225), (800, 450)):
        add(f'matpad-{tw}x{th}', matpad(tw, th), (tw, th))
    add('design-system', system_sheet())
    json.dump(jobs, open(os.path.join(HERE, 'jobs.json'), 'w'), indent=1)
    json.dump(TOKENS, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=1)
    print(len(jobs), 'pages')


if __name__ == '__main__':
    build()
