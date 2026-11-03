"""Wrapshap package-side sticker, black + white. 42 x 76 mm, CMYK, 100% vector.

Source: source-sticker.ai (the Illustrator file, opened as PDF). Everything in it
is kept as-is except:
  1. the QR code     -> regenerated for INSTAGRAM_URL
  2. the website line -> WEBSITE, set in the brand headline font
                        (Big Shoulders Stencil Display Black) as outlines
  3. white version   -> background white, cream text/icons black; yellow,
                        logo and QR untouched
Run:  python3 build.py      (needs: pymupdf, segno, fonttools)
"""
import os, re
import pymupdf as fitz, segno
from fontTools.ttLib import TTFont
from fontTools.pens.basePen import BasePen

INSTAGRAM_URL = "https://www.instagram.com/wrapshappk/"
WEBSITE = "WRAPSHAP.PR"
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = f"{HERE}/BigShouldersStencilDisplay-Black.ttf"

YELLOW, BLACK, WHITE = "0.1 0.18 0.9 0", "0 0 0 1", "0 0 0 0"
RICH_BLACK, CREAM, CREAM2 = "0.6 0.4 0.4 1", "0.03 0.03 0.07 0", "0.039 0.035 0.07 0"

# ---------- text -> PDF outline ops ----------------------------------------
class PdfPen(BasePen):
    def __init__(s, gs, sc, dx, dy):
        super().__init__(gs); s.o = []; s.sc, s.dx, s.dy = sc, dx, dy; s.cur = (0, 0)
    def P(s, p): return f"{p[0]*s.sc+s.dx:.3f} {p[1]*s.sc+s.dy:.3f}"
    def _moveTo(s, p): s.o.append(s.P(p)+" m"); s.cur = p
    def _lineTo(s, p): s.o.append(s.P(p)+" l"); s.cur = p
    def _curveToOne(s, a, b, c): s.o.append(f"{s.P(a)} {s.P(b)} {s.P(c)} c"); s.cur = c
    def _qCurveToOne(s, a, b):
        p0 = s.cur
        c1 = (p0[0]+2/3*(a[0]-p0[0]), p0[1]+2/3*(a[1]-p0[1]))
        c2 = (b[0]+2/3*(a[0]-b[0]), b[1]+2/3*(a[1]-b[1]))
        s._curveToOne(c1, c2, b)
    def _closePath(s): s.o.append("h")

def text_ops(txt, cx, baseline, cap_h, tracking=0.04):
    f = TTFont(FONT); gs = f.getGlyphSet(); cmap = f.getBestCmap()
    capu = f["OS/2"].sCapHeight; sc = cap_h / capu
    names = [cmap[ord(ch)] for ch in txt]
    adv = [f["hmtx"][n][0]*sc for n in names]
    track = tracking * cap_h / 0.7
    width = sum(adv) + track*(len(txt)-1)
    x = cx - width/2; ops = []
    for n, a in zip(names, adv):
        pen = PdfPen(gs, sc, x, baseline); gs[n].draw(pen); ops += pen.o
        x += a + track
    return "\n".join(ops) + "\nf\n", width

# ---------- QR -> PDF ops (same box as the original QR) ---------------------
def qr_ops():
    m = segno.make(INSTAGRAM_URL, error="m", boost_error=False).matrix
    n = len(m)
    px, py, pw = 19.984, 69.591, 79.087            # white panel (PDF coords)
    size = 57.0; mod = size/n
    x0 = px + (pw-size)/2; ytop = py + (pw+size)/2
    o = [f"{BLACK} k"]
    for r, row in enumerate(m):
        for c, v in enumerate(row):
            if v: o.append(f"{x0+c*mod:.3f} {ytop-(r+1)*mod:.3f} {mod+0.02:.3f} {mod+0.02:.3f} re")
    o.append("f")
    return "\n".join(o) + "\n", n, mod

def build(mode):
    doc = fitz.open(f"{HERE}/source-sticker.ai"); page = doc[0]
    s = page.read_contents().decode("latin1")
    # 1. QR: replace the run of 2.299pt modules after the white panel
    qr, n, mod = qr_ops()
    a = s.index("19.984 69.591 79.087 79.087 re\nf*\n") + len("19.984 69.591 79.087 79.087 re\nf*\n")
    m = re.compile(r"(?:0 0 0 1 k\n)?(?:[\d.]+ [\d.]+ 2\.299 2\.299 re\nf\*\n)+").match(s, a)
    assert m, "QR block not found"
    s = s[:a] + qr + s[m.end():]
    # 2. website line: drop the live text, add outlined stencil text after ET
    old = re.search(r"0\.1 0\.18 0\.9 0 k\n/TT1 1 Tf\n6\.5 0 0 6\.5 38\.0776 24\.3779 Tm\n\(WRAPSHAP\.AE\)Tj\n", s)
    assert old, "website text not found"
    s = s[:old.start()] + "/TT1 1 Tf\n" + s[old.end():]
    web, w = text_ops(WEBSITE, 59.53, 23.6, 6.4)
    col = YELLOW if mode == "black" else BLACK
    et = s.index("ET\n", old.start()) + 3
    s = s[:et] + f"q\n{col} k\n{web}Q\n" + s[et:]
    # 3. white version: recolour background + cream elements only
    if mode == "white":
        s = s.replace(f"{RICH_BLACK} k", f"{WHITE} k", 1)
        for c in (CREAM, CREAM2):
            s = s.replace(f"{c} k", f"{BLACK} k").replace(f"{c} K", f"{BLACK} K")
    doc.update_stream(page.get_contents()[0], s.encode("latin1"))
    doc.set_metadata({"title": f"Wrapshap package sticker ({mode})", "creator": "Wrapshap"})
    out = f"{HERE}/wrapshap-sticker-{mode}.pdf"
    doc.save(out, garbage=3, deflate=True)
    page = fitz.open(out)[0]
    page.get_pixmap(dpi=600).save(f"{HERE}/wrapshap-sticker-{mode}.png")
    print(mode, f"QR {n}x{n} modules, {mod*25.4/72:.2f} mm each; website width {w*25.4/72:.1f} mm")

for mode in ("black", "white"):
    build(mode)
