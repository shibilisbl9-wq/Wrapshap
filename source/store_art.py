"""Store artwork: the mobile poster and the counter-front panel, rebuilt from the references.

Raster assets come from Higgsfield (gpt_image_2_5, references in references/store-artwork/):
  plate.png   poster background: phone, peeling film, yellow splatter (no text)
  letter.png  "STAY PROTECTED." dry-brush lettering on black  -> traced to vector
  gl.png      counter, left graffiti (crown, splatter, scribble) on white -> traced to vector
  gr.png      counter, right graffiti (star, smiley, bolt, spray line) on white -> traced to vector

Everything else is vector and drawn here: the original logo (placed unchanged from logo.pdf),
the ghost logo, the icon row, labels (Montserrat, converted to outlines), dividers, the swoosh
and burst lines.

usage: python3 store_art.py <asset_dir> <out_dir>
needs: pymupdf, potracer, numpy, opencv-python-headless, shapely, fonttools; Montserrat variable TTF
       at <asset_dir>/Montserrat.ttf
"""
import io, os, sys
import numpy as np
import cv2
import potrace
import pymupdf as fitz
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer
from fontTools.pens.recordingPen import DecomposingRecordingPen
from shapely.geometry import Polygon
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS, OUT = sys.argv[1], sys.argv[2]
MM = 72 / 25.4
BLEED = 3.0
LOGO = fitz.open(os.path.join(HERE, 'logo.pdf'))
LW_PT, LH_PT = LOGO[0].rect.width, LOGO[0].rect.height


def hexc(h):
    return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))


WHITE = hexc('#FFFFFF')
CREAM = hexc('#F4EEE3')
POSTER_DIV = hexc('#5A5A5A')


# ---- low-level path drawing (all coordinates in mm, y down) -------------------
class Pen:
    """Collects closed subpaths of lines/cubics in mm and draws them onto a page in one go."""

    def __init__(self):
        self.subs = []

    def move(self, p):
        self.subs.append([tuple(p)])

    def line(self, p):
        self.subs[-1].append(('l', tuple(p)))

    def curve(self, c1, c2, p):
        self.subs[-1].append(('c', tuple(c1), tuple(c2), tuple(p)))

    def transformed(self, a, b, c, d, e, f):
        def T(p):
            return (a * p[0] + c * p[1] + e, b * p[0] + d * p[1] + f)
        out = Pen()
        for s in self.subs:
            out.subs.append([T(s[0])] + [(seg[0],) + tuple(T(q) for q in seg[1:]) for seg in s[1:]])
        return out

    def draw(self, page, fill, opacity=1.0, even_odd=True):
        sh = page.new_shape()
        for s in self.subs:
            cur = fitz.Point(s[0][0] * MM, s[0][1] * MM)
            start = cur
            for seg in s[1:]:
                pts = [fitz.Point(x * MM, y * MM) for x, y in seg[1:]]
                if seg[0] == 'l':
                    sh.draw_line(cur, pts[0])
                else:
                    sh.draw_bezier(cur, pts[0], pts[1], pts[2])
                cur = pts[-1]
            if abs(cur.x - start.x) > 1e-6 or abs(cur.y - start.y) > 1e-6:
                sh.draw_line(cur, start)
        sh.finish(fill=fill, color=None, even_odd=even_odd, fill_opacity=opacity, closePath=True)
        sh.commit()


def strokes(page, polylines, color, width, opacity=1.0):
    """Open/closed polylines and cubic runs as round-capped strokes. Each item is a list of
    ('M', p) / ('L', p) / ('C', c1, c2, p) / ('Z',) in mm."""
    sh = page.new_shape()
    for pl in polylines:
        cur = start = None
        for op in pl:
            if op[0] == 'M':
                cur = start = fitz.Point(op[1][0] * MM, op[1][1] * MM)
            elif op[0] == 'L':
                p = fitz.Point(op[1][0] * MM, op[1][1] * MM)
                sh.draw_line(cur, p)
                cur = p
            elif op[0] == 'C':
                c1, c2, p = (fitz.Point(x * MM, y * MM) for x, y in op[1:])
                sh.draw_bezier(cur, c1, c2, p)
                cur = p
            elif op[0] == 'Z':
                sh.draw_line(cur, start)
                cur = start
    sh.finish(color=color, fill=None, width=width * MM, lineCap=1, lineJoin=1, stroke_opacity=opacity,
              closePath=False)
    sh.commit()


