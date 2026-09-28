"""Minimal prepress for Option C's envelope-only mockups: place the original vector logo,
set Trim/Bleed boxes, export JPG previews. No CMYK conversion — these are RGB mockups for
picking a direction, not print-ready files (see README), so this skips post.py's to_cmyk
step and its ICC dependency entirely.
"""
import json, os
import pymupdf as fitz
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
MM = 72 / 25.4
PX = 0.75
BLEED = 3.0

jobs = json.load(open(os.path.join(HERE, 'jobs_c.json')))
slots = json.load(open(os.path.join(HERE, 'slots_c.json')))
logo = fitz.open(os.path.join(HERE, 'logo.pdf'))
for d in ('placed', 'preview'):
    os.makedirs(os.path.join(HERE, d), exist_ok=True)


def place_logos(pg, name):
    for s in slots[name]:
        r = fitz.Rect(s['x'] * PX, s['y'] * PX, (s['x'] + s['w']) * PX, (s['y'] + s['h']) * PX)
        pg.show_pdf_page(r, logo, 0, keep_proportion=True)


def set_boxes(pg, j):
    doc, x = pg.parent, pg.xref
    mb = pg.mediabox
    W, H = min(j['w'] * MM, mb.width), min(j['h'] * MM, mb.height)
    y1 = mb.y1
    arr = lambda *v: '[' + ' '.join('%.4f' % n for n in v) + ']'
    doc.xref_set_key(x, 'MediaBox', arr(0, y1 - H, W, y1))
    doc.xref_set_key(x, 'CropBox', 'null')
    if j['trim']:
        b = BLEED * MM
        tw, th = j['trim'][0] * MM, j['trim'][1] * MM
        doc.xref_set_key(x, 'BleedBox', arr(0, y1 - H, W, y1))
        doc.xref_set_key(x, 'TrimBox', arr(b, max(y1 - b - th, y1 - H), min(b + tw, W), y1 - b))


for j in jobs:
    name = j['name']
    raw = os.path.join(HERE, 'raw', name + '.pdf')
    doc = fitz.open(raw)
    pg = doc[0]
    assert abs(pg.rect.width - j['w'] * MM) < 1 and abs(pg.rect.height - j['h'] * MM) < 1, name
    place_logos(pg, name)
    set_boxes(pg, j)
    placed = os.path.join(HERE, 'placed', name + '.pdf')
    doc.save(placed, garbage=3, deflate=True)
    pix = fitz.open(placed)[0].get_pixmap(dpi=300, clip=fitz.open(placed)[0].trimbox)
    Image.frombytes('RGB', (pix.width, pix.height), pix.samples).save(
        os.path.join(HERE, 'preview', name + '.jpg'), quality=93, dpi=(300, 300), optimize=True)
    print('placed', name)
