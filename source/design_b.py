"""Option B — Graffiti (spray). Same logo, same print pipeline, real spray-can texture.

Three marks, taken from the reference textures:
  * airbrush strokes — solid core dissolving into grain (Amber)
  * sprayed swash — overlapping passes + overspray, with running drips (Chalk), behind the logo
  * dry-brush drag — broken bristle streaks (Orange), under the headline
Textures are 1-bit stipple fields (spray.py) stored per page in tex/<name>.npz; post.py lays
them into the PDF as ImageMasks filled with exact CMYK colours. Type, card, drips and the
logo stay vector on top.
"""
import json, math, os
import numpy as np
import design as A
from paint import drip, spray_specks, g
from spray import Paint

HERE = A.HERE
FONTS = A.FONTS
BLEED = A.BLEED
LOGO_RATIO = A.LOGO_RATIO

TOKENS_B = dict(A.TOKENS)
TOKENS_B.update({'Chalk': ('#F2EFE8', (3, 3, 7, 0))})        # off-white spray paint
C = {k: v[0] for k, v in TOKENS_B.items()}
INK, AMBER, ORANGE, WHITE, CHALK = (C[k] for k in ('Wrap Black', 'Amber', 'Orange', 'White', 'Chalk'))
LAYERS = [['amber', 'Amber'], ['chalk', 'Chalk'], ['orange', 'Orange']]      # draw order, bottom -> top

STENCIL_CSS = (f"@font-face{{font-family:'Stencil';font-weight:900;src:url('file://{FONTS}/BigShouldersStencil-900.ttf')}}"
               ".st{font-family:'Stencil';font-weight:900;text-transform:uppercase;line-height:.88;letter-spacing:.01em}")


def dot(color):
    return (f'<svg style="display:inline-block;width:.3em;height:.3em;vertical-align:.2em;margin:0 .3em" viewBox="0 0 10 10">'
            f'<circle cx="5" cy="5" r="5" fill="{color}"/></svg>')          # vector: the stencil face has no U+25CF


def sticker(x, y, w, h, deg, head_pt, lab_pt, head='This device belongs to'):
    """'HELLO MY NAME IS' style slap sticker with Name / Number write-on lines."""
    band = h * 0.3
    rule = f"position:absolute;left:{w * 0.2:.2f}mm;right:{w * 0.05:.2f}mm;border-bottom:.3mm solid {C['Card Rule']}"
    lab = f"position:absolute;left:{w * 0.05:.2f}mm;font-size:{lab_pt}pt;color:{C['Card Text']};line-height:1;font-weight:500"
    return f"""
<div class="abs" style="left:{x}mm;top:{y}mm;width:{w}mm;height:{h}mm;transform:rotate({deg}deg);transform-origin:50% 50%;
     background:{WHITE};border-radius:3mm;overflow:hidden">
  <div style="position:absolute;left:0;top:0;right:0;height:{band:.2f}mm;background:{ORANGE}"></div>
  <div class="st" style="position:absolute;left:0;right:0;top:{band * 0.5:.2f}mm;transform:translateY(-50%);text-align:center;
       font-size:{head_pt}pt;color:{WHITE};letter-spacing:.04em">{head}</div>
  <div style="{lab};top:{band + (h - band) * 0.34:.2f}mm">Name</div><div style="{rule};top:{band + (h - band) * 0.34 + lab_pt * 0.3:.2f}mm"></div>
  <div style="{lab};top:{band + (h - band) * 0.72:.2f}mm">Number</div><div style="{rule};top:{band + (h - band) * 0.72 + lab_pt * 0.3:.2f}mm"></div>
</div>"""


def page(W, H, svg, html):
    """Foreground only (transparent): background + textures are laid underneath in post.py."""
    return A.page(W, H, 'transparent', svg, html, extra_css=STENCIL_CSS)


