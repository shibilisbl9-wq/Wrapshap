"""Wrapshap t-shirt collection: the six designs from the reference board, built on the original logo.

  1 Signature Graffiti - black tee (built by tee.py; reused as is)
  2 Playful Character  - white tee, back: phone mascot with sunglasses and peace hands, logo with drips
  3 Minimal Bold       - black tee, front: one-colour white logo, marker tagline, crown
  4 Abstract           - cream tee, back: painted smiley with a crown, one-colour black logo
  5 Clean Tagline      - black tee, front: crown and stacked tagline (the reference has no wordmark)
  6 Vertical Bold      - orange tee, back: the logo turned upright as white bubble letters, crowns, splats

The logo is never redrawn. Logo slots are filled by post.py with the original vector artwork, either
untouched or recoloured one-colour from its own paths (logo_variants.py). Outlines and drips around it
are true offsets of the logo's own silhouette. Every piece is vector, RGB, with type converted to outlines.

Designs 2, 4 and 6 are laid out on a grid in reference-image pixels (the 4x crops of the board) and
scaled to print millimetres, so positions follow the reference closely.
"""
import json, math, os
import numpy as np
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union
from shapely import affinity
import design as A
import tee as T

HERE = A.HERE
ORANGE, WHITE, INK = A.ORANGE, '#FFFFFF', T.LINE
GARMENT = {'black': '#111113', 'white': '#F4F4F2', 'cream': '#EFE8D8', 'orange': '#F39200'}


# ---- logo placement ------------------------------------------------------------------------
def sil(cx, cy, lw, rot=0):
    """Logo silhouette centred on (cx, cy), lw wide, turned rot degrees counter-clockwise."""
    s = lw / T.LW_PT
    g = affinity.affine_transform(T.SIL, [s, 0, 0, s, cx - lw / 2, cy - lw / A.LOGO_RATIO / 2])
    return affinity.rotate(g, -rot, origin=(cx, cy)) if rot else g


def bottom(geom, x):
    ln = LineString([(x, -1e5), (x, 1e5)]).intersection(geom)
    return max(c[1] for g in getattr(ln, 'geoms', [ln]) for c in g.coords)


def ring(shape, lw, gap, width, drips=(), color=INK):
    """Outline around a logo silhouette (gap, width as fractions of logo width) with paint drips.
    drips: (x, length, width) in page units, hanging from the outline's lowest edge at x."""
    inner = shape.buffer(gap * lw if gap else -0.003 * lw, quad_segs=12)
    outer = shape.buffer((gap + width) * lw, quad_segs=12)
    body = unary_union([outer] + [T.drip(x, bottom(outer, x), L, w) for x, L, w in drips])
    k = 0.012 * lw                                   # melt the drip joins
    body = body.buffer(k, quad_segs=8).buffer(-k, quad_segs=8)
    return f'<path d="{T.to_path(body.difference(inner).simplify(0.01))}" fill="{color}" fill-rule="evenodd"/>'


def slot(cx, cy, lw, variant='full', rot=0, S=1.0):
    """Logo slot (in mm, after scaling by S). post.py reads variant and rotation from the id."""
    lh = lw / A.LOGO_RATIO
    a = math.radians(rot)
    bw, bh = lw * abs(math.cos(a)) + lh * abs(math.sin(a)), lw * abs(math.sin(a)) + lh * abs(math.cos(a))
    sid = 'logo' if variant == 'full' and not rot else f'logo--{variant}--r{rot}'
    return (f'<div class="logo-slot" id="{sid}" style="left:{(cx - bw / 2) * S:.4f}mm;top:{(cy - bh / 2) * S:.4f}mm;'
            f'width:{bw * S:.4f}mm;height:{bh * S:.4f}mm"></div>')


# ---- paint marks ---------------------------------------------------------------------------------
def path(geom, color):
    return f'<path d="{T.to_path(geom)}" fill="{color}" fill-rule="evenodd"/>'


