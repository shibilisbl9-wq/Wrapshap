"""Flat polo mockup (front + back): black body, orange knit collar and cuffs, print at true scale (size L)."""
import os, subprocess
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'fonts'))
OUT = os.path.join(HERE, 'mockup')
os.makedirs(OUT, exist_ok=True)

for n in ('polo-front', 'polo-back'):
    fitz.open(os.path.join(HERE, 'placed', n + '.pdf'))[0].get_pixmap(dpi=305, alpha=True).save(os.path.join(OUT, n + '.png'))
bw, bh = [v / 72 * 25.4 for v in fitz.open(os.path.join(HERE, 'placed', 'polo-back.pdf'))[0].rect[2:]]
fw, fh = [v / 72 * 25.4 for v in fitz.open(os.path.join(HERE, 'placed', 'polo-front.pdf'))[0].rect[2:]]

KNIT = '#F39200'          # collar + cuffs (brand Orange)
KNIT_DK = '#C97800'
# flat polo, size L, mm; x centred, y = 0 at the high point of the shoulder
NK, SH, ST, SB, AP = (92, 0), (245, 32), (398, 180), (318, 262), (272, 232)
ux, uy = (ST[0] - SH[0]), (ST[1] - SH[1])
ul = (ux * ux + uy * uy) ** 0.5
ux, uy = ux / ul, uy / ul
CUFF = 24


def body():
    (nx, ny), (sx, sy), (tx, ty), (hx, hy), (ax, ay) = NK, SH, ST, SB, AP
    p = f"M{-nx} {ny} L{-sx} {sy} L{-tx} {ty} L{-hx} {hy} L{-ax} {ay} "
    p += f"C{-ax + 3} 420 {-ax - 6} 600 {-ax - 10} 742 Q0 750 {ax + 10} 742 "
    p += f"C{ax + 6} 600 {ax - 3} 420 {ax} {ay} L{hx} {hy} L{tx} {ty} L{sx} {sy} L{nx} {ny} Z"
    return p


def cuff(side):
    s = side
    t, h = (s * ST[0], ST[1]), (s * SB[0], SB[1])
    ti = (t[0] - s * CUFF * ux, t[1] - CUFF * uy)
    hi = (h[0] - s * CUFF * ux, h[1] - CUFF * uy)
    ribs = ''.join(
        f'<line x1="{t[0] - s * d * ux:.1f}" y1="{t[1] - d * uy:.1f}" x2="{h[0] - s * d * ux:.1f}" y2="{h[1] - d * uy:.1f}" '
        f'stroke="{KNIT_DK}" stroke-width=".8" stroke-opacity=".7"/>' for d in (5, 10, 15, 20))
    return (f'<path d="M{t[0]} {t[1]} L{h[0]} {h[1]} L{hi[0]:.1f} {hi[1]:.1f} L{ti[0]:.1f} {ti[1]:.1f} Z" fill="{KNIT}"/>' + ribs +
            f'<line x1="{ti[0]:.1f}" y1="{ti[1]:.1f}" x2="{hi[0]:.1f}" y2="{hi[1]:.1f}" stroke="#000" stroke-opacity=".35" stroke-width="1.2"/>')


def vents():
    return ''.join(f'<path d="M{s * 279} 742 L{s * 276} 706 M{s * 283} 706 L{s * 270} 706" stroke="#000" stroke-opacity=".55" '
                   f'stroke-width="1.6" fill="none"/>' for s in (-1, 1))


def front_collar():
    back_stand = f'<path d="M-92 2 C-60 -12 60 -12 92 2 L86 16 C55 4 -55 4 -86 16 Z" fill="{KNIT_DK}"/>'
    placket = ('<rect x="-15" y="58" width="30" height="128" rx="2" fill="#1C1C1F"/>'
               '<rect x="-15" y="58" width="30" height="128" rx="2" fill="none" stroke="#000" stroke-opacity=".55" stroke-width="1"/>'
               '<rect x="-11.5" y="61" width="23" height="122" rx="1.5" fill="none" stroke="#2E2E33" stroke-width=".6" stroke-dasharray="2 1.6"/>'
               + ''.join(f'<circle cx="0" cy="{y}" r="5.6" fill="#2A2A2E" stroke="#0A0A0B" stroke-width=".8"/>'
                         f'<circle cx="-1.6" cy="{y}" r=".8" fill="#0A0A0B"/><circle cx="1.6" cy="{y}" r=".8" fill="#0A0A0B"/>'
                         for y in (98, 138, 172)))
    wing = 'M-96 -2 C-104 30 -86 70 -60 102 L-15 64 C-26 44 -48 18 -72 6 Z'
    wings = (f'<path d="{wing}" fill="{KNIT}"/><path d="{wing}" fill="{KNIT}" transform="scale(-1 1)"/>'
             f'<path d="M-72 6 C-48 18 -26 44 -15 64" fill="none" stroke="{KNIT_DK}" stroke-width="1.6"/>'
             f'<path d="M-72 6 C-48 18 -26 44 -15 64" fill="none" stroke="{KNIT_DK}" stroke-width="1.6" transform="scale(-1 1)"/>'
             f'<path d="M-92 4 C-99 32 -83 70 -60 96" fill="none" stroke="{KNIT_DK}" stroke-width=".9" stroke-opacity=".8"/>'
             f'<path d="M-92 4 C-99 32 -83 70 -60 96" fill="none" stroke="{KNIT_DK}" stroke-width=".9" stroke-opacity=".8" transform="scale(-1 1)"/>')
    shadow = ('<path d="M-60 102 L-15 64 L15 64 L60 102 L15 76 L-15 76 Z" fill="#000" opacity=".35"/>')
    return back_stand + placket + shadow + wings