def swash_drips(P, x0, x1, n, max_to, w=(0.9, 2.2), seed=0, scale=1.0):
    """Drips hanging from the bottom edge of the chalk swash, never past y = max_to."""
    r = np.random.default_rng(seed)
    out = []
    for x in np.sort(r.uniform(x0, x1, n)):
        y0 = P.bottom_edge('chalk', x, thr=0.9)
        if y0 is None:
            continue
        room = max_to - y0
        if room < 3 * scale:
            continue
        L = max(2.5 * scale, room * r.random() ** 1.4)
        out.append(drip(x, y0 - 0.6 * scale, L, r.uniform(*w) * scale, r.uniform(-0.25, 0.25) * scale))
    return g('\n'.join(out), CHALK)


def save_tex(name, P):
    os.makedirs(os.path.join(HERE, 'tex'), exist_ok=True)
    m = P.finalize()
    np.savez_compressed(os.path.join(HERE, 'tex', name + '.npz'), **{k: m.get(k, np.zeros((P.ny, P.nx), bool)) for k, _ in LAYERS})
    return f'tex/{name}.npz'


# ---- ENVELOPE -------------------------------------------------------------
def envelope_front():
    tw, th = A.ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, cy, lw = W / 2, b + 66, 96
    P = Paint(W, H, 0.12, 301)
    P.stroke('amber', [(-12, 150), (10, 124), (14, 76), (-2, 34), (-14, 20)], 15, pressure=0.95)
    P.stroke('amber', [(104, -12), (146, 6), (165, 52), (160, 96), (184, 120)], 13, pressure=0.95)
    P.stroke('amber', [(110, H + 10), (140, H - 14), (184, H - 22)], 15, pressure=0.7)
    P.swash('chalk', 20, 150, cy, 44, passes=4, tilt=-0.03)
    P.spatter('chalk', cx + 20, cy + 6, 36, 50, 0.14, 1.1)
    brush_y = b + 124
    P.dry_brush('orange', (12, brush_y + 4), (157, brush_y - 3), 33, bend=1.2, dryness=0.45, solid=0.75)
    svg = swash_drips(P, 30, 140, 10, brush_y - 17, seed=302)
    svg += g(spray_specks(303, 0, 0, W, H, 40, 0.25), AMBER, 0.85)
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs" style="left:{b}mm;width:{tw}mm;top:{brush_y - 11.5}mm;text-align:center;transform:rotate(-1.4deg)">
  <div class="st" style="font-size:33pt;color:{C['Ink Text']}">Stay wrapped.</div>
  <div class="st" style="font-size:33pt;color:{C['Ink Text']};margin-top:.8mm">Stay protected.</div>
</div>
<div class="abs" style="left:{b}mm;width:{tw}mm;top:{brush_y + 20}mm;text-align:center;font-weight:400;font-size:8.6pt;color:{C['Smoke']}">
  Invisible protection. Made for your device.</div>""" + sticker(b + 22, b + 158, tw - 44, 37, -2.5, 11.5, 7.8)
    return W, H, page(W, H, svg, html), save_tex('b-envelope-front', P), 0.12


def envelope_back():
    tw, th = A.ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, cy, lw = W / 2, H / 2 - 6, 100
    P = Paint(W, H, 0.12, 311)
    P.stroke('amber', [(-14, 190), (12, 160), (18, 106), (0, 56), (-16, 36)], 17, pressure=0.95)
    P.stroke('amber', [(116, -14), (154, 10), (168, 60), (158, 104), (186, 140)], 14, pressure=0.95)
    P.swash('chalk', 16, 153, cy, 50, passes=5, tilt=0.025)
    P.spatter('chalk', cx - 30, cy + 4, 40, 60, 0.14, 1.2)
    brush_y = H - b - 20
    P.dry_brush('orange', (20, brush_y + 2), (149, brush_y - 2), 15, bristles=90, bend=0.6, dryness=0.45, solid=0.75)
    svg = swash_drips(P, 24, 146, 12, brush_y - 16, seed=312)
    svg += g(spray_specks(313, 0, 0, W, H, 40, 0.25), AMBER, 0.85)
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs st" style="left:{b}mm;width:{tw}mm;top:{brush_y - 3.2}mm;text-align:center;font-size:17pt;color:{C['Ink Text']};letter-spacing:.05em">
  Stay wrapped {dot(C['Ink Text'])} Stay protected</div>"""
    return W, H, page(W, H, svg, html), save_tex('b-envelope-back', P), 0.12