def _noise(r, n, k=6):
    x = r.normal(0, 1, n + 4 * k)
    g = np.exp(-np.linspace(-2, 2, 2 * k + 1) ** 2)
    return np.convolve(x, g / g.sum(), 'same')[2 * k:2 * k + n] * 2.2


def paint(pts, w, seed, taper=(0.1, 0.88), rough=0.07, streaks=5, n=14):
    """Dry-brush stroke as one filled shape: swelling width, ragged edges, bristle gaps at the tail."""
    r = np.random.default_rng(seed)
    c = T.smooth(pts, n)
    s = np.concatenate([[0], np.cumsum(np.hypot(*np.diff(c, axis=0).T))])
    ss = np.linspace(0, s[-1], max(24, int(s[-1] / (w * 0.12))))
    c = np.stack([np.interp(ss, s, c[:, 0]), np.interp(ss, s, c[:, 1])], 1)
    d = np.gradient(c, axis=0)
    d /= np.linalg.norm(d, axis=1, keepdims=True) + 1e-9
    nrm = np.stack([-d[:, 1], d[:, 0]], 1)
    t = ss / ss[-1]
    a, b = taper
    prof = 0.4 + 0.6 * np.clip(np.minimum(t / a, (1 - t) / (1 - b)), 0, 1) ** 0.6
    hl = w / 2 * prof * (1 + rough * _noise(r, len(t)))
    hr = w / 2 * prof * (1 + rough * _noise(r, len(t)))
    shape = Polygon(np.vstack([c + nrm * hl[:, None], (c - nrm * hr[:, None])[::-1]])).buffer(0)
    shape = shape.union(Point(*c[0]).buffer(min(hl[0], hr[0]) * 0.95, quad_segs=8))
    cuts = []
    for _ in range(streaks):                        # bristles running dry
        off = r.uniform(-0.42, 0.42) * w
        sel = ss >= ss[-1] - r.uniform(0.8, 2.6) * w
        if sel.sum() > 2:
            cuts.append(LineString(c[sel] + nrm[sel] * off).buffer(r.uniform(0.018, 0.045) * w, cap_style='flat'))
    return shape.difference(unary_union(cuts)) if cuts else shape


def star4(cx, cy, r, k=0.22, rot=0, rough=0.0, seed=0):
    """Four-point sparkle as a shape (optionally with a hand-painted wobble)."""
    q = k * r
    pts = []
    tips = [(0, -r), (r, 0), (0, r), (-r, 0)]
    for i in range(4):
        p0, p2 = np.array(tips[i]), np.array(tips[(i + 1) % 4])
        p1 = np.array([q if (p0 + p2)[0] > 0 else -q, q if (p0 + p2)[1] > 0 else -q])
        for tt in np.linspace(0, 1, 12, endpoint=False):
            pts.append((1 - tt) ** 2 * p0 + 2 * (1 - tt) * tt * p1 + tt ** 2 * p2)
    P = np.array(pts)
    if rough:
        P *= 1 + rough * _noise(np.random.default_rng(seed), len(P), 3)[:, None]
    g = Polygon(P).buffer(0)
    return affinity.translate(affinity.rotate(g, rot, origin=(0, 0)), cx, cy)


def splat(cx, cy, r, seed, arms=8, drops=7, arm_len=(1.3, 2.3)):
    """Paint splat: ragged blob, tapered arms, loose droplets."""
    rr = np.random.default_rng(seed)
    a = np.linspace(0, 2 * np.pi, 72, endpoint=False)
    rad = r * (1 + 0.16 * _noise(rr, 72, 3))
    parts = [Polygon(np.stack([cx + np.cos(a) * rad, cy + np.sin(a) * rad], 1)).buffer(0)]
    for ang in rr.uniform(0, 2 * np.pi, arms):
        L = r * rr.uniform(*arm_len)
        w = r * rr.uniform(0.18, 0.34)
        tip = (cx + np.cos(ang) * L, cy + np.sin(ang) * L)
        sx, sy = -np.sin(ang) * w, np.cos(ang) * w
        parts.append(Polygon([(cx + sx, cy + sy), tip, (cx - sx, cy - sy)]))
        parts.append(Point(*tip).buffer(w * rr.uniform(0.35, 0.6), quad_segs=6))
    for _ in range(drops):
        ang, dist = rr.uniform(0, 2 * np.pi), r * rr.uniform(1.9, 3.2)
        parts.append(Point(cx + np.cos(ang) * dist, cy + np.sin(ang) * dist).buffer(r * rr.uniform(0.06, 0.2), quad_segs=6))
    return unary_union(parts)