# ---- tracing (Higgsfield rasters -> vector) -----------------------------------
def trace(mask, turd=3):
    """Binary mask -> Pen in pixel units (potrace, smooth curves)."""
    bm = potrace.Bitmap(~mask.astype(bool))            # potracer traces the dark (False) pixels
    plist = bm.trace(turdsize=turd, turnpolicy=potrace.POTRACE_TURNPOLICY_MINORITY, alphamax=1.0,
                     opticurve=True, opttolerance=0.2)
    pen = Pen()
    for curve in plist:
        pen.move((curve.start_point.x, curve.start_point.y))
        for seg in curve.segments:
            if seg.is_corner:
                pen.line((seg.c.x, seg.c.y))
                pen.line((seg.end_point.x, seg.end_point.y))
            else:
                pen.curve((seg.c1.x, seg.c1.y), (seg.c2.x, seg.c2.y), (seg.end_point.x, seg.end_point.y))
    return pen


def load(name, scale=1.0):
    img = cv2.imread(os.path.join(ASSETS, name), cv2.IMREAD_COLOR)
    if scale != 1.0:
        img = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
    return img


def mean_color(img, mask):
    b, g, r = (np.median(img[..., i][mask]) for i in range(3))
    return (r / 255, g / 255, b / 255)


def separate(img, bg):
    """Split a flat-colour artwork into yellow / white / black ink masks on a black or white bg."""
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = hsv[..., 0].astype(int), hsv[..., 1].astype(int), hsv[..., 2].astype(int)
    yellow = (h >= 12) & (h <= 40) & (s > 110) & (v > 120)
    if bg == 'black':
        white = (s < 60) & (v > 150)
        return {'yellow': yellow, 'white': white}
    black = (v < 110) & ~yellow
    return {'yellow': yellow, 'black': black}


def bbox(masks):
    m = np.logical_or.reduce(list(masks))
    ys, xs = np.nonzero(m)
    return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def place(pen, src_box, dst_box):
    """Fit src_box (px) inside dst_box (mm), preserving ratio, centred."""
    x0, y0, x1, y1 = src_box
    X0, Y0, X1, Y1 = dst_box
    k = min((X1 - X0) / (x1 - x0), (Y1 - Y0) / (y1 - y0))
    ox = X0 + ((X1 - X0) - (x1 - x0) * k) / 2 - x0 * k
    oy = Y0 + ((Y1 - Y0) - (y1 - y0) * k) / 2 - y0 * k
    return pen.transformed(k, 0, 0, k, ox, oy)


def clean(mask, open_px=0):
    m = mask.astype(np.uint8)
    if open_px:
        m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((open_px, open_px), np.uint8))
    return m.astype(bool)


# ---- type to outlines ---------------------------------------------------------
_F = {}


def font(wght):
    if wght not in _F:
        vf = TTFont(os.path.join(ASSETS, 'Montserrat.ttf'))
        f = instancer.instantiateVariableFont(vf, {'wght': wght})
        _F[wght] = (f.getGlyphSet(), f.getBestCmap(), f['hmtx'], f['head'].unitsPerEm)
    return _F[wght]