# ---- MAT PADS -------------------------------------------------------------
def matpad(tw, th, seed):
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    u = min(tw, th)
    k = u / 163                                    # scale relative to the envelope
    wide = tw / th > 1.2
    cell = round(0.12 * k, 3)                      # grain grows with the format so it still reads
    cx, cy = W / 2, H / 2 - u * 0.05
    lw = u * (0.6 if not wide else 0.72)
    P = Paint(W, H, cell, seed, k=k)
    if wide:
        P.stroke('amber', [(-0.1 * u, 0.95 * H), (0.12 * u, 0.62 * H), (0.2 * u, 0.3 * H), (0.05 * u, -0.1 * H)], 0.13 * u, pressure=0.95)
        P.stroke('amber', [(W + 0.1 * u, 0.05 * H), (W - 0.14 * u, 0.3 * H), (W - 0.2 * u, 0.7 * H), (W - 0.02 * u, 1.1 * H)], 0.12 * u, pressure=0.95)
        P.stroke('amber', [(0.3 * W, H + 0.08 * u), (0.5 * W, H - 0.06 * u), (0.7 * W, H + 0.06 * u)], 0.09 * u, pressure=0.55)
        sw = (0.22 * W, 0.78 * W)
    else:
        P.stroke('amber', [(-0.1 * u, 0.9 * H), (0.1 * u, 0.62 * H), (0.14 * u, 0.3 * H), (-0.04 * u, 0.05 * H)], 0.11 * u, pressure=0.95)
        P.stroke('amber', [(0.62 * W, -0.08 * u), (0.9 * W, 0.08 * H), (0.97 * W, 0.4 * H), (W + 0.1 * u, 0.62 * H)], 0.1 * u, pressure=0.95)
        sw = (0.1 * W, 0.9 * W)
    P.swash('chalk', sw[0], sw[1], cy, 0.3 * u, passes=5, tilt=-0.02)
    P.spatter('chalk', cx + 0.12 * u, cy + 0.03 * u, 0.24 * u, 70, 0.1 * k, 1.1 * k)
    brush_y = H - b - 0.1 * u
    size = round(u * 0.042 * 2.8346, 1)                      # pt
    text_w = 29 * 0.43 * size * 0.3528                         # mm, ~29 glyphs of condensed stencil
    bx0 = cx - text_w / 2 - 0.07 * u
    solid_to = cx + text_w / 2 + 0.05 * u
    bL = solid_to - bx0 + 0.22 * u
    P.dry_brush('orange', (bx0, brush_y + 0.01 * u), (bx0 + bL, brush_y - 0.01 * u), 0.085 * u,
                bristles=130, bend=0.004 * u, dryness=0.45, solid=(solid_to - bx0) / bL)
    svg = swash_drips(P, sw[0] + 0.05 * u, sw[1] - 0.05 * u, 14, brush_y - 0.1 * u, w=(0.9, 2.3), seed=seed + 1, scale=k)
    svg += g(spray_specks(seed + 2, 0, 0, W, H, 60, 0.25 * k, 0.06 * k), AMBER, 0.85)
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs st" style="left:{b}mm;width:{tw}mm;top:{brush_y - 0.018 * u:.2f}mm;text-align:center;font-size:{size}pt;color:{C['Ink Text']};letter-spacing:.05em">
  Stay wrapped {dot(C['Ink Text'])} Stay protected</div>"""
    return W, H, page(W, H, svg, html), save_tex(f'b-matpad-{tw}x{th}', P), cell


# ---- DESIGN SHEET ---------------------------------------------------------
def system_sheet():
    W, H = 420, 297
    m = 16
    lab = f"font-size:6.4pt;color:{C['Label']};line-height:1"
    P = Paint(W, H, 0.14, 341)
    hx, hy, hw, hh = m, 34, 226, 150
    hcx, hcy, hlw = hx + hw / 2, hy + hh / 2 - 8, 112
    P.stroke('amber', [(hx - 6, hy + hh - 6), (hx + 26, hy + 96), (hx + 30, hy + 40), (hx + 6, hy - 6)], 26)
    P.stroke('amber', [(hx + hw - 70, hy - 6), (hx + hw - 18, hy + 30), (hx + hw - 26, hy + 90), (hx + hw + 8, hy + 130)], 22)
    P.swash('chalk', hx + 42, hx + hw - 42, hcy, 52, passes=5, tilt=-0.02)
    P.dry_brush('orange', (hx + 56, hy + hh - 20), (hx + hw - 56, hy + hh - 23), 16, bristles=90, dryness=0.45, solid=0.75)
    cy0, ch = 196, 81
    cw = (W - 2 * m - 2 * 8) / 3
    P.stroke('amber', [(m + 14, cy0 + 60), (m + 30, cy0 + 26), (m + 62, cy0 + 16)], 16)
    x2 = m + cw + 8
    P.swash('chalk', x2 + 12, x2 + 64, cy0 + 26, 20, passes=3)
    x3 = m + 2 * (cw + 8)
    P.dry_brush('orange', (x3 + 10, cy0 + 26), (x3 + 70, cy0 + 24), 18, bristles=80)
    # clip every texture to its panel: the sheet background stays clean
    keep = np.zeros((P.ny, P.nx), bool)
    for (x, y, w, h) in [(hx, hy, hw, hh)] + [(m + i * (cw + 8), cy0, cw, ch) for i in range(3)]:
        keep[int(y / P.cell):int((y + h) / P.cell), int(x / P.cell):int((x + w) / P.cell)] = True
    for f in P.fields.values():
        f[~keep] = 0
    svg = [f'<rect x="{m + i * (cw + 8)}" y="{cy0}" width="{cw}" height="{ch}" rx="3.5" fill="none" stroke="{C["Tick"]}" stroke-width=".25"/>'
           for i in range(3)]
    svg.append(f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" fill="none" stroke="{C["Tick"]}" stroke-width=".25"/>')
    svg.append(f'<line x1="{m}" y1="25" x2="{W - m}" y2="25" stroke="{C["Tick"]}" stroke-width=".25"/>')
    svg.append(swash_drips(P, hx + 60, hx + hw - 60, 10, hy + hh - 30, seed=342))
    svg.append(swash_drips(P, x2 + 18, x2 + 58, 5, cy0 + 62, w=(0.7, 1.4), seed=343))
    sw = []
    for i, nme in enumerate(['Wrap Black', 'Chalk', 'Amber', 'Orange']):
        hexv, cmyk = TOKENS_B[nme]
        x, y = 256 + (i % 2) * 75, 40 + (i // 2) * 50
        border = f"border:.25mm solid {C['Tick']};" if nme == 'Wrap Black' else ''
        sw.append(f"""<div class="abs" style="left:{x}mm;top:{y}mm;width:71mm">
  <div style="height:28mm;border-radius:2.4mm;background:{hexv};{border}"></div>
  <div style="margin-top:2.6mm;font-size:8pt;font-weight:600;color:{WHITE};line-height:1">{nme}</div>
  <div class="mono" style="margin-top:1.8mm;font-size:5.6pt;letter-spacing:.08em;color:{C['Label']};line-height:1.45">{hexv}<br>CMYK {'/'.join(str(v) for v in cmyk)}</div>