def specks(box, n, rmin, rmax, seed, avoid=None):
    """Scattered paint dots in box = (x0, y0, x1, y1), optionally kept off a shape."""
    rr = np.random.default_rng(seed)
    out = []
    while len(out) < n:
        x, y = rr.uniform(box[0], box[2]), rr.uniform(box[1], box[3])
        rad = rmin + (rmax - rmin) * rr.random() ** 2
        c = Point(x, y).buffer(rad, quad_segs=6)
        if avoid is None or not c.intersects(avoid):
            out.append(c)
    return unary_union(out)


def crown_clean(x, y, w, color, sw):
    """Clean line crown (designs 3 and 5): three points over a band."""
    h = w * 0.74
    P = [(0.12, 0.98), (0.03, 0.14), (0.31, 0.46), (0.5, 0.02), (0.69, 0.46), (0.97, 0.14), (0.88, 0.98)]
    d = 'M' + ' L'.join(f'{x + px * w:.3f} {y + py * h:.3f}' for px, py in P) + 'Z'
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{sw}" stroke-linejoin="round"/>'
            f'<path d="M{x + 0.1 * w:.3f} {y + 0.76 * h:.3f} L{x + 0.9 * w:.3f} {y + 0.76 * h:.3f}" stroke="{color}" stroke-width="{sw}"/>')


def fit_text(font, s, width, **kw):
    """Em size that makes s exactly `width` wide."""
    return width / T.text_width(font, s, 1.0, kw.get('track', 0.0))


# ---- design 2: playful character --------------------------------------------------------------------
def glove(x, y, s, rot, flip=False, sw=4.6):
    """Cartoon glove making a peace sign. Local units: palm ~60 wide, fingers up."""
    ln = f'fill="{WHITE}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round" stroke-linecap="round"'

    def cap(p, q, r):
        return LineString([p, q]).buffer(r, quad_segs=10)

    def shp(g):
        return f'<path d="{T.to_path(g)}" {ln}/>'
    palm = Polygon([(-25, -10), (25, -10), (25, 34), (-25, 34)]).buffer(0).buffer(-14).buffer(14, quad_segs=10)
    hand = unary_union([palm, cap((-11, -6), (-19, -58), 10), cap((10, -6), (17, -60), 10)])
    art = (shp(Polygon([(-21, 30), (21, 30), (21, 44), (-21, 44)]).buffer(4, quad_segs=6))      # cuff
           + shp(hand)                                                                              # palm, V fingers
           + shp(cap((4, 1), (26, 1), 7)) + shp(cap((4, 14), (24, 14), 6.6))                       # curled fingers
           + shp(cap((-22, 22), (10, 12), 8.2))                                                     # thumb
           + f'<path d="M-15 -30 L-17 -42 M13 -32 L14 -44" fill="none" stroke="{INK}" '
             f'stroke-width="{sw * 0.6}" stroke-linecap="round"/>')
    fl = ' scale(-1 1)' if flip else ''
    return f'<g transform="translate({x} {y}) rotate({rot}) scale({s}){fl}">{art}</g>'