def text_pen(s, size, wght, track=0.0):
    """Glyph outlines; size = em in mm; baseline at y=0, starting x=0. Returns (pen, advance)."""
    gs, cmap, hmtx, upm = font(wght)
    k = size / upm
    pen, x = Pen(), 0.0
    for i, ch in enumerate(s):
        g = cmap[ord(ch)]
        rp = DecomposingRecordingPen(gs)
        gs[g].draw(rp)
        cur = None
        for op, args in rp.value:
            P = [(x + a * k, -b * k) for a, b in args]
            if op == 'moveTo':
                pen.move(P[0]); cur = P[0]
            elif op == 'lineTo':
                pen.line(P[0]); cur = P[0]
            elif op == 'curveTo':
                pen.curve(*P); cur = P[-1]
            elif op == 'qCurveTo':                      # TrueType quadratic splines -> cubics
                pts = list(P)
                for j in range(len(pts) - 1):
                    q = pts[j]
                    e = pts[j + 1] if j == len(pts) - 2 else ((pts[j][0] + pts[j + 1][0]) / 2,
                                                             (pts[j][1] + pts[j + 1][1]) / 2)
                    c1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
                    c2 = (e[0] + 2 / 3 * (q[0] - e[0]), e[1] + 2 / 3 * (q[1] - e[1]))
                    pen.curve(c1, c2, e); cur = e
        x += hmtx[g][0] * k + (track * size if i < len(s) - 1 else 0)
    return pen, x


def put_text(page, s, x, y, size, wght, color, track=0.0, anchor='middle'):
    pen, adv = text_pen(s, size, wght, track)
    if anchor == 'middle':
        x -= adv / 2
    pen.transformed(1, 0, 0, 1, x, y).draw(page, color, even_odd=False)


# ---- logo -----------------------------------------------------------------------
def logo_pens():
    """The logo's three layers (white rim, orange outline, yellow letters) as Pens in logo pt."""
    out = []
    for d in LOGO[0].get_drawings():
        pen, last = Pen(), None
        for it in d['items']:
            if it[0] == 'l':
                a, b = it[1], it[2]
                if last is None or abs(a.x - last.x) + abs(a.y - last.y) > 0.01:
                    pen.move((a.x, a.y))
                pen.line((b.x, b.y)); last = b
            elif it[0] == 'c':
                a, c1, c2, b = it[1:]
                if last is None or abs(a.x - last.x) + abs(a.y - last.y) > 0.01:
                    pen.move((a.x, a.y))
                pen.curve((c1.x, c1.y), (c2.x, c2.y), (b.x, b.y)); last = b
        out.append(pen)
    return out


LOGO_LAYERS = logo_pens()


def logo_silhouette_pen(grow_pt):
    """Outer silhouette of the logo grown by grow_pt (logo units), as a Pen."""
    polys = []
    for s in LOGO_LAYERS[0].subs:
        pts, cur = [], s[0]
        for seg in s[1:]:
            if seg[0] == 'l':
                pts.append(seg[1])
            else:
                p0, c1, c2, p3 = np.array(cur), *map(np.array, seg[1:])
                for t in np.linspace(0.1, 1, 10):
                    pts.append(tuple((1 - t) ** 3 * p0 + 3 * (1 - t) ** 2 * t * c1 + 3 * (1 - t) * t ** 2 * c2 + t ** 3 * p3))
            cur = seg[-1]
        if len(pts) > 2:
            polys.append(Polygon([s[0]] + pts).buffer(0))
    geom = unary_union(polys).buffer(0.5 + grow_pt, join_style='round', quad_segs=10)
    pen = Pen()
    for p in getattr(geom, 'geoms', [geom]):
        for ring in [p.exterior, *p.interiors]:
            c = list(ring.coords)
            pen.move(c[0])
            for q in c[1:]:
                pen.line(q)
    return pen


def place_logo(page, cx, top, width):
    """The original vector logo, unchanged. Returns its rect in mm."""
    h = width * LH_PT / LW_PT
    r = fitz.Rect((cx - width / 2) * MM, top * MM, (cx + width / 2) * MM, (top + h) * MM)
    page.show_pdf_page(r, LOGO, 0)
    return cx - width / 2, top, cx + width / 2, top + h


def logo_tf(cx, top, width):
    k = width / LW_PT
    return (k, 0, 0, k, cx - width / 2, top)


