"""Wrapshap brand board in the MÜLER style: writes board.html (and one page per export).

Layout is in CSS px on a 1024 x 1536 board (the reference's 2:3 format). Photos come from
img/ (see prep_photos.py), brushes and doodles from kit/ (see extract_kit.py). Brushes, doodles
and the logo are CSS masks, so each one can take any brand colour.

    python3 build.py && node shot.mjs board.html out.png 1024 1536 3
"""
import json
import math
import random

KIT = json.load(open('kit/sizes.json'))
IMG = json.load(open('img/sizes.json'))
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


def logo(color, x, y, w, rot=0, z=None, anchor='tl', rough=True):
    """The Wrapshap wordmark, one colour, distressed like printed poster type."""
    h = round(w / LOGO_AR, 2)
    cls = 'logo rough' if rough else 'logo'
    return f'<i class="{cls}" style="{box(x, y, w, h, rot, False, z, anchor)};background:{col(color)}"></i>'


def photo(name, x, y, h, z=None, anchor='tl', flip=False):
    w = round(h * IMG[name]['w'] / IMG[name]['h'], 2)
    return f'<img class="ph" src="img/{name}.webp" style="{box(x, y, w, h, 0, flip, z, anchor)}">'


def hand(text, x, y, size, color='ink', rot=-12, z=None, anchor='tl', lh=0.98, align='left', w=None):
    st = box(x, y, w or 'auto', None, rot, False, z, anchor).replace('width:autopx', 'width:auto')
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


# ---------------------------------------------------------------- sections

def hero():
    e = []
    # brushes behind the wordmark
    e.append(mk('brush-dab', 'yellow', 330, 262, 360, rot=-24, z=1))
    e.append(mk('brush-zigzag', 'yellow', 640, 250, 330, rot=-14, z=1))
    e.append(mk('brush-swoosh', 'yellow', 610, -40, 150, rot=38, z=1))
    e.append(mk('brush-loop', 'yellow', 30, 150, 150, rot=-10, z=1))
    e.append(logo('ink', 36, 60, 690, rot=-5, z=2))
    # the model sits in front of the wordmark, as in the reference
    e.append(photo('hero', 606, 10, 436, z=4))
    e.append(mk('doodle-crown', 'ink', 104, 30, 58, rot=-10, z=5))
    e.append(label('SMALL<br>TECH.<br>BIG<br>ENERGY.', 26, 26, 11.5))
    e.append(label('LOUD<br>OUTSIDE.<br>EXACT<br>INSIDE.', 26, 26, 11.5, anchor='tr', align='right'))
    # left: stamp
    e.append(svg(rough_ring(7, 52, 44), 40, 300, 124, 104, '0 0 120 100', rot=-8, z=5))
    e.append(hand('GOOD<br>VIBES<br>ONLY.', 66, 316, 16.5, z=6, rot=-14))
    e.append(lines(3, 92, 392, 86, z=5))
    # right: smiley with crown, and the tagline on a paint dab
    e.append(mk('doodle-smiley', 'pink', 892, 128, 92, rot=-8, z=5))
    e.append(mk('doodle-crown', 'pink', 924, 100, 38, rot=6, z=5))
    e.append(mk('brush-dab', 'yellow', 852, 350, 176, rot=-20, z=3))
    e.append(mk('doodle-crown', 'ink', 974, 294, 30, rot=8, z=6))
    e.append(hand('NO MORE<br>ALMOST.', 880, 332, 20, z=6, rot=-15))
    e.append(lines(11, 900, 398, 84, z=6))
    return f'<section class="hero" style="height:440px">{"".join(e)}</section>'


POSTERS = [
    # bg, label, logo colour, brush layer, model, copy, doodles
    dict(bg='yellow', lab='clear.', logo='white', model='p1',
         brush=[('brush-zigzag-arrow', 'white', 16, 84, 180, 6)],
         copy=('CRYSTAL<br>CLEAR.', 10, 34, 15, 'ink'),
         doodles=[('doodle-smiley', 'cobalt', 10, 84, 38, -6, 'bl')]),
    dict(bg='white', lab='privacy.', logo='ink', model='p2',
         brush=[('brush-loop', 'yellow', 20, 108, 170, -8)],
         copy=('EYES OFF<br>MY SCREEN.', 112, 44, 12.5, 'ink'),
         doodles=[('ast', 'pink', 166, 84, 20, 0, 'tl'), ('crown', 'pink', 150, 100, 28, 8, 'bl')]),
    dict(bg='cobalt', lab='tuff.', logo='white', model='p3', lab_color='white',
         brush=[('brush-m', 'yellow', 12, 118, 176, -6, 'v')],
         copy=('EVERY<br>PHONE<br>FALLS.', 134, 36, 14, 'white'),
         doodles=[('crown', 'yellow', 16, 128, 34, -10, 'tl')]),
    dict(bg='white', lab='matte.', logo='ink', model='p4',
         brush=[('brush-zigzag-arrow', 'yellow', 26, 96, 170, -18)],
         copy=('NO<br>GLARE.', 134, 150, 18, 'ink'),
         doodles=[('ast', 'green', 164, 98, 18, 0, 'tl'), ('doodle-smiley', 'green', 12, 98, 34, -6, 'tl')]),
    dict(bg='yellow', lab='60&nbsp;sec.', logo='white', model='p5',
         brush=[('brush-zigzag', 'white', -30, 190, 280, -58)],
         copy=('SHOP<br>NOW', 12, 40, 19, 'ink'),
         doodles=[('doodle-arrow', 'violet', 64, 8, 28, -60, 'bl'), ('crown', 'violet', 20, 104, 30, -8, 'tl')]),
]

