"""Shared hand-drawn primitives for the concept-mockup options (C, D, E). Numpy only —
no shapely/fontTools — so these run in an environment that only has the base pipeline deps.
"""
import math
import numpy as np


def wob(pts, amt, rng):
    pts = np.asarray(pts, float)
    return pts + (rng.normal(0, amt, pts.shape) if amt else 0)


def poly_d(pts, close=False):
    s = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts)
    return s + ('Z' if close else '')


def smooth(pts, n=10):
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


def stroke(pts, w, color, n=10, jitter=0.0, rng=None, close=False):
    c = smooth(wob(pts, jitter, rng) if jitter else np.asarray(pts, float), n)
    if close:
        c = np.vstack([c, c[:1]])
    return (f'<path d="{poly_d(c)}" fill="none" stroke="{color}" stroke-width="{w:.2f}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def blob(cx, cy, r, seed, n=9, jitter=0.3, squash=1.0):
    """A closed, organic 'lava lamp' silhouette: n points around a circle, radius jittered,
    smoothed through Catmull-Rom. Returns a path `d` string, centred on (cx, cy)."""
    rng = np.random.default_rng(seed)
    a = np.linspace(0, 2 * math.pi, n, endpoint=False)
    rr = r * (1 + rng.uniform(-jitter, jitter, n))
    pts = np.stack([cx + np.cos(a) * rr, cy + np.sin(a) * rr * squash], 1)
    pts = np.vstack([pts, pts[:3]])                     # wrap so the closed curve joins cleanly
    c = smooth(pts, 14)[:n * 14]                        # keep exactly the n segments of the cycle
    return poly_d(np.vstack([c, c[:1]]))


# ---- icon library: each draws inside a unit box centred on the origin ----
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


def ic_x(w, color, sw, rng):
    k = w * 0.36
    a = stroke([(-k, -k), (k, k)], sw, color, n=1, jitter=0.03 * w, rng=rng)
    b = stroke([(-k, k), (k, -k)], sw, color, n=1, jitter=0.03 * w, rng=rng)
    return a + b


def ic_arrow(w, color, sw, rng):
    pts = [(-w * 0.42, w * 0.3), (w * 0.1, -w * 0.28), (w * 0.44, w * 0.1)]
    shaft = stroke(pts, sw, color, n=8, jitter=0.02 * w, rng=rng)
    hx, hy = pts[-1]
    head = stroke([(hx - w * 0.16, hy - w * 0.2), (hx, hy), (hx - w * 0.2, hy + w * 0.04)], sw, color, n=4, rng=rng)
    return shaft + head


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
