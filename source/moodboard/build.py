"""Wrapshap brand board in the MÜLER style: writes board.html (and one page per export).

Layout is in CSS px on a 1024 x 1536 board (the reference's 2:3 format). Photos come from
img/ (see prep_photos.py), brushes and doodles from kit/ (see extract_kit.py), stickers from
stickers/ (your earlier sticker set). Brushes, doodles and the logo are CSS masks, so each one can
take any brand colour. Every background carries a faint tone-on-tone doodle pattern.

    python3 build.py && node shot.mjs board.html out.png 1024 1536 3
"""
import json
import math
import random

KIT = json.load(open('kit/sizes.json'))
IMG = json.load(open('img/sizes.json'))
STK = json.load(open('stickers/sizes.json'))
LOGO_AR = 219.12 / 79.92

C = {
    'yellow': '#FFE014', 'paper': '#F7F7F2', 'white': '#FFFFFF', 'ink': '#0E0E0E',
    'graphite': '#4B4B4B', 'mist': '#D5D5D0', 'orange': '#F39200',
    'pink': '#FF3DA5', 'cobalt': '#2350F0', 'green': '#19B85B', 'violet': '#7C4DFF',
}


def col(c):
    return C.get(c, c)


# ---------------------------------------------------------------- primitives

def box(x, y, w, h=None, rot=0, flip=False, z=None, anchor='tl'):
    """Absolute-position style. anchor 'bl' / 'br' / 'tr' measure y or x from the far edge."""
    s = []
    s.append(('right' if anchor[1] == 'r' else 'left') + f':{x}px')
    s.append(('bottom' if anchor[0] == 'b' else 'top') + f':{y}px')
    s.append(f'width:{w}px')
    if h is not None:
        s.append(f'height:{h}px')
    t = []
    if rot:
        t.append(f'rotate({rot}deg)')
    if flip == 'v':
        t.append('scaleY(-1)')
    elif flip:
        t.append('scaleX(-1)')
    if t:
        s.append('transform:' + ' '.join(t))
    if z is not None:
        s.append(f'z-index:{z}')
    return ';'.join(s)


def mk(name, color, x, y, w, rot=0, flip=False, z=None, anchor='tl', op=None):
    """A kit brush/doodle as a coloured mask."""
    iw, ih = KIT[name]
    h = round(w * ih / iw, 2)
    st = box(x, y, w, h, rot, flip, z, anchor)
    st += f';--m:url(kit/{name}.png);background:{col(color)}'
    if op:
        st += f';opacity:{op}'
    return f'<i class="mk" style="{st}"></i>'


def logo(color, x, y, w, rot=0, z=None, anchor='tl'):
    """The Wrapshap wordmark in one flat colour (no texture on the logotype)."""
    h = round(w / LOGO_AR, 2)
    return f'<i class="logo" style="{box(x, y, w, h, rot, False, z, anchor)};background:{col(color)}"></i>'


def photo(name, x, y, h, z=None, anchor='tl', flip=False):
    w = round(h * IMG[name]['w'] / IMG[name]['h'], 2)
    return f'<img class="ph" src="img/{name}.webp" style="{box(x, y, w, h, 0, flip, z, anchor)}">'


def hand(text, x, y, size, color='ink', rot=-12, z=None, anchor='tl', lh=0.98, align='left', w=None):
    st = box(x, y, w or 'auto', None, rot, False, z, anchor).replace('width:autopx', 'width:auto')
    st = st.replace(f'rotate({rot}deg)', f'rotate({rot}deg) scaleX(0.86)') if rot else st + ';transform:scaleX(0.86)'
    return (f'<div class="hand" style="{st};font-size:{size}px;color:{col(color)};'
            f'line-height:{lh};text-align:{align}">{text}</div>')


