"""Spray-paint texture engine for the Graffiti option.

Each paint colour is a probability field on a page grid (cell = grain size in mm). Strokes,
swashes, dry-brush marks and spatter add paint into a field; `finalize` turns every field into
a 1-bit stochastic stipple — the same grain a spray can leaves. post.py places each mask in the
PDF as an ImageMask filled with one exact CMYK colour, so the grain stays crisp at any size.
"""
import math
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage


def catmull(points, per=60):
    pts = np.asarray(points, float)
    P = np.vstack([pts[0] * 2 - pts[1], pts, pts[-1] * 2 - pts[-2]])
    out = []
    for i in range(len(pts) - 1):
        p0, p1, p2, p3 = P[i], P[i + 1], P[i + 2], P[i + 3]
        for t in np.linspace(0, 1, per, endpoint=False):
            t2, t3 = t * t, t * t * t
            out.append(0.5 * (2 * p1 + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(pts[-1])
    return np.array(out)


def smoothstep(x):
    x = np.clip(x, 0, 1)
    return x * x * (3 - 2 * x)


class Paint:
    def __init__(self, W, H, cell, seed, k=1.0):
        self.W, self.H, self.cell, self.k = W, H, cell, k          # k scales texture feature sizes
        self.nx, self.ny = int(math.ceil(W / cell)), int(math.ceil(H / cell))
        self.rng = np.random.default_rng(seed)
        self.fields = {}

    # ---- helpers ----------------------------------------------------------------------
    def field(self, name):
        if name not in self.fields:
            self.fields[name] = np.zeros((self.ny, self.nx), np.float32)
        return self.fields[name]

    def _box(self, x0, y0, x1, y1):
        c = self.cell
        i0, j0 = max(0, int(x0 / c)), max(0, int(y0 / c))
        i1, j1 = min(self.nx, int(math.ceil(x1 / c))), min(self.ny, int(math.ceil(y1 / c)))
        return i0, j0, i1, j1

    def _merge(self, name, box, p):
        i0, j0, i1, j1 = box
        F = self.field(name)[j0:j1, i0:i1]
        F[:] = 1 - (1 - F) * (1 - np.clip(p, 0, 1))

    def noise(self, shape, scale_mm, octaves=2):
        """Smooth value noise, roughly N(0,1), feature size ~scale_mm."""
        h, w = shape
        tot = np.zeros(shape, np.float32)
        amp, s = 1.0, scale_mm / self.cell
        for _ in range(octaves):
            gh, gw = max(2, int(h / s) + 3), max(2, int(w / s) + 3)
            g = self.rng.standard_normal((gh, gw)).astype(np.float32)
            z = ndimage.zoom(g, (h / (gh - 2), w / (gw - 2)), order=3)
            z = np.pad(z, ((0, max(0, h - z.shape[0])), (0, max(0, w - z.shape[1]))), 'edge')
            tot += amp * z[:h, :w]
            amp, s = amp * 0.5, s / 2.3
        return tot / (tot.std() + 1e-6)

    def noise_aniso(self, shape, sy_mm, sx_mm):
        """Stretched noise (long along x): streaky breaks for dry brush."""
        h, w = shape
        gh, gw = max(2, int(h * self.cell / sy_mm) + 3), max(2, int(w * self.cell / sx_mm) + 3)
        g = self.rng.standard_normal((gh, gw)).astype(np.float32)
        z = ndimage.zoom(g, (h / (gh - 2), w / (gw - 2)), order=1)
        z = np.pad(z, ((0, max(0, h - z.shape[0])), (0, max(0, w - z.shape[1]))), 'edge')[:h, :w]
        return z / (z.std() + 1e-6)

    def _noise1d(self, n, waves=4):
        t = np.linspace(0, 1, n)
        v = np.zeros(n)
        for k in range(1, waves + 1):
            v += np.sin(t * math.pi * self.rng.uniform(1, 3.5) * k + self.rng.uniform(0, 6.28)) / k
        return v / (np.abs(v).max() + 1e-6)

    # ---- marks ------------------------------------------------------------------------
    def stroke(self, name, points, width, core=0.55, soft=0.45, pressure=1.0, halo=0.02, taper=(0.15, 0.15),
               blotch=0.1, blotch_mm=8.0, press_var=0.2):
        """Airbrush stroke along a smooth path: solid core that dissolves into grain."""
        line = catmull(points)
        pad = width * 2.2
        x0, y0 = line.min(0) - pad
        x1, y1 = line.max(0) + pad
        box = self._box(x0, y0, x1, y1)
        i0, j0, i1, j1 = box
        if i1 <= i0 or j1 <= j0:
            return
        lw, lh = i1 - i0, j1 - j0
        img = Image.new('I', (lw, lh), 0)
        dr = ImageDraw.Draw(img)
        pix = (line - [i0 * self.cell, j0 * self.cell]) / self.cell
        for k in range(len(pix) - 1):
            dr.line([tuple(pix[k]), tuple(pix[k + 1])], fill=k + 1, width=1)
        a = np.array(img)
        if not a.any():
            return
        dist, (iy, ix) = ndimage.distance_transform_edt(a == 0, return_indices=True)
        t = (a[iy, ix] - 1) / max(1, len(pix) - 2)
        tp = smoothstep(np.minimum(t / taper[0], (1 - t) / taper[1]))
        prof = self._noise1d(len(pix))
        pv = 1 + press_var * prof[np.clip((t * (len(pix) - 1)).astype(int), 0, len(pix) - 1)]
        w = width * (0.5 + 0.5 * tp) * pv
        d = dist * self.cell
        rc = w / 2 * core
        p = np.where(d < rc, 1.0, np.exp(-np.maximum(0, (d - rc) / (w / 2 * soft)) ** 1.6))
        p = p * pressure * (0.35 + 0.65 * tp) + halo * np.exp(-(d / (w * 1.4)) ** 2) * tp
        solid = d < rc * 0.9                                   # a real spray core is solid; grain lives in the falloff
        p = np.where(solid, p, p * np.clip(1 + blotch * self.noise(p.shape, blotch_mm * self.k), 0.2, 1.6))
        self._merge(name, box, p)

    def swash(self, name, x0, x1, yc, height, passes=4, tilt=0.0, seed_jitter=1.0):
        """Wide sprayed swash made of overlapping passes (like a can swept back and forth)."""
        r = self.rng
        band = height / passes
        for i in range(passes):
            y = yc + (i - (passes - 1) / 2) * band * 0.82 + r.normal(0, band * 0.12)
            xs = x0 + r.uniform(0, 0.12) * (x1 - x0) * seed_jitter
            xe = x1 - r.uniform(0, 0.16) * (x1 - x0) * seed_jitter
            mid = (xs + xe) / 2
            pts = [(xs, y + r.normal(0, band * .25)), (mid - (xe - xs) * .22, y + r.normal(0, band * .2)),
                   (mid + (xe - xs) * .22, y + r.normal(0, band * .2)), (xe, y + r.normal(0, band * .25))]
            pts = [(px, py + (px - (x0 + x1) / 2) * math.tan(tilt)) for px, py in pts]
            self.stroke(name, pts, band * 1.55, core=0.72, soft=0.32, halo=0.06, taper=(0.06, 0.1),
                        blotch=0.12, blotch_mm=10, press_var=0.12)
        # soft overspray cloud around the whole swash
        self.stroke(name, [(x0 - 2, yc), ((x0 + x1) / 2, yc), (x1 + 2, yc)], height * 1.05, core=0.0, soft=0.75,
                    pressure=0.1, halo=0.0, taper=(0.2, 0.2), blotch=0.5, blotch_mm=10)

    def dry_brush(self, name, p0, p1, width, bristles=140, dryness=0.6, load=0.55, bend=0.0, solid=0.0):
        """Dry-brush drag from p0 to p1: clumped, broken bristle streaks on rough 'paper',
        heavy paint where the brush lands, running dry and ragged towards the end."""
        r, c = self.rng, self.cell
        L = math.dist(p0, p1)
        ang = math.atan2(p1[1] - p0[1], p1[0] - p0[0])
        pad = width * 0.25
        nl, nw = int(L / c) + 1, int((width + 2 * pad) / c) + 1
        xs = np.arange(nl) * c
        rows = np.arange(nw)[:, None] * c - pad
        kk = self.k
        paper = self.noise_aniso((nw, nl), 0.3 * kk, 7.0 * kk) + 0.6 * self.noise_aniso((nw, nl), 0.18 * kk, 2.2 * kk)
        paper /= paper.std() + 1e-6
        streak = self.noise_aniso((nw, nl), 1.2 * kk, 18.0 * kk)
        cov = np.zeros((nw, nl), np.float32)
        inkmap = np.zeros((nw, nl), np.float32)
        clumps = [(r.beta(2, 2) * width, r.uniform(0.6, 1.2)) for _ in range(max(4, bristles // 9))]
        arc = bend * np.sin(xs / L * math.pi)
        for _ in range(bristles):
            cy, cstr = clumps[r.integers(len(clumps))]
            yb = np.clip(cy + r.normal(0, width * 0.07), -pad * 0.2, width + pad * 0.2)
            th = r.uniform(0.15, 1.1) * kk
            s = abs(r.normal(0, 0.05)) * L
            e = L * np.clip(r.normal(0.82, 0.18), 0.3, 1.02)
            k1 = max(3, int(L / (r.uniform(4, 16) * kk)))
            n1 = np.interp(xs, np.linspace(0, L, k1), r.standard_normal(k1))
            ink = cstr * r.uniform(0.75, 1.1) * (1 - dryness * (xs / L) ** 1.2) + 0.28 * n1
            ink = ink * np.clip((xs - s) / (0.02 * L + 1e-6), 0, 1) * np.clip((e - xs) / (0.06 * L + 1e-6), 0, 1)
            wob = r.uniform(0.2, 1.2) * kk * np.sin(xs / L * math.pi * r.uniform(0.3, 1.4) + r.uniform(0, 6.28))
            half = th / 2
            m = np.abs(rows - (yb + wob + arc)[None, :]) <= half
            inkmap = np.where(m, np.maximum(inkmap, ink[None, :]), inkmap)
            cov = np.maximum(cov, m)
        # paint sticks where there's enough ink for the local paper roughness
        arr = (cov > 0) & (inkmap + 0.22 * paper + 0.12 * streak > 0.72)
        # heavy load where the brush first touched down (ragged leading edge); with `solid`
        # the loaded body carries on for that fraction of the stroke, so type set on it stays clean
        lo = r.uniform(0.22, 0.4) * L
        lead = np.interp(rows[:, 0], np.linspace(-pad, width + pad, 12), np.abs(r.normal(0, 0.04, 12)) * L)[:, None]
        body = np.exp(-((rows - width / 2 - arc[None, :]) / (width * 0.44)) ** 6)
        tail_end = lead + solid * L + np.interp(rows[:, 0], np.linspace(-pad, width + pad, 9), r.normal(0, 0.05, 9) * L)[:, None]
        run = np.where(xs[None, :] < tail_end, 1.0, np.clip(1 - (xs[None, :] - tail_end) / lo, 0, 1) ** 1.2)
        heavy = (xs[None, :] > lead) & (run * load * 1.8 * body + 0.22 * paper > 0.55)
        arr = (arr | heavy).astype(np.float32)
        # map into the page
        cs, sn = math.cos(ang), math.sin(ang)
        corners = [(p0[0] + u * cs - v * sn, p0[1] + u * sn + v * cs) for u in (0, L) for v in (-width / 2 - pad - abs(bend), width / 2 + pad + abs(bend))]
        xsx, ysy = [q[0] for q in corners], [q[1] for q in corners]
        box = self._box(min(xsx), min(ysy), max(xsx), max(ysy))
        i0, j0, i1, j1 = box
        if i1 <= i0 or j1 <= j0:
            return
        X = (np.arange(i0, i1) + 0.5)[None, :] * c - p0[0]
        Y = (np.arange(j0, j1) + 0.5)[:, None] * c - p0[1]
        U = (X * cs + Y * sn) / c
        V = (-X * sn + Y * cs + width / 2 + pad) / c
        ui, vi = np.round(U).astype(int), np.round(V).astype(int)
        ok = (ui >= 0) & (ui < nl) & (vi >= 0) & (vi < nw)
        p = np.zeros(U.shape, np.float32)
        p[ok] = arr[vi[ok], ui[ok]]
        self._merge(name, box, p)

    def spatter(self, name, cx, cy, spread, n, rmin, rmax):
        """Flicked droplets: solid discs, bigger ones nearer the centre."""
        r, c = self.rng, self.cell
        for _ in range(n):
            ang = r.uniform(0, 2 * math.pi)
            dd = abs(r.normal(0, spread))
            x, y = cx + dd * math.cos(ang), cy + dd * math.sin(ang) * 0.8
            rad = rmin + (rmax - rmin) * r.random() ** 2.5 * math.exp(-dd / (spread * 1.5))
            box = self._box(x - rad - c, y - rad - c, x + rad + c, y + rad + c)
            i0, j0, i1, j1 = box
            if i1 <= i0 or j1 <= j0:
                continue
            X = (np.arange(i0, i1) + 0.5)[None, :] * c - x
            Y = (np.arange(j0, j1) + 0.5)[:, None] * c - y
            self._merge(name, box, ((X * X + Y * Y) <= rad * rad).astype(np.float32))

    # ---- queries / output --------------------------------------------------------------
    def bottom_edge(self, name, x, thr=0.92):
        """Lowest dense point of a colour at x (smoothed, so stray droplets don't count)."""
        i = min(self.nx - 1, max(0, int(x / self.cell)))
        k = max(1, int(1.5 / self.cell))
        col = ndimage.uniform_filter1d(self.field(name)[:, max(0, i - k):i + k + 1].mean(1), size=2 * k + 1)
        idx = np.where(col > thr)[0]
        return None if len(idx) == 0 else (idx.max() + 0.5) * self.cell

    def fade_edges(self, mm):
        """Soften every colour to nothing within `mm` of the artboard edge (garment prints: no hard cut)."""
        yy = (np.arange(self.ny) + 0.5)[:, None] * self.cell
        xx = (np.arange(self.nx) + 0.5)[None, :] * self.cell
        d = np.minimum(np.minimum(xx, self.W - xx), np.minimum(yy, self.H - yy))
        f = np.clip(d / mm, 0, 1) ** 1.5
        for v in self.fields.values():
            v *= f

    def finalize(self):
        """Stochastic 1-bit stipple per colour (True = paint)."""
        return {k: self.rng.random(v.shape, dtype=np.float32) < v for k, v in self.fields.items()}