def phone(x0, y0, x1, y1):
    """The mascot: a phone with sunglasses, happy eyes and a big grin."""
    w = x1 - x0
    out = [f'<rect x="{x0}" y="{y0}" width="{w}" height="{y1 - y0}" rx="34" fill="{WHITE}" stroke="{INK}" stroke-width="12"/>',
           f'<rect x="{x0 + 15}" y="{y0 + 15}" width="{w - 30}" height="{y1 - y0 - 30}" rx="21" fill="none" stroke="{INK}" stroke-width="4"/>',
           f'<rect x="{x0 + w / 2 - 16}" y="{y0 + 5}" width="32" height="5" rx="2.5" fill="{WHITE}"/>']
    cx = x0 + w / 2
    for ex in (cx - 32, cx + 30):                              # happy closed eyes
        out.append(T.stroke([(ex - 14, y0 + 88), (ex, y0 + 76), (ex + 14, y0 + 86)], 5.5, INK))
    lens = lambda lx: (f'M{lx - 40} {y0 + 118} L{lx + 40} {y0 + 118} Q{lx + 41} {y0 + 168} {lx + 4} {y0 + 172} '
                       f'Q{lx - 38} {y0 + 172} {lx - 40} {y0 + 118} Z')
    out.append(f'<path d="{lens(cx - 50)} {lens(cx + 50)}" fill="{INK}" stroke="{INK}" stroke-width="5" stroke-linejoin="round"/>')
    out.append(f'<path d="M{x0 - 6} {y0 + 121} L{x1 + 6} {y0 + 121}" stroke="{INK}" stroke-width="9" stroke-linecap="round"/>')
    for lx in (cx - 50, cx + 50):                              # lens glints
        out.append(f'<path d="M{lx - 26} {y0 + 133} L{lx - 12} {y0 + 133} M{lx - 27} {y0 + 145} L{lx - 21} {y0 + 145}" '
                   f'stroke="{WHITE}" stroke-width="4.5" stroke-linecap="round"/>')
    out.append(f'<path d="M{cx - 44} {y0 + 196} Q{cx} {y0 + 205} {cx + 46} {y0 + 192} Q{cx + 30} {y0 + 252} {cx} {y0 + 250} '
               f'Q{cx - 34} {y0 + 250} {cx - 44} {y0 + 196} Z" fill="{INK}"/>')
    return ''.join(out)


def bolt(x, y, s, color, sw):
    P = [(0, 0), (-24, 50), (-5, 50), (-20, 96), (30, 34), (10, 34), (24, 0)]
    d = 'M' + ' L'.join(f'{x + px * s:.2f} {y + py * s:.2f}' for px, py in P) + 'Z'
    return f'<path d="{d}" fill="{color}" stroke="{INK}" stroke-width="{sw}" stroke-linejoin="round"/>'


def star_doodle(cx, cy, r, seed):
    """Spiky hand-drawn star with a drip, filled black."""
    rr = np.random.default_rng(seed)
    a = np.linspace(-np.pi / 2, 1.5 * np.pi, 11)[:-1]
    rad = np.where(np.arange(10) % 2 == 0, r, r * 0.42) * rr.uniform(0.85, 1.15, 10)
    g = Polygon(np.stack([cx + np.cos(a) * rad, cy + np.sin(a) * rad], 1)).buffer(1.5, quad_segs=3)
    g = g.union(T.drip(cx + r * 0.1, cy + r * 0.3, r * 0.9, r * 0.2))
    return path(g, INK)


