"""Flat mockups of the six-design t-shirt collection (size L, prints at true scale).

Writes mockup/collection-overview.jpg (the six shirts in a row, like the reference board)
and mockup/collection-d<N>.jpg (each design on its own, front and/or back).
"""
import os, subprocess
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.abspath(os.path.join(HERE, '..', 'fonts'))
OUT = os.path.join(HERE, 'mockup')
os.makedirs(OUT, exist_ok=True)
MMPT = 25.4 / 72

CLOTH = {'black': dict(a='#121214', b='#1B1B1E', rib='#1D1D20', inner='#070708', seam=.35, fold=.28),
         'white': dict(a='#E9E9E6', b='#F7F7F5', rib='#E2E2DE', inner='#CFCFCB', seam=.14, fold=.12),
         'cream': dict(a='#E6DFCC', b='#F2ECDD', rib='#E0D8C3', inner='#C9C0AA', seam=.14, fold=.12),
         'orange': dict(a='#E88900', b='#F69A14', rib='#E48600', inner='#B86A00', seam=.2, fold=.16)}
R = [(95, 0), (262, 30), (430, 205), (340, 300), (290, 256)]          # boxy, dropped shoulder (as tee_mockup.py)

# design -> (shirt colour, name, views); a view = (side, [(piece, x, y, anchor)][, caption]); x is the piece centre
# ('c') or its left edge ('l'), in mm from the shirt's centre line; y is the top edge below the shoulder line.
DESIGNS = [
    ('black', 'Signature Graffiti', [('back', [('tee-black-back', 0, 100, 'c')]),
                                     ('front', [('tee-black-chest', 132, 118, 'c')])]),
    ('white', 'Playful Character', [('back', [('c2-back', 0, 88, 'c')])]),
    ('black', 'Minimal Bold', [('front', [('c3-front', 0, 140, 'c')])]),
    ('cream', 'Abstract', [('back', [('c4-back', 0, 80, 'c')])]),
    ('black', 'Clean Tagline', [('front', [('c5-chest', 14, 112, 'l')]),
                                ('back', [('c5-back-neck', 0, 44, 'c')], 'OPTIONAL BACK-NECK LOGO')]),
    ('orange', 'Vertical Bold', [('back', [('c6-back', -36, 55, 'l')])]),
]

SIZE = {}


def piece(name):
    if name not in SIZE:
        pg = fitz.open(os.path.join(HERE, 'placed', name + '.pdf'))[0]
        pg.get_pixmap(dpi=150, alpha=True).save(os.path.join(OUT, name + '.png'))
        SIZE[name] = (pg.rect.width * MMPT, pg.rect.height * MMPT)
    return SIZE[name]


def body_path():
    (nx, ny), (sx, sy), (tx, ty), (hx, hy), (ax, ay) = R
    p = f"M{-nx} {ny} L{-sx} {sy} L{-tx} {ty} L{-hx} {hy} L{-ax} {ay} "
    p += f"C{-ax + 3} 420 {-ax - 3} 600 {-ax - 4} 742 Q0 750 {ax + 4} 742 "
    p += f"C{ax + 3} 600 {ax - 3} 420 {ax} {ay} L{hx} {hy} L{tx} {ty} L{sx} {sy} L{nx} {ny} Z"
    return p


def img(name, x, y, anchor='c'):
    w, h = piece(name)
    left = x - w / 2 if anchor == 'c' else x
    return f'<image href="{name}.png" x="{left:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}"/>'


