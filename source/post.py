"""Prepress: token RGB -> exact CMYK, place the original vector logo, convert the rest to CMYK,
set Trim/Bleed boxes. Writes placed/<name>.pdf (RGB, for previews) and print/<name>.pdf."""
import json, os, re, sys
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
MM = 72 / 25.4
PX = 0.75                      # CSS px -> PDF pt
BLEED = 3.0

jobs = json.load(open(os.path.join(HERE, 'jobs.json')))
slots = json.load(open(os.path.join(HERE, 'slots.json')))
tokens = json.load(open(os.path.join(HERE, 'tokens.json')))
logo = fitz.open(os.path.join(HERE, 'logo.pdf'))
only = sys.argv[1:]
for d in ('placed', 'print', 'preview'):
    os.makedirs(os.path.join(HERE, d), exist_ok=True)

from PIL import Image, ImageCms

TOK = {}
for name, (hexv, cmyk) in tokens.items():
    TOK[tuple(int(hexv[i:i + 2], 16) for i in (1, 3, 5))] = tuple(v / 100 for v in cmyk)
AMB = next(k for n, (h, _) in tokens.items() if n == 'Amber' for k in [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))])
ORG = next(k for n, (h, _) in tokens.items() if n == 'Orange' for k in [tuple(int(h[i:i + 2], 16) for i in (1, 3, 5))])
_ICC = ImageCms.buildTransform(ImageCms.createProfile('sRGB'),
                               ImageCms.getOpenProfile('/usr/share/color/icc/ghostscript/default_cmyk.icc'), 'RGB', 'CMYK')


def rgb_to_cmyk(rgb):
    """Token colours -> exact spec; amber->orange blends -> blend of the two specs; else ICC."""
    rgb = tuple(round(v) for v in rgb)
    if rgb in TOK:
        return TOK[rgb]
    d = [o - a for a, o in zip(AMB, ORG)]
    t = sum((c - a) * dd for c, a, dd in zip(rgb, AMB, d)) / sum(dd * dd for dd in d)
    if -0.02 <= t <= 1.02 and all(abs(a + dd * t - c) <= 2.5 for a, dd, c in zip(AMB, d, rgb)):
        t = min(1, max(0, t))
        return tuple(x + (y - x) * t for x, y in zip(TOK[AMB], TOK[ORG]))
    px = ImageCms.applyTransform(Image.new('RGB', (1, 1), rgb), _ICC).getpixel((0, 0))
    return tuple(v / 255 for v in px)


def fmt(c):
    return ' '.join('%.4g' % v for v in c)


COLOR_OP = re.compile(rb'(?<![\w.])(-?[\d.]+)\s+(-?[\d.]+)\s+(-?[\d.]+)\s+(rg|RG)\b')
ARR = re.compile(r'/(C0|C1) \[ ([\d.\-]+) ([\d.\-]+) ([\d.\-]+) \]')


def to_cmyk(doc):
    """Convert all artwork colour in a Chromium/Skia PDF to DeviceCMYK, keeping it vector.

    Solid rg/RG operators and the colour patterns' shading functions are converted;
    soft-mask (alpha) groups are left as they are — they only carry luminosity."""
    n = doc.xref_length()
    mask_forms, stack = set(), []
    for x in range(1, n):
        for g in re.findall(r'/SMask\s*<<[^>]*?/G (\d+) 0 R', doc.xref_object(x), re.S):
            stack.append(int(g))
    mask_refs = set()
    while stack:                                   # everything reachable from a mask group
        x = stack.pop()
        if x in mask_refs:
            continue
        mask_refs.add(x)
        stack += [int(r) for r in re.findall(r'(\d+) 0 R', doc.xref_object(x))]
    stats = {'ops': 0, 'shadings': 0, 'groups': 0}
    contents = set(doc[0].get_contents())
    for x in range(1, n):
        if x in mask_refs:
            continue
        obj = doc.xref_object(x)
        if doc.xref_is_stream(x) and (x in contents or '/Subtype /Form' in obj):
            def rep(m):
                stats['ops'] += 1
                c = rgb_to_cmyk([float(v) * 255 for v in m.groups()[:3]])
                return (fmt(c) + (' k' if m.group(4) == b'rg' else ' K')).encode()
            doc.update_stream(x, COLOR_OP.sub(rep, doc.xref_stream(x)))
        new = obj
        if '/ShadingType' in obj and '/DeviceRGB' in obj:
            new = ARR.sub(lambda m: '/%s [ %s ]' % (m.group(1), fmt(rgb_to_cmyk([float(v) * 255 for v in m.groups()[1:]]))), new)
            new = new.replace('/ColorSpace /DeviceRGB', '/ColorSpace /DeviceCMYK')
            stats['shadings'] += 1
        if '/S /Transparency' in new and '/CS /DeviceRGB' in new:
            new = new.replace('/CS /DeviceRGB', '/CS /DeviceCMYK')
            stats['groups'] += 1
        if new != obj:
            doc.update_object(x, new)
    return stats


def set_boxes(pg, j):
    """Snap the page to its exact size (Chrome rounds to 1/96 in) and set Trim/Bleed boxes.
    Boxes are written directly in PDF user space (bottom-left origin), top-left anchored."""
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


def place_logos(pg, name):
    for s in slots[name]:
        r = fitz.Rect(s['x'] * PX, s['y'] * PX, (s['x'] + s['w']) * PX, (s['y'] + s['h']) * PX)
        pg.show_pdf_page(r, logo, 0, keep_proportion=True)


for j in jobs:
    name = j['name']
    if only and name not in only:
        continue
    raw = os.path.join(HERE, 'raw', name + '.pdf')
    doc = fitz.open(raw)
    if doc.page_count != 1:
        print('WARN', name, 'has', doc.page_count, 'pages'); doc.select([0])
    pg = doc[0]
    assert abs(pg.rect.width - j['w'] * MM) < 1 and abs(pg.rect.height - j['h'] * MM) < 1, name
    # 1) RGB preview master
    place_logos(pg, name)
    set_boxes(pg, j)
    placed = os.path.join(HERE, 'placed', name + '.pdf')
    doc.save(placed, garbage=3, deflate=True)
    # 2) print master
    out = os.path.join(HERE, 'print', name + '.pdf')
    if j['cmyk']:
        doc = fitz.open(raw)
        doc.select([0])
        stats = to_cmyk(doc)
        place_logos(doc[0], name)                 # original logo is already CMYK
        set_boxes(doc[0], j)
        doc.set_metadata({'title': 'Wrapshap — ' + name, 'creator': 'Wrapshap visual system'})
        doc.save(out, garbage=3, deflate=True)
        print('print', name, 'CMYK', stats)
    else:
        d2 = fitz.open(placed)
        d2.set_metadata({'title': 'Wrapshap — ' + name, 'creator': 'Wrapshap visual system'})
        d2.save(out, garbage=3, deflate=True)
        print('print', name, '(RGB, garment)')
    dpi = min(150, int(2400 / (max(j['w'], j['h']) / 25.4)))
    fitz.open(placed)[0].get_pixmap(dpi=dpi, alpha=not j['trim'] and not j['cmyk']).save(
        os.path.join(HERE, 'preview', name + '.png'))
    fitz.open(out)[0].get_pixmap(dpi=dpi).save(os.path.join(HERE, 'preview', name + '.print.png'))