def design2(logo='full'):
    x0, y0, x1, y1 = 195, 190, 805, 990                       # grid in reference px
    S = 340 / (x1 - x0)                                        # -> 340 mm wide
    lw, lcx, lcy = 572, 507, 572
    svg = []
    svg.append(path(unary_union([splat(382, 486, 11, 1, arms=6, drops=5), splat(628, 404, 10, 2, arms=6, drops=5),
                                 splat(452, 478, 5, 3, arms=4, drops=3)]), ORANGE))
    svg.append(phone(398, 222, 610, 560))
    svg.append(glove(294, 450, 1.42, -14))
    svg.append(glove(714, 372, 1.55, 14, flip=True))
    svg.append(bolt(672, 206, 0.98, ORANGE, 4.5))
    svg.append(star_doodle(338, 282, 34, 5))
    svg.append(path(specks((215, 205, 795, 470), 16, 2.5, 6.5, 7, avoid=Polygon([(380, 215), (630, 215), (630, 600), (380, 600)])), INK))
    svg.append(path(specks((215, 205, 795, 470), 12, 2.5, 7, 8, avoid=Polygon([(380, 215), (630, 215), (630, 600), (380, 600)])), ORANGE))
    shape = sil(lcx, lcy, lw)
    svg.append(ring(shape, lw, *T.GARMENTS['white']['ring'],
                    drips=[(236, 118, 11), (262, 60, 8), (300, 150, 12), (338, 40, 7), (700, 42, 8), (752, 110, 11), (776, 58, 8)]))
    # doodles under the piece
    yb = lcy + lw / A.LOGO_RATIO / 2
    svg.append(path(paint([(318, yb + 50), (372, yb + 46), (432, yb + 40)], 17, 21, streaks=3), INK))
    svg.append(T.stroke([(352, yb + 44), (348, yb + 82)], 6, INK, n=1))
    cloud = unary_union([Point(622, yb + 18).buffer(20), Point(652, yb + 10).buffer(24), Point(680, yb + 22).buffer(17),
                         Point(650, yb + 30).buffer(18)])
    svg.append(f'<path d="{T.to_path(cloud)}" fill="{WHITE}" stroke="{INK}" stroke-width="5"/>')
    svg.append(T.stroke([(512, yb + 22), (560, yb + 18), (600, yb + 24)], 5, INK))
    # tagline, black marker handwriting
    ts = fit_text('Kalam-700', 'Stay wrapped.', 372)
    tag = (T.text('Kalam-700', 'Stay wrapped.', 0, 0, ts, INK, jitter=0.005)
           + T.text('Kalam-700', 'Stay protected.', 8, ts * 0.98, ts, INK, jitter=0.005))
    svg.append(f'<g transform="translate(310 {yb + 150}) rotate(-7)">{tag}</g>')
    svg.append(path(star4(246, yb + 128, 30, k=0.2), INK))
    svg.append(path(star4(730, yb + 128, 11, k=0.2), INK))
    svg.append(path(unary_union([Point(292, yb + 188).buffer(4), Point(706, yb + 196).buffer(3.5), Point(210, yb + 60).buffer(4.5)]), ORANGE))
    # swoosh
    sy = yb + 262
    svg.append(T.brush([(410, sy + 28), (470, sy + 18), (560, sy), (650, sy - 34)], 21, INK, rough=0.03))
    svg.append(T.brush([(636, sy - 20), (662, sy - 26), (676, sy - 44)], 10, INK))
    body = f'<g transform="scale({S:.6f}) translate({-x0} {-y0})">{"".join(svg)}</g>'
    W, H = (x1 - x0) * S, (y1 - y0) * S
    return W, H, A.page(W, H, 'transparent', body, slot(lcx - x0, lcy - y0, lw, logo, 0, S))


# ---- design 3: minimal bold -------------------------------------------------------------------------
def design3(logo='white'):
    W = 290
    lw = 262
    lh = lw / A.LOGO_RATIO
    tag = 'STAY WRAPPED. STAY PROTECTED.'
    ts = fit_text('PermanentMarker-400', tag, W - 4, track=0.02)
    ty = lh + 9 + ts * 0.74
    cw = 36
    cy = ty + 10
    H = cy + cw * 0.74 + 2
    svg = (T.text('PermanentMarker-400', tag, W / 2, ty, ts, ORANGE, track=0.02, anchor='middle')
           + crown_clean(W / 2 - cw / 2, cy, cw, ORANGE, 2.8))
    return W, H, A.page(W, H, 'transparent', svg, slot(W / 2, lh / 2 + 1, lw, logo))