def tee(cx, g, side, prints, uid):
    c = CLOTH[g]
    back = side == 'back'
    neck = "M-95 0 C-90 26 90 26 95 0" if back else "M-95 0 C-95 118 95 118 95 0"
    inner = ''
    if not back:
        piece('tee-black-neck')
        piece('tee-label')
        inner = (f'<path d="M-95 0 C-90 26 90 26 95 0 C95 118 -95 118 -95 0 Z" fill="{c["inner"]}"/>'
                 + (img('tee-black-neck', 0, 30) if g == 'black' else '')
                 + f'<path d="M-95 0 C-90 26 90 26 95 0" fill="none" stroke="{c["rib"]}" stroke-width="10"/>')
    lab = '' if back else (f'<clipPath id="lc{uid}"><rect x="-10" y="0" width="20" height="16"/></clipPath>'
                           f'<g transform="translate(232 742)"><image href="tee-label.png" x="-10" y="-16" width="20" height="32" '
                           f'clip-path="url(#lc{uid})"/></g>')
    arm = lambda s: (f'<path d="M{s * R[4][0]} {R[4][1]} L{s * R[3][0]} {R[3][1]} L{s * R[2][0]} {R[2][1]} L{s * R[1][0]} {R[1][1]} Z" '
                     f'fill="#000" opacity="{c["fold"] * .5}"/>'
                     f'<path d="M{s * R[4][0]} {R[4][1]} L{s * (R[1][0] - 10)} {R[1][1] + 6}" stroke="#000" stroke-opacity="{c["seam"]}" stroke-width="2" fill="none"/>'
                     f'<path d="M{s * (R[3][0] - 6)} {R[3][1] - 9} L{s * (R[2][0] - 8)} {R[2][1] - 7}" stroke="#000" stroke-opacity="{c["seam"]}" stroke-width="1.2" fill="none"/>')
    art = ''.join(img(n, x, y, a) for n, x, y, a in prints)
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


def label(x, y, size, text, weight=500, fill='#3A3834', spacing=3.6):
    return (f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Geist" font-weight="{weight}" font-size="{size}" '
            f'letter-spacing="{spacing}" fill="{fill}">{text}</text>')


def render(name, shirts, captions, header, px_w=3600):
    step = 920
    n = len(shirts)
    vb = (-500, -150, (n - 1) * step + 1000, 1120)
    H = round(px_w * vb[3] / vb[2])
    body = ''.join(tee(i * step, g, side, prints, f'{name}{i}') for i, (g, side, prints) in enumerate(shirts))
    caps = ''.join(label(i * step, 862, 30, top, 600, '#2A2926', 3) + label(i * step, 904, 21, sub, 500, '#55524C', 3.4)
                   for i, (top, sub) in enumerate(captions))
    html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:'Geist';font-weight:500;src:url('file://{FONTS}/Geist-500.ttf')}}
@font-face{{font-family:'Geist';font-weight:600;src:url('file://{FONTS}/Geist-600.ttf')}}
html,body{{margin:0;background:#D2D0CB}} svg{{display:block}}
</style></head><body>
<svg xmlns="http://www.w3.org/2000/svg" width="{px_w}" height="{H}" viewBox="{' '.join(map(str, vb))}">
<defs><filter id="sh" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="14"/></filter>{grads()}</defs>
<text x="-440" y="-92" font-family="Geist" font-weight="500" font-size="17" letter-spacing="3.6" fill="#6E6B64">{header[0]}</text>
<text x="{(n - 1) * step + 440}" y="-92" text-anchor="end" font-family="Geist" font-weight="500" font-size="17" letter-spacing="3.6" fill="#6E6B64">{header[1]}</text>
{body}{caps}
</svg></body></html>"""
    p = os.path.join(OUT, name + '.html')
    open(p, 'w').write(html)
    subprocess.run(['node', os.path.join(HERE, 'shot.mjs'), p, os.path.join(OUT, name + '.jpg'), str(px_w), str(H)], check=True)
    print('mockup', name, px_w, H)


if __name__ == '__main__':
    # overview: one shirt per design, in the view the reference shows
    shirts = [(g, views[0][0], views[0][1]) for g, _, views in DESIGNS]
    caps = [(f'DESIGN {i + 1}', nm.upper()) for i, (_, nm, _) in enumerate(DESIGNS)]
    render('collection-overview', shirts, caps, ('WRAPSHAP — T-SHIRT COLLECTION', 'SIZE L · PRINTS AT 100%'), px_w=4800)
    for i, (g, nm, views) in enumerate(DESIGNS):
        shirts = [(g, v[0], v[1]) for v in views]
        caps = [(f'DESIGN {i + 1} · {v[0].upper()}', v[2] if len(v) > 2 else f'{nm.upper()} · {g.upper()} TEE') for v in views]
        render(f'collection-d{i + 1}', shirts, caps, (f'WRAPSHAP — DESIGN {i + 1}: {nm.upper()}', 'SIZE L · PRINTS AT 100%'),
               px_w=1800 * len(views))
