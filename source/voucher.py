"""Receipt voucher (Option A system), A5 landscape, one per office. Same fields as the
supplied reference voucher; drawn as SVG in mm so every rule and box is exact."""
import json, os
import design as A
from stationery import OFFICES

HERE = A.HERE
C, B = A.C, A.BLEED
INK, WHITE, SIGNAL, ORANGE = A.INK, A.WHITE, A.SIGNAL, A.ORANGE
TEXT = C['Ink Text']
CUR = {'uae': dict(major='Dhs.', minor='Fils', words='Dirhams'),
       'pakistan': dict(major='Rs.', minor='Paisa', words='Rupees')}


def T(x, y, s, size, weight=500, color=TEXT, anchor='start', mono=False, track=0):
    fam = "'Geist Mono'" if mono else "'Geist'"
    tr = f' letter-spacing="{track}em"' if track else ''
    s = s.replace('&', '&amp;').replace('  ', '\u00a0\u00a0')
    return (f'<text x="{x:.2f}" y="{y:.2f}" font-family="{fam}" font-weight="{weight}" font-size="{size * 25.4 / 72:.3f}" '
            f'fill="{color}" text-anchor="{anchor}"{tr}>{s}</text>')


def line(x0, y0, x1, y1, w=0.25, color=TEXT):
    return f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="{color}" stroke-width="{w}"/>'


def rect(x, y, w, h, sw=0.3, fill='none', color=TEXT):
    return f'<rect x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" fill="{fill}" stroke="{color}" stroke-width="{sw}"/>'


def icon(kind, x, y):
    """3 mm line icons, centred on (x, y)."""
    s = f'fill="none" stroke="{ORANGE}" stroke-width=".28" stroke-linecap="round" stroke-linejoin="round"'
    if kind == 'mail':
        return (f'<rect x="{x - 1.45}" y="{y - 1.05}" width="2.9" height="2.1" rx=".35" {s}/>'
                f'<path d="M{x - 1.3} {y - .8} L{x} {y + .15} L{x + 1.3} {y - .8}" {s}/>')
    if kind == 'web':
        return (f'<circle cx="{x}" cy="{y}" r="1.35" {s}/><ellipse cx="{x}" cy="{y}" rx=".6" ry="1.35" {s}/>'
                f'<path d="M{x - 1.35} {y} H{x + 1.35}" {s}/>')
    return (f'<path d="M{x} {y + 1.5} C{x - .4} {y + .9} {x - 1.2} {y + .1} {x - 1.2} {y - .5} A1.2 1.2 0 0 1 {x + 1.2} {y - .5} '
            f'C{x + 1.2} {y + .1} {x + .4} {y + .9} {x} {y + 1.5}Z" {s}/><circle cx="{x}" cy="{y - .5}" r=".42" {s}/>')