def label(text, x, y, size=10.5, color='ink', weight=900, anchor='tl', align='left', ls=0.02, lh=1.05):
    st = box(x, y, 'auto', None, 0, False, None, anchor).replace('width:autopx', 'width:auto')
    return (f'<div class="lab" style="{st};font-size:{size}px;font-weight:{weight};color:{col(color)};'
            f'text-align:{align};letter-spacing:{ls}em;line-height:{lh}">{text}</div>')


def svg(inner, x, y, w, h, vb, rot=0, z=None, anchor='tl'):
    return (f'<svg class="sv" viewBox="{vb}" style="{box(x, y, w, h, rot, False, z, anchor)}">'
            f'{inner}</svg>')


def rough_ring(seed, rx=50, ry=40, loops=1.85, jitter=2.2, color='ink', sw=3.2):
    """A marker circle drawn fast: nearly two loops that don't quite close."""
    rng = random.Random(seed)
    pts = []
    n = 120
    ph = [rng.uniform(0, 6.28) for _ in range(3)]
    for i in range(n + 1):
        t = loops * 2 * math.pi * i / n + 0.4
        k = 1 + 0.04 * math.sin(3 * t + ph[0]) + 0.03 * math.sin(5 * t + ph[1]) + 0.05 * (i / n)
        x = 60 + rx * k * math.cos(t) + rng.uniform(-jitter, jitter) * 0.3
        y = 50 + ry * k * math.sin(t) + rng.uniform(-jitter, jitter) * 0.3
        pts.append((x, y))
    d = 'M' + ' L'.join(f'{x:.1f} {y:.1f}' for x, y in pts)
    return (f'<path d="{d}" fill="none" stroke="{col(color)}" stroke-width="{sw}" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def scribble_lines(seed, n=3, w=100, color='ink', sw=3.4, slope=-4):
    """Stacked quick underline strokes, like the reference's '≡' marks."""
    rng = random.Random(seed)
    out = []
    for i in range(n):
        y = 8 + i * 9 + rng.uniform(-1, 1)
        x0 = 4 + rng.uniform(0, 10) + i * 4
        x1 = w - 4 - rng.uniform(0, 14) - i * 6
        c = rng.uniform(-3, 3)
        out.append(f'<path d="M{x0:.1f} {y + (x0 / w) * slope * -1:.1f} Q{(x0 + x1) / 2:.1f} {y + c:.1f} '
                   f'{x1:.1f} {y + slope:.1f}" fill="none" stroke="{col(color)}" stroke-width="{sw - i * 0.5}" '
                   f'stroke-linecap="round"/>')
    return ''.join(out)


def asterisk(color='ink', sw=9):
    """Hand-drawn six-arm asterisk."""
    arms = [(-2, 50, 102, 48), (14, 12, 88, 90), (86, 10, 16, 88)]
    return ''.join(f'<path d="M{a} {b} Q{(a + c) / 2 + 3} {(b + d) / 2 - 2} {c} {d}" fill="none" '
                   f'stroke="{col(color)}" stroke-width="{sw}" stroke-linecap="round"/>' for a, b, c, d in arms)


def ast(color, x, y, w, rot=0, z=None, anchor='tl'):
    return svg(asterisk(color), x, y, w, w, '-8 -2 116 104', rot, z, anchor)


def lines(seed, x, y, w, color='ink', n=3, rot=-8, z=None, anchor='tl', sw=3.4):
    return svg(scribble_lines(seed, n, 100, color, sw), x, y, w, w * 0.34, '0 0 100 34', rot, z, anchor)


def st(name, x, y, w, rot=0, z=5, anchor='tl'):
    """One of the die-cut stickers, slapped on with a soft shadow."""
    iw, ih = STK[name]
    return f'<img class="st" src="stickers/st-{name}.webp" style="{box(x, y, w, round(w * ih / iw, 2), rot, False, z, anchor)}">'


BG_DOODLES = ['doodle-crown', 'doodle-smiley', 'doodle-star', 'ast']   # clean shapes only
BG_TONE = {  # doodle colour and strength per background: texture, not decoration
    'paper': ('ink', 0.055), 'white': ('ink', 0.05), 'yellow': ('#A87E00', 0.26), 'cobalt': ('white', 0.10),
}


def bg_doodles(seed, w, h, bg, cell=90, size=(22, 30), keep=0.45):
    """A sparse tone-on-tone doodle wallpaper behind everything else."""
    color, op = BG_TONE[bg]
    rng = random.Random(seed)
    e = []
    for gy in range(-1, int(h / cell) + 1):
        for gx in range(-1, int(w / cell) + 1):
            if rng.random() > keep:
                continue
            x = gx * cell + (cell / 2 if gy % 2 else 0) + rng.uniform(0, 0.4) * cell
            y = gy * cell + rng.uniform(0, 0.4) * cell
            name, sz, rot = rng.choice(BG_DOODLES), rng.uniform(*size), rng.uniform(-25, 25)
            if name == 'ast':
                e.append(ast(color, round(x, 1), round(y, 1), round(sz * 0.7, 1), round(rot)))
            else:
                e.append(mk(name, color, round(x, 1), round(y, 1), round(sz, 1), rot=round(rot)))
    return f'<div class="bgd" style="opacity:{op}">{"".join(e)}</div>'


# ---------------------------------------------------------------- sections

HERO_H = 450


def hero():
    e = [bg_doodles(1, 1024, HERO_H, 'paper')]
    # big confident strokes behind the model, like the reference
    e.append(mk('brush-dab', 'yellow', 250, 250, 520, rot=-16, z=1))
    e.append(mk('brush-zigzag', 'yellow', 420, 150, 420, rot=-12, z=1))
    # the whole wordmark across the top; the model overlaps only its lower edge
    e.append(logo('ink', 92, 18, 840, rot=-4, z=2))
    e.append(mk('doodle-crown', 'ink', 118, 56, 58, rot=-14, z=5))
    e.append(photo('hero', 190, 0, 402, z=4, anchor='bl'))
    e.append(label('SMALL<br>TECH.<br>BIG<br>ENERGY.', 24, 22, 11))
    e.append(label('LOUD<br>OUTSIDE.<br>EXACT<br>INSIDE.', 24, 22, 11, anchor='tr', align='right'))
    # one element each side, as in the reference
    e.append(svg(rough_ring(7, 52, 44), 26, 300, 124, 104, '0 0 120 100', rot=-8, z=5))
    e.append(hand('GOOD<br>VIBES<br>ONLY.', 50, 318, 17, z=6, rot=-12))
    e.append(lines(3, 72, 396, 80, z=5))
    e.append(st('nomore', 874, 300, 122, rot=7, z=6))
    return f'<section class="hero" style="height:{HERO_H}px">{"".join(e)}</section>'


# Every poster follows one template: label, logo, one brush, a big model bleeding off the bottom,
# a handwritten line in the lower third, one pop-colour doodle and one sticker in the same corner.
POSTERS = [
    dict(bg='yellow', lab='clear.', logo='white', model='p1', mh=292, mx=34,
         brush=('brush-zigzag-arrow', 'white', 6, 88, 196, 4),
         copy=('CRYSTAL<br>CLEAR.', 'l'), pop=('doodle-smiley', 'cobalt'), sticker='sparkle'),
    dict(bg='white', lab='privacy.', logo='ink', model='p2', mh=286, mx=-30,
         brush=('brush-loop', 'yellow', 26, 104, 170, -8),
         copy=('EYES OFF<br>MY SCREEN.', 'r'), pop=('doodle-crown', 'pink'), sticker='wegotyou'),
    dict(bg='cobalt', lab='tuff.', logo='white', model='p3', mh=250, mx=-24, lab_color='white',
         brush=('brush-m', 'yellow', 10, 110, 180, -6, 'v'),
         copy=('EVERY<br>PHONE<br>FALLS.', 'r', 'white'), pop=('doodle-crown', 'yellow', (46, 108, 36, -10)),
         sticker='smiley'),
    dict(bg='white', lab='matte.', logo='ink', model='p4', mh=236, mx=0,
         brush=('brush-zigzag-arrow', 'yellow', 22, 80, 176, -20),
         copy=('NO<br>GLARE.', 'rhigh'), pop=('ast', 'green'), sticker='exactfit'),
    dict(bg='yellow', lab='60&nbsp;sec.', logo='white', model='p5', mh=286, mx=26,
         brush=('brush-zigzag', 'white', -36, 196, 290, -58),
         copy=('SHOP<br>NOW', 'l'), pop=('doodle-arrow', 'violet'), sticker='cut60', sticker_left=True),
]
PH = 355.5556


def poster(p, x=0, y=0):
    e = [bg_doodles(10 + len(p['lab']), 200, PH, p['bg'], cell=70, size=(16, 22), keep=0.5)]
    e.append(label(p['lab'], 12, 12, 10.5, p.get('lab_color', 'ink'), weight=700, ls=0))
    e.append(logo(p['logo'], 8, 28, 186, rot=-5, z=3))
    name, c, bx, by, bw, rot, *fl = p['brush']
    e.append(mk(name, c, bx, by, bw, rot=rot, flip=fl[0] if fl else False, z=1))
    w = p['mh'] * IMG[p['model']]['w'] / IMG[p['model']]['h']
    e.append(photo(p['model'], round((200 - w) / 2 + p['mx'], 1), -14, p['mh'], z=2, anchor='bl'))
    text, side, *tc = p['copy']
    tc = tc[0] if tc else 'ink'
    cx, cy = {'l': (10, 30), 'r': (116, 30), 'rhigh': (130, 150)}[side]
    e.append(hand(text, cx, cy, 15, tc, z=4, anchor='bl', rot=-10))
    e.append(lines(len(text), cx + 2, cy - 18, 58, tc, n=2, z=4, anchor='bl', sw=3))
    # the pop doodle sits just above the handwriting
    dn, dc, *at = p['pop']
    if at:  # a placed doodle, e.g. the crown on the tuff model's head
        px, py, pw, pr = at[0]
        e.append(mk(dn, dc, px, py, pw, rot=pr, z=4))
    elif dn == 'ast':
        e.append(ast(dc, cx + 4, cy + 52, 18, z=4, anchor='bl'))
    else:
        e.append(mk(dn, dc, cx + 2, cy + 50, 28, rot=-8, z=4, anchor='bl'))
    # one sticker, always top-right under the logo
    sw = 44 if p['sticker'] != 'exactfit' else 58
    if p.get('sticker_left'):
        e.append(st(p['sticker'], 8, 96, 40, rot=-10, z=5))
    else:
        e.append(st(p['sticker'], 10, 98, sw, rot=10, z=5, anchor='tr'))
    return (f'<div class="poster" style="left:{x}px;top:{y}px;background:{col(p["bg"])}">'
            f'{"".join(e)}</div>')


TILE_H = 330


def tiles():
    t1 = [bg_doodles(21, 298, TILE_H, 'paper', cell=80),
          mk('brush-swoosh', 'yellow', 110, -40, 150, rot=58, z=1),
          mk('brush-dab', 'yellow', -40, 190, 260, rot=-36, z=1),
          mk('doodle-crown', 'yellow', 24, 12, 100, rot=-10, z=1),
          photo('phone', -30, -28, 340, z=2, anchor='br'),
          hand('EXACT<br>FIT.', 14, 60, 26, z=3, anchor='bl'),
          lines(21, 16, 30, 80, z=3, anchor='bl')]
    t2 = [bg_doodles(22, 408, TILE_H, 'paper', cell=80),
          mk('brush-dab', 'yellow', -12, 32, 92, rot=-10, z=1),
          logo('ink', 54, 14, 296, rot=-4, z=3),
          photo('group', 34, -12, 246, z=2, anchor='bl'),
          hand('APPLE<br>SAMSUNG<br>XIAOMI<br>OPPO<br>VIVO<br>+ MORE', 12, 118, 10.5, z=3, rot=-8, lh=1.12),
          mk('doodle-arrow', 'ink', 38, 206, 20, rot=-24, z=3),
          mk('doodle-smiley', 'yellow', 346, 122, 50, rot=-8, z=3)]
    t3 = [bg_doodles(23, 306, TILE_H, 'yellow', cell=80),
          mk('brush-m', 'white', -12, 52, 200, rot=-10, flip='v', z=1),
          photo('face', -52, 4, 346, z=2, anchor='tr'),
          mk('doodle-crown', 'ink', 30, 32, 58, rot=-8, z=3),
          hand('IT JUST<br>FITS.', 18, 56, 24, z=3, anchor='bl'),
          lines(31, 20, 28, 84, z=3, anchor='bl')]
    return (f'<div class="tile" style="left:0;width:298px;background:{C["paper"]}">{"".join(t1)}</div>'
            f'<div class="tile" style="left:304px;width:408px;background:{C["paper"]}">{"".join(t2)}</div>'
            f'<div class="tile" style="left:718px;width:306px;background:{C["yellow"]}">{"".join(t3)}</div>')


STRIP_H = 80
STRIP = [  # sticker, height, rotation
    ('crown', 54, -8), ('cut60', 60, 6), ('exactfit', 44, -6), ('logo-orig', 44, 0),
    ('nomore', 60, 5), ('smiley', 56, -5), ('sparkle', 56, 10), ('wegotyou', 60, 4),
]


def strip():
    """The full sticker pack on a flat cobalt band, like your sticker strip."""
    e = [label('STICKER<br>PACK', 18, 29, 8.5, 'white', weight=900, ls=0.08, lh=1.15)]
    widths = [h * STK[n][0] / STK[n][1] for n, h, _ in STRIP]
    x0, x1 = 110, 1024 - 30
    gap = (x1 - x0 - sum(widths)) / (len(STRIP) - 1)
    x = x0
    for (n, h, rot), w in zip(STRIP, widths):
        e.append(st(n, round(x, 1), round((STRIP_H - h) / 2, 1), round(w, 1), rot=rot, z=2))
        x += w + gap
    return f'<section class="strip" style="height:{STRIP_H}px">{"".join(e)}</section>'


def swatch(x, y, sq, bg, inner=''):
    return f'<i class="tx" style="left:{x}px;top:{y}px;width:{sq}px;height:{sq}px;background:{bg}">{inner}</i>'


GUIDE_H = 1536 - HERO_H - PH - TILE_H - STRIP_H - 4 * 6


def guide():
    g = []
    head = lambda t, x: label(t, x, 20, 9.5, weight=700, ls=0.08)
    # 1 colour: the MÜLER layout, plus one row of pops
    x = 28
    g.append(head('COLOUR PALETTE', x))
    for i, (c, bd) in enumerate([('yellow', 0), ('paper', 1), ('ink', 0), ('graphite', 0), ('mist', 0)]):
        border = ';box-shadow:inset 0 0 0 1px #cfcfca' if bd else ''
        g.append(f'<i class="sw" style="left:{x + i * 40}px;top:44px;width:32px;height:32px;'
                 f'border-radius:50%;background:{col(c)}{border}"></i>')
    for i, c in enumerate(['pink', 'cobalt', 'green', 'violet', 'orange']):
        g.append(f'<i class="sw" style="left:{x + i * 40 + 7}px;top:86px;width:18px;height:18px;'
                 f'border-radius:50%;background:{col(c)}"></i>')
    grads = [f'linear-gradient(90deg,{C["yellow"]},#FFF6B8 55%,{C["paper"]})',
             f'linear-gradient(90deg,{C["ink"]},#6a6a6a 60%,{C["mist"]})',
             'linear-gradient(90deg,#9FB6FF,#F6A6D6 50%,#FFE39A)']
    for i, gr in enumerate(grads):
        g.append(f'<i class="sw" style="left:{x + i * 66}px;top:118px;width:58px;height:30px;background:{gr}"></i>')
    g.append(hand('BOLD<br>BRIGHT<br>FUN<br>PREMIUM', x + 2, 172, 14, rot=-10, lh=1.0))
    g.append(mk('doodle-crown', 'ink', x + 74, 172, 26, rot=6))
    g.append(lines(41, x + 4, 238, 80))
    # 2 typography
    x = 262
    g.append(head('TYPOGRAPHY', x))
    g.append(logo('ink', x - 2, 44, 196, rot=-4))
    g.append(label('DM SANS', x, 134, 10, weight=900, ls=0.06))
    g.append(label('ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>0123456789', x, 152, 8.2, weight=500, ls=0.04, lh=1.6))
    g.append(label('abcdefghijklmnopqrstuvwxyz<br>0123456789', x, 184, 8.2, weight=400, ls=0.04, lh=1.6))
    g.append(label('PERMANENT MARKER', x, 222, 10, weight=900, ls=0.06))
    g.append(hand('Hand-lettered, loud &amp; fast.', x, 240, 13, rot=-3))
    # 3 graphic elements: fewer, with room around them
    x = 500
    g.append(head('GRAPHIC ELEMENTS', x))
    g.append(mk('doodle-crown', 'ink', x + 6, 48, 46, rot=-6))
    g.append(mk('doodle-smiley', 'ink', x + 78, 44, 50))
    g.append(ast('ink', x + 150, 50, 30))
    g.append(lines(51, x + 2, 118, 70, rot=-18, sw=4.2))
    g.append(mk('brush-m', 'yellow', x + 88, 104, 84, rot=-8, flip='v'))
    g.append(mk('brush-loop', 'ink', x + 4, 186, 64, rot=-6))
    g.append(mk('brush-dab', 'yellow', x + 84, 232, 96, rot=-10))
    g.append(hand('60 SEC', x + 102, 222, 20, rot=-14))
    # 4 texture: 2 x 2 like the reference, with the doodle pattern as one of them
    x = 712
    g.append(head('TEXTURE / OVERLAYS', x))
    sq = 74
    g.append(swatch(x, 44, sq, C['paper'], mk('brush-zigzag', 'yellow', -72, 0, 240, rot=-38)))
    g.append(swatch(x + 84, 44, sq, C['ink']).replace('class="tx"', 'class="tx grunge"'))
    g.append(swatch(x, 128, sq, C['paper'], mk('brush-zigzag-arrow', 'mist', -8, -34, 94, rot=12)))
    g.append(swatch(x + 84, 128, sq, C['yellow'], bg_doodles(42, 74, 74, 'yellow', cell=30, size=(12, 16), keep=0.8)
                    .replace('opacity:0.26', 'opacity:0.6')))
    g.append(label('DOODLE PATTERN', x + 84, 208, 6.5, weight=700, ls=0.06, color='graphite'))
    # 5 mood
    x = 906
    g.append(head('MOOD', x))
    for i, w in enumerate(['ENERGY', 'YOUTH', 'TECH', 'FASHION', 'FUN', 'CONFIDENCE', 'COMMUNITY', 'PREMIUM']):
        g.append(label(w, x + 4, 48 + i * 26, 9.5, weight=500, ls=0.1))
    rules = ''.join(f'<i class="rule" style="left:{v}px"></i>' for v in (242, 480, 694, 886))
    return f'<section class="guide" style="height:{GUIDE_H:.2f}px">{rules}{"".join(g)}</section>'


CSS = """
@font-face{font-family:'DM Sans';src:url(../../fonts/DMSans-Regular.ttf);font-weight:400}
@font-face{font-family:'DM Sans';src:url(../../fonts/DMSans-Medium.ttf);font-weight:500}
@font-face{font-family:'DM Sans';src:url(../../fonts/DMSans-Bold.ttf);font-weight:700}
@font-face{font-family:'DM Sans';src:url(../../fonts/DMSans-Black.ttf);font-weight:900}
@font-face{font-family:'Permanent Marker';src:url(../../fonts/PermanentMarker-Regular.ttf)}
*{margin:0;padding:0;box-sizing:border-box}
html,body{background:#fff}
body{width:1024px;font-family:'DM Sans',sans-serif;-webkit-font-smoothing:antialiased}
section,.poster,.tile{position:relative;overflow:hidden}
.hero{background:PAPER}
.row{position:relative;height:355.5556px;margin-top:6px}
.poster{position:absolute;width:200px;height:355.5556px}
.tiles{position:relative;height:330px;margin-top:6px}
.tile{position:absolute;top:0;height:330px}
.ph{filter:contrast(1.05) saturate(1.08) brightness(1.02)}
.strip{background:COBALT;margin-top:6px}
.guide{background:#FAFAF7;margin-top:6px}
.mk,.logo,.ph,.sv,.hand,.lab,.sw,.tx,.st{position:absolute;display:block}
.st{filter:drop-shadow(0 1.5px 2px rgba(0,0,0,.25))}
.bgd{position:absolute;inset:0;z-index:0;pointer-events:none}
.mk{-webkit-mask:var(--m) center/100% 100% no-repeat;mask:var(--m) center/100% 100% no-repeat;transform-origin:50% 50%}
.logo{-webkit-mask:url(logo-mono-black.svg) center/100% 100% no-repeat;mask:url(logo-mono-black.svg) center/100% 100% no-repeat}
.hand{font-family:'Permanent Marker',cursive;white-space:nowrap;transform-origin:0 50%}
.lab{white-space:nowrap}
.sv{overflow:visible}
.tx{overflow:hidden}
.grunge{-webkit-mask:url(kit/texture-grunge.png) center/cover;mask:url(kit/texture-grunge.png) center/cover}
.grunge-neg{position:absolute;inset:0;background:PAPER;
  -webkit-mask:linear-gradient(#000,#000),url(kit/texture-grunge.png) center/260%;-webkit-mask-composite:xor;
  mask:linear-gradient(#000,#000),url(kit/texture-grunge.png) center/260%;mask-composite:exclude}
.rule{position:absolute;top:22px;bottom:22px;width:1px;background:#d9d9d4}
""".replace('PAPER', C['paper']).replace('COBALT', C['cobalt'])


def page(body, width=1024, extra_css=''):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>Wrapshap brand board</title>'
            f'<style>{CSS}{extra_css}</style></head><body style="width:{width}px">{body}</body></html>')


if __name__ == '__main__':
    row = ''.join(poster(p, x=i * 206) for i, p in enumerate(POSTERS))
    body = (hero() + f'<div class="row">{row}</div>' + f'<div class="tiles">{tiles()}</div>' + strip() + guide())
    open('board.html', 'w').write(page(body))
    open('hero.html', 'w').write(page(hero()))
    # the background doodle pattern on its own: solid ink on transparent, 1080 x 1080
    pat = bg_doodles(7, 1080, 1080, 'paper', cell=120, size=(40, 56), keep=0.6).replace(
        f'opacity:{BG_TONE["paper"][1]}', 'opacity:1')
    open('pattern.html', 'w').write(page(f'<section style="height:1080px">{pat}</section>', 1080,
                                         'html,body{background:transparent}'))
    for i, p in enumerate(POSTERS, 1):
        # zoom 5.4 makes the 200 x 355.56 poster exactly 1080 x 1920
        open(f'poster-{i}.html', 'w').write(page(poster(p), 200, '.poster{position:relative}body{zoom:5.4}'))
    print('ok')