MODEL = {  # height and x offset of each poster's cut-out
    'p1': (268, 30), 'p2': (256, -34), 'p3': (226, -34), 'p4': (212, -14), 'p5': (262, 22),
}


def poster(p, x=0, y=0):
    e = []
    e.append(label(p['lab'], 12, 12, 10.5, p.get('lab_color', 'ink'), weight=700, ls=0))
    e.append(logo(p['logo'], 8, 30, 186, rot=-5, z=3))
    for name, c, bx, by, bw, rot, *fl in p['brush']:
        e.append(mk(name, c, bx, by, bw, rot=rot, flip=fl[0] if fl else False, z=1))
    h, dx = MODEL[p['model']]
    w = h * IMG[p['model']]['w'] / IMG[p['model']]['h']
    e.append(photo(p['model'], round((200 - w) / 2 + dx, 1), 0, h, z=2, anchor='bl'))
    text, cx, cy, size, c = p['copy']
    e.append(hand(text, cx, cy, size, c, z=4, anchor='bl'))
    for name, c, dx_, dy, dw, rot, anchor in p['doodles']:
        if name == 'ast':
            e.append(ast(c, dx_, dy, dw, rot, z=4, anchor=anchor))
        elif name == 'crown':
            e.append(mk('doodle-crown', c, dx_, dy, dw, rot=rot, z=4, anchor=anchor))
        else:
            e.append(mk(name, c, dx_, dy, dw, rot=rot, z=4, anchor=anchor))
    return (f'<div class="poster" style="left:{x}px;top:{y}px;background:{col(p["bg"])}">'
            f'{"".join(e)}</div>')


def tiles():
    t1 = [mk('brush-swoosh', 'yellow', 70, -30, 150, rot=62, z=1),
          mk('brush-dab', 'yellow', -30, 220, 250, rot=-38, z=1),
          mk('doodle-crown', 'yellow', 30, 18, 104, rot=-10, z=1),
          photo('phone', 86, 0, 330, z=2, anchor='bl'),
          hand('EXACT<br>FIT.', 12, 66, 26, z=3, anchor='bl'),
          lines(21, 14, 36, 84, z=3, anchor='bl')]
    t2 = [mk('brush-dab', 'yellow', -10, 40, 90, rot=-10, z=1),
          logo('ink', 44, 20, 330, rot=-4, z=3),
          photo('group', 22, 0, 262, z=2, anchor='bl'),
          hand('APPLE<br>SAMSUNG<br>XIAOMI<br>OPPO<br>VIVO<br>+ MORE', 12, 124, 10.5, z=3, rot=-8, lh=1.12),
          mk('doodle-arrow', 'ink', 40, 212, 22, rot=-24, z=3),
          mk('doodle-smiley', 'yellow', 334, 130, 58, rot=-8, z=3)]
    t3 = [mk('brush-m', 'white', -10, 56, 210, rot=-10, flip='v', z=1),
          photo('face', -54, 8, 392, z=2, anchor='tr'),
          mk('doodle-crown', 'ink', 30, 36, 60, rot=-8, z=3),
          hand('IT JUST<br>FITS.', 18, 64, 25, z=3, anchor='bl'),
          lines(31, 20, 36, 90, z=3, anchor='bl')]
    return (f'<div class="tile" style="left:0;width:298px;background:{C["paper"]}">{"".join(t1)}</div>'
            f'<div class="tile" style="left:304px;width:408px;background:{C["paper"]}">{"".join(t2)}</div>'
            f'<div class="tile" style="left:718px;width:306px;background:{C["yellow"]}">{"".join(t3)}</div>')


