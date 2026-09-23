"""Vector paint generator for the Graffiti option: splats, drips, spray specks, sprayed strokes.

Everything is plain SVG geometry (paths, circles, ellipses) — no filters or blur — so it
stays crisp vector in PDF/AI and prints cleanly. All units are millimetres. Seeded, so
every layout is reproducible.
"""
import math, random


def _f(v):
    return f'{v:.2f}'


def smooth_closed(pts):
    """Closed Catmull-Rom spline through pts, as cubic Bezier path data."""
    n = len(pts)
    d = [f'M{_f(pts[0][0])} {_f(pts[0][1])}']
    for i in range(n):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[(i + 1) % n], pts[(i + 2) % n]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d.append(f'C{_f(c1[0])} {_f(c1[1])} {_f(c2[0])} {_f(c2[1])} {_f(p2[0])} {_f(p2[1])}')
    return ' '.join(d) + 'Z'


def circle(x, y, r):
    return f'<circle cx="{_f(x)}" cy="{_f(y)}" r="{_f(r)}"/>'


def ellipse(x, y, rx, ry, deg):
    return f'<ellipse cx="{_f(x)}" cy="{_f(y)}" rx="{_f(rx)}" ry="{_f(ry)}" transform="rotate({deg:.1f} {_f(x)} {_f(y)})"/>'


def splat(seed, cx, cy, R, arms=18, droplets=46, specks=90, squash=1.0, tilt=0.0, bias=None,
          spread=1.0, arm_len=1.0, arm_w=1.0, min_speck=0.08):
    """A thrown paint splat: lumpy core, tendrils that taper and end in beads, satellite drops
    and fine specks. `bias` (radians) is the throw direction: arms/drops lean that way."""
    rng = random.Random(seed)

    def place(ang, dist):
        x, y = dist * math.cos(ang), dist * math.sin(ang) * squash
        return cx + x * math.cos(tilt) - y * math.sin(tilt), cy + x * math.sin(tilt) + y * math.cos(tilt)

    def toward(a):
        return 0 if bias is None else math.cos(math.atan2(math.sin(a - bias), math.cos(a - bias)))

    # core: low-frequency wobble plus small lumps
    harm = [(k, rng.uniform(0.01, 0.05) / math.sqrt(k), rng.uniform(0, 6.283)) for k in range(2, 13)]
    lumps = [(rng.uniform(0, 6.283), rng.uniform(0.06, 0.2), R * rng.uniform(0.03, 0.12)) for _ in range(22)]
    pts = []
    for i in range(240):
        t = 2 * math.pi * i / 240
        r = R * (1 + sum(amp * math.sin(k * t + ph) for k, amp, ph in harm))
        for a, w, L in lumps:
            dt = math.atan2(math.sin(t - a), math.cos(t - a))
            r += L * math.exp(-(dt / w) ** 2)
        pts.append(place(t, r))
    out = [f'<path d="{smooth_closed(pts)}"/>']

    # tendrils: separate tapered shapes, so they thin out as they travel (real paint does)
    for _ in range(arms):
        a = rng.uniform(0, 2 * math.pi) if bias is None or rng.random() < 0.35 else bias + rng.gauss(0, 0.8 * spread)
        L = R * (0.12 + 1.5 * rng.random() ** 2.4) * arm_len * (1 + 0.6 * max(0, toward(a)))
        wb = R * rng.uniform(0.09, 0.2) * arm_w
        wt = wb * rng.uniform(0.22, 0.42)
        bend = rng.uniform(-0.12, 0.12)
        r0, r1 = R * 0.72, R + L
        left, right = [], []
        for j in range(9):
            u = j / 8
            aa = a + bend * u * u
            rr = r0 + (r1 - r0) * u
            w = wb + (wt - wb) * (u ** 0.7)
            da = (w / 2) / rr
            left.append(place(aa - da, rr))
            right.append(place(aa + da, rr))
        out.append(f'<path d="{smooth_closed(left + right[::-1])}"/>')
        tip = place(a + bend, r1)
        out.append(circle(tip[0], tip[1], wt * rng.uniform(0.7, 1.15)))
        if rng.random() < 0.55:                                   # a detached bead beyond the tip
            bx, by = place(a + bend * 1.1, r1 + wt * rng.uniform(1.4, 4))
            out.append(circle(bx, by, wt * rng.uniform(0.35, 0.8)))

    for _ in range(droplets):                                     # satellites, bigger + rounder near the core
        a = bias + rng.gauss(0, 0.8 * spread) if bias is not None and rng.random() < 0.6 else rng.uniform(0, 2 * math.pi)
        dn = 1.2 + rng.expovariate(1.3) * 1.2 * (1 + 0.5 * max(0, toward(a)))
        s = R * 0.075 * math.exp(-(dn - 1) * 0.8) * rng.uniform(0.3, 1.1)
        s = max(s, min_speck)                                     # never smaller than the print minimum
        x, y = place(a, R * dn)
        el = 1 + min(1.2, (dn - 1) * rng.uniform(0.1, 0.5))
        out.append(ellipse(x, y, s * el, s, math.degrees(a + tilt)))
    for _ in range(specks):                                       # fine spray specks
        a = rng.uniform(0, 2 * math.pi) if bias is None or rng.random() < 0.4 else bias + rng.gauss(0, spread)
        dn = 1.1 + rng.expovariate(0.9) * 1.4
        x, y = place(a, R * dn)
        out.append(circle(x, y, R * rng.uniform(0.003, 0.011) + min_speck))
    return '\n'.join(out)


