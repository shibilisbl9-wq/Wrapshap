"""Option B — Graffiti. Same logo, same pipeline, paint-splatter art direction.

Poured-paint drips along the top edge, a thrown splat behind the wordmark, stencil
headlines and a 'HELLO MY NAME IS'-style sticker for the ownership card.
"""
import json, math, os
import design as A
from paint import splat, drip_band, splat_drips, spray_specks, g

HERE = A.HERE
FONTS = A.FONTS
BLEED = A.BLEED
LOGO_RATIO = A.LOGO_RATIO

TOKENS_B = dict(A.TOKENS)
TOKENS_B.update({
    'Burnt':   ('#B8480A', (10, 78, 100, 8)),     # shadow paint behind the logo
    'Chalk':   ('#F2EFE8', (3, 3, 7, 0)),         # off-white paint
})
C = {k: v[0] for k, v in TOKENS_B.items()}
INK, AMBER, ORANGE, SIGNAL, WHITE, BURNT, CHALK = (C[k] for k in ('Wrap Black', 'Amber', 'Orange', 'Signal', 'White', 'Burnt', 'Chalk'))

STENCIL_CSS = (f"@font-face{{font-family:'Stencil';font-weight:800;src:url('file://{FONTS}/BigShouldersStencil-800.ttf')}}"
               f"@font-face{{font-family:'Stencil';font-weight:900;src:url('file://{FONTS}/BigShouldersStencil-900.ttf')}}"
               ".st{font-family:'Stencil';font-weight:900;text-transform:uppercase;line-height:.88;letter-spacing:.01em}")


DOT = (f'<svg style="display:inline-block;width:.3em;height:.3em;vertical-align:.2em;margin:0 .3em" viewBox="0 0 10 10">'
       f'<circle cx="5" cy="5" r="5" fill="{ORANGE}"/></svg>')          # vector dot: the stencil face has no U+25CF


def paint_grad(gid, y0, y1):
    """Vertical amber -> orange, the logo's own gradient, for poured paint."""
    return (f'<defs><linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="0" y1="{y0}" x2="0" y2="{y1}">'
            f'<stop offset="0" stop-color="{AMBER}"/><stop offset="1" stop-color="{ORANGE}"/></linearGradient></defs>')


def mist(cx, cy, rx, ry, color, op, gid):
    return A.glow(cx, cy, rx, ry, color=color, opacity=op, gid=gid)


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


def page(W, H, bg, svg, html):
    return A.page(W, H, bg, svg, html, extra_css=STENCIL_CSS)


# ---- ENVELOPE -------------------------------------------------------------
def envelope_front():
    tw, th = A.ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, cy, lw = W / 2, b + 72, 96
    svg = [paint_grad('pg', 0, 70)]
    svg.append(mist(cx, cy, 70, 42, ORANGE, 0.16, 'm1'))
    svg.append(g(splat(11, cx - 3, cy + 2, 31, arms=30, droplets=80, specks=170, squash=0.6, tilt=-0.08, arm_len=0.8), BURNT))
    svg.append(g(splat_drips(12, cx - 3, cy + 2, 31 * 0.6, 8, 24), BURNT))
    svg.append(g(drip_band(13, 0, W, 0, b + 5, 17, 40), 'url(#pg)'))
    svg.append(g(splat(14, -2, H - 30, 15, arms=14, droplets=40, specks=90, bias=-0.5, arm_len=0.55), AMBER))
    svg.append(g(splat(15, W + 4, b + 142, 8, arms=10, droplets=26, specks=60, bias=math.pi + 0.3, arm_len=0.6), CHALK))
    svg.append(g(spray_specks(16, 0, 0, W, H, 70, 0.3), ORANGE, 0.8))
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs" style="left:{b}mm;width:{tw}mm;top:{b + 111}mm;text-align:center">
  <div class="st" style="font-size:34pt;color:{WHITE}">Stay wrapped.</div>
  <div class="st" style="font-size:34pt;color:{SIGNAL};margin-top:.8mm">Stay protected.</div>
  <div style="margin-top:3.6mm;font-weight:400;font-size:8.6pt;color:{C['Smoke']}">Invisible protection. Made for your device.</div>
