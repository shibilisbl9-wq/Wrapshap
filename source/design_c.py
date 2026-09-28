"""Option C — Icon Pattern. Same logo, same mm-accurate pipeline, a scattered field of
hand-drawn device icons (phone, laptop, bolt, crown, smiley, sparkle, "W" mark) standing in
for the reference's icon-pattern envelope. Only the envelope (front + back) is built for this
option — see README for why.

The reference's front used a bright yellow ground under a monochrome wordmark; the real
Wrapshap logo is amber/orange with a white-and-orange rim, so it goes on the same Amber ground
here and the rim still separates it from the field. The back inverts the idea: the pattern
sits tone-on-tone on Wrap Black, quiet enough to read as texture rather than noise, with a
small hand-drawn crown standing in for a seal above the logo.

Icons are placed by seeded rejection sampling (numpy only, no shapely/fontTools): candidates
are rolled until enough land outside the keep-out zones around the logo, headline and card,
and clear of icons already placed.
"""
import os, json
import numpy as np
import design as A
from handdrawn import ic_crown, scatter

HERE = A.HERE
FONTS = A.FONTS
BLEED = A.BLEED
LOGO_RATIO = A.LOGO_RATIO
ENV = A.ENV
TOKENS_C = dict(A.TOKENS)
C = {k: v[0] for k, v in TOKENS_C.items()}
INK, AMBER, ORANGE, WHITE, GRAPHITE = (C[k] for k in ('Wrap Black', 'Amber', 'Orange', 'White', 'Graphite'))


# ---- ENVELOPE ---------------------------------------------------------------
def envelope_front():
    tw, th = ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, cy, lw = W / 2, b + 63, 86
    lh = lw / LOGO_RATIO
    head_top, tag_top = b + 104, b + 104 + 27.5
    card_top, card_h, m = b + 152, 39, 14
    cw = tw - 2 * m
    logo_box = (cx - lw / 2 - 9, cy - lh / 2 - 7, cx + lw / 2 + 9, cy + lh / 2 + 9)
    text_box = (b + 6, head_top - 5, W - b - 6, tag_top + 12)
    card_box = (b + m - 4, card_top - 4, b + m + cw + 4, card_top + card_h + 4)
    pattern = scatter(W, H, 501, 30, [logo_box, text_box, card_box], INK, size=(12, 26))
    rule = f"position:absolute;left:21mm;right:6mm;border-bottom:.28mm solid {C['Card Rule']}"
    lab = f"position:absolute;left:6mm;font-size:7.6pt;color:{C['Card Text']};line-height:1"
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs" style="left:{b}mm;width:{tw}mm;top:{head_top}mm;text-align:center">
  <div style="font-weight:800;font-size:22pt;line-height:1.08;letter-spacing:-.01em;text-transform:uppercase;color:{INK}">Stay wrapped.</div>
  <div style="font-weight:800;font-size:22pt;line-height:1.08;letter-spacing:-.01em;text-transform:uppercase;color:{INK}">Stay protected.</div>
</div>
<div class="abs" style="left:{b}mm;width:{tw}mm;top:{tag_top}mm;text-align:center;font-weight:500;font-size:8.6pt;color:{C['Graphite']}">
  Invisible protection. Made for your device.</div>
<div class="abs" style="left:{b + m}mm;top:{card_top}mm;width:{cw}mm;height:{card_h}mm;background:{WHITE};border-radius:3.2mm">
  <div class="mono" style="position:absolute;left:6mm;top:5.6mm;font-size:6.4pt;line-height:1;color:{INK};display:flex;align-items:center;gap:2.2mm">
    <svg width="2.1mm" height="2.1mm" viewBox="0 0 21 21"><rect width="21" height="21" rx="5" fill="{ORANGE}"/></svg>This device belongs to</div>
  <div class="mono" style="position:absolute;right:6mm;top:5.9mm;font-size:5.6pt;line-height:1;color:{C['Card Muted']};letter-spacing:.14em">Wrapshap</div>
  <div style="{lab};top:17.2mm">Name</div><div style="{rule};top:19.6mm"></div>
  <div style="{lab};top:29.2mm">Number</div><div style="{rule};top:31.6mm"></div>
</div>"""
    return W, H, A.page(W, H, AMBER, pattern, html)


def envelope_back():
    tw, th = ENV
    W, H = tw + 2 * BLEED, th + 2 * BLEED
    b = BLEED
    cx, cy, lw = W / 2, H / 2 + 4, 92
    lh = lw / LOGO_RATIO
    crown_cy = cy - lh / 2 - 14
    tag_top = cy + lh / 2 + 9
    logo_box = (cx - lw / 2 - 10, crown_cy - 8, cx + lw / 2 + 10, cy + lh / 2 + 10)
    text_box = (b + 10, tag_top - 3, W - b - 10, tag_top + 9)
    pattern = scatter(W, H, 511, 42, [logo_box, text_box], GRAPHITE, size=(10, 22), opacity=1.0)
    pattern += scatter(W, H, 522, 7, [logo_box, text_box], AMBER, size=(12, 20), opacity=0.16, pad=1.1)
    pattern += f'<g transform="translate({cx:.2f} {crown_cy:.2f})">{ic_crown(15, AMBER, 1.1, np.random.default_rng(9))}</g>'
    dotsep = (f'<svg style="display:inline-block;width:.26em;height:.26em;vertical-align:.14em;margin:0 .35em" viewBox="0 0 10 10">'
              f'<circle cx="5" cy="5" r="5" fill="{C["Label"]}"/></svg>')
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs mono" style="left:{b}mm;width:{tw}mm;top:{tag_top}mm;text-align:center;font-size:8.2pt;color:{C['Label']}">
  Stay wrapped{dotsep}Stay protected</div>"""
    return W, H, A.page(W, H, INK, pattern, html)


def build():
    os.makedirs(os.path.join(HERE, 'html'), exist_ok=True)
    jobs = []

    def add(name, spec, trim):
        W, H, doc = spec
        p = os.path.join(HERE, 'html', name + '.html')
        open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=trim))
        print('built', name)

    add('c-envelope-front', envelope_front(), ENV)
    add('c-envelope-back', envelope_back(), ENV)
    json.dump(jobs, open(os.path.join(HERE, 'jobs_c.json'), 'w'), indent=1)


if __name__ == '__main__':
    build()
