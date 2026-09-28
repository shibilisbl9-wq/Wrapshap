"""Option D — Vibrant/Modern. Same logo, same mm-accurate pipeline, fluid gradient "lava lamp"
shapes standing in for the reference's vibrant-gradient envelope. Only the envelope (front +
back) is built for this option — see README for why.

Colour note: the reference's vibrant option uses a cool blue -> purple -> pink gradient. The
real Wrapshap logo is warm amber-to-orange, so a cool gradient behind it would fight the logo
rather than frame it (the same reasoning as Option C's background choice — see its module
docstring). This keeps the *shape* language of the reference (soft overlapping blob forms,
premium/modern feel) but shifts the gradient warm: Amber -> Orange -> a new Rose accent, so it
reads as one family with the logo instead of a clashing sticker. Rose is a new token, flagged
in the README the same way Option B flagged Chalk.

Blobs are seeded organic polygons (handdrawn.blob: jittered points on a circle, smoothed
through Catmull-Rom), layered with `mix-blend-mode: screen` on the black ground so their
overlaps brighten and blend like coloured light rather than stacking as flat shapes.
"""
import os, json
import numpy as np
import design as A
from handdrawn import blob

HERE = A.HERE
FONTS = A.FONTS
BLEED = A.BLEED
LOGO_RATIO = A.LOGO_RATIO
ENV = A.ENV
TOKENS_D = dict(A.TOKENS)
TOKENS_D['Rose'] = ('#F2545B', (0, 74, 54, 0))          # new: warm accent to extend the amber->orange gradient
C = {k: v[0] for k, v in TOKENS_D.items()}
INK, AMBER, ORANGE, ROSE, WHITE, SMOKE = (C[k] for k in ('Wrap Black', 'Amber', 'Orange', 'Rose', 'White', 'Smoke'))


def grad_defs():
    return f"""<defs>
  <linearGradient id="dg1" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0" stop-color="{AMBER}"/><stop offset="1" stop-color="{ORANGE}"/>
  </linearGradient>
  <linearGradient id="dg2" x1="0" y1="1" x2="1" y2="0">
    <stop offset="0" stop-color="{ORANGE}"/><stop offset="1" stop-color="{ROSE}"/>
  </linearGradient>
  <linearGradient id="dg3" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{ROSE}"/><stop offset="1" stop-color="{AMBER}"/>
  </linearGradient>
</defs>"""


def blob_field(specs, blend='screen'):
    """specs: list of (cx, cy, r, seed, fill, squash). `screen` lights up sparse overlaps
    (the front's corner blobs); a dense, tightly clipped field (the back's band) washes out
    under `screen`, so it takes `normal` instead to keep each blob's colour distinct."""
    out = [grad_defs()]
    op = '0.92' if blend == 'screen' else '1'
    for cx, cy, r, seed, fill, squash in specs:
        d = blob(cx, cy, r, seed, n=10, jitter=0.26, squash=squash)
        out.append(f'<path d="{d}" fill="{fill}" style="mix-blend-mode:{blend}" opacity="{op}"/>')
    return '\n'.join(out)


# ---- ENVELOPE ---------------------------------------------------------------
def envelope_front():
    tw, th = ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, cy, lw = W / 2, H / 2 - 6, 92
    lh = lw / LOGO_RATIO
    svg = blob_field([
        (b - 6, b + 4, 58, 701, 'url(#dg1)', 0.85),
        (W - b + 4, b + 44, 46, 702, 'url(#dg2)', 1.1),
        (b + 6, H - b - 10, 50, 703, 'url(#dg3)', 0.9),
        (W - b - 2, H - b - 30, 62, 704, 'url(#dg2)', 1.15),
    ])
    tag_top = cy + lh / 2 + 10
    card_top, card_h, m = H - b - 47, 33, 14
    cw = tw - 2 * m
    rule = f"position:absolute;left:20mm;right:6mm;border-bottom:.26mm solid {C['Card Rule']}"
    lab = f"position:absolute;left:6mm;font-size:7pt;color:{C['Card Text']};line-height:1"
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs" style="right:{b + 12}mm;top:{b + 16}mm;width:120mm;text-align:right">
  <div style="font-weight:600;font-size:19pt;line-height:1.12;letter-spacing:-.02em;color:{WHITE}">Stay wrapped.<br>Stay protected.</div>
</div>
<div class="abs" style="left:{b}mm;width:{tw}mm;top:{tag_top}mm;text-align:center;font-weight:400;font-size:8.4pt;color:{SMOKE}">
  Invisible protection. Made for your device.</div>
<div class="abs" style="left:{b + m}mm;top:{card_top}mm;width:{cw}mm;height:{card_h}mm;background:{C['Paper']};border-radius:3mm">
  <div class="mono" style="position:absolute;left:5.5mm;top:5mm;font-size:6pt;line-height:1;color:{C['Ink Text']};display:flex;align-items:center;gap:2mm">
    <svg width="2mm" height="2mm" viewBox="0 0 21 21"><rect width="21" height="21" rx="5" fill="url(#dg1)"/></svg>This device belongs to</div>
  <div style="{lab};top:14.6mm">Name</div><div style="{rule};top:16.6mm"></div>
  <div style="{lab};top:23.6mm">Number</div><div style="{rule};top:25.6mm"></div>
</div>"""
    return W, H, A.page(W, H, INK, svg, html)


def envelope_back():
    tw, th = ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    band_h = H * 0.3
    cx, cy, lw = W / 2, band_h + (H - band_h) * 0.42, 96
    lh = lw / LOGO_RATIO
    svg = blob_field([
        (W * 0.08, -H * 0.04, 74, 711, 'url(#dg1)', 1.3),
        (W * 0.46, band_h * 0.24, 66, 712, 'url(#dg2)', 1.35),
        (W * 0.85, band_h * 0.06, 68, 713, 'url(#dg3)', 1.2),
        (W * 0.99, band_h * 0.55, 62, 714, 'url(#dg1)', 1.2),
    ], blend='normal')
    svg = f'<clipPath id="dband"><rect x="0" y="0" width="{W}" height="{band_h}"/></clipPath><g clip-path="url(#dband)">{svg}</g>'
    tag_top = cy + lh / 2 + 12
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs" style="left:{b}mm;width:{tw}mm;top:{tag_top}mm;text-align:center;font-weight:400;font-size:8.4pt;color:{SMOKE}">
  Invisible protection. Made for your device.</div>"""
    return W, H, A.page(W, H, INK, svg, html)


def build():
    os.makedirs(os.path.join(HERE, 'html'), exist_ok=True)
    jobs = []

    def add(name, spec, trim):
        W, H, doc = spec
        p = os.path.join(HERE, 'html', name + '.html')
        open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=trim))
        print('built', name)

    add('d-envelope-front', envelope_front(), ENV)
    add('d-envelope-back', envelope_back(), ENV)
    json.dump(jobs, open(os.path.join(HERE, 'jobs_d.json'), 'w'), indent=1)


if __name__ == '__main__':
    build()
