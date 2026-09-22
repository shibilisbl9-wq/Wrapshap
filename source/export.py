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
    for (d, cap), w, h in zip(srcs, ws, hs):
        y = margin * MM
        if garment:                                   # garment colour backing (not part of the print)
            pad = 6 * MM
            pg.draw_rect(fitz.Rect(x - pad, y - pad, x + w + pad, y + h + pad), color=None, fill=garment, radius=0.02)
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


made = []

# 00 design system
save_pdf(['design-system'], out('00-design-system', 'wrapshap-design-system.pdf'), 'Wrapshap — Visual system')
save_ai([('design-system', '')], out('00-design-system', 'wrapshap-design-system.ai'), 'Wrapshap — Visual system', labels=False, margin=0)
made.append(jpg('design-system', out('00-design-system', 'wrapshap-design-system.jpg'), 200))

# 01 envelope
save_pdf(['envelope-front', 'envelope-back'], out('01-envelope', 'wrapshap-envelope-163x205mm-print.pdf'), 'Wrapshap — Envelope 163 x 205 mm')
save_ai([('envelope-front', 'Front — 163 x 205 mm trim + 3 mm bleed'), ('envelope-back', 'Back — 163 x 205 mm trim + 3 mm bleed')],
        out('01-envelope', 'wrapshap-envelope-163x205mm.ai'), 'Wrapshap — Envelope 163 x 205 mm')
made.append(jpg('envelope-front', out('01-envelope', 'wrapshap-envelope-front.jpg'), 300))
made.append(jpg('envelope-back', out('01-envelope', 'wrapshap-envelope-back.jpg'), 300))

# 02 mat pads
for tw, th, folder, dpi in ((250, 250, '1x1', 200), (350, 350, '1x1', 200), (400, 225, '16x9', 200), (800, 450, '16x9', 150)):
    n = f'matpad-{tw}x{th}'
    base = f'wrapshap-matpad-{folder.replace("x", "-")}-{tw}x{th}mm'
    save_pdf([n], out('02-mat-pad', folder, base + '-print.pdf'), f'Wrapshap — Mat pad {tw} x {th} mm')
    save_ai([(n, f'Mat pad {folder.replace("x", ":")} — {tw} x {th} mm trim + 3 mm bleed')], out('02-mat-pad', folder, base + '.ai'),
            f'Wrapshap — Mat pad {tw} x {th} mm')
    made.append(jpg(n, out('02-mat-pad', folder, base + '.jpg'), dpi))

# 03 t-shirt
save_pdf(['tee-back', 'tee-front'], out('03-tshirt', 'wrapshap-tee-print.pdf'), 'Wrapshap — Tee print artwork')
save_ai([('tee-back', 'Back print — 300 x 268 mm  (dark panel = garment colour, not printed)'),
         ('tee-front', 'Left chest — 90 mm wide')],
        out('03-tshirt', 'wrapshap-tee-print.ai'), 'Wrapshap — Tee print artwork', cmyk=False,
        gap=30, garment=(0.067, 0.067, 0.075))
made.append(png('tee-back', out('03-tshirt', 'wrapshap-tee-back-print-300dpi.png'), 300))
made.append(png('tee-front', out('03-tshirt', 'wrapshap-tee-front-chest-print-300dpi.png'), 300))
shutil.copy(os.path.join(HERE, 'mockup', 'tee-mockup.jpg'), out('03-tshirt', 'wrapshap-tee-mockup.jpg'))

print(made)
