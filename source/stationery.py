"""Stationery (Option A, Wrap Halo): A4 letterhead + 90 x 50 mm business card, per country."""
import json, os
import design as A

HERE = A.HERE
C, B = A.C, A.BLEED
INK, WHITE, SIGNAL, ORANGE = A.INK, A.WHITE, A.SIGNAL, A.ORANGE

OFFICES = {
    'pakistan': dict(label='Pakistan',
                     address=['17-A Cooper Rd, Garhi Shahu,', 'Lahore, 54000, Pakistan'],
                     web='www.wrapshap.pk', email='info@wrapshap.pk',
                     phone='+92 3XX XXX XXXX'),                 # placeholder: no number supplied
    'uae': dict(label='UAE',
                address=['406, Building 11, Bay Square,', 'Business Bay, Dubai, UAE'],
                web='www.wrapshap.ae', email='info@wrapshap.ae',
                phone='+971 5X XXX XXXX'),                      # placeholder: no number supplied
}


def letterhead(o):
    tw, th = 210, 297
    W, H = tw + 2 * B, th + 2 * B
    band = B + 36
    lw = 44
    lcx, lcy = B + 18 + lw / 2, B + 18
    svg = (f'<defs><clipPath id="hb"><rect width="{W}" height="{band}"/></clipPath></defs>'
           f'<rect width="{W}" height="{band}" fill="{INK}"/>'
           f'<g clip-path="url(#hb)">{A.halo(lcx, lcy, lw, n=16, step=2.3, stroke=0.25, growth=0.05, a0=0.9, a1=0.05)}</g>'
           f'<rect y="{band}" width="{W}" height="1.2" fill="{ORANGE}"/>'
           f'<line x1="{B + 18}" y1="{H - B - 14}" x2="{W - B - 18}" y2="{H - B - 14}" stroke="{C["Card Rule"]}" stroke-width=".2"/>')
    val = f"font-size:8pt;line-height:1.45;color:{WHITE}"
    html = A.logo_slot(lcx, lcy, lw) + f"""
<div class="abs" style="right:{B + 18}mm;top:{B + 8.5}mm;text-align:right">
  <div class="mono" style="font-size:5.6pt;color:{C['Label']};line-height:1;margin-bottom:2.2mm">Wrapshap&nbsp;&nbsp;{o['label']}</div>
  <div style="{val}">{o['address'][0]}<br>{o['address'][1]}</div>
  <div style="{val};margin-top:1mm"><span style="color:{SIGNAL}">{o['web']}</span>&nbsp;&nbsp;<span style="color:{C['Label']}">·</span>&nbsp;&nbsp;{o['email']}</div>
</div>
<div class="abs mono" style="left:{B + 18}mm;top:{H - B - 11.2}mm;font-size:5.8pt;color:{C['Card Muted']};line-height:1">Wrapshap&nbsp;&nbsp;—&nbsp;&nbsp;{o['label']}</div>
<div class="abs mono" style="right:{B + 18}mm;top:{H - B - 11.2}mm;font-size:5.8pt;color:{C['Card Muted']};line-height:1;text-align:right">
  {o['web']}&nbsp;&nbsp;·&nbsp;&nbsp;Stay wrapped&nbsp;&nbsp;·&nbsp;&nbsp;Stay protected</div>"""
    return W, H, A.page(W, H, WHITE, svg, html)


def card_front(o):
    tw, th = 90, 50
    W, H = tw + 2 * B, th + 2 * B
    cx, cy, lw = W / 2, H / 2, 48
    svg = A.glow(cx, cy, 34, 20, opacity=0.18, gid='gc') + A.halo(cx, cy, lw, n=12, step=2.2, stroke=0.22, growth=0.05, a1=0.06)
    html = A.logo_slot(cx, cy, lw)
    return W, H, A.page(W, H, INK, svg, html)


def card_back(o):
    tw, th = 90, 50
    W, H = tw + 2 * B, th + 2 * B
    x0 = B + 6
    lw = 21
    svg = (A.halo(W - B - 6 - lw / 2, B + 9, lw, n=9, step=1.3, stroke=0.18, growth=0.06, a0=0.7, a1=0.04)
           + f'<rect x="{x0}" y="{B + 17.2}" width="8" height=".45" fill="{ORANGE}"/>')
    row = lambda k, v: (f'<div style="display:flex;align-items:baseline;gap:2.4mm;margin-top:1.15mm">'
                        f'<span class="mono" style="font-size:5pt;color:{SIGNAL};width:2.4mm;letter-spacing:0">{k}</span>'
                        f'<span style="font-size:6.6pt;color:{WHITE};line-height:1.3">{v}</span></div>')
    html = A.logo_slot(W - B - 6 - lw / 2, B + 9, lw) + f"""
<div class="abs" style="left:{x0}mm;top:{B + 6}mm">
  <div style="font-weight:600;font-size:10pt;letter-spacing:-.01em;color:{WHITE};line-height:1.1">Full Name</div>
  <div style="font-size:6.6pt;color:{C['Label']};margin-top:.9mm;line-height:1.1">Designation</div>
</div>
<div class="abs" style="left:{x0}mm;bottom:{B + 5.5}mm;width:{tw - 12}mm">
  {row('T', o['phone'])}{row('E', o['email'])}{row('W', o['web'])}{row('A', ', '.join(o['address']).replace(',,', ','))}
</div>"""
    return W, H, A.page(W, H, INK, svg, html)


if __name__ == '__main__':
    jobs = []
    for key, o in OFFICES.items():
        for part, fn, trim in (('letterhead', letterhead, (210, 297)), ('card-front', card_front, (90, 50)),
                               ('card-back', card_back, (90, 50))):
            name = f'st-{key}-{part}'
            W, H, doc = fn(o)
            p = os.path.join(HERE, 'html', name + '.html')
            open(p, 'w').write(doc)
            jobs.append(dict(name=name, html=p, w=W, h=H, trim=trim, cmyk=True))
    json.dump(jobs, open(os.path.join(HERE, 'jobs_stat.json'), 'w'), indent=1)
    print([j['name'] for j in jobs])