def guide():
    g = []
    # 1 colour
    x = 28
    g.append(label('COLOUR PALETTE', x, 22, 9.5, weight=700, ls=0.08))
    for i, (c, bd) in enumerate([('yellow', 0), ('paper', 1), ('ink', 0), ('graphite', 0), ('mist', 0)]):
        border = ';box-shadow:inset 0 0 0 1px #cfcfca' if bd else ''
        g.append(f'<i class="sw" style="left:{x + i * 40}px;top:46px;width:32px;height:32px;'
                 f'border-radius:50%;background:{col(c)}{border}"></i>')
        g.append(label(C[c][1:], x + i * 40 + 16, 82, 6, weight=500, color='graphite', ls=0.04)
                 .replace('left:', 'margin-left:-14px;width:28px;text-align:center;left:').replace('width:auto;', ''))
    grads = [f'linear-gradient(90deg,{C["yellow"]},#FFF6B8 55%,{C["paper"]})',
             f'linear-gradient(90deg,{C["ink"]},#6a6a6a 60%,{C["mist"]})',
             'linear-gradient(90deg,#9FB6FF,#F6A6D6 50%,#FFE39A)']
    for i, gr in enumerate(grads):
        g.append(f'<i class="sw" style="left:{x + i * 66}px;top:98px;width:58px;height:28px;background:{gr}"></i>')
    g.append(label('POPS · ONE PER PIECE', x, 138, 7.5, weight=700, ls=0.08, color='graphite'))
    for i, c in enumerate(['pink', 'cobalt', 'green', 'violet', 'orange']):
        g.append(f'<i class="sw" style="left:{x + i * 40 + 5}px;top:152px;width:22px;height:22px;'
                 f'border-radius:50%;background:{col(c)}"></i>')
        g.append(label(C[c][1:], x + i * 40 + 16, 178, 6, weight=500, color='graphite', ls=0.04)
                 .replace('left:', 'margin-left:-14px;width:28px;text-align:center;left:').replace('width:auto;', ''))
    g.append(hand('BOLD<br>BRIGHT<br>FUN<br>PREMIUM', x + 2, 202, 14.5, rot=-10, lh=1.0))
    g.append(mk('doodle-crown', 'ink', x + 74, 204, 26, rot=6))
    g.append(lines(41, x + 4, 280, 84))
    # 2 typography
    x = 262
    g.append(label('TYPOGRAPHY', x, 22, 9.5, weight=700, ls=0.08))
    g.append(logo('ink', x - 2, 44, 196, rot=-4))
    g.append(f'<img src="logo-colour.svg" style="position:absolute;left:{x + 132}px;top:118px;width:66px">')
    g.append(label('DM SANS', x, 132, 10, weight=900, ls=0.06))
    g.append(label('ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>0123456789', x, 150, 8.2, weight=500, ls=0.04, lh=1.5))
    g.append(label('abcdefghijklmnopqrstuvwxyz<br>0123456789', x, 180, 8.2, weight=400, ls=0.04, lh=1.5))
    g.append(label('PERMANENT MARKER', x, 222, 10, weight=900, ls=0.06))
    g.append(hand('Hand-lettered, loud &amp; fast.', x, 240, 12.5, rot=-3))
    g.append(label('Logo in one colour for display · full colour for packaging &amp; signage', x, 270, 7,
                   weight=500, color='graphite', ls=0.02, lh=1.35).replace('width:auto', 'width:196px;white-space:normal'))
    # 3 graphic elements
    x = 500
    g.append(label('GRAPHIC ELEMENTS', x, 22, 9.5, weight=700, ls=0.08))
    g.append(mk('doodle-crown', 'ink', x + 4, 50, 46, rot=-6))
    g.append(mk('doodle-smiley', 'ink', x + 72, 46, 52))
    g.append(ast('ink', x + 146, 52, 32))
    g.append(lines(51, x + 2, 112, 70, rot=-18, sw=4.2))
    g.append(mk('brush-m', 'yellow', x + 82, 100, 92, rot=-8, flip='v'))
    g.append(mk('doodle-star-smiley', 'pink', x + 6, 178, 50, rot=-8))
    g.append(mk('doodle-scribble', 'ink', x + 62, 196, 70))
    g.append(mk('doodle-arrow', 'cobalt', x + 150, 188, 26, rot=-20))
    g.append(mk('brush-dab', 'yellow', x + 76, 262, 100, rot=-10))
    g.append(hand('60 SEC', x + 96, 250, 21, rot=-14))
    g.append(mk('doodle-squiggle', 'green', x + 172, 104, 14, rot=-8))
    # 4 texture
    x = 712
    g.append(label('TEXTURE / OVERLAYS', x, 22, 9.5, weight=700, ls=0.08))
    sq = 70
    g.append(f'<i class="tx" style="left:{x}px;top:48px;width:{sq}px;height:{sq}px;background:{C["paper"]}">'
             f'{mk("brush-zigzag", "yellow", -70, -6, 230, rot=-38)}</i>')
    g.append(f'<i class="tx grunge" style="left:{x + 82}px;top:48px;width:{sq}px;height:{sq}px;'
             f'background:{C["ink"]}"></i>')
    g.append(f'<i class="tx" style="left:{x}px;top:130px;width:{sq}px;height:{sq}px;background:{C["paper"]}">'
             f'{mk("brush-zigzag-arrow", "mist", -8, -34, 90, rot=12)}</i>')
    g.append(f'<i class="tx" style="left:{x + 82}px;top:130px;width:{sq}px;height:{sq}px;background:{C["paper"]}">'
             f'<i class="grunge-neg" style="background:{C["ink"]}"></i></i>')
    g.append(f'<i class="tx" style="left:{x}px;top:212px;width:{sq}px;height:{sq}px;background:'
             f'radial-gradient(circle,{C["yellow"]} 42%,transparent 45%) 0 0/7px 7px,{C["paper"]}"></i>')
    g.append(f'<i class="tx" style="left:{x + 82}px;top:212px;width:{sq}px;height:{sq}px;background:{C["paper"]}">'
             f'{mk("doodle-scribble", "ink", -10, 16, 96, rot=-12)}</i>')
    # 5 mood
    x = 906
    g.append(label('MOOD', x, 22, 9.5, weight=700, ls=0.08))
    for i, w in enumerate(['ENERGY', 'YOUTH', 'TECH', 'FASHION', 'FUN', 'CONFIDENCE', 'COMMUNITY', 'PREMIUM']):
        g.append(label(w, x + 4, 52 + i * 27, 9.5, weight=500, ls=0.1))
    rules = ''.join(f'<i class="rule" style="left:{v}px"></i>' for v in (242, 480, 694, 886))
    return f'<section class="guide" style="height:340px">{rules}{"".join(g)}</section>'


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
.tiles{position:relative;height:382px;margin-top:6px}
.tile{position:absolute;top:0;height:382px}
.guide{background:#FAFAF7;margin-top:6px}
.mk,.logo,.ph,.sv,.hand,.lab,.sw,.tx{position:absolute;display:block}
.mk{-webkit-mask:var(--m) center/100% 100% no-repeat;mask:var(--m) center/100% 100% no-repeat;transform-origin:50% 50%}
.logo{-webkit-mask:url(logo-mono-black.svg) center/100% 100% no-repeat;mask:url(logo-mono-black.svg) center/100% 100% no-repeat}
.logo.rough{-webkit-mask:url(logo-mono-black.svg) center/100% 100% no-repeat,url(kit/texture-grunge.png) center/cover;
  mask:url(logo-mono-black.svg) center/100% 100% no-repeat,url(kit/texture-grunge.png) center/cover;
  -webkit-mask-composite:source-in;mask-composite:intersect}
.hand{font-family:'Permanent Marker',cursive;white-space:nowrap;transform-origin:0 50%}
.lab{white-space:nowrap}
.sv{overflow:visible}
.tx{overflow:hidden}
.grunge{-webkit-mask:url(kit/texture-grunge.png) center/cover;mask:url(kit/texture-grunge.png) center/cover}
.grunge-neg{position:absolute;inset:0;background:PAPER;
  -webkit-mask:linear-gradient(#000,#000),url(kit/texture-grunge.png) center/260%;-webkit-mask-composite:xor;
  mask:linear-gradient(#000,#000),url(kit/texture-grunge.png) center/260%;mask-composite:exclude}
.rule{position:absolute;top:22px;bottom:22px;width:1px;background:#d9d9d4}
""".replace('PAPER', C['paper'])


def page(body, width=1024, extra_css=''):
    return (f'<!doctype html><html><head><meta charset="utf-8"><title>Wrapshap brand board</title>'
            f'<style>{CSS}{extra_css}</style></head><body style="width:{width}px">{body}</body></html>')


if __name__ == '__main__':
    row = ''.join(poster(p, x=i * 206) for i, p in enumerate(POSTERS))
    body = (hero() + f'<div class="row">{row}</div>' + f'<div class="tiles">{tiles()}</div>' + guide())
    open('board.html', 'w').write(page(body))
    open('hero.html', 'w').write(page(hero()))
    for i, p in enumerate(POSTERS, 1):
        # zoom 5.4 makes the 200 x 355.56 poster exactly 1080 x 1920
        open(f'poster-{i}.html', 'w').write(page(poster(p), 200, '.poster{position:relative}body{zoom:5.4}'))
    print('ok')