# ---- icons (24-unit grid, Lucide-style geometry) -----------------------------------
def icon(page, kind, cx, cy, size, color, sw):
    k = size / 24
    T = lambda x, y: (cx + (x - 12) * k, cy + (y - 12) * k)
    M = lambda x, y: ('M', T(x, y))
    L = lambda x, y: ('L', T(x, y))
    C = lambda a, b, c, d, e, f: ('C', T(a, b), T(c, d), T(e, f))
    if kind == 'clear':                                  # diamond
        P = [[M(6, 3), L(18, 3), L(22, 9), L(12, 22), L(2, 9), ('Z',)],
             [M(11, 3), L(8, 9), L(12, 22), L(16, 9), L(13, 3)],
             [M(2, 9), L(22, 9)]]
    elif kind == 'matte':                                # stacked layers
        P = [[M(12, 2), L(22, 7), L(12, 12), L(2, 7), ('Z',)],
             [M(2, 12), L(12, 17), L(22, 12)],
             [M(2, 17), L(12, 22), L(22, 17)]]
    elif kind == 'privacy':                              # eye with slash
        r = 3.2
        c = 0.5523 * r
        P = [[M(2, 12), C(5, 6.2, 9, 5, 12, 5), C(15, 5, 19, 6.2, 22, 12),
              C(19, 17.8, 15, 19, 12, 19), C(9, 19, 5, 17.8, 2, 12), ('Z',)],
             [M(12 + r, 12), C(12 + r, 12 + c, 12 + c, 12 + r, 12, 12 + r), C(12 - c, 12 + r, 12 - r, 12 + c, 12 - r, 12),
              C(12 - r, 12 - c, 12 - c, 12 - r, 12, 12 - r), C(12 + c, 12 - r, 12 + r, 12 - c, 12 + r, 12), ('Z',)],
             [M(5, 20.5), L(19, 3.5)]]
    elif kind == 'tuff':                                 # shield with tick
        P = [[M(12, 2), L(20, 5), L(20, 11), C(20, 16.5, 16.5, 20, 12, 22), C(7.5, 20, 4, 16.5, 4, 11), L(4, 5), ('Z',)],
             [M(8.5, 12), L(11, 14.5), L(15.8, 9.4)]]
    strokes(page, P, color, sw * k)


ROW = (('clear', 'CLEAR'), ('matte', 'MATTE'), ('privacy', 'PRIVACY'), ('tuff', 'TUFF'))


# ---- page helpers -------------------------------------------------------------------
def new_doc(W, H):
    doc = fitz.open()
    pg = doc.new_page(width=(W + 2 * BLEED) * MM, height=(H + 2 * BLEED) * MM)
    return doc, pg


def finish(doc, pg, W, H, stem, title, preview_bg=None):
    """preview_bg: flat colour behind the JPG preview only (not in the .ai / PDF)."""
    trim = fitz.Rect(BLEED * MM, BLEED * MM, (W + BLEED) * MM, (H + BLEED) * MM)
    pg.set_trimbox(trim)
    pg.set_bleedbox(pg.rect)
    doc.set_metadata({'title': title, 'author': 'Wrapshap', 'creator': 'Wrapshap store artwork (store_art.py)'})
    os.makedirs(OUT, exist_ok=True)
    doc.save(os.path.join(OUT, stem + '.ai'), garbage=3, deflate=True)
    doc.save(os.path.join(OUT, stem + '-print.pdf'), garbage=3, deflate=True)
    src = pg
    if preview_bg:
        tmp = fitz.open()
        src = tmp.new_page(width=pg.rect.width, height=pg.rect.height)
        src.draw_rect(src.rect, color=None, fill=preview_bg)
        src.show_pdf_page(src.rect, doc, pg.number)
    pix = src.get_pixmap(dpi=max(20, int(2400 / (W / 25.4))), clip=trim)
    pix.pil_save(os.path.join(OUT, stem + '.jpg'), quality=90)
    print('wrote', stem)


