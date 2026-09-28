"""Option E — Street Pop. Same logo, same mm-accurate pipeline: a fresh take on the reference
image's graffiti/street column, built to match ITS specific layout (headline top-left in plain
bold type, doodles scattered loosely around the logo, paint smears bleeding off two corners),
which differs from the existing Option B (spray-can texture, dry-brush headline stripe) built
earlier from a different, texture-heavy reference. Only the envelope (front + back) is built
for this option — see README for why, and for how this differs from Option B.

Paint smears are the same organic blob shapes as Option D (handdrawn.blob), just squashed flat
and coloured Amber instead of gradient-filled, so they read as a rough painted smear rather than
a soft lava-lamp shape. Doodles (crown, smiley, sparkle, bolt, X marks, arrow) are hand-drawn
via handdrawn.scatter, the same engine as Option C's icon field, with a small, loose count and
a wider size range so they read as scattered marker doodles rather than a dense repeating
pattern.
"""
import os, json
import numpy as np
import design as A
from handdrawn import blob, scatter, ic_crown, ic_smiley, ic_sparkle, ic_bolt, ic_x, ic_arrow

HERE = A.HERE
FONTS = A.FONTS
BLEED = A.BLEED
LOGO_RATIO = A.LOGO_RATIO
ENV = A.ENV
C = {k: v[0] for k, v in A.TOKENS.items()}
INK, AMBER, ORANGE, WHITE, SMOKE = (C[k] for k in ('Wrap Black', 'Amber', 'Orange', 'White', 'Smoke'))

DOODLES = [ic_crown, ic_smiley, ic_sparkle, ic_bolt, ic_x, ic_arrow]
DOODLE_WEIGHTS = [1, 2, 3, 2, 2, 1]


def smear(cx, cy, rx, ry, seed, color=AMBER, rot=0):
    d = blob(0, 0, rx, seed, n=9, jitter=0.34, squash=ry / rx)
    return f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({rot})"><path d="{d}" fill="{color}"/></g>'


# ---- ENVELOPE ---------------------------------------------------------------
def envelope_front():
    tw, th = ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, cy, lw = W / 2, H / 2 - 4, 94
    lh = lw / LOGO_RATIO
    svg = smear(b - 8, b - 4, 46, 20, 801, rot=18)
    svg += smear(W - b + 6, H - b + 2, 56, 24, 802, rot=-24)
    logo_box = (cx - lw / 2 - 10, cy - lh / 2 - 8, cx + lw / 2 + 10, cy + lh / 2 + 10)
    head_box = (b + 4, b + 4, b + 100, b + 42)
    card_top, card_h, m = H - b - 47, 33, 14
    cw = tw - 2 * m
    card_box = (b + m - 4, card_top - 4, b + m + cw + 4, card_top + card_h + 4)
    svg += scatter(W, H, 811, 11, [logo_box, head_box, card_box], AMBER, size=(13, 26), sw_k=0.1,
                   icons=DOODLES, weights=DOODLE_WEIGHTS, pad=0.95)
    svg += scatter(W, H, 812, 4, [logo_box, head_box, card_box], WHITE, size=(10, 16), sw_k=0.11,
                   icons=DOODLES, weights=DOODLE_WEIGHTS, pad=0.95)
    tag_top = cy + lh / 2 + 11
    rule = f"position:absolute;left:20mm;right:6mm;border-bottom:.26mm solid {C['Card Rule']}"
    lab = f"position:absolute;left:6mm;font-size:7pt;color:{C['Card Text']};line-height:1"
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs" style="left:{b + 6}mm;top:{b + 8}mm;width:100mm">
  <div style="font-weight:800;font-size:16pt;line-height:1.12;letter-spacing:-.01em;color:{WHITE}">Stay wrapped.<br>Stay protected.</div>
</div>
<div class="abs" style="left:{b}mm;width:{tw}mm;top:{tag_top}mm;text-align:center;font-weight:400;font-size:8.4pt;color:{SMOKE}">
  Invisible protection. Made for your device.</div>
<div class="abs" style="left:{b + m}mm;top:{card_top}mm;width:{cw}mm;height:{card_h}mm;background:{C['Paper']};border-radius:3mm">
  <div class="mono" style="position:absolute;left:5.5mm;top:5mm;font-size:6pt;line-height:1;color:{C['Ink Text']};display:flex;align-items:center;gap:2mm">
    <svg width="2mm" height="2mm" viewBox="0 0 21 21"><rect width="21" height="21" rx="5" fill="{ORANGE}"/></svg>This device belongs to</div>
  <div style="{lab};top:14.6mm">Name</div><div style="{rule};top:16.6mm"></div>
  <div style="{lab};top:23.6mm">Number</div><div style="{rule};top:25.6mm"></div>
</div>"""
    return W, H, A.page(W, H, INK, svg, html)


def envelope_back():
    tw, th = ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, crown_cy, lw = W / 2, H * 0.3, 92
    lh = lw / LOGO_RATIO
    logo_cy = H * 0.3 + 28
    svg = smear(b - 4, b - 6, 40, 16, 821, rot=22)
    svg += smear(W - b + 2, H - b - 2, 50, 20, 822, rot=-16)
    svg += f'<g transform="translate({cx:.2f} {crown_cy:.2f})">{ic_crown(22, AMBER, 1.4, np.random.default_rng(9))}</g>'
    tag_top = logo_cy + lh / 2 + 14
    html = A.logo_slot(cx, logo_cy, lw) + f"""
<div class="abs mono" style="left:{b}mm;width:{tw}mm;top:{tag_top}mm;text-align:center;font-size:8.4pt;color:{C['Label']}">
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

    add('e-envelope-front', envelope_front(), ENV)
    add('e-envelope-back', envelope_back(), ENV)
    json.dump(jobs, open(os.path.join(HERE, 'jobs_e.json'), 'w'), indent=1)


if __name__ == '__main__':
    build()
