"""Flat mockup of the graffiti tee: black and white, front and back, prints at true scale (size L)."""
import os, subprocess
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'fonts'))
OUT = os.path.join(HERE, 'mockup')
os.makedirs(OUT, exist_ok=True)
MMPT = 25.4 / 72
SIZE = {}
for g in ('black', 'white'):
    for p in ('back', 'chest', 'neck'):
        n = f'tee-{g}-{p}'
        pg = fitz.open(os.path.join(HERE, 'placed', n + '.pdf'))[0]
        pg.get_pixmap(dpi=305, alpha=True).save(os.path.join(OUT, n + '.png'))
        SIZE[n] = (pg.rect.width * MMPT, pg.rect.height * MMPT)
fitz.open(os.path.join(HERE, 'placed', 'tee-label.pdf'))[0].get_pixmap(dpi=305, alpha=True).save(os.path.join(OUT, 'tee-label.png'))

CLOTH = {'black': dict(a='#121214', b='#1B1B1E', rib='#1D1D20', inner='#070708', seam=.35, fold=.28),
         'white': dict(a='#E9E9E6', b='#F7F7F5', rib='#E2E2DE', inner='#CFCFCB', seam=.14, fold=.12)}
R = [(95, 0), (262, 30), (430, 205), (340, 300), (290, 256)]          # boxy, dropped shoulder


def body_path():
    (nx, ny), (sx, sy), (tx, ty), (hx, hy), (ax, ay) = R
    p = f"M{-nx} {ny} L{-sx} {sy} L{-tx} {ty} L{-hx} {hy} L{-ax} {ay} "
    p += f"C{-ax + 3} 420 {-ax - 3} 600 {-ax - 4} 742 Q0 750 {ax + 4} 742 "
    p += f"C{ax + 3} 600 {ax - 3} 420 {ax} {ay} L{hx} {hy} L{tx} {ty} L{sx} {sy} L{nx} {ny} Z"
    return p


def img(name, x, y):
    w, h = SIZE[name]
    return f'<image href="{name}.png" x="{x - w / 2:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"/>'


def tee(cx, g, back):
    c = CLOTH[g]
    neck = "M-95 0 C-90 26 90 26 95 0" if back else "M-95 0 C-95 118 95 118 95 0"
    inner = '' if back else (f'<path d="M-95 0 C-90 26 90 26 95 0 C95 118 -95 118 -95 0 Z" fill="{c["inner"]}"/>'
                             + img(f'tee-{g}-neck', 0, 30)
                             + f'<path d="M-95 0 C-90 26 90 26 95 0" fill="none" stroke="{c["rib"]}" stroke-width="10"/>')
    art = img(f'tee-{g}-back', 0, 100) if back else img(f'tee-{g}-chest', 132, 118)
    lab = '' if back else ('<clipPath id="lc"><rect x="-10" y="0" width="20" height="16"/></clipPath>'
                           '<g transform="translate(-232 742)"><image href="tee-label.png" x="-10" y="-16" width="20" height="32" clip-path="url(#lc)"/></g>')
    arm = lambda s: (f'<path d="M{s * R[4][0]} {R[4][1]} L{s * R[3][0]} {R[3][1]} L{s * R[2][0]} {R[2][1]} L{s * R[1][0]} {R[1][1]} Z" '
                     f'fill="#000" opacity="{c["fold"] * .5}"/>'
                     f'<path d="M{s * R[4][0]} {R[4][1]} L{s * (R[1][0] - 10)} {R[1][1] + 6}" stroke="#000" stroke-opacity="{c["seam"]}" stroke-width="2" fill="none"/>'
                     f'<path d="M{s * (R[3][0] - 6)} {R[3][1] - 9} L{s * (R[2][0] - 8)} {R[2][1] - 7}" stroke="#000" stroke-opacity="{c["seam"]}" stroke-width="1.2" fill="none"/>')
    return f'''<g transform="translate({cx} 0)">
  <path d="{body_path()}" fill="#000" opacity=".2" filter="url(#sh)" transform="translate(0 16)"/>
  <path d="{body_path()}" fill="url(#cl-{g})"/>
  {arm(-1)}{arm(1)}
  {inner}
  <path d="{neck}" fill="none" stroke="{c['rib']}" stroke-width="{16 if not back else 13}"/>
  <path d="{neck}" fill="none" stroke="#000" stroke-opacity="{c['seam']}" stroke-width="1.4" transform="translate(0 {8 if not back else 6.5})"/>
  <path d="M-290 726 Q0 734 290 726" fill="none" stroke="#000" stroke-opacity="{c['seam']}" stroke-width="1.4"/>
  {art}{lab}
  <path d="{body_path()}" fill="url(#fold-{g})"/>
</g>'''


def grads():
    out = ''
    for g, c in CLOTH.items():
        out += (f'<linearGradient id="cl-{g}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{c["a"]}"/>'
                f'<stop offset=".5" stop-color="{c["b"]}"/><stop offset="1" stop-color="{c["a"]}"/></linearGradient>'
                f'<linearGradient id="fold-{g}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#000" stop-opacity="0"/>'
                f'<stop offset=".82" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#000" stop-opacity="{c["fold"]}"/></linearGradient>')
    return out


STEP = 920
VB = (-500, -150, 3 * STEP + 1000, 1080)
cap = lambda x, t: (f'<text x="{x}" y="860" text-anchor="middle" font-family="Geist Mono" font-weight="500" font-size="17" '
                    f'letter-spacing="3.6" fill="#6E6B64">{t}</text>')
bw, bh = SIZE['tee-black-back']
fw, fh = SIZE['tee-black-chest']
html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Geist Mono';font-weight:500;src:url('file://{FONTS}/GeistMono-500.ttf')}}
html,body{{margin:0;background:#D9D7D2}} svg{{display:block}}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="3600" height="{3600 * VB[3] / VB[2]:.0f}" viewBox="{' '.join(map(str, VB))}">
<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>{grads()}</defs>
<text x="-440" y="-92" font-family="Geist Mono" font-weight="500" font-size="17" letter-spacing="3.6" fill="#6E6B64">WRAPSHAP — GRAFFITI TEE</text>
<text x="{3 * STEP + 440}" y="-92" text-anchor="end" font-family="Geist Mono" font-weight="500" font-size="17" letter-spacing="3.6" fill="#6E6B64">SIZE L · PRINTS AT 100%</text>
{tee(0, 'black', False)}{tee(STEP, 'black', True)}{tee(2 * STEP, 'white', False)}{tee(3 * STEP, 'white', True)}
{cap(0, f'BLACK · FRONT — CHEST {fw:.0f} × {fh:.0f} MM')}{cap(STEP, f'BLACK · BACK — {bw:.0f} × {bh:.0f} MM')}
{cap(2 * STEP, 'WHITE · FRONT')}{cap(3 * STEP, 'WHITE · BACK')}
</svg></body></html>"""
p = os.path.join(OUT, 'tee-graffiti-mockup.html')
open(p, 'w').write(html)
H = round(3600 * VB[3] / VB[2])
subprocess.run(['node', os.path.join(HERE, 'shot.mjs'), p, os.path.join(OUT, 'tee-graffiti-mockup.jpg'), '3600', str(H)], check=True)
print('mockup', 3600, H)
