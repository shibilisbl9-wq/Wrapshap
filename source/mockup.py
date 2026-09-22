"""Flat t-shirt mockup (front + back) with the print artwork placed at true scale (size L)."""
import os, subprocess
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'fonts'))
OUT = os.path.join(HERE, 'mockup')
os.makedirs(OUT, exist_ok=True)

# print artwork -> transparent PNG at 12 px/mm (~305 dpi)
for n in ('tee-front', 'tee-back'):
    fitz.open(os.path.join(HERE, 'placed', n + '.pdf'))[0].get_pixmap(dpi=305, alpha=True).save(os.path.join(OUT, n + '.png'))
bw, bh = [v / 72 * 25.4 for v in fitz.open(os.path.join(HERE, 'placed', 'tee-back.pdf'))[0].rect[2:]]
fw, fh = [v / 72 * 25.4 for v in fitz.open(os.path.join(HERE, 'placed', 'tee-front.pdf'))[0].rect[2:]]

# flat tee, size L, units = mm, x centred, y = 0 at high point of shoulder
R = [(95, 0), (250, 35), (420, 190), (329, 290), (280, 246)]


def body_path():
    (nx, ny), (sx, sy), (tx, ty), (hx, hy), (ax, ay) = R
    p = f"M{-nx} {ny} L{-sx} {sy} L{-tx} {ty} L{-hx} {hy} L{-ax} {ay} "
    p += f"C{-ax + 4} 420 {-ax - 4} 600 {-ax - 5} 742 Q0 750 {ax + 5} 742 "
    p += f"C{ax + 4} 600 {ax - 4} 420 {ax} {ay} L{hx} {hy} L{tx} {ty} L{sx} {sy} L{nx} {ny} Z"
    return p


def tee(cx, back):
    front_neck = "M-95 0 C-95 125 95 125 95 0" if not back else "M-95 0 C-90 26 90 26 95 0"
    inner = '' if back else ('<path d="M-95 0 C-90 26 90 26 95 0 C95 125 -95 125 -95 0 Z" fill="#070708"/>'
                             '<path d="M-95 0 C-90 26 90 26 95 0" fill="none" stroke="#1E1E21" stroke-width="10"/>')
    art = (f'<image href="tee-back.png" x="{-bw / 2}" y="92" width="{bw}" height="{bh}"/>' if back else
           f'<image href="tee-front.png" x="{128 - fw / 2}" y="{150 - fh / 2}" width="{fw}" height="{fh}"/>')
    return f'''<g transform="translate({cx} 0)">
  <path d="{body_path()}" fill="#000" opacity=".22" filter="url(#sh)" transform="translate(0 16)"/>
  <path d="{body_path()}" fill="url(#cloth)"/>
  <path d="M{-R[4][0]} {R[4][1]} L{-R[3][0]} {R[3][1]} L{-R[2][0]} {R[2][1]} L{-R[1][0]} {R[1][1]} Z" fill="#000" opacity=".16"/>
  <path d="M{R[4][0]} {R[4][1]} L{R[3][0]} {R[3][1]} L{R[2][0]} {R[2][1]} L{R[1][0]} {R[1][1]} Z" fill="#000" opacity=".16"/>
  <path d="M{-R[4][0]} {R[4][1]} L{-R[1][0] + 8} {R[1][1] + 6}" stroke="#000" stroke-opacity=".35" stroke-width="2" fill="none"/>
  <path d="M{R[4][0]} {R[4][1]} L{R[1][0] - 8} {R[1][1] + 6}" stroke="#000" stroke-opacity=".35" stroke-width="2" fill="none"/>
  {inner}
  <path d="{front_neck}" fill="none" stroke="#1C1C1F" stroke-width="{18 if not back else 14}"/>
  <path d="{front_neck}" fill="none" stroke="#000" stroke-opacity=".5" stroke-width="1.4" transform="translate(0 {9 if not back else 7})"/>
  <path d="M-285 728 Q0 736 285 728" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="1.4"/>
  <path d="M{-R[3][0] + 6} {R[3][1] - 8} L{-R[2][0] + 8} {R[2][1] - 6}" fill="none" stroke="#000" stroke-opacity=".3" stroke-width="1.2"/>
  <path d="M{R[3][0] - 6} {R[3][1] - 8} L{R[2][0] - 8} {R[2][1] - 6}" fill="none" stroke="#000" stroke-opacity=".3" stroke-width="1.2"/>
  {art}
  <path d="{body_path()}" fill="url(#fold)" style="mix-blend-mode:multiply"/>
</g>'''


VB = (-560, -150, 2120, 1060)
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Geist Mono';font-weight:500;src:url('file://{FONTS}/GeistMono-500.ttf')}}
@font-face{{font-family:'Geist';font-weight:600;src:url('file://{FONTS}/Geist-600.ttf')}}
html,body{{margin:0;background:#E7E5E0}}
svg{{display:block}}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="3200" height="{3200 * VB[3] / VB[2]:.0f}" viewBox="{' '.join(map(str, VB))}">
<defs>
  <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
  <linearGradient id="cloth" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#121214"/><stop offset=".5" stop-color="#1A1A1D"/><stop offset="1" stop-color="#121214"/></linearGradient>
  <linearGradient id="fold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".8" stop-color="#fff" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity=".25"/></linearGradient>
</defs>
<text x="-500" y="-92" font-family="Geist Mono" font-weight="500" font-size="15" letter-spacing="3.4" fill="#6E6B64">WRAPSHAP — TEE</text>
<text x="1500" y="-92" text-anchor="end" font-family="Geist Mono" font-weight="500" font-size="15" letter-spacing="3.4" fill="#6E6B64">BLACK TEE · SIZE L · PRINT AT 100%</text>
{tee(0, False)}
{tee(1000, True)}
<text x="0" y="850" text-anchor="middle" font-family="Geist Mono" font-weight="500" font-size="15" letter-spacing="3.4" fill="#6E6B64">FRONT — LEFT CHEST {fw:.0f} MM</text>
<text x="1000" y="850" text-anchor="middle" font-family="Geist Mono" font-weight="500" font-size="15" letter-spacing="3.4" fill="#6E6B64">BACK — {bw:.0f} × {bh:.0f} MM</text>
</svg></body></html>"""
open(os.path.join(OUT, 'tee-mockup.html'), 'w').write(html)

shot = os.path.join(HERE, 'shot.mjs')
open(shot, 'w').write("""import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [html, out, w, h] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h } });
await p.goto('file://' + html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
await p.screenshot({ path: out, type: 'jpeg', quality: 92, clip: { x: 0, y: 0, width: +w, height: +h } }); await b.close();
""")
H = round(3200 * VB[3] / VB[2])
subprocess.run(['node', shot, os.path.join(OUT, 'tee-mockup.html'), os.path.join(OUT, 'tee-mockup.jpg'), '3200', str(H)], check=True)
print('mockup', 3200, H)
