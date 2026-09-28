"""One-colour versions of the original Wrapshap logo (source/logo.pdf), kept fully vector.

The original draws each letter as a gradient image clipped to the letter shape, plus an orange
outline and an amber highlight on top, over a white rim. Swapping each gradient image for a flat
rectangle (still clipped to the letter) and dropping the outline and highlight gives the exact
letter shapes in a single colour. Nothing is redrawn.
"""
import re
import pymupdf

INK, WHITE = '#0E0E0E', '#FFFFFF'

raw = pymupdf.open('../logo.pdf')[0].get_svg_image(text_as_path=True)
open('logo-colour.svg', 'w').write(raw)


def mono(ink, rim=None):
    s = re.sub(r'<image [^>]*/>', f'<rect x="0" y="0" width="219.12" height="79.92" fill="{ink}"/>', raw)
    s = s.replace('fill="#f7941f"', 'fill="none"').replace('fill="#e9c93b"', 'fill="none"')
    if rim is None:
        s = re.sub(r'<path [^>]*fill="#ffffff"/>', '', s)
        s = re.sub(r'<path [^>]*stroke="#ffffff"[^>]*/>', '', s)
    else:
        s = s.replace('#ffffff', rim)
    return s


open('logo-mono-black.svg', 'w').write(mono(INK))
open('logo-mono-white.svg', 'w').write(mono(WHITE))
open('logo-mono-black-rim.svg', 'w').write(mono(INK, WHITE))
