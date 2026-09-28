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
import math, os, json
import numpy as np
import design as A

HERE = A.HERE
FONTS = A.FONTS
BLEED = A.BLEED
LOGO_RATIO = A.LOGO_RATIO
ENV = A.ENV
TOKENS_C = dict(A.TOKENS)
C = {k: v[0] for k, v in TOKENS_C.items()}
INK, AMBER, ORANGE, WHITE, GRAPHITE = (C[k] for k in ('Wrap Black', 'Amber', 'Orange', 'White', 'Graphite'))


# ---- hand-drawn primitives (numpy only) ------------------------------------
def wob(pts, amt, rng):
    pts = np.asarray(pts, float)
    return pts + (rng.normal(0, amt, pts.shape) if amt else 0)


def poly_d(pts, close=False):
    s = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts)
    return s + ('Z' if close else '')


def smooth(pts, n=10):
    P = np.asarray(pts, float)
    P = np.vstack([P[0], P, P[-1]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        for t in np.linspace(0, 1, n, endpoint=False):
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(P[-2])
    return np.array(out)


def stroke(pts, w, color, n=10, jitter=0.0, rng=None, close=False):
    c = smooth(wob(pts, jitter, rng) if jitter else np.asarray(pts, float), n)
    if close:
        c = np.vstack([c, c[:1]])
    return (f'<path d="{poly_d(c)}" fill="none" stroke="{color}" stroke-width="{w:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


# ---- icon library: each draws inside a unit box centred on the origin -----
def ic_phone(w, color, sw, rng):
    bw, bh = w * 0.46, w * 0.82
    body = f'<rect x="{-bw/2:.2f}" y="{-bh/2:.2f}" width="{bw:.2f}" height="{bh:.2f}" rx="{w*0.1:.2f}" fill="none" stroke="{color}" stroke-width="{sw:.2f}"/>'
    cam = f'<circle cx="0" cy="{-bh/2+w*0.1:.2f}" r="{sw*0.9:.2f}" fill="{color}"/>'
    home = f'<line x1="{-bw*0.16:.2f}" y1="{bh/2-w*0.09:.2f}" x2="{bw*0.16:.2f}" y2="{bh/2-w*0.09:.2f}" stroke="{color}" stroke-width="{sw:.2f}" stroke-linecap="round"/>'
    return body + cam + home


def ic_laptop(w, color, sw, rng):
    sw_, sh = w * 0.72, w * 0.46
    screen = f'<rect x="{-sw_/2:.2f}" y="{-sh-w*0.06:.2f}" width="{sw_:.2f}" height="{sh:.2f}" rx="{w*0.05:.2f}" fill="none" stroke="{color}" stroke-width="{sw:.2f}"/>'
    deck = (f'<path d="M{-sw_/2-w*0.1:.2f} {-w*0.06:.2f} L{-sw_*0.62:.2f} {w*0.12:.2f} L{sw_*0.62:.2f} {w*0.12:.2f} '
            f'L{sw_/2+w*0.1:.2f} {-w*0.06:.2f}" fill="none" stroke="{color}" stroke-width="{sw:.2f}" stroke-linejoin="round"/>')
    return screen + deck


def ic_bolt(w, color, sw, rng):
    pts = [(w * 0.12, -w * 0.5), (-w * 0.22, w * 0.06), (w * 0.02, w * 0.06), (-w * 0.12, w * 0.5), (w * 0.24, -w * 0.1), (0, -w * 0.1)]
    return f'<path d="{poly_d(pts, close=True)}" fill="{color}"/>'


def ic_w(w, color, sw, rng):
    y0, y1 = -w * 0.34, w * 0.34
    pts = [(-w * 0.44, y0), (-w * 0.22, y1), (0, y0 * 0.25), (w * 0.22, y1), (w * 0.44, y0)]
    return stroke(pts, sw, color, n=6, rng=rng)


def ic_crown(w, color, sw, rng):
    h = w * 0.72
    p = [(-0.44, 0.42), (-0.50, -0.36), (-0.20, 0.02), (0.0, -0.54), (0.20, 0.02), (0.50, -0.36), (0.44, 0.42)]
    pts = [(x * w, y * h) for x, y in p]
    body = stroke(pts + [pts[0]], sw, color, n=8, jitter=0.012 * w, rng=rng)
    dots = ''.join(f'<circle cx="{x:.2f}" cy="{y - sw * 1.25:.2f}" r="{sw * 0.95:.2f}" fill="{color}"/>' for x, y in (pts[1], pts[3], pts[5]))
    return body + dots


def ic_smiley(w, color, sw, rng):
    r = w * 0.46
    a = np.linspace(math.radians(-60), math.radians(318), 32)
    rr = r * (1 + 0.03 * np.sin(a * 3))
    circ = np.stack([np.cos(a) * rr, np.sin(a) * rr], 1)
    eyes = ''.join(stroke([(x * r, -0.32 * r), (x * r + 0.02 * r, -0.08 * r)], sw * 1.05, color, n=1, rng=rng) for x in (-0.3, 0.3))
    mouth = stroke([(-0.5 * r, 0.12 * r), (-0.2 * r, 0.46 * r), (0.2 * r, 0.47 * r), (0.52 * r, 0.1 * r)], sw, color, n=8, rng=rng)
    face = f'<path d="{poly_d(smooth(circ, 4))}" fill="none" stroke="{color}" stroke-width="{sw:.2f}" stroke-linecap="round"/>'
    return face + eyes + mouth


def ic_sparkle(w, color, sw, rng):
    r, k = w * 0.5, 0.16
    d = (f'M0 {-r:.2f} Q{k*r:.2f} {-k*r:.2f} {r:.2f} 0 Q{k*r:.2f} {k*r:.2f} 0 {r:.2f} '
         f'Q{-k*r:.2f} {k*r:.2f} {-r:.2f} 0 Q{-k*r:.2f} {-k*r:.2f} 0 {-r:.2f}Z')
    return f'<path d="{d}" fill="{color}"/>'


ICONS = [ic_phone, ic_laptop, ic_bolt, ic_w, ic_crown, ic_smiley, ic_sparkle]
WEIGHTS = [3, 2, 3, 2, 1, 1, 2]


def scatter(W, H, seed, count, keepouts, color, size=(11, 24), sw_k=0.09, opacity=1.0, pad=0.86, icons=None, weights=None):
    """Rejection-sample `count` icons outside `keepouts` ((x0,y0,x1,y1) rects, expanded by
    each candidate's own radius) and clear of icons already placed."""
    rng = np.random.default_rng(seed)
    pool = icons or ICONS
    wts = np.array(weights or WEIGHTS, float)
    wts /= wts.sum()
    placed, out = [], []
    tries = 0
    while len(placed) < count and tries < count * 60:
        tries += 1
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        w = rng.uniform(*size)
        r = w * 0.62
        if any(x0 - r <= x <= x1 + r and y0 - r <= y <= y1 + r for x0, y0, x1, y1 in keepouts):
            continue
        if any(math.hypot(x - px, y - py) < (r + pr) * pad for px, py, pr in placed):
            continue
        fn = pool[rng.choice(len(pool), p=wts)]
        rot = rng.uniform(-26, 26)
        body = fn(w, color, max(0.35, w * sw_k), rng)
        out.append(f'<g transform="translate({x:.2f} {y:.2f}) rotate({rot:.1f})" opacity="{opacity:.3f}">{body}</g>')
        placed.append((x, y, r))
    return '\n'.join(out)


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
