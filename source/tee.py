"""Graffiti t-shirt: the original Wrapshap wordmark dressed as a street piece.

The logo itself is never redrawn: post.py places the vector original. Around it this builds
an outline ring with drips (true vector offset of the logo's silhouette), a hand-drawn crown,
a smiley, sparkles, marker dashes, a handwritten tagline and an orange brush swoosh.
All type is converted to outlines, so the print files need no fonts.

Pieces per garment colour: back print, left-chest print, inside-neck print; plus one woven
sleeve label (same for both colours).
"""
import json, math, os
import numpy as np
import pymupdf as fitz
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from shapely.geometry import Polygon, Point, LineString, box
from shapely.ops import unary_union
from shapely import affinity
import design as A

HERE = A.HERE
FONTS = A.FONTS
WHITE, ORANGE, AMBER = '#FFFFFF', A.ORANGE, A.AMBER
LINE = '#111111'
LW_PT, LH_PT = 219.12, 79.92
BACK_W = 320                             # back print width, mm

GARMENTS = {
    # ring: (gap, width) around the logo, as a fraction of logo width. On black the gap is
    # left unprinted, so the tee shows through as a dark line between logo and outline.
    'black': dict(bg='#111113', line=WHITE, ring=(0.0064, 0.0136), accent=ORANGE),
    'white': dict(bg='#F4F4F2', line=LINE, ring=(0.0, 0.0136), accent=ORANGE),
}


# ---- geometry helpers ------------------------------------------------------
def _bez(p0, p1, p2, p3, n=10):
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3 * p3)


def logo_silhouette():
    """Union of the logo's outermost (white rim) contours, in logo pt, y down."""
    d = fitz.open(os.path.join(HERE, 'logo.pdf'))[0].get_drawings()[0]
    subs, cur, last = [], [], None
    for it in d['items']:
        pts = [np.array([p.x, p.y]) for p in it[1:]]
        if last is None or np.hypot(*(pts[0] - last)) > 0.01:
            if len(cur) > 2:
                subs.append(cur)
            cur = [pts[0]]
        if it[0] == 'l':
            cur.append(pts[1])
        elif it[0] == 'c':
            cur += list(_bez(*pts)[1:])
        last = pts[-1]
    if len(cur) > 2:
        subs.append(cur)
    polys = [Polygon(s).buffer(0) for s in subs]
    # the white rim is filled + stroked at 1 pt
    return unary_union(polys).buffer(0.5, join_style='round', quad_segs=8)


SIL = logo_silhouette()


def place_sil(cx, top, lw):
    s = lw / LW_PT
    return affinity.affine_transform(SIL, [s, 0, 0, s, cx - lw / 2, top])


def to_path(geom, prec=2):
    polys = getattr(geom, 'geoms', [geom])
    out = []
    for p in polys:
        for ring in [p.exterior, *p.interiors]:
            c = np.asarray(ring.coords)
            out.append('M' + ' L'.join(f'{x:.{prec}f} {y:.{prec}f}' for x, y in c[:-1]) + 'Z')
    return ''.join(out)


def bottom_at(geom, x):
    ln = LineString([(x, -1000), (x, 1000)]).intersection(geom)
    return max(c[1] for g in getattr(ln, 'geoms', [ln]) for c in g.coords)


def drip(x, y0, length, w):
    """Paint drip hanging from y0: a stem with a slightly fat rounded end."""
    r = w * 0.62
    stem = box(x - w / 2, y0 - w, x + w / 2, y0 + length - r)
    return unary_union([stem, Point(x, y0 + length - r).buffer(r, quad_segs=12)])


def outline_ring(cx, top, lw, gap, width, drips=(), drops=()):
    sil = place_sil(cx, top, lw)
    inner = sil.buffer(gap * lw, quad_segs=12) if gap else sil
    outer = sil.buffer((gap + width) * lw, quad_segs=12)
    shapes = [outer]
    for fx, L, w in drips:
        x = cx - lw / 2 + fx * lw
        shapes.append(drip(x, bottom_at(outer, x), L, w))
    body = unary_union(shapes)
    k = 0.012 * lw                                  # melt the drip joins (closing)
    body = body.buffer(k, quad_segs=8).buffer(-k, quad_segs=8)
    geom = body.difference(inner).simplify(0.01)
    for x, y, r in drops:
        geom = geom.union(Point(x, y).buffer(r, quad_segs=10))
    return geom