</div>""")
    cards = [
        ('02 — Airbrush', 'Amber strokes with a solid core that dissolves into spray grain. They frame the layout and pass behind everything else.'),
        ('03 — Swash + drips', 'A Chalk swash sprayed in 3–5 passes with overspray. The logo sits on it and drips run straight down from its lower edge.'),
        ('04 — Dry brush', 'An Orange dry-brush drag carries the headline, set in black stencil type. Heavy paint where the brush lands, ragged where it runs dry.'),
    ]
    ctext = []
    for i, (t, body) in enumerate(cards):
        x = m + i * (cw + 8)
        ctext.append(f"""<div class="abs" style="left:{x + 70}mm;top:{cy0 + 12}mm;width:{cw - 80}mm">
  <div class="mono" style="font-size:6.4pt;color:{ORANGE};line-height:1">{t}</div>
  <div style="margin-top:3mm;font-size:8pt;line-height:1.42;color:{C['Label']}">{body}</div></div>""")
    html = A.logo_slot(hcx, hcy, hlw) + f"""
<div class="abs mono" style="left:{m}mm;top:16mm;{lab}">Wrapshap&nbsp;&nbsp;/&nbsp;&nbsp;Visual system&nbsp;&nbsp;—&nbsp;&nbsp;Option B: Graffiti</div>
<div class="abs mono" style="right:{m}mm;top:16mm;{lab}">v2.0&nbsp;&nbsp;—&nbsp;&nbsp;2026</div>
<div class="abs st" style="left:{hx}mm;width:{hw}mm;top:{hy + hh - 26}mm;text-align:center;font-size:15pt;color:{C['Ink Text']};letter-spacing:.05em">
  Stay wrapped {dot(C['Ink Text'])} Stay protected</div>