def voucher(key, o):
    tw, th = 210, 148
    W, H = tw + 2 * B, th + 2 * B
    cur = CUR[key]
    X = lambda v: B + v                      # trim -> page coordinates
    x0, x1 = 10, 200
    svg = []
    # header: contact (left), logo (centre), number + date (right)
    rows = [('mail', [o['email']]), ('web', [o['web']]), ('pin', o['address'])]
    y = 11.2
    for kind, lines in rows:
        svg.append(icon(kind, X(x0 + 1.5), X(y - 1.0)))
        for i, s in enumerate(lines):
            svg.append(T(X(x0 + 5), X(y + i * 3.4), s.rstrip(','), 7.2, 500))
        y += 4.9 + 3.4 * (len(lines) - 1)
    lw, lcx, lcy = 46, X(105), X(19.5)
    for lab, yy in (('No.', 16.5), ('Date', 26.5)):
        svg.append(T(X(146), X(yy), lab, 9, 600))
        svg.append(line(X(158), X(yy + 0.6), X(x1), X(yy + 0.6), 0.25))
    # title band + orange rule (as on the letterhead)
    svg.append(f'<rect x="0" y="{X(33.5)}" width="{W}" height="8.5" fill="{INK}"/>')
    svg.append(f'<rect x="0" y="{X(42)}" width="{W}" height=".9" fill="{ORANGE}"/>')
    svg.append(T(W / 2, X(39.15), 'RECEIPT VOUCHER', 9.6, 700, WHITE, 'middle', track=0.22))
    # amount boxes
    by, bh = 49, 8
    svg.append(T(X(x0 + 0.6), X(by - 1.3), cur['major'].upper(), 5.6, 500, C['Card Text'], mono=True, track=0.12))
    svg.append(T(X(40.6), X(by - 1.3), cur['minor'].upper(), 5.6, 500, C['Card Text'], mono=True, track=0.12))
    svg.append(T(X(62.6), X(by - 1.3), 'BEING PAYMENT FOR', 5.6, 500, C['Card Text'], mono=True, track=0.12))
    svg += [rect(X(x0), X(by), 44, bh, 0.35), line(X(40), X(by), X(40), X(by + bh), 0.35), rect(X(62), X(by), x1 - 62, bh, 0.35)]
    # written lines
    for lab, yy in (('Received from Mr./M/s:', 65), (f"The sum of {cur['words']}:", 73)):
        svg.append(T(X(x0), X(yy), lab, 9, 500))
        lx = x0 + (38 if 'Received' in lab else 32.5)
        svg.append(line(X(lx), X(yy + 0.6), X(x1), X(yy + 0.6)))
    # payment table
    cols = [(x0, 'S.No'), (20, 'Cheque Date'), (62, 'Cheque Number'), (112, 'Bank / Cash'), (156, 'Amount')]
    ty, hh, rh, n = 78, 6, 4.7, 7
    svg.append(f'<rect x="{X(x0)}" y="{X(ty)}" width="{x1 - x0}" height="{hh}" fill="{INK}"/>')
    edges = [c[0] for c in cols] + [x1]
    for (cx, lab), nx in zip(cols, edges[1:]):
        svg.append(T(X((cx + nx) / 2), X(ty + 4.05), lab.upper(), 5.8, 500, WHITE, 'middle', mono=True, track=0.1))
    bot = ty + hh + n * rh
    for i in range(1, n):
        svg.append(line(X(x0), X(ty + hh + i * rh), X(x1), X(ty + hh + i * rh), 0.2))
    for e in edges[1:-1]:
        svg.append(line(X(e), X(ty + hh), X(e), X(bot), 0.2))
    svg.append(rect(X(x0), X(ty), x1 - x0, bot - ty, 0.35))
    # note + customer / signatures
    svg.append(T(X(x0), X(bot + 4.6), 'Note: This receipt is valid only when signed by an authorised Wrapshap representative. '
                 'Cheques are subject to realisation.', 6.6, 400, C['Card Text']))
    for lab, yy, xa, xb, lx in (('Customer No:', bot + 11, x0, 98, 22), ('Customer E-mail:', bot + 17.5, x0, 98, 27.5),
                                ('Customer Signature:', bot + 11, 112, x1, 33), ('Authorised Signature:', bot + 17.5, 112, x1, 35.5)):
        svg.append(T(X(xa), X(yy), lab, 9, 500))
        svg.append(line(X(xa + lx), X(yy + 0.6), X(xb), X(yy + 0.6)))
    # footer band
    fy = 140
    svg.append(f'<rect x="0" y="{X(fy)}" width="{W}" height="{H - X(fy)}" fill="{INK}"/>')
    svg.append(T(X(x0), X(fy + 5.1), f"WRAPSHAP  —  {o['label'].upper()}", 5.6, 500, C['Label'], mono=True, track=0.16))
    svg.append(T(W / 2, X(fy + 5.2), f"{o['web']}   ·   {o['email']}", 7.4, 500, WHITE, 'middle'))
    svg.append(T(X(x1), X(fy + 5.1), 'STAY WRAPPED  ·  STAY PROTECTED', 5.6, 500, SIGNAL, 'end', mono=True, track=0.16))
    return W, H, A.page(W, H, WHITE, ''.join(svg), A.logo_slot(lcx, lcy, lw))


if __name__ == '__main__':
    jobs = []
    for key, o in OFFICES.items():
        name = f'st-{key}-voucher'
        W, H, doc = voucher(key, o)
        p = os.path.join(HERE, 'html', name + '.html')
        open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=(210, 148), cmyk=True))
    json.dump(jobs, open(os.path.join(HERE, 'jobs_voucher.json'), 'w'), indent=1)
    print([j['name'] for j in jobs])
