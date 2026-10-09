"""Spray bottle: logo-only die-cut sticker (vertical + horizontal), plus a mockup on the supplied bottle photo.

The sticker is the original vector logo with a white contour border. The cut line is a separate
spot colour named CutContour (the name most sticker printers' RIPs read as the cut path).
Usage: python3 bottle.py <repo> <bottle-photo.jpg>"""
import math, os, sys
import numpy as np
import pymupdf as fitz
from PIL import Image, ImageFilter
from shapely.geometry import Polygon
from shapely import affinity

HERE = os.path.dirname(os.path.abspath(__file__))
MM = 72 / 25.4
REPO, PHOTO = sys.argv[1], sys.argv[2]
OUT = os.path.join(REPO, 'retail', '01-spray-bottle')
os.makedirs(OUT, exist_ok=True)

LOGO = fitz.open(os.path.join(HERE, 'logo.pdf'))
LW, LH = LOGO[0].rect.width, LOGO[0].rect.height          # 219.12 x 79.92 pt = 77.3 x 28.2 mm
BORDER = 1.5                                              # white contour border, mm
MARGIN = 5.0                                              # sheet margin around the cut line, mm

# Each variant: logo length along its reading direction (mm) and whether it is turned to read bottom-to-top.
VARIANTS = [('vertical', 69.6, True), ('horizontal', 30.0, False)]


def silhouette():
    """The logo's outer shape (its white base path), flattened to a polygon in logo pt, y down."""
    d = next(dr for dr in LOGO[0].get_drawings() if dr.get('fill') == (1.0, 1.0, 1.0))
    pts = [(d['items'][0][1].x, d['items'][0][1].y)]
    for it in d['items']:
        if it[0] == 'l':
            pts.append((it[2].x, it[2].y))
        else:                                             # cubic bezier
            p0, p1, p2, p3 = it[1:5]
            for i in range(1, 17):
                t = i / 16
                a, b, c, e = (1 - t) ** 3, 3 * (1 - t) ** 2 * t, 3 * (1 - t) * t * t, t ** 3
                pts.append((a * p0.x + b * p1.x + c * p2.x + e * p3.x, a * p0.y + b * p1.y + c * p2.y + e * p3.y))
    poly = Polygon(pts)
    return poly if poly.is_valid else poly.buffer(0)


def path_ops(poly, H):
    """Shapely polygon in page pt (y down) -> PDF path operators (y up)."""
    rings = [poly.exterior] + list(poly.interiors)
    out = []
    for r in rings:
        c = list(r.coords)
        out.append('%.3f %.3f m' % (c[0][0], H - c[0][1]))
        out += ['%.3f %.3f l' % (x, H - y) for x, y in c[1:]]
        out.append('h')
    return '\n'.join(out)


def build(name, length, vertical):
    s = length / (LW / MM)                                # scale of the logo
    lw, lh = LW * s, LH * s                               # logo size in pt, unrotated
    shape = affinity.scale(silhouette(), s, s, origin=(0, 0))
    if vertical:                                          # turn 90 deg CCW: reads bottom-to-top
        shape = affinity.affine_transform(shape, [0, 1, -1, 0, 0, lw])   # (x, y) -> (y, lw - x)
        aw, ah = lh, lw
    else:
        aw, ah = lw, lh
    cut = shape.buffer(BORDER * MM, join_style=1, quad_segs=24).simplify(0.05)
    minx, miny, maxx, maxy = cut.bounds
    off = MARGIN * MM
    W, H = (maxx - minx) + 2 * off, (maxy - miny) + 2 * off
    dx, dy = off - minx, off - miny
    cut = affinity.translate(cut, dx, dy)

    doc = fitz.open()
    pg = doc.new_page(width=W, height=H)
    pg.show_pdf_page(fitz.Rect(dx, dy, dx + aw, dy + ah), LOGO, 0, rotate=90 if vertical else 0)
    logo_stream = pg.get_contents()
    # White border (no ink on white vinyl; it carries the border in previews and for a white-ink layer).
    under = doc.get_new_xref()
    doc.update_object(under, '<<>>')
    doc.update_stream(under, ('q 0 0 0 0 k\n%s\nf Q' % path_ops(cut, H)).encode())
    # Cut line: spot colour CutContour, 0.25 pt hairline, overprinted so it never knocks out the art.
    top = doc.get_new_xref()
    doc.update_object(top, '<<>>')
    doc.update_stream(top, ('q /GSop gs /CSCut CS 1 SCN 0.25 w 1 j\n%s\nS Q' % path_ops(cut, H)).encode())
    doc.xref_set_key(pg.xref, 'Contents', '[%d 0 R %s %d 0 R]' % (under, ' '.join('%d 0 R' % x for x in logo_stream), top))
    res = doc.xref_get_key(pg.xref, 'Resources')
    rx = int(res[1].split()[0]) if res[0] == 'xref' else pg.xref
    pre = '' if res[0] == 'xref' else 'Resources/'
    doc.xref_set_key(rx, pre + 'ColorSpace/CSCut',
                     '[/Separation /CutContour /DeviceCMYK <</FunctionType 2 /Domain [0 1] /C0 [0 0 0 0] /C1 [0 1 0 0] /N 1>>]')
    doc.xref_set_key(rx, pre + 'ExtGState/GSop', '<</Type /ExtGState /OP true /op true /OPM 1>>')
    cw, ch = (maxx - minx) / MM, (maxy - miny) / MM
    doc.set_metadata({'title': f'Wrapshap spray bottle sticker, {name}: {cw:.1f} x {ch:.1f} mm at the cut line',
                      'author': 'Wrapshap', 'creator': 'Wrapshap prepress'})
    base = f'wrapshap-bottle-sticker-{name}-{round(cw)}x{round(ch)}mm'
    doc.save(os.path.join(OUT, base + '-print.pdf'), garbage=4, deflate=True)
    doc.save(os.path.join(OUT, base + '.ai'), garbage=4, deflate=True)

    # Transparent preview of the cut sticker (no cut line), 600 dpi.
    prev = fitz.open(os.path.join(OUT, base + '-print.pdf'))
    p = prev[0]
    doc2 = fitz.open()
    q = doc2.new_page(width=W, height=H)
    q.draw_polyline([(x, y) for x, y in cut.exterior.coords], color=None, fill=(1, 1, 1), closePath=True)
    q.show_pdf_page(fitz.Rect(dx, dy, dx + aw, dy + ah), LOGO, 0, rotate=90 if vertical else 0)
    pix = q.get_pixmap(dpi=600, alpha=True)
    img = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples)
    k = 600 / 72
    img = img.crop((int(off * k) - 4, int(off * k) - 4, int((W - off) * k) + 4, int((H - off) * k) + 4))
    img.save(os.path.join(OUT, base + '-preview.png'))
    return img, (cw, ch), base