def jpeg_bytes(img_bgr, q=93):
    ok, buf = cv2.imencode('.jpg', img_bgr, [cv2.IMWRITE_JPEG_QUALITY, q])
    return buf.tobytes()


# =====================================================================================
# 1. Mobile poster
# =====================================================================================
def poster(W=600, H=900):
    doc, pg = new_doc(W, H)
    o = BLEED                                            # trim origin offset
    TW, TH = W + 2 * BLEED, H + 2 * BLEED
    pg.draw_rect(pg.rect, color=None, fill=(0, 0, 0))

    # background plate (Higgsfield), full bleed, cover-fit
    plate = load('plate.png')
    ph, pw = plate.shape[:2]
    k = max(TW / pw, TH / ph)
    rw, rh = pw * k, ph * k
    pg.insert_image(fitz.Rect((TW - rw) / 2 * MM, (TH - rh) / 2 * MM, (TW + rw) / 2 * MM, (TH + rh) / 2 * MM),
                    stream=jpeg_bytes(plate))

    # fade the plate to black behind the icon row (black, stepped opacity: prints as plain vector)
    y0, y1 = o + H * 0.765, o + H * 0.845
    n = 24
    for i in range(n):
        ya = y0 + (y1 - y0) * i / n
        pg.draw_rect(fitz.Rect(0, ya * MM, TW * MM, TH * MM), color=None, fill=(0, 0, 0), fill_opacity=1 / (n - i + 1))
    pg.draw_rect(fitz.Rect(0, y1 * MM, TW * MM, TH * MM), color=None, fill=(0, 0, 0))

    # ghost logo: the logo's own shapes, very dark, oversized and cropped at the top
    gw, gcx, gtop = W * 1.32, o + W * 0.5, o - H * 0.045
    tf = logo_tf(gcx, gtop, gw)
    for pen, col in zip(LOGO_LAYERS, ('#2C2410', '#1A160A', '#231D0C')):
        pen.transformed(*tf).draw(pg, hexc(col), even_odd=False)

    # main logo
    lw, lcx, ltop = W * 0.80, o + W * 0.475, o + H * 0.118
    lx0, ly0, lx1, ly1 = place_logo(pg, lcx, ltop, lw)
    put_text(pg, '®', lx1 + W * 0.012, ly1 - H * 0.012, W * 0.032, 700, WHITE, anchor='start')

    # STAY PROTECTED. (traced dry-brush lettering)
    img = load('letter.png', 0.6)
    m = separate(img, 'black')
    m = {c: clean(v, 2) for c, v in m.items()}
    box = bbox(m.values())
    dst = (o + W * 0.10, o + H * 0.285, o + W * 0.935, o + H * 0.478)
    for c in ('yellow', 'white'):
        place(trace(m[c], turd=6), box, dst).draw(pg, WHITE if c == 'white' else mean_color(img, m[c]))
    yellow = mean_color(img, m['yellow'])

    # icon row
    xs = [o + W * f for f in (0.165, 0.39, 0.61, 0.835)]
    cy, ty = o + H * 0.868, o + H * 0.925
    for x, (kind, lab) in zip(xs, ROW):
        icon(pg, kind, x, cy, W * 0.072, yellow, 1.55)
        put_text(pg, lab, x, ty, W * 0.026, 800, WHITE, track=0.04)
    for a, b in zip(xs, xs[1:]):
        x = (a + b) / 2
        strokes(pg, [[('M', (x, o + H * 0.838)), ('L', (x, o + H * 0.935))]], POSTER_DIV, W * 0.0018)
    finish(doc, pg, W, H, f'wrapshap-poster-mobile-{W}x{H}mm', 'Wrapshap - mobile poster')


# =====================================================================================
# 2. Counter panel
# =====================================================================================
ORANGE_LINE = hexc('#F3A20F')
DARK_RIM = hexc('#2B1D0E')