<div class="abs mono" style="left:256mm;top:34mm;{lab};color:{ORANGE}">Colour</div>
{''.join(sw)}
<div class="abs mono" style="left:256mm;top:146mm;{lab};color:{ORANGE}">Type</div>
<div class="abs" style="left:256mm;top:152mm;width:148mm">
  <div class="st" style="font-size:30pt;color:{WHITE}">Stay wrapped. <span style="color:{ORANGE}">Stay protected.</span></div>
  <div style="display:flex;gap:10mm;margin-top:4.2mm">
    <div style="font-size:7.4pt;line-height:1.4;color:{C['Label']}"><b style="color:{WHITE};font-weight:600">Big Shoulders Stencil</b> — headlines<br>Black 900, all caps</div>
    <div style="font-size:7.4pt;line-height:1.4;color:{C['Label']}"><b style="color:{WHITE};font-weight:600">Geist</b> — body 400<br>8–10 pt</div>
  </div>
</div>
{''.join(ctext)}"""
    return W, H, page(W, H, '\n'.join(svg), html), save_tex('b-design-system', P), 0.14


def build():
    os.makedirs(os.path.join(HERE, 'html'), exist_ok=True)
    jobs = []

    def add(name, spec, trim=None, cmyk=True, bg='Wrap Black'):
        W, H, doc, tex, cell = spec
        p = os.path.join(HERE, 'html', name + '.html')
        open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=trim, cmyk=cmyk, tex=tex, cell=cell, layers=LAYERS, bg=bg))
        print('built', name)

    add('b-envelope-front', envelope_front(), A.ENV)
    add('b-envelope-back', envelope_back(), A.ENV)
    for tw, th in ((250, 250), (350, 350), (400, 225), (800, 450)):
        add(f'b-matpad-{tw}x{th}', matpad(tw, th, 400 if tw == th else 420), (tw, th))
    add('b-design-system', system_sheet())
    json.dump(jobs, open(os.path.join(HERE, 'jobs_b.json'), 'w'), indent=1)
    json.dump(TOKENS_B, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=1)


if __name__ == '__main__':
    build()