</div>""" + sticker(b + 22, b + 156, tw - 44, 38, -2.5, 11.5, 7.8)
    return W, H, page(W, H, INK, '\n'.join(svg), html)


def envelope_back():
    tw, th = A.ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, cy, lw = W / 2, H / 2 + 4, 100
    svg = [paint_grad('pg', 0, 60)]
    svg.append(mist(cx, cy, 80, 60, ORANGE, 0.18, 'm1'))
    svg.append(g(splat(21, cx, cy, 37, arms=32, droplets=110, specks=260, squash=0.66, arm_len=0.8), BURNT))
    svg.append(g(splat(22, cx + 6, cy - 3, 24, arms=16, droplets=50, specks=90, squash=0.6, arm_len=0.6), ORANGE))
    svg.append(g(splat_drips(23, cx, cy, 37 * 0.66, 9, 44), BURNT))
    svg.append(g(splat_drips(24, cx + 6, cy - 3, 24 * 0.6, 5, 28), ORANGE))
    svg.append(g(drip_band(25, 0, W, 0, b + 3, 13, 26), 'url(#pg)'))
    svg.append(g(spray_specks(26, 0, 0, W, H, 60, 0.3), AMBER, 0.8))
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs st" style="left:{b}mm;width:{tw}mm;bottom:{b + 11}mm;text-align:center;font-size:15pt;color:{WHITE};letter-spacing:.06em">
  Stay wrapped {DOT} Stay protected</div>"""
    return W, H, page(W, H, INK, '\n'.join(svg), html)


# ---- MAT PADS -------------------------------------------------------------
def matpad(tw, th, seed):
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    u = min(tw, th)
    k = u / 163                                    # paint scale relative to the envelope
    wide = tw / th > 1.2
    cx, cy = W / 2, H / 2 - u * 0.01
    lw = u * (0.62 if not wide else 0.76)
    R = u * (0.21 if not wide else 0.25)
    sq = 0.62 if not wide else 0.52
    text_top = H - b - u * 0.055 - u * 0.05
    drip_room = text_top - u * 0.035 - (cy + R * sq * 0.82)
    svg = [paint_grad('pg', 0, u * 0.36)]
    svg.append(mist(cx, cy, R * 2.6, R * 1.6, ORANGE, 0.17, 'm1'))
    svg.append(g(splat(seed, cx, cy, R, arms=36, droplets=130, specks=320, squash=sq, arm_len=0.85 if not wide else 1.05,
                       min_speck=0.1 * k), BURNT))
    svg.append(g(splat(seed + 1, cx + R * 0.2, cy - R * 0.08, R * 0.64, arms=16, droplets=50, specks=90, squash=sq,
                       arm_len=0.6, min_speck=0.1 * k), ORANGE))
    svg.append(g(splat_drips(seed + 2, cx, cy, R * sq, 10, drip_room * 0.85, scale=k), BURNT))
    svg.append(g(splat_drips(seed + 3, cx + R * 0.2, cy - R * 0.08, R * 0.64 * sq, 5, drip_room * 0.5, scale=k), ORANGE))
    svg.append(g(drip_band(seed + 4, 0, W, 0, b + u * 0.022, int(W / (10 * k)) + 4, u * 0.19, scale=k), 'url(#pg)'))
    # accents: amber thrown in from the left edge, chalk flick on the right
    svg.append(g(splat(seed + 5, -u * 0.012, H * 0.6, u * 0.075, arms=16, droplets=46, specks=100, bias=-0.35,
                       arm_len=0.6, min_speck=0.1 * k), AMBER))
    svg.append(g(splat(seed + 6, W + u * 0.012, H * 0.4, u * 0.045, arms=12, droplets=30, specks=70,
                       bias=math.pi + 0.3, arm_len=0.6, min_speck=0.1 * k), CHALK))
    svg.append(g(spray_specks(seed + 9, 0, 0, W, H, int(110 * W * H / (169 * 211) ** 0.5 / 180) + 60, 0.3 * k, 0.06 * k), ORANGE, 0.8))
    size = round(u * 0.05 * 2.8346, 1)
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs st" style="left:{b}mm;width:{tw}mm;bottom:{b + u * 0.055:.2f}mm;text-align:center;font-size:{size}pt;color:{WHITE};letter-spacing:.06em">
  Stay wrapped {DOT} Stay protected</div>"""
    return W, H, page(W, H, INK, '\n'.join(svg), html)


# ---- T-SHIRT --------------------------------------------------------------
def tee_back():
    """Garment art: solid paint only (no mist/transparency), specks >= 0.5 mm so DTG holds them."""
    W, H = 300, 330
    cx, lw = W / 2, 200
    cy = 104
    R = 62
    svg = [g(splat(41, cx, cy, R, arms=32, droplets=110, specks=160, squash=0.64, arm_len=0.75, min_speck=0.45), BURNT),
           g(splat(42, cx + 12, cy - 6, R * 0.62, arms=16, droplets=46, specks=60, squash=0.6, arm_len=0.55, min_speck=0.45), ORANGE),
           g(splat_drips(43, cx, cy, R * 0.64, 9, 70, scale=2.2), BURNT),
           g(splat_drips(44, cx + 12, cy - 6, R * 0.6 * 0.62, 5, 40, scale=2.2), ORANGE)]
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs" style="left:0;width:{W}mm;top:232mm;text-align:center">
  <div class="st" style="font-size:86pt;color:{WHITE}">Stay wrapped.</div>
  <div class="st" style="font-size:86pt;color:{SIGNAL};margin-top:1.5mm">Stay protected.</div>
</div>"""
    return W, H, page(W, H, 'transparent', '\n'.join(svg), html)