# ---- design 4: abstract -------------------------------------------------------------------------------
def design4(logo='black'):
    x0, y0, x1, y1 = 135, 160, 845, 1115
    S = 360 / (x1 - x0)                                        # -> 360 mm wide
    paintg = []
    cx, cy, R = 575, 612, 193
    a = np.radians(np.linspace(-118, 250, 40))
    paintg.append(paint(list(zip(cx + R * np.cos(a), cy + R * np.sin(a) * 1.02)), 44, 1, taper=(0.04, 0.93), streaks=7, n=6))
    paintg.append(paint([(500, 536), (502, 568), (504, 600)], 32, 2, taper=(0.2, 0.8), streaks=2))
    paintg.append(paint([(592, 520), (593, 552), (595, 586)], 32, 3, taper=(0.2, 0.8), streaks=2))
    paintg.append(paint([(442, 668), (492, 722), (566, 740), (638, 708), (684, 640)], 38, 4, taper=(0.08, 0.9), streaks=4))
    paintg.append(paint([(400, 450), (344, 330), (430, 368), (478, 206), (538, 322), (598, 224), (606, 412)], 30, 5,
                        taper=(0.05, 0.94), streaks=4, n=2))
    paintg.append(paint([(396, 452), (480, 438), (560, 424)], 26, 6, taper=(0.05, 0.9), streaks=3))
    paintg += [Point(477, 182).buffer(15), Point(604, 202).buffer(13), Point(342, 318).buffer(8)]
    paintg += [star4(272, 488, 56, k=0.2, rot=8, rough=0.05, seed=1), star4(712, 336, 44, k=0.2, rot=-6, rough=0.05, seed=2),
               star4(240, 750, 64, k=0.22, rot=12, rough=0.06, seed=3), star4(318, 262, 12, k=0.25, seed=4),
               star4(760, 520, 10, k=0.25, seed=5)]
    paintg.append(splat(222, 780, 16, 9, arms=7, drops=8))
    paintg.append(splat(268, 470, 8, 10, arms=5, drops=6))
    paintg.append(splat(730, 356, 7, 11, arms=5, drops=5))
    paintg.append(specks((170, 180, 820, 1090), 55, 1.8, 6.5, 12, avoid=Point(cx, cy).buffer(R + 26)))
    # orange swoosh under the word
    paintg.append(paint([(452, 1050), (600, 1004), (796, 950)], 30, 7, taper=(0.06, 0.9), streaks=4))
    paintg.append(paint([(566, 1090), (680, 1066), (772, 1046)], 22, 8, taper=(0.06, 0.88), streaks=3))
    svg = [path(unary_union(paintg), ORANGE)]
    lw, lcx, lcy, rot = 654, 492, 915, 9
    body = f'<g transform="scale({S:.6f}) translate({-x0} {-y0})">{"".join(svg)}</g>'
    W, H = (x1 - x0) * S, (y1 - y0) * S
    return W, H, A.page(W, H, 'transparent', body, slot(lcx - x0, lcy - y0, lw, logo, rot, S))


# ---- design 5: clean tagline ----------------------------------------------------------------------------
def design5():
    lines = [('Stay', WHITE), ('wrapped.', WHITE), ('Stay', ORANGE), ('protected.', ORANGE)]
    W = 145
    ts = fit_text('Geist-700', 'protected.', W - 1, track=-0.02)
    cw = 0.28 * W
    lead = ts * 1.02
    top = cw * 0.74 + 7
    svg = [crown_clean(1.6, 1.6, cw, ORANGE, 3.0)]
    for i, (s, c) in enumerate(lines):
        svg.append(T.text('Geist-700', s, 0, top + ts * 0.73 + i * lead, ts, c, track=-0.02))
    H = top + ts * 0.73 + 3 * lead + ts * 0.24
    return W, H, A.page(W, H, 'transparent', ''.join(svg), '')