def counter(W=2400, H=450):
    """Graphics only, transparent background: it is printed and applied onto the wooden counter."""
    doc, pg = new_doc(W, H)
    o = BLEED
    TW, TH = W + 2 * BLEED, H + 2 * BLEED
    u = W / 1600                                          # reference band is 1600 px wide

    def P(px, py):                                        # reference px (band coords) -> page mm
        return o + px * u, o + py * u

    # graffiti, left and right (traced from Higgsfield)
    for name, dst in (('gl.png', (P(112, 48) + P(492, 298))), ('gr.png', (P(1232, 12) + P(1512, 262)))):
        img = load(name, 0.55)
        m = separate(img, 'white')
        box = bbox(m.values())
        for c in ('yellow', 'black'):
            col = mean_color(img, m[c]) if c == 'yellow' else hexc('#121110')
            place(trace(m[c], turd=2), box, dst).draw(pg, col)

    # white burst lines at the logo's top-left
    burst = [[('M', P(470, 92)), ('L', P(505, 99))],
             [('M', P(478, 58)), ('L', P(506, 80))],
             [('M', P(500, 35)), ('L', P(516, 68))]]
    strokes(pg, burst, WHITE, 5.2 * u)

    # logo: soft shadow + thin dark rim around the original logo's white edge
    lw = 490 * u
    lcx, ltop = P(800, 20)
    tf = logo_tf(lcx, ltop, lw)
    sk = lw / LW_PT
    for i, (grow, a) in enumerate(((5.0, 0.10), (3.6, 0.14), (2.4, 0.18))):
        logo_silhouette_pen(grow).transformed(sk, 0, 0, sk, lcx - lw / 2 + 0.6 * u, ltop + 2.6 * u).draw(
            pg, (0, 0, 0), opacity=a, even_odd=False)
    logo_silhouette_pen(1.5).transformed(*tf).draw(pg, DARK_RIM, even_odd=False)
    lx0, ly0, lx1, ly1 = place_logo(pg, lcx, ltop, lw)
    put_text(pg, '®', lx1 - 2 * u, ly1 - 26 * u, 15 * u, 700, CREAM, anchor='start')

    # tagline, swoosh
    x, y = P(805, 194)
    put_text(pg, 'STAY PROTECTED.', x, y, 19.5 * u, 600, CREAM, track=0.34)
    sw = Pen()
    x0, yb = P(745, 209)
    x1, _ = P(872, 209)
    L = x1 - x0
    sw.move((x0, yb + 1.8 * u))
    sw.curve((x0 + L * 0.35, yb - 1.2 * u), (x0 + L * 0.7, yb - 2.6 * u), (x1, yb - 2.2 * u))
    sw.curve((x1 + 1.2 * u, yb - 1.6 * u), (x1 + 0.6 * u, yb - 0.4 * u), (x1 - 2 * u, yb - 0.2 * u))
    sw.curve((x0 + L * 0.7, yb + 0.6 * u), (x0 + L * 0.35, yb + 2.2 * u), (x0, yb + 3.4 * u))
    sw.curve((x0 - 1.2 * u, yb + 3.0 * u), (x0 - 1.2 * u, yb + 2.0 * u), (x0, yb + 1.8 * u))
    sw.draw(pg, ORANGE_LINE, even_odd=False)

    # icon row
    cols = (600, 735, 876, 1002)
    for px, (kind, lab) in zip(cols, ROW):
        cx, cy = P(px, 244)
        icon(pg, kind, cx, cy, 34 * u, CREAM, 1.5)
        tx, ty = P(px, 282)
        put_text(pg, lab, tx, ty, 11.5 * u, 700, CREAM, track=0.16)
    for px in (667, 806, 946):
        strokes(pg, [[('M', P(px, 228)), ('L', P(px, 282))]], ORANGE_LINE, 2.6 * u)

    finish(doc, pg, W, H, f'wrapshap-counter-panel-{W}x{H}mm', 'Wrapshap - counter panel',
           preview_bg=hexc('#7A5838'))


if __name__ == '__main__':
    which = os.environ.get('ONLY', 'poster,counter').split(',')
    if 'poster' in which:
        poster()
    if 'counter' in which:
        counter()