def back_collar():
    c = 'M-96 -2 C-60 16 60 16 96 -2 L104 30 C60 54 -60 54 -104 30 Z'
    return (f'<path d="{c}" fill="{KNIT}"/>'
            f'<path d="M-104 30 C-60 54 60 54 104 30" fill="none" stroke="#000" stroke-opacity=".3" stroke-width="1.4"/>'
            f'<path d="M-100 22 C-60 44 60 44 100 22" fill="none" stroke="{KNIT_DK}" stroke-width=".9"/>'
            f'<path d="M-98 12 C-60 32 60 32 98 12" fill="none" stroke="{KNIT_DK}" stroke-width=".9" stroke-opacity=".7"/>')


def polo(cx, back):
    shade = ''.join(f'<path d="M{s * AP[0]} {AP[1]} L{s * SB[0]} {SB[1]} L{s * ST[0]} {ST[1]} L{s * SH[0]} {SH[1]} Z" fill="#000" opacity=".16"/>'
                    f'<path d="M{s * AP[0]} {AP[1]} L{s * (SH[0] - 8)} {SH[1] + 6}" stroke="#000" stroke-opacity=".35" stroke-width="2" fill="none"/>'
                    for s in (-1, 1))
    art = (f'<image href="polo-back.png" x="{-bw / 2:.1f}" y="100" width="{bw:.1f}" height="{bh:.1f}"/>' if back else
           f'<image href="polo-front.png" x="{118 - fw / 2:.1f}" y="{152 - fh / 2:.1f}" width="{fw:.1f}" height="{fh:.1f}"/>')
    return f'''<g transform="translate({cx} 0)">
  <path d="{body()}" fill="#000" opacity=".22" filter="url(#sh)" transform="translate(0 16)"/>
  <path d="{body()}" fill="url(#cloth)"/>
  {shade}
  {cuff(-1)}{cuff(1)}
  {vents()}
  <path d="M-276 730 Q0 738 276 730" fill="none" stroke="#000" stroke-opacity=".35" stroke-width="1.4"/>
  {art}
  {back_collar() if back else front_collar()}
  <path d="{body()}" fill="url(#fold)" style="mix-blend-mode:multiply"/>
</g>'''


VB = (-560, -150, 2120, 1060)
H = round(3200 * VB[3] / VB[2])
lab = 'font-family="Geist Mono" font-weight="500" font-size="15" letter-spacing="3.4" fill="#6E6B64"'
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Geist Mono';font-weight:500;src:url('file://{FONTS}/GeistMono-500.ttf')}}
html,body{{margin:0;background:#E7E5E0}} svg{{display:block}}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="3200" height="{H}" viewBox="{' '.join(map(str, VB))}">
<defs>
  <filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>
  <linearGradient id="cloth" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0" stop-color="#121214"/><stop offset=".5" stop-color="#1A1A1D"/><stop offset="1" stop-color="#121214"/></linearGradient>
  <linearGradient id="fold" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".8" stop-color="#fff" stop-opacity="0"/>
    <stop offset="1" stop-color="#000" stop-opacity=".25"/></linearGradient>
</defs>
<text x="-500" y="-92" {lab}>WRAPSHAP — POLO</text>
<text x="1500" y="-92" text-anchor="end" {lab}>BLACK POLO · ORANGE COLLAR &amp; CUFFS · SIZE L · PRINT AT 100%</text>
{polo(0, False)}
{polo(1000, True)}
<text x="0" y="850" text-anchor="middle" {lab}>FRONT — LEFT CHEST LOGO {fw:.0f} MM</text>
<text x="1000" y="850" text-anchor="middle" {lab}>BACK — {bw:.0f} × {bh:.0f} MM, TOP ~90 MM BELOW BACK NECK SEAM</text>
</svg></body></html>"""
open(os.path.join(OUT, 'polo-mockup.html'), 'w').write(html)
shot = os.path.join(HERE, 'shot.mjs')
open(shot, 'w').write("""import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
const [html, out, w, h] = process.argv.slice(2);
const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: +w, height: +h } });
await p.goto('file://' + html); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
await p.screenshot({ path: out, type: 'jpeg', quality: 92, clip: { x: 0, y: 0, width: +w, height: +h } }); await b.close();
""")
subprocess.run(['node', shot, os.path.join(OUT, 'polo-mockup.html'),
                os.path.join(OUT, 'polo-mockup.jpg'), '3200', str(H)], check=True)
print('polo mockup', 3200, H)
