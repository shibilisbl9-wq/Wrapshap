"""Polo shirt (Option A system): front = logo only on the left chest, back = Wrap Halo + tagline."""
import json, os
import design as A

HERE = A.HERE
GARMENT = '#111113'
HALO = dict(n=8, step=5.5, growth=0.06)


def polo_back():
    W, H = 282, 236
    cx, lw = W / 2, 150
    pad = lw / A.LOGO_RATIO * 0.32
    hw, hh = A.halo_extent(lw, pad=pad, **HALO)
    taper = (1.2, 0.6)
    cy = hh / 2 + taper[0]
    svg = A.halo(cx, cy, lw, stroke=1, pad=pad, taper=taper, a0=1.0, a1=0.3, blend_bg=GARMENT, **HALO)
    html = A.logo_slot(cx, cy, lw) + f"""
<div class="abs" style="left:0;width:{W}mm;top:{hh + 13:.1f}mm;text-align:center">
  <div style="font-weight:600;font-size:50pt;line-height:1.02;letter-spacing:-.03em;color:{A.WHITE}">Stay wrapped.</div>
  <div style="font-weight:600;font-size:50pt;line-height:1.02;letter-spacing:-.03em;color:{A.SIGNAL}">Stay protected.</div>
</div>"""
    return W, H, A.page(W, H, 'transparent', svg, html)


def polo_front():
    W = 85                                  # left-chest logo, mm
    H = W / A.LOGO_RATIO
    return W, H, A.page(W, H, 'transparent', '', A.logo_slot(W / 2, H / 2, W))


if __name__ == '__main__':
    jobs = []
    for name, spec in (('polo-back', polo_back()), ('polo-front', polo_front())):
        W, H, doc = spec
        p = os.path.join(HERE, 'html', name + '.html')
        open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=None, cmyk=False))
    json.dump(jobs, open(os.path.join(HERE, 'jobs_polo.json'), 'w'), indent=1)
    print([j['name'] for j in jobs])