def mockup(sticker, size_mm, path):
    """Wrap the vertical sticker around the bottle in the supplied photo (cylinder seen from above)."""
    photo = Image.open(PHOTO).convert('RGB')
    P = np.asarray(photo).astype(np.float32) / 255
    Hh, Ww = P.shape[:2]
    # Bottle body edges measured on the photo (px): x at two heights, linear between them.
    y0, y1 = 600, 1150
    l0, l1, r0, r1 = 462, 488, 722, 710
    S = np.asarray(sticker).astype(np.float32) / 255
    sh, sw = S.shape[:2]
    cw, ch = size_mm
    ys, xs = np.mgrid[0:Hh, 0:Ww].astype(np.float32)
    t = (ys - y0) / (y1 - y0)
    left, right = l0 + (l1 - l0) * t, r0 + (r1 - r0) * t
    cx, r = (left + right) / 2, (right - left) / 2
    sx = np.clip((xs - cx) / r, -1, 1)
    theta = np.arcsin(sx)
    pxmm = (2 * r) / 38.0                                 # bottle assumed 38 mm across
    u = theta * 19.0                                      # arc length from front, mm
    bow = 0.45 * r * np.cos(theta)                        # rings bow downward toward the front (camera above)
    yc = 900                                              # sticker centre on the photo
    v = ((ys - bow) - (yc - 0.45 * np.interp(yc, [y0, y1], [(r0 - l0) / 2, (r1 - l1) / 2]))) / (pxmm * 0.87)
    su = (u / cw + 0.5) * sw
    sv = (v / ch + 0.5) * sh
    inside = (np.abs(sx) < 0.999) & (su >= 0) & (su < sw - 1) & (sv >= 0) & (sv < sh - 1)
    iu, iv = np.clip(su.astype(int), 0, sw - 1), np.clip(sv.astype(int), 0, sh - 1)
    col = S[iv, iu]
    a = np.where(inside, col[..., 3], 0)[..., None]
    shade = (0.72 + 0.28 * np.cos(theta))[..., None] * (0.96 + 0.04 * np.cos(theta * 3))[..., None]
    rgb = col[..., :3] * shade
    hl = np.exp(-((theta + 0.35) / 0.12) ** 2)[..., None] * 0.18      # soft specular stripe, matching the photo's light
    rgb = np.clip(rgb + hl, 0, 1)
    A = Image.fromarray((a[..., 0] * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(0.6))
    a = np.asarray(A).astype(np.float32)[..., None] / 255
    outp = P * (1 - a) + rgb * a
    Image.fromarray((outp * 255).astype(np.uint8)).save(path, quality=92)


results = {name: build(name, length, vert) for name, length, vert in VARIANTS}
tmp = []
for name in ('vertical', 'horizontal'):
    tmp.append(os.path.join(OUT, f'_mock-{name}.jpg'))
    mockup(results[name][0], results[name][1], tmp[-1])
ims = [Image.open(p).crop((250, 150, 950, 1350)) for p in tmp]
sheet = Image.new('RGB', (ims[0].width * 2 + 20, ims[0].height), 'white')
for i, im in enumerate(ims):
    sheet.paste(im, (i * (im.width + 20), 0))
sheet.save(os.path.join(OUT, 'wrapshap-bottle-mockup.jpg'), quality=90)
for p in tmp:
    os.remove(p)
for name, (_, size, base) in results.items():
    print(name, '%.1f x %.1f mm' % size, base)
