"""Package deliverables into the repo: print PDF, .ai (PDF-compatible Illustrator file), JPG, PNG."""
import os, shutil, sys
import pymupdf as fitz
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = sys.argv[1]
FONTS = os.path.abspath(os.path.join(HERE, '..', 'fonts'))
MM = 72 / 25.4
MONO = os.path.join(FONTS, 'GeistMono-500.ttf')


def P(kind, name):
    return fitz.open(os.path.join(HERE, kind, name + '.pdf'))


def out(*parts):
    p = os.path.join(REPO, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def meta(doc, title):
    doc.set_metadata({'title': title, 'author': 'Wrapshap', 'creator': 'Wrapshap visual system v1.0',
                      'subject': 'Wrapshap brand application'})


def save_pdf(names, path, title):
    """Print-ready PDF: one page per artwork, boxes preserved."""
    doc = fitz.open()
    for n in names:
        doc.insert_pdf(P('print', n))
    meta(doc, title)
    doc.save(path, garbage=3, deflate=True)


def save_ai(items, path, title, cmyk=True, gap=24, margin=18, labels=True, garment=None):
    """One canvas holding every artwork side by side (Illustrator opens one PDF page as one
    artboard), with crop marks at trim and a small caption under each piece."""
    srcs = [(P('print', n), cap) for n, cap in items]
    garments = garment if isinstance(garment, list) else [garment] * len(srcs)   # one colour, or one per item
    ws = [d[0].rect.width for d, _ in srcs]
    hs = [d[0].rect.height for d, _ in srcs]
    cap_h = 12 * MM if labels else 0
    W = sum(ws) + gap * MM * (len(ws) - 1) + 2 * margin * MM
    H = max(hs) + 2 * margin * MM + cap_h
    doc = fitz.open()
    pg = doc.new_page(width=W, height=H)
    pg.insert_font(fontname='gm', fontfile=MONO)
    x = margin * MM
    k = (0, 0, 0, 1) if cmyk else (0, 0, 0)
    grey = (0, 0, 0, 0.55) if cmyk else (0.45, 0.45, 0.45)
    for (d, cap), w, h, gcol in zip(srcs, ws, hs, garments):
        y = margin * MM
        if gcol:                                      # garment colour backing (not part of the print)
            pad = 6 * MM
            pg.draw_rect(fitz.Rect(x - pad, y - pad, x + w + pad, y + h + pad), color=None, fill=gcol, radius=0.02)
        pg.show_pdf_page(fitz.Rect(x, y, x + w, y + h), d, 0)
        t = d[0].trimbox
        if abs(t.width - w) > 1:                      # has bleed -> crop marks at trim
            tx0, ty0, tx1, ty1 = x + t.x0, y + t.y0, x + t.x1, y + t.y1
            L, off = 5 * MM, 1 * MM
            sh = pg.new_shape()
            for cx in (tx0, tx1):
                sh.draw_line((cx, y - off - L), (cx, y - off))
                sh.draw_line((cx, y + h + off), (cx, y + h + off + L))
            for cy in (ty0, ty1):
                sh.draw_line((x - off - L, cy), (x - off, cy))
                sh.draw_line((x + w + off, cy), (x + w + off + L, cy))
            sh.finish(color=k, width=0.25)
            sh.commit()
        if labels:
            pg.insert_text((x, y + h + 8 * MM), cap.upper(), fontname='gm', fontsize=7, color=grey)
        x += w + gap * MM
    meta(doc, title)
    doc.save(path, garbage=3, deflate=True)


def jpg(name, path, dpi):
    pg = P('placed', name)[0]
    pix = pg.get_pixmap(dpi=dpi, clip=pg.trimbox)
    Image.frombytes('RGB', (pix.width, pix.height), pix.samples).save(path, quality=93, dpi=(dpi, dpi), optimize=True)
    return pix.width, pix.height


def png(name, path, dpi):
    pix = P('placed', name)[0].get_pixmap(dpi=dpi, alpha=True)
    pix.set_dpi(dpi, dpi)
    pix.save(path)
    return pix.width, pix.height


def size_mm(name):
    r = P('print', name)[0].rect
    return round(r.width / MM), round(r.height / MM)


def export_option(pre, root, title):
    made = []
    o = lambda *p: out(root, *p)
    # 00 design system
    save_pdf([pre + 'design-system'], o('00-design-system', 'wrapshap-design-system.pdf'), f'Wrapshap — Visual system ({title})')
    save_ai([(pre + 'design-system', '')], o('00-design-system', 'wrapshap-design-system.ai'), f'Wrapshap — Visual system ({title})',
            labels=False, margin=0)
    made.append(jpg(pre + 'design-system', o('00-design-system', 'wrapshap-design-system.jpg'), 200))
    shutil.copy(os.path.join(HERE, 'logo.pdf'), o('00-design-system', 'wrapshap-logo-vector.pdf'))
    shutil.copy(os.path.join(HERE, 'logo.pdf'), o('00-design-system', 'wrapshap-logo-vector.ai'))
    # 01 envelope
    save_pdf([pre + 'envelope-front', pre + 'envelope-back'], o('01-envelope', 'wrapshap-envelope-163x205mm-print.pdf'),
             f'Wrapshap — Envelope 163 x 205 mm ({title})')
    save_ai([(pre + 'envelope-front', 'Front — 163 x 205 mm trim + 3 mm bleed'), (pre + 'envelope-back', 'Back — 163 x 205 mm trim + 3 mm bleed')],
            o('01-envelope', 'wrapshap-envelope-163x205mm.ai'), f'Wrapshap — Envelope 163 x 205 mm ({title})')
    made.append(jpg(pre + 'envelope-front', o('01-envelope', 'wrapshap-envelope-front.jpg'), 300))
    made.append(jpg(pre + 'envelope-back', o('01-envelope', 'wrapshap-envelope-back.jpg'), 300))
    # 02 mat pads
    for tw, th, folder, dpi in ((250, 250, '1x1', 200), (350, 350, '1x1', 200), (400, 225, '16x9', 200), (800, 450, '16x9', 150)):
        n = f'{pre}matpad-{tw}x{th}'
        base = f'wrapshap-matpad-{folder.replace("x", "-")}-{tw}x{th}mm'
        save_pdf([n], o('02-mat-pad', folder, base + '-print.pdf'), f'Wrapshap — Mat pad {tw} x {th} mm ({title})')
        save_ai([(n, f'Mat pad {folder.replace("x", ":")} — {tw} x {th} mm trim + 3 mm bleed')], o('02-mat-pad', folder, base + '.ai'),
                f'Wrapshap — Mat pad {tw} x {th} mm ({title})')
        made.append(jpg(n, o('02-mat-pad', folder, base + '.jpg'), dpi))
    overview(REPO + '/' + root, os.path.join(REPO, root, 'wrapshap-overview.jpg'))
    return made


def overview(base, path):
    rows = [['01-envelope/wrapshap-envelope-front.jpg', '01-envelope/wrapshap-envelope-back.jpg', '00-design-system/wrapshap-design-system.jpg'],
            ['02-mat-pad/1x1/wrapshap-matpad-1-1-250x250mm.jpg', '02-mat-pad/1x1/wrapshap-matpad-1-1-350x350mm.jpg',
             '02-mat-pad/16x9/wrapshap-matpad-16-9-400x225mm.jpg', '02-mat-pad/16x9/wrapshap-matpad-16-9-800x450mm.jpg'],
            ['03-polo-shirt/wrapshap-polo-mockup.jpg'], ['03-t-shirt/wrapshap-tee-mockup.jpg']]
    rows = [[f for f in r if os.path.exists(os.path.join(base, f))] for r in rows]
    rows = [r for r in rows if r]
    W, M, G = 3200, 120, 48
    built = []
    for r in rows:
        ims = [Image.open(os.path.join(base, f)).convert('RGB') for f in r]
        h = round((W - 2 * M - G * (len(ims) - 1)) / sum(i.width / i.height for i in ims))
        built.append([i.resize((round(i.width * h / i.height), h), Image.LANCZOS) for i in ims])
    H = M * 2 + sum(r[0].height for r in built) + G * (len(built) - 1)
    c = Image.new('RGB', (W, H), (231, 229, 224))
    y = M
    for r in built:
        x = M
        for i in r:
            c.paste(i, (x, y))
            x += i.width + G
        y += r[0].height + G
    c.save(path, quality=90, optimize=True)


def export_polo(root):
    o = lambda *p: out(root, '03-polo-shirt', *p)
    bw, bh = size_mm('polo-back')
    fw, fh = size_mm('polo-front')
    save_pdf(['polo-back', 'polo-front'], o('wrapshap-polo-print.pdf'), 'Wrapshap — Polo print artwork')
    save_ai([('polo-back', f'Back print — {bw} x {bh} mm  (dark panel = garment colour, not printed)'),
             ('polo-front', f'Left chest logo — {fw} x {fh} mm')],
            o('wrapshap-polo-print.ai'), 'Wrapshap — Polo print artwork', cmyk=False, gap=30, garment=(0.067, 0.067, 0.075))
    made = [png('polo-back', o('wrapshap-polo-back-print-300dpi.png'), 300),
            png('polo-front', o('wrapshap-polo-front-chest-print-300dpi.png'), 300)]
    shutil.copy(os.path.join(HERE, 'mockup', 'polo-mockup.jpg'), o('wrapshap-polo-mockup.jpg'))
    overview(os.path.join(REPO, root), os.path.join(REPO, root, 'wrapshap-overview.jpg'))
    return made


def export_tee(root):
    o = lambda *p: out(root, '03-t-shirt', *p)
    made = []
    panel = {'black': (0.067, 0.067, 0.075), 'white': (0.93, 0.93, 0.92)}
    for g in ('black', 'white'):
        n = lambda p: f'tee-{g}-{p}'
        dims = {p: size_mm(n(p)) for p in ('back', 'chest', 'neck')}
        save_pdf([n('back'), n('chest'), n('neck'), 'tee-label'], o(f'wrapshap-tee-{g}-print.pdf'), f'Wrapshap — Graffiti tee, {g}')
        save_ai([(n('back'), 'Back — %d x %d mm' % dims['back']), (n('chest'), 'Left chest — %d x %d mm' % dims['chest']),
                 (n('neck'), 'Inside neck — %d x %d mm' % dims['neck']), ('tee-label', 'Label 20 x 32')],
                o(f'wrapshap-tee-{g}.ai'), f'Wrapshap — Graffiti tee, {g} (panel = garment colour, not printed)',
                cmyk=False, gap=30, garment=panel[g])
        for p in ('back', 'chest', 'neck'):
            made.append(png(n(p), o(f'wrapshap-tee-{g}-{p}-print-300dpi.png'), 300))
    made.append(png('tee-label', o('wrapshap-tee-label-300dpi.png'), 300))
    shutil.copy(os.path.join(HERE, 'mockup', 'tee-graffiti-mockup.jpg'), o('wrapshap-tee-mockup.jpg'))
    overview(os.path.join(REPO, root), os.path.join(REPO, root, 'wrapshap-overview.jpg'))
    return made


PANEL = {'black': (0.067, 0.067, 0.075), 'white': (0.957, 0.957, 0.949),
         'cream': (0.937, 0.91, 0.847), 'orange': (0.953, 0.573, 0.0)}
SHARED = [('tee-black-neck', 'neck', 'Inside neck'), ('tee-label', 'label', 'Woven label 20 x 32 mm (reference for the label maker)')]
# folder, title, shirt colour, pieces: (piece, file slug, caption)
COLLECTION = [
    ('design-1-signature-graffiti', 'Signature Graffiti', 'black',
     [('tee-black-back', 'back', 'Back'), ('tee-black-chest', 'chest', 'Left chest')] + SHARED),
    ('design-2-playful-character', 'Playful Character', 'white', [('c2-back', 'back', 'Back')]),
    ('design-3-minimal-bold', 'Minimal Bold', 'black',
     [('c3-front', 'front', 'Front'), ('c3-front-alt', 'front-alt-full-colour-logo', 'Alternative: full-colour logo')] + SHARED),
    ('design-4-abstract', 'Abstract', 'cream',
     [('c4-back', 'back', 'Back'), ('c4-back-alt', 'back-alt-full-colour-logo', 'Alternative: full-colour logo')]),
    ('design-5-clean-tagline', 'Clean Tagline', 'black',
     [('c5-chest', 'chest', 'Left chest'), ('c5-back-neck', 'back-neck-optional', 'Optional: back neck logo')] + SHARED),
    ('design-6-vertical-bold', 'Vertical Bold', 'orange',
     [('c6-back', 'back', 'Back'), ('c6-back-alt', 'back-alt-full-colour-logo', 'Alternative: full-colour logo')]),
]


def export_collection(root):
    made = []
    for i, (folder, title, shirt, pieces) in enumerate(COLLECTION, 1):
        o = lambda *p: out(root, folder, *p)
        base = f'wrapshap-tee-d{i}-{folder.split("-", 2)[2]}'
        full = f'Wrapshap — T-shirt design {i}: {title} ({shirt} tee)'
        save_pdf([n for n, _, _ in pieces], o(base + '-print.pdf'), full)
        caps = [(n, '%s — %d x %d mm' % ((cap,) + size_mm(n))) for n, _, cap in pieces]
        save_ai(caps, o(base + '.ai'), full + ' — panel = shirt colour, not printed', cmyk=False, gap=30, garment=PANEL[shirt])
        for n, slug, _ in pieces:
            made.append(png(n, o(f'{base}-{slug}-print-300dpi.png'), 300))
        shutil.copy(os.path.join(HERE, 'mockup', f'collection-d{i}.jpg'), o(base + '-mockup.jpg'))
    # every design's main print on one canvas
    save_ai([(p[0][0], f'Design {i} — {t}') for i, (_, t, _, p) in enumerate(COLLECTION, 1)],
            out(root, 'wrapshap-tshirt-collection.ai'), 'Wrapshap — T-shirt collection, designs 1-6 (panels = shirt colour, not printed)',
            cmyk=False, gap=40, garment=[PANEL[s] for _, _, s, _ in COLLECTION])
    shutil.copy(os.path.join(HERE, 'mockup', 'collection-overview.jpg'), out(root, 'wrapshap-tshirt-collection-overview.jpg'))
    return made


def export_photos(root):
    """Photo-style rendered mockups (photo_mockup.py) next to each design's files."""
    made = []
    for i, (folder, _, _, _) in enumerate(COLLECTION, 1):
        for view in ('front', 'back'):
            src = os.path.join(HERE, 'mockup', f'photo-d{i}-{view}.jpg')
            if os.path.exists(src):
                dst = out(root, folder, f'wrapshap-tee-d{i}-{folder.split("-", 2)[2]}-photo-{view}.jpg')
                shutil.copy(src, dst)
                made.append(os.path.relpath(dst, REPO))
    dst = out(root, 'wrapshap-tshirt-collection-photo.jpg')
    shutil.copy(os.path.join(HERE, 'mockup', 'photo-collection.jpg'), dst)
    return made + [os.path.relpath(dst, REPO)]


def export_voucher(root):
    made = []
    for key, label in (('pakistan', 'Pakistan'), ('uae', 'UAE')):
        o = lambda *p: out(root, '04-stationery', key, *p)
        n = f'st-{key}-voucher'
        base = f'wrapshap-receipt-voucher-{key}-A5'
        save_pdf([n], o(base + '-print.pdf'), f'Wrapshap — Receipt voucher {label} (A5)')
        save_ai([(n, f'Receipt voucher {label} — A5 landscape 210 x 148 mm trim + 3 mm bleed')], o(base + '.ai'),
                f'Wrapshap — Receipt voucher {label} (A5)')
        made.append(jpg(n, o(base + '.jpg'), 200))
    return made


def export_stationery(root):
    made = []
    for key, label in (('pakistan', 'Pakistan'), ('uae', 'UAE')):
        o = lambda *p: out(root, '04-stationery', key, *p)
        n = f'st-{key}'
        save_pdf([n + '-letterhead'], o(f'wrapshap-letterhead-{key}-A4-print.pdf'), f'Wrapshap — Letterhead {label} (A4)')
        save_ai([(n + '-letterhead', f'Letterhead {label} — A4 210 x 297 mm trim + 3 mm bleed')],
                o(f'wrapshap-letterhead-{key}-A4.ai'), f'Wrapshap — Letterhead {label} (A4)')
        made.append(jpg(n + '-letterhead', o(f'wrapshap-letterhead-{key}-A4.jpg'), 200))
        save_pdf([n + '-card-front', n + '-card-back'], o(f'wrapshap-business-card-{key}-90x50mm-print.pdf'),
                 f'Wrapshap — Business card {label} (90 x 50 mm)')
        save_ai([(n + '-card-front', f'Card front — 90 x 50 mm trim + 3 mm bleed'),
                 (n + '-card-back', f'Card back ({label}) — replace name, designation, phone before printing')],
                o(f'wrapshap-business-card-{key}-90x50mm.ai'), f'Wrapshap — Business card {label} (90 x 50 mm)', gap=14, margin=12)
        made.append(jpg(n + '-card-front', o(f'wrapshap-business-card-{key}-front.jpg'), 600))
        made.append(jpg(n + '-card-back', o(f'wrapshap-business-card-{key}-back.jpg'), 600))
    return made


if __name__ == '__main__':
    opt = sys.argv[2] if len(sys.argv) > 2 else 'a'
    if opt == 'tee':
        print(export_tee('option-b-graffiti'))
        sys.exit()
    if opt == 'collection':
        print(export_collection('t-shirt-collection'))
        sys.exit()
    if opt == 'photos':
        print(export_photos('t-shirt-collection'))
        sys.exit()
    if opt == 'voucher':
        print(export_voucher('option-a-wrap-halo'))
        sys.exit()
    if opt == 'stationery':
        print(export_stationery('option-a-wrap-halo'))
        sys.exit()
    if opt == 'polo':
        print(export_polo('option-a-wrap-halo'))
        overview(os.path.join(REPO, 'option-b-graffiti'), os.path.join(REPO, 'option-b-graffiti', 'wrapshap-overview.jpg'))
        sys.exit()
    if opt == 'a':
        print(export_option('', 'option-a-wrap-halo', 'Option A: Wrap Halo'))
    else:
        print(export_option('b-', 'option-b-graffiti', 'Option B: Graffiti'))