def back_neck_logo():
    """Optional small logo under the back collar (design 5 has no wordmark on the front)."""
    lw = 80
    lh = lw / A.LOGO_RATIO
    return lw + 2, lh + 2, A.page(lw + 2, lh + 2, 'transparent', '', slot(lw / 2 + 1, lh / 2 + 1, lw))


# ---- design 6: vertical bold -------------------------------------------------------------------------------
def crown_drip(cx, cy, w, rot, seed, sw):
    """Black line crown with dots on the tips and paint running off its base."""
    rr = np.random.default_rng(seed)
    base_y = cy + w * 0.72 * 0.42
    drips = unary_union([T.drip(cx + w * f, base_y, w * L, sw * 0.7) for f, L in ((-0.22, rr.uniform(0.14, 0.2)), (0.2, rr.uniform(0.24, 0.32)))])
    g = affinity.rotate(drips, rot, origin=(cx, cy))
    return T.crown(cx, cy, w, INK, sw, rot=rot) + path(g, INK)


def design6(logo='inverse'):
    x0, y0, x1, y1 = 312, 140, 848, 1180
    S = 490 / (y1 - y0)                                       # -> 490 mm tall
    lw, lcx, lcy = 900, 660, 634                               # logo turned upright, reads bottom to top
    shape = sil(lcx, lcy, lw, 90)
    svg = []
    whites = [splat(548, 228, 40, 21, arms=9, drops=7), splat(506, 470, 44, 22, arms=9, drops=8),
              splat(556, 830, 14, 23, arms=6, drops=5), splat(578, 1066, 16, 24, arms=6, drops=5),
              splat(540, 1000, 8, 25, arms=5, drops=4)]
    svg.append(path(unary_union(whites), WHITE))
    svg.append(path(specks((420, 180, 600, 1100), 34, 2.5, 9, 26, avoid=shape.buffer(20)), INK))
    svg.append(path(unary_union([Point(510, 240).buffer(6), Point(492, 488).buffer(7), Point(520, 455).buffer(4)]), INK))
    svg.append(crown_drip(420, 744, 104, -10, 31, 9))
    svg.append(crown_drip(404, 958, 138, 16, 32, 11))
    svg.append(path(unary_union([star4(560, 902, 14, k=0.22), star4(548, 368, 9, k=0.22)]), WHITE))
    svg.append(ring(shape, lw, 0.0, 0.016, drips=[(600, 70, 13), (636, 36, 10), (690, 96, 14)]))
    body = f'<g transform="scale({S:.6f}) translate({-x0} {-y0})">{"".join(svg)}</g>'
    W, H = (x1 - x0) * S, (y1 - y0) * S
    return W, H, A.page(W, H, 'transparent', body, slot(lcx - x0, lcy - y0, lw, logo, 90, S))


PIECES = {
    'c2-back': lambda: design2(),
    'c3-front': lambda: design3(),
    'c3-front-alt': lambda: design3('full'),
    'c4-back': lambda: design4(),
    'c4-back-alt': lambda: design4('full'),
    'c5-chest': design5,
    'c5-back-neck': back_neck_logo,
    'c6-back': lambda: design6(),
    'c6-back-alt': lambda: design6('full'),
}

if __name__ == '__main__':
    import sys
    only = sys.argv[1:]
    os.makedirs(os.path.join(HERE, 'html'), exist_ok=True)
    jobs = []
    for name, fn in PIECES.items():
        W, H, doc = fn() if not only or name in only else (0, 0, None)
        p = os.path.join(HERE, 'html', name + '.html')
        if doc:
            open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=None, cmyk=False))
    if only:                                   # keep sizes of pieces not rebuilt
        old = {j['name']: j for j in json.load(open(os.path.join(HERE, 'jobs_coll.json')))}
        jobs = [j if j['name'] in only else old[j['name']] for j in jobs]
    json.dump(jobs, open(os.path.join(HERE, 'jobs_coll.json'), 'w'), indent=1)
    print({j['name']: (round(j['w']), round(j['h'])) for j in jobs})