def drip(x, y0, L, w, wob=0.0):
    """One running drip: stem from y0 (hidden under its source) down to a round bead."""
    b = w * 0.62
    xe = x + wob
    return (f'<path d="M{_f(x - w / 2)} {_f(y0 - w)} L{_f(x + w / 2)} {_f(y0 - w)} '
            f'C{_f(x + w / 2)} {_f(y0 + L * .45)} {_f(xe + w * .36)} {_f(y0 + L * .7)} {_f(xe + w * .34)} {_f(y0 + L)} '
            f'L{_f(xe - w * .34)} {_f(y0 + L)} '
            f'C{_f(xe - w * .36)} {_f(y0 + L * .7)} {_f(x - w / 2)} {_f(y0 + L * .45)} {_f(x - w / 2)} {_f(y0 - w)}Z"/>'
            + circle(xe, y0 + L, b))


def drip_band(seed, x0, x1, y_edge, depth, n, max_len, w=(1.0, 4.2), step=2.2, scale=1.0):
    """Paint poured along an edge: a wavy band from above y_edge down to ~depth, with n drips."""
    rng = random.Random(seed)
    w, step = (w[0] * scale, w[1] * scale), step * scale
    pts, x = [], x0 - 5
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    while x <= x1 + 5:
        xs_ = x / scale
        y = y_edge + depth * (0.55 + 0.25 * math.sin(xs_ / 9 + ph[0]) + 0.15 * math.sin(xs_ / 3.7 + ph[1])
                              + 0.08 * math.sin(xs_ / 1.6 + ph[2]))
        pts.append((x, y))
        x += step
    d = f'M{_f(x0 - 5)} {_f(y_edge - 10)} ' + ' '.join(f'L{_f(px)} {_f(py)}' for px, py in pts) + \
        f' L{_f(x1 + 5)} {_f(y_edge - 10)}Z'
    out = [f'<path d="{d}"/>']
    xs = sorted(rng.uniform(x0 + 2, x1 - 2) for _ in range(n))
    for x in xs:
        base = min(pts, key=lambda p: abs(p[0] - x))[1]
        L = max_len * (rng.random() ** 1.7) + 2
        ww = rng.uniform(*w) * (0.75 + 0.5 * min(1, L / max_len))
        out.append(drip(x, base, L, ww, rng.uniform(-0.4, 0.4)))
    return '\n'.join(out)


def splat_drips(seed, cx, cy, R, n, max_len, w=(0.8, 2.6), span=0.75, scale=1.0):
    """Drips running down from the lower edge of a splat core."""
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        x = cx + rng.uniform(-span, span) * R
        y0 = cy + math.sqrt(max(0.0, 1 - ((x - cx) / (R * 1.05)) ** 2)) * R * 0.82
        L = max_len * (rng.random() ** 1.5) + R * 0.1
        out.append(drip(x, y0, L, rng.uniform(*w) * scale, rng.uniform(-0.3, 0.3) * scale))
    return '\n'.join(out)


def spray_specks(seed, x0, y0, x1, y1, n, rmax=0.35, rmin=0.06):
    rng = random.Random(seed)
    return '\n'.join(circle(rng.uniform(x0, x1), rng.uniform(y0, y1), rng.uniform(0.08, rmax) * rng.random() ** 0.5 + rmin)
                     for _ in range(n))


def g(content, fill, opacity=None, extra=''):
    op = f' fill-opacity="{opacity}"' if opacity is not None else ''
    return f'<g fill="{fill}"{op}{extra}>{content}</g>'