# ---- hand-drawn marks --------------------------------------------------------
rng = np.random.default_rng(7)


def wob(pts, amt):
    pts = np.asarray(pts, float)
    return pts + rng.normal(0, amt, pts.shape)


def poly_d(pts, close=False):
    s = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts)
    return s + ('Z' if close else '')


def smooth(pts, n=12):
    """Catmull-Rom through pts."""
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


def stroke(pts, w, color, n=12, jitter=0.0):
    c = smooth(wob(pts, jitter) if jitter else pts, n)
    return (f'<path d="{poly_d(c)}" fill="none" stroke="{color}" stroke-width="{w:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def brush(pts, w, color, taper=(0.25, 1.0), rough=0.0, n=16):
    """Tapered brush stroke as a filled outline (width follows a swell profile)."""
    c = smooth(pts, n)
    seg = np.diff(c, axis=0)
    seg = np.vstack([seg, seg[-1]])
    nrm = np.stack([-seg[:, 1], seg[:, 0]], 1)
    nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-9
    t = np.linspace(0, 1, len(c))
    a, b = taper
    prof = np.minimum(1, np.minimum(t / max(a, 1e-3), (1 - t) / max(1 - b, 1e-3) if b < 1 else 1)) ** 0.7
    prof = np.clip(0.18 + 0.82 * np.sin(np.pi * np.clip(t, 0, 1)) ** 0.35, 0, 1) * np.maximum(prof, 0.18)
    hw = w / 2 * prof * (1 + rng.normal(0, rough, len(c)))
    L, R = c + nrm * hw[:, None], c - nrm * hw[:, None]
    shape = Polygon(np.vstack([L, R[::-1]])).buffer(0)
    shape = unary_union([shape, Point(*c[0]).buffer(hw[0], 10), Point(*c[-1]).buffer(hw[-1], 10)])
    return f'<path d="{to_path(shape)}" fill="{color}"/>'


def crown(cx, cy, w, color, sw, rot=-10):
    h = w * 0.72
    p = [(-0.44, 0.42), (-0.50, -0.36), (-0.20, 0.02), (0.0, -0.54), (0.20, 0.02), (0.50, -0.36), (0.44, 0.42)]
    pts = [(x * w, y * h) for x, y in p]
    body = stroke(pts + [pts[0], (pts[0][0] + 0.06 * w, pts[0][1] - 0.01 * h)], sw, color, n=1, jitter=0.012 * w)
    dots = ''.join(f'<circle cx="{x:.2f}" cy="{y - sw * 1.25:.2f}" r="{sw * 0.95:.2f}" fill="{color}"/>'
                   for x, y in (pts[1], pts[3], pts[5]))
    return f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({rot})">{body}{dots}</g>'


def smiley(cx, cy, r, color, sw):
    a = np.linspace(math.radians(-60), math.radians(318), 40)
    rr = r * (1 + 0.03 * np.sin(a * 3))
    circ = np.stack([np.cos(a) * rr, np.sin(a) * rr], 1)
    eyes = ''.join(stroke([(x * r, -0.32 * r), (x * r + 0.02 * r, -0.08 * r)], sw * 1.05, color, n=1) for x in (-0.3, 0.3))
    mouth = stroke([(-0.5 * r, 0.12 * r), (-0.2 * r, 0.46 * r), (0.2 * r, 0.47 * r), (0.52 * r, 0.1 * r)], sw, color)
    ticks = ''.join(stroke([(math.cos(t) * r * 1.28, math.sin(t) * r * 1.28), (math.cos(t) * r * 1.5, math.sin(t) * r * 1.5)], sw * 0.7, color, n=1)
                    for t in (math.radians(-110), math.radians(-70), math.radians(-30)))
    return (f'<g transform="translate({cx:.2f} {cy:.2f}) rotate(-8)">'
            f'<path d="{poly_d(smooth(circ, 4))}" fill="none" stroke="{color}" stroke-width="{sw:.2f}" stroke-linecap="round"/>'
            f'{eyes}{mouth}{ticks}</g>')


def sparkle(cx, cy, r, color, k=0.16):
    q = k * r
    d = (f'M{cx} {cy - r} Q{cx + q} {cy - q} {cx + r} {cy} Q{cx + q} {cy + q} {cx} {cy + r} '
         f'Q{cx - q} {cy + q} {cx - r} {cy} Q{cx - q} {cy - q} {cx} {cy - r}Z')
    return f'<path d="{d}" fill="{color}"/>'


def dot(cx, cy, r, color):
    return f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{r:.2f}" fill="{color}"/>'


def plus(cx, cy, s, color, sw):
    return stroke([(cx - s, cy), (cx + s, cy)], sw, color, n=1) + stroke([(cx, cy - s), (cx, cy + s)], sw, color, n=1)


# ---- type to outlines ----------------------------------------------------------
_FONTS = {}


def font(name):
    if name not in _FONTS:
        f = TTFont(os.path.join(FONTS, name + '.ttf'))
        _FONTS[name] = (f, f.getGlyphSet(), f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm)
    return _FONTS[name]


def text_width(name, s, size, track=0.0):
    f, gs, cmap, hmtx, upm = font(name)
    return sum(hmtx[cmap[ord(ch)]][0] for ch in s) * size / upm + track * size * (len(s) - 1)


def text(name, s, x, y, size, color, track=0.0, jitter=0.0, anchor='start'):
    """Glyph outlines; size = em size in mm; (x, y) = baseline start."""
    f, gs, cmap, hmtx, upm = font(name)
    k = size / upm
    if anchor == 'middle':
        x -= text_width(name, s, size, track) / 2
    out = []
    for ch in s:
        g = cmap[ord(ch)]
        pen = SVGPathPen(gs)
        gs[g].draw(pen)
        d = pen.getCommands()
        if d:
            dy = rng.normal(0, jitter * size) if jitter else 0
            rot = rng.normal(0, jitter * 40) if jitter else 0
            out.append(f'<path transform="translate({x:.3f} {y + dy:.3f}) rotate({rot:.2f}) scale({k:.5f} {-k:.5f})" d="{d}"/>')
        x += hmtx[g][0] * k + track * size
    return f'<g fill="{color}">{"".join(out)}</g>'


# ---- pieces ------------------------------------------------------------------------
def back(gname):
    g = GARMENTS[gname]
    ln, ac = g['line'], g['accent']
    W, H = 290, 253
    lw, cx, top = 250, 145, 50
    lh = lw / A.LOGO_RATIO
    ring = outline_ring(cx, top, lw, *g['ring'],
                        drips=[(0.085, 15, 4.4), (0.215, 7, 3.4), (0.355, 24, 4.9), (0.515, 10, 3.6),
                               (0.655, 21, 5.2), (0.79, 8, 3.4), (0.95, 17, 4.5)])
    svg = [f'<path d="{to_path(ring)}" fill="{ln}" fill-rule="evenodd"/>']
    # above the piece
    svg.append(crown(58, 30, 40, ln, 2.3, rot=-12))
    svg += [stroke([(26, 26), (19, 21)], 1.8, ln, n=1), stroke([(31, 16), (28, 8)], 1.8, ln, n=1), stroke([(40, 11), (41, 3)], 1.8, ln, n=1)]
    svg.append(smiley(208, 26, 15, ac, 2.6))
    svg += [sparkle(100, 20, 6.5, ln), sparkle(117, 34, 3.4, ac), sparkle(254, 28, 7, ln), sparkle(272, 50, 3.6, ac),
            dot(142, 30, 1.6, ac), dot(164, 16, 1.2, ln), dot(238, 48, 1.4, ln), dot(12, 52, 1.3, ac)]
    yb = top + lh
    svg.append(brush([(22, yb + 24), (38, yb + 18), (58, yb + 14)], 4.0, ac, rough=0.03))
    svg.append(brush([(50, yb + 20), (56, yb + 23)], 2.2, ac))
    # tagline, marker handwriting
    ts = 28
    tag = (text('Kalam-700', 'Stay wrapped.', 0, 0, ts, ln, jitter=0.005)
           + text('Kalam-700', 'Stay protected.', 7, ts * 1.0, ts, ln, jitter=0.005))
    svg.append(f'<g transform="translate(44 {yb + 59}) rotate(-6)">{tag}</g>')
    svg += [sparkle(28, yb + 71, 5.2, ln), plus(258, yb + 39, 3.0, ln, 1.5), sparkle(262, yb + 69, 4.2, ac),
            dot(34, yb + 91, 1.3, ac)]
    # orange swoosh under the tagline
    sy = yb + 95
    svg.append(brush([(70, sy + 12), (115, sy + 8), (165, sy + 1), (215, sy - 9)], 7.0, ac, rough=0.035))
    svg.append(brush([(206, sy - 1), (219, sy - 3), (229, sy - 13)], 3.6, ac))
    S = BACK_W / W                       # drawn on a 290-unit grid, printed at BACK_W mm
    return (W * S, H * S, A.page(W * S, H * S, 'transparent', f'<g transform="scale({S:.6f})">{"".join(svg)}</g>',
                                 A.logo_slot(cx * S, (top + lh / 2) * S, lw * S)))


def chest(gname):
    g = GARMENTS[gname]
    ln, ac = g['line'], g['accent']
    W, H = 108, 60
    lw, cx, top = 90, 55, 18
    lh = lw / A.LOGO_RATIO
    ring = outline_ring(cx, top, lw, *g['ring'],
                        drips=[(0.12, 5.5, 1.9), (0.36, 9, 2.2), (0.66, 11, 2.3), (0.93, 6, 1.9)])
    svg = [f'<path d="{to_path(ring)}" fill="{ln}" fill-rule="evenodd"/>',
           crown(25, 9.2, 17, ln, 1.1, rot=-12),
           sparkle(8, 12, 2.6, ac), sparkle(46, 7, 2.0, ln), dot(40, 13, 0.7, ac),
           sparkle(97, 9, 2.8, ln), sparkle(103, 20, 1.5, ac), dot(88, 5, 0.6, ln),
           brush([(14, top + lh + 6.5), (22, top + lh + 4.6), (31, top + lh + 3.4)], 1.8, ac)]
    return W, H, A.page(W, H, 'transparent', ''.join(svg), A.logo_slot(cx, top + lh / 2, lw))


def neck(gname):
    g = GARMENTS[gname]
    ln, ac = g['line'], g['accent']
    W, H = 56, 30
    svg = [crown(W / 2, 5.4, 11, ln, 0.9, rot=0),
           text('Geist-600', 'Stay wrapped.', W / 2, 19, 7.2, ln, track=-0.02, anchor='middle'),
           text('Geist-600', 'Stay protected.', W / 2, 27, 7.2, ac, track=-0.02, anchor='middle')]
    return W, H, A.page(W, H, 'transparent', ''.join(svg), '')


def label():
    W, H = 20, 32                       # woven loop label, shown flat (folds at the dashed line)
    svg = [f'<rect x="0" y="0" width="{W}" height="{H}" rx="1" fill="{ORANGE}"/>',
           f'<line x1="0" y1="{H / 2}" x2="{W}" y2="{H / 2}" stroke="{LINE}" stroke-opacity=".35" stroke-width=".2" stroke-dasharray=".8 .8"/>',
           crown(W / 2, H * 0.75 + 0.6, 10, LINE, 0.85, rot=0),
           f'<g transform="rotate(180 {W / 2} {H / 4})">{crown(W / 2, H * 0.25 + 0.6, 10, LINE, 0.85, rot=0)}</g>']
    return W, H, A.page(W, H, 'transparent', ''.join(svg), '')


if __name__ == '__main__':
    jobs = []
    specs = [(f'tee-{g}-{part}', fn, g) for g in GARMENTS for part, fn in (('back', back), ('chest', chest), ('neck', neck))]
    for name, fn, g in specs + [('tee-label', lambda _: label(), None)]:
        W, H, doc = fn(g)
        p = os.path.join(HERE, 'html', name + '.html')
        open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=None, cmyk=False))
    json.dump(jobs, open(os.path.join(HERE, 'jobs_tee.json'), 'w'), indent=1)
    print([j['name'] for j in jobs])