def tee_front():
    W, H = 110, 58
    cx, cy, lw = W / 2, H / 2, 90
    svg = g(splat(51, cx, cy + 1, 17, arms=18, droplets=30, specks=30, squash=0.62, arm_len=0.55, min_speck=0.45), BURNT)
    return W, H, page(W, H, 'transparent', svg, A.logo_slot(cx, cy, lw))


# ---- DESIGN SHEET ---------------------------------------------------------
def system_sheet():
    W, H = 420, 297
    m = 16
    lab = f"font-size:6.4pt;color:{C['Label']};line-height:1"
    svg = []
    hx, hy, hw, hh = m, 34, 226, 150
    hcx, hcy, hlw = hx + hw / 2, hy + hh / 2 + 4, 110
    svg.append(f'<defs><clipPath id="hc"><rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="4"/></clipPath></defs>'
               f'<rect x="{hx}" y="{hy}" width="{hw}" height="{hh}" rx="4" fill="{INK}"/>' + paint_grad('pg', hy, hy + 60) +
               f'<g clip-path="url(#hc)">{mist(hcx, hcy, 90, 60, ORANGE, 0.17, "ms")}'
               + g(splat(61, hcx, hcy, 38, arms=30, droplets=110, specks=240, squash=0.64, arm_len=0.8), BURNT)
               + g(splat(62, hcx + 8, hcy - 4, 24, arms=16, droplets=50, specks=80, squash=0.6, arm_len=0.6), ORANGE)
               + g(splat_drips(63, hcx, hcy, 38 * 0.64, 9, 46), BURNT)
               + g(drip_band(64, hx, hx + hw, hy, 5, 26, 34), 'url(#pg)') + '</g>')
    svg.append(f'<line x1="{m}" y1="25" x2="{W - m}" y2="25" stroke="{C["Tick"]}" stroke-width=".25"/>')
    cy0, ch = 196, 81
    cw = (W - 2 * m - 2 * 8) / 3
    for i in range(3):
        x = m + i * (cw + 8)
        svg.append(f'<rect x="{x}" y="{cy0}" width="{cw}" height="{ch}" rx="3.5" fill="{C["Graphite"]}"/>')
    # card demos (each clipped to its card)
    for i in range(3):
        x = m + i * (cw + 8)
        svg.append(f'<defs><clipPath id="c{i}"><rect x="{x}" y="{cy0}" width="{cw}" height="{ch}" rx="3.5"/></clipPath></defs>')
    x1 = m + 12
    svg.append(f'<g clip-path="url(#c0)">' + g(splat(71, x1 + 30, cy0 + 40, 13, arms=18, droplets=40, specks=70, bias=-0.3,
                                                     arm_len=0.7), BURNT) + '</g>')
    x2 = m + cw + 8
    svg.append(paint_grad('pg2', cy0, cy0 + 40)
               + f'<g clip-path="url(#c1)">' + g(drip_band(72, x2, x2 + cw, cy0, 4, 14, 30), 'url(#pg2)') + '</g>')
    sw = []
    names = ['Wrap Black', 'Burnt', 'Orange', 'Amber', 'Signal', 'Chalk']
    for i, nme in enumerate(names):
        hexv, cmyk = TOKENS_B[nme]
        col, row = i % 3, i // 3
        x, y = 256 + col * 50, 40 + row * 50
        border = f"border:.25mm solid {C['Tick']};" if nme == 'Wrap Black' else ''
        sw.append(f"""<div class="abs" style="left:{x}mm;top:{y}mm;width:46mm">
  <div style="height:28mm;border-radius:2.4mm;background:{hexv};{border}"></div>
  <div style="margin-top:2.6mm;font-size:8pt;font-weight:600;color:{WHITE};line-height:1">{nme}</div>
  <div class="mono" style="margin-top:1.8mm;font-size:5.6pt;letter-spacing:.08em;color:{C['Label']};line-height:1.45">{hexv}<br>CMYK {'/'.join(str(v) for v in cmyk)}</div>
</div>""")
    cards = [
        ('02 — Splat', 'Thrown paint behind the wordmark: a Burnt base splat with an Orange splat on top. Tendrils taper and end in beads. Keep the core behind the logo and let the arms break out.'),
        ('03 — Drips', 'Paint poured along the top edge in the logo gradient (Amber → Orange), plus runs dripping from the base of the splat. Drips always fall straight down.'),
        ('04 — Sticker', 'The ownership card is a slap sticker, tilted −2.5°: an Orange band with a stencil header on a white write-on panel. Name and Number rules stay straight enough to write on.'),
    ]
    ctext = []
    for i, (t, body) in enumerate(cards):
        x = m + i * (cw + 8)
        left = x + (68 if i == 0 else 12)
        width = cw - (80 if i == 0 else 24)
        top = cy0 + (14 if i == 0 else 50)
        ctext.append(f"""<div class="abs" style="left:{left}mm;top:{top}mm;width:{width}mm">
  <div class="mono" style="font-size:6.4pt;color:{SIGNAL};line-height:1">{t}</div>
  <div style="margin-top:3mm;font-size:8.2pt;line-height:1.42;color:{C['Label']}">{body}</div></div>""")
    x3 = m + 2 * (cw + 8)
    html = A.logo_slot(hcx, hcy, hlw) + f"""
<div class="abs mono" style="left:{m}mm;top:16mm;{lab}">Wrapshap&nbsp;&nbsp;/&nbsp;&nbsp;Visual system&nbsp;&nbsp;—&nbsp;&nbsp;Option B: Graffiti</div>
<div class="abs mono" style="right:{m}mm;top:16mm;{lab}">v1.0&nbsp;&nbsp;—&nbsp;&nbsp;2026</div>
<div class="abs mono" style="left:{m + 8}mm;top:{hy + hh - 10}mm;font-size:6pt;color:{C['Label']};line-height:1">01 — Splat lockup</div>
<div class="abs mono" style="left:256mm;top:34mm;{lab};color:{SIGNAL}">Colour</div>
{''.join(sw)}
<div class="abs mono" style="left:256mm;top:146mm;{lab};color:{SIGNAL}">Type</div>
<div class="abs" style="left:256mm;top:152mm;width:148mm">
  <div class="st" style="font-size:30pt;color:{WHITE}">Stay wrapped. <span style="color:{SIGNAL}">Stay protected.</span></div>
  <div style="display:flex;gap:10mm;margin-top:4.2mm">
    <div style="font-size:7.4pt;line-height:1.4;color:{C['Label']}"><b style="color:{WHITE};font-weight:600">Big Shoulders Stencil</b> — headlines<br>Black 900, all caps</div>
    <div style="font-size:7.4pt;line-height:1.4;color:{C['Label']}"><b style="color:{WHITE};font-weight:600">Geist</b> — body 400<br>8–10 pt</div>
  </div>
</div>
{''.join(ctext)}
{sticker(x3 + 14, cy0 + 12, cw - 28, 30, -2.5, 9, 6.4)}"""
    return W, H, page(W, H, INK, '\n'.join(svg), html)


def build(names=None):
    os.makedirs(os.path.join(HERE, 'html'), exist_ok=True)
    jobs = []

    def add(name, spec, trim=None, cmyk=True):
        W, H, doc = spec
        p = os.path.join(HERE, 'html', name + '.html')
        open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=trim, cmyk=cmyk))

    add('b-envelope-front', envelope_front(), A.ENV)
    add('b-envelope-back', envelope_back(), A.ENV)
    for i, (tw, th) in enumerate(((250, 250), (350, 350), (400, 225), (800, 450))):
        add(f'b-matpad-{tw}x{th}', matpad(tw, th, 100 + 10 * i if (tw, th) not in ((350, 350), (800, 450)) else 100 + 10 * (i - 1)), (tw, th))
    add('b-tee-back', tee_back(), cmyk=False)
    add('b-tee-front', tee_front(), cmyk=False)
    add('b-design-system', system_sheet())
    json.dump(jobs, open(os.path.join(HERE, 'jobs_b.json'), 'w'), indent=1)
    json.dump(TOKENS_B, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=1)
    print(len(jobs), 'pages')


if __name__ == '__main__':
    build()
