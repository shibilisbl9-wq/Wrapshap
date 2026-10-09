"""Retail (Pakistan, Yellow Edition): acrylic displays, tri-fold flyers, roll-up standee.

Yellow + black, matching the launch plan: Wrap Yellow #FFD60A on Wrap Black, Anton headlines,
Geist for prices and body, Permanent Marker for the hand-written accent. The yellow brush and
spray marks are 1-bit textures (spray.py), placed under the vector artwork by post.py.
Every price comes from data/pricing_pk.json, which was parsed from the supplied price review PDF.
"""
import json, os
import numpy as np
import design as A
import design_b as B
from spray import Paint

HERE = A.HERE
FONTS = A.FONTS
BL = A.BLEED

TOKENS_R = dict(B.TOKENS_B)
TOKENS_R.update({
    'Wrap Yellow': ('#FFD60A', (0, 15, 100, 0)),     # launch-plan yellow
    'Row':         ('#1A1A1D', (70, 60, 55, 82)),    # table row on black
    'Row Alt':     ('#232327', (65, 55, 50, 72)),
    'Rule Dark':   ('#3A3A3F', (0, 0, 0, 82)),
})
C = {k: v[0] for k, v in TOKENS_R.items()}
INK, YEL, WHITE, ROW, ROW2 = C['Wrap Black'], C['Wrap Yellow'], C['White'], C['Row'], C['Row Alt']
GREY, MUTED = C['Label'], C['Smoke']
LAYERS = [['yellow', 'Wrap Yellow']]
PRICES = json.load(open(os.path.join(HERE, 'data', 'pricing_pk.json')))
SEC = {s['name']: s['rows'] for s in PRICES['sections']}

OFFICE = dict(address='17-A Cooper Rd, Garhi Shahu, Lahore 54000', web='www.wrapshap.pk', email='info@wrapshap.pk')

CSS = (f"@font-face{{font-family:'Anton';src:url('file://{FONTS}/Anton-400.ttf')}}"
       f"@font-face{{font-family:'Marker';src:url('file://{FONTS}/PermanentMarker-400.ttf')}}"
       f"@font-face{{font-family:'Geist';font-weight:900;src:url('file://{FONTS}/Geist-900.ttf')}}" + """
.an{font-family:'Anton';font-weight:400;text-transform:uppercase;line-height:.95;letter-spacing:.005em}
.mk{font-family:'Marker';line-height:1}
.num{font-variant-numeric:tabular-nums;font-feature-settings:'tnum' 1}
table.t{border-collapse:separate;border-spacing:0;table-layout:fixed;width:100%}
table.t td,table.t th{padding:0;white-space:nowrap;overflow:hidden;vertical-align:middle}
.flex{display:flex}.col{display:flex;flex-direction:column}
""")

# ---- icons (24-unit line icons, drawn for this set) ------------------------------------------
ICON = {
    'phone': '<rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M11 18.6h2"/>',
    'tablet': '<rect x="4.5" y="2.5" width="15" height="19" rx="2"/><path d="M11 18.6h2"/>',
    'laptop': '<rect x="5" y="5" width="14" height="10" rx="1.2"/><path d="M2.5 18.5h19l-1.6-2.6H4.1z"/>',
    'watch': '<rect x="6.5" y="6.5" width="11" height="11" rx="2.8"/><path d="M9 6.5l.6-4h4.8l.6 4M9 17.5l.6 4h4.8l.6-4M12 9.6v2.6l1.6 1.1"/>',
    'camera': '<path d="M3 8.6A1.6 1.6 0 0 1 4.6 7h3l1.6-2.5h5.6L16.4 7h3A1.6 1.6 0 0 1 21 8.6v8.8a1.6 1.6 0 0 1-1.6 1.6H4.6A1.6 1.6 0 0 1 3 17.4z"/><circle cx="12" cy="12.8" r="3.4"/>',
    'earbuds': '<path d="M7.4 3.2a3.4 3.4 0 0 0-1.3 6.5l.6.3V19a1.4 1.4 0 0 0 2.8 0V6.6a3.4 3.4 0 0 0-2.1-3.4z"/><path d="M16.6 3.2a3.4 3.4 0 0 1 1.3 6.5l-.6.3V19a1.4 1.4 0 0 1-2.8 0V6.6a3.4 3.4 0 0 1 2.1-3.4z"/>',
    'ring': '<circle cx="12" cy="14" r="6.5"/><path d="M9.4 4.2h5.2l-1.3 3.4h-2.6z"/>',
    'screen': '<rect x="3" y="5" width="18" height="12" rx="1.6"/><path d="M9 21h6M12 17v4"/>',
    'diamond': '<path d="M6.5 4h11L21 9l-9 11L3 9z"/><path d="M3 9h18M9.6 4 8.2 9 12 20l3.8-11-1.4-5"/>',
    'shield': '<path d="M12 2.8l7.5 3v5.6c0 4.8-3.2 8.3-7.5 9.8-4.3-1.5-7.5-5-7.5-9.8V5.8z"/><path d="M8.6 12l2.4 2.4 4.4-4.6"/>',
    'layers': '<path d="M12 3l9 4.8-9 4.8-9-4.8z"/><path d="M3 12.2l9 4.8 9-4.8"/><path d="M3 16.4l9 4.8 9-4.8"/>',
    'sun': '<circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.2M12 19.3v2.2M2.5 12h2.2M19.3 12h2.2M5.3 5.3l1.6 1.6M17.1 17.1l1.6 1.6M5.3 18.7l1.6-1.6M17.1 6.9l1.6-1.6"/>',
    'finger': '<path d="M6.3 17.6A11.5 11.5 0 0 1 5 12a7 7 0 0 1 12.2-4.7"/><path d="M19 10.8c.1.7.1 1.4.1 2.2 0 1.6-.2 3.2-.6 4.6"/><path d="M8.7 19.8A15 15 0 0 1 7.3 13a4.7 4.7 0 0 1 9.4 0c0 2.4-.3 4.7-1 6.7"/><path d="M12 12.6c0 3.1.5 6 1.6 8.3"/>',
    'hammer': '<path d="M13.6 3.2l6.9 6.9-2.6 2.6-6.9-6.9z"/><path d="M13 9.3l-9 9 1.7 1.7 9-9"/>',
    'eyeoff': '<path d="M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12z"/><circle cx="12" cy="12" r="3"/><path d="M4 4l16 16"/>',
    'infinity': '<path d="M12 12c-2-2.7-3.6-4-5.4-4a4 4 0 0 0 0 8c1.8 0 3.4-1.3 5.4-4zm0 0c2 2.7 3.6 4 5.4 4a4 4 0 0 0 0-8c-1.8 0-3.4 1.3-5.4 4z"/>',
    'clock': '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.2 2"/>',
    'bubbles': '<circle cx="9" cy="14" r="5.2"/><circle cx="17.2" cy="6.8" r="3"/><circle cx="18.2" cy="15.8" r="1.7"/>',
    'refresh': '<path d="M20 11A8 8 0 0 0 5.8 6.4L4 8.5"/><path d="M4 3.5v5h5"/><path d="M4 13a8 8 0 0 0 14.2 4.6L20 15.5"/><path d="M20 20.5v-5h-5"/>',
    'check': '<path d="M5 12.5l4.5 4.5L19 7.5"/>',
    'cut': '<circle cx="6" cy="6.5" r="2.8"/><circle cx="6" cy="17.5" r="2.8"/><path d="M8.3 8.1 20 18M8.3 15.9 20 6"/>',
    'timer': '<circle cx="12" cy="13.5" r="7.5"/><path d="M12 9.5v4l2.5 1.5M9.5 2.5h5"/>',
    'receipt': '<path d="M6 2.5h12v19l-2-1.5-2 1.5-2-1.5-2 1.5-2-1.5-2 1.5z"/><path d="M9 7.5h6M9 11h6M9 14.5h4"/>',
    'pin': '<path d="M12 21.5s-7-6.2-7-11.5a7 7 0 0 1 14 0c0 5.3-7 11.5-7 11.5z"/><circle cx="12" cy="10" r="2.5"/>',
    'globe': '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c2.5 2.6 3.7 5.6 3.7 9s-1.2 6.4-3.7 9c-2.5-2.6-3.7-5.6-3.7-9S9.5 5.6 12 3z"/>',
    'mail': '<rect x="3" y="5.5" width="18" height="13" rx="1.6"/><path d="M3.6 6.6 12 13l8.4-6.4"/>',
    'info': '<circle cx="12" cy="12" r="9"/><path d="M12 11v5.6M12 7.7v.1"/>',
    'x': '<path d="M6.5 6.5l11 11M17.5 6.5l-11 11"/>',
    'swap': '<path d="M4 8h14l-3.5-3.5M20 16H6l3.5 3.5"/>',
    'device': '<rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M10 5.5h4"/>',
    'tag': '<path d="M3 12.2V4.5A1.5 1.5 0 0 1 4.5 3h7.7l8.8 8.8-9.2 9.2z"/><circle cx="8" cy="8" r="1.6"/>',
    'one': '<rect x="7" y="2.5" width="10" height="19" rx="2.2"/><path d="M7 12h10" stroke-dasharray="1.6 1.6"/><path d="M7.6 3.4 16.4 11.6" opacity=".0"/>',
}


def icon(name, size_mm, color=YEL, sw=1.8, extra=''):
    return (f'<svg style="width:{size_mm}mm;height:{size_mm}mm;flex:none;{extra}" viewBox="0 0 24 24" fill="none" stroke="{color}" '
            f'stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{ICON[name]}</svg>')


def fmt(v):
    return '—' if v is None else f'{v:,}'


# ---- page shell -------------------------------------------------------------------------
def page(W, H, svg, html):
    return A.page(W, H, 'transparent', svg, html, extra_css=B.STENCIL_CSS + CSS)


def save_tex(name, P):
    os.makedirs(os.path.join(HERE, 'tex'), exist_ok=True)
    m = P.finalize()
    np.savez_compressed(os.path.join(HERE, 'tex', name + '.npz'), yellow=m.get('yellow', np.zeros((P.ny, P.nx), bool)))
    return f'tex/{name}.npz'


def grunge_a4(P, W, H, seed, top=True, bottom=True, side=None):
    """Yellow brush + spray marks at the edges of an A4 panel, kept clear of the text areas."""
    r = np.random.default_rng(seed)
    if top:
        P.dry_brush('yellow', (W * 0.58, -3), (W + 6, 4.5), 9, bristles=100, dryness=0.5, solid=0.35, bend=0.8)
        P.spatter('yellow', W - 30, 3, 14, 30, 0.12, 0.6)
    if bottom:
        P.dry_brush('yellow', (-6, H - 4), (W * 0.45, H + 3), 13, bristles=110, dryness=0.55, solid=0.3, bend=-1)
        P.dry_brush('yellow', (W * 0.62, H + 4), (W + 6, H - 7), 12, bristles=100, dryness=0.55, solid=0.45, bend=1)
        P.spatter('yellow', W - 24, H - 1, 9, 26, 0.12, 0.6)
    if side == 'left':
        P.dry_brush('yellow', (-4, H * 0.2), (3, H * 0.62), 9, bristles=80, dryness=0.6, solid=0.2)


# ---- shared blocks ----------------------------------------------------------------------
def tab_title(label, ico, size_pt=17, sub=None, w='auto'):
    """Section title: yellow tab with black Anton type + icon (the 'tab' from the mockups)."""
    sub = f'<span style="font-family:Geist;font-weight:500;font-size:{size_pt * 0.42:.1f}pt;color:{GREY};text-transform:none;margin-left:3mm;letter-spacing:0">{sub}</span>' if sub else ''
    return f"""<div class="flex" style="align-items:center;gap:2.6mm">
  <div class="flex" style="align-items:center;gap:2mm;background:{YEL};padding:1.5mm 5mm 1.5mm 2.4mm;border-radius:1.4mm;
       clip-path:polygon(0 0,100% 0,calc(100% - 2.6mm) 100%,0 100%)">
    {icon(ico, size_pt * 0.36, INK, 2.2)}<div class="an" style="font-size:{size_pt}pt;color:{INK}">{label}</div></div>{sub}</div>"""


def legend(fs=7.6, compact=False):
    """Standard vs Lifetime Care, said once, in plain words."""
    item = lambda ico, head, body: f"""<div class="flex" style="align-items:center;gap:2.2mm;flex:1">
  {icon(ico, fs * 0.85, YEL, 2)}<div style="font-size:{fs}pt;line-height:1.25;color:{WHITE}"><b style="font-weight:700;color:{YEL}">{head}</b> {body}</div></div>"""
    return f"""<div class="flex" style="gap:5mm;border:.3mm solid {C['Rule Dark']};border-radius:2mm;padding:2.2mm 3.4mm">
  {item('tag', 'Standard', 'One-time protection. No replacement.')}
  {item('infinity', 'Lifetime Care', 'Replace whenever you need, for the fee shown, every time.')}</div>"""


def disclosure(fs=7.6):
    return f"""<div class="flex" style="align-items:center;gap:3mm;background:{YEL};border-radius:2mm;padding:2.4mm 4mm">
  {icon('info', fs * 0.95, INK, 2.2)}<div style="font-size:{fs}pt;line-height:1.3;color:{C['Ink Text']}">
  <b style="font-weight:800">Lifetime Care replacements are not free.</b> The replacement fee applies every time, including the first.
  The Full Body fee is for both sides replaced together.</div></div>"""


def split_name(n):
    """'Camera Tuff Matte - Full Body' -> ('Tuff Matte', 'Full Body')."""
    head, cov = n.split(' - ')
    for pre in ('Camera ',):
        if head.startswith(pre):
            head = head[len(pre):]
    return head, cov


MATS = ['Clear', 'Matte', 'Tuff', 'Tuff Matte', 'Privacy', 'Tuff Privacy']
MAT_ICON = {'Clear': 'diamond', 'Matte': 'layers', 'Tuff': 'shield', 'Tuff Matte': 'hammer', 'Privacy': 'eyeoff', 'Tuff Privacy': 'eyeoff'}


def pivot(rows, cov_a='1 Side', cov_b='Full Body'):
    """Price rows -> {material: {coverage: (std, lc, rep)}}, keeping the material order."""
    out = {}
    for n, s, l, r in rows:
        m, c = split_name(n)
        out.setdefault(m, {})[c] = (s, l, r)
    return [(m, out[m].get(cov_a), out[m].get(cov_b)) for m in MATS if m in out]


def pivot_table(rows, row_h, fs, label_a='1 Side', label_b='Full Body', name_w=34, head_fs=None, tab=None, head_h=None):
    """Material rows x (coverage A | coverage B) x (Standard, Lifetime Care, Replacement fee)."""
    head_fs = head_fs or fs * 0.62
    cell = f'text-align:center;font-size:{fs}pt;font-weight:600;color:{WHITE}'
    sub = (f'font-size:{head_fs:.2f}pt;font-weight:700;letter-spacing:.06em;text-transform:uppercase;text-align:center;'
           f'line-height:1.1;color:{GREY};padding-bottom:1.2mm')
    grp = f'background:{YEL};color:{INK};text-align:center;font-family:Anton;font-size:{fs * 1.08:.2f}pt;letter-spacing:.04em;text-transform:uppercase'
    gap = '<td style="width:2.2mm"></td>'
    th_sub = (f'<th style="{sub}">Standard</th><th style="{sub};color:{YEL}">Lifetime<br>Care</th>'
              f'<th style="{sub}">Replacement<br>fee</th>')
    gh, sh = head_h or (row_h * 0.72, row_h * 0.95)
    lead = (f'<td rowspan="2" style="vertical-align:bottom;padding-bottom:1.6mm">{tab}</td>' if tab else '<td></td>')
    h = [f'<tr style="height:{gh:.2f}mm">{lead}{gap}<td colspan="3" style="{grp};border-radius:1.4mm 1.4mm 0 0">{label_a}</td>{gap}'
         f'<td colspan="3" style="{grp};border-radius:1.4mm 1.4mm 0 0">{label_b}</td></tr>',
         f'<tr style="height:{sh:.2f}mm">{"" if tab else "<th></th>"}{gap}{th_sub}{gap}{th_sub}</tr>']
    body = []
    for i, (m, a, b) in enumerate(rows):
        bg = ROW if i % 2 == 0 else ROW2
        def three(v):
            if v is None:
                return ''.join(f'<td class="num" style="{cell};background:{bg};color:{MUTED}">—</td>' for _ in range(3))
            s, l, r = v
            return (f'<td class="num" style="{cell};background:{bg}">{fmt(s)}</td>'
                    f'<td class="num" style="{cell};background:{bg};color:{YEL};font-weight:700">{fmt(l)}</td>'
                    f'<td class="num" style="{cell};background:{bg}">{fmt(r)}</td>')
        last = i == len(rows) - 1
        rad = 'border-radius:0 0 0 1.4mm;' if last else ''
        body.append(f'<tr style="height:{row_h}mm"><td style="background:{bg};padding-left:2.4mm;{rad}border-radius:{"1.4mm 0 0 0" if i == 0 else ("0 0 0 1.4mm" if last else "0")}">'
                    f'<div class="flex" style="align-items:center;gap:2mm">{icon(MAT_ICON[m], fs * 0.62, YEL, 2)}'
                    f'<span style="font-size:{fs}pt;font-weight:700;color:{WHITE}">{m}</span></div></td>{gap}{three(a)}{gap}{three(b)}</tr>')
    cols = f'<col style="width:{name_w}mm"><col style="width:2.2mm"><col><col><col><col style="width:2.2mm"><col><col><col>'
    return f'<table class="t"><colgroup>{cols}</colgroup>{"".join(h)}{"".join(body)}</table>'


def list_table(rows, row_h, fs, name_w=None, head=True, label='Product', zebra=0):
    """Product | Standard | Lifetime Care | Replacement fee."""
    cell = f'text-align:right;font-size:{fs}pt;font-weight:600;color:{WHITE};padding-right:2.2mm'
    sub = (f'font-size:{fs * 0.62:.2f}pt;font-weight:700;letter-spacing:.06em;text-transform:uppercase;line-height:1.1;'
           f'color:{INK};background:{YEL};text-align:right;padding-right:2.2mm')
    cols = f'<col style="width:{name_w}mm"><col><col><col>' if name_w else '<col style="width:43%"><col><col><col>'
    out = [f'<table class="t"><colgroup>{cols}</colgroup>']
    if head:
        out.append(f'<tr style="height:{row_h * 1.05:.2f}mm"><th style="{sub};text-align:left;padding-left:2.4mm;border-radius:1.4mm 0 0 1.4mm">{label}</th>'
                   f'<th style="{sub}">Standard</th><th style="{sub};white-space:normal">Lifetime<br>Care</th>'
                   f'<th style="{sub};border-radius:0 1.4mm 1.4mm 0;white-space:normal">Replacement<br>fee</th></tr>')
    for i, (n, s, l, r) in enumerate(rows):
        bg = ROW if (i + zebra) % 2 == 0 else ROW2
        out.append(f'<tr style="height:{row_h}mm"><td style="background:{bg};padding-left:2.4mm;font-size:{fs}pt;font-weight:500;color:{WHITE}">{n}</td>'
                   f'<td class="num" style="{cell};background:{bg}">{fmt(s)}</td>'
                   f'<td class="num" style="{cell};background:{bg};color:{YEL};font-weight:700">{fmt(l)}</td>'
                   f'<td class="num" style="{cell};background:{bg}">{fmt(r)}</td></tr>')
    out.append('</table>')
    return ''.join(out)


def header_a4(W, title_html, kicker, logo_w=56, note='Premium device protection<br>All prices in Pakistani Rupees (Rs.)'):
    """Logo top-left, kicker top-right, big headline below."""
    x0, y0 = BL + 10, BL + 10
    lh = logo_w / A.LOGO_RATIO
    return A.logo_slot(x0 + logo_w / 2, y0 + lh / 2, logo_w) + f"""
<div class="abs" style="right:{BL + 10}mm;top:{y0 + 1}mm;text-align:right">
  <div class="mono" style="font-size:6.6pt;color:{YEL};line-height:1">{kicker}</div>
  <div style="font-size:7pt;color:{GREY};margin-top:1.8mm;line-height:1.3">{note}</div>
</div>
<div class="abs" style="left:{x0}mm;top:{y0 + lh + 5}mm">{title_html}</div>"""


def header_compact(title_html, kicker, logo_w=48):
    x0, y0 = BL + 10, BL + 9
    lh = logo_w / A.LOGO_RATIO
    return A.logo_slot(x0 + logo_w / 2, y0 + lh / 2, logo_w) + f"""
<div class="abs" style="right:{BL + 10}mm;top:{y0}mm;text-align:right">
  <div class="mono" style="font-size:6.2pt;color:{YEL};line-height:1">{kicker}&nbsp;&nbsp;·&nbsp;&nbsp;<span style="color:{GREY}">Prices in Rs.</span></div>
  <div style="margin-top:2.6mm">{title_html}</div>
</div>"""


# ---- ACRYLIC 1: pricing -----------------------------------------------------------------
def acrylic1_front():
    W, H = 210 + 2 * BL, 297 + 2 * BL
    P = Paint(W, H, 0.14, 701)
    grunge_a4(P, W, H, 701)
    x0, w = BL + 10, 190
    title = f'<div class="an" style="font-size:40pt;color:{WHITE}">Smartphone <span style="color:{YEL}">price list</span></div>'
    combos = SEC['Mobile Full Body Combos']
    half = (len(combos) + 1) // 2
    html = header_a4(W, title, 'Official price list&nbsp;&nbsp;·&nbsp;&nbsp;Pakistan') + f"""
<div class="abs col" style="left:{x0}mm;width:{w}mm;top:{BL + 58}mm;height:{297 - 58 - 10}mm;justify-content:space-between">
  {legend(7.8)}
  <div>{tab_title('Smartphone', 'phone', 15, 'Pick a protection, then 1 side or full body')}<div style="height:3mm"></div>
    {pivot_table(pivot(SEC['Smartphone']), 11.2, 11, name_w=40)}</div>
  <div>{tab_title('Full body combos', 'swap', 15, 'A different film on the front and the back')}<div style="height:3mm"></div>
    <div class="flex" style="gap:4mm"><div style="flex:1">{list_table(combos[:half], 7.6, 8.6, label='Front + back')}</div>
    <div style="flex:1">{list_table(combos[half:], 7.6, 8.6, label='Front + back')}</div></div></div>
  {disclosure(7.6)}
</div>"""
    return W, H, page(W, H, '', html), save_tex('r-acrylic1-front', P), 0.14


def acrylic1_back():
    W, H = 210 + 2 * BL, 297 + 2 * BL
    P = Paint(W, H, 0.14, 711)
    grunge_a4(P, W, H, 711)
    x0, w = BL + 10, 190
    title = f'<div class="an" style="font-size:27pt;color:{WHITE}">Tablets, laptops <span style="color:{YEL}">&amp; more</span></div>'
    cam = [r for r in SEC['Camera and Other Devices'] if r[0].startswith('Camera')]
    other = SEC['Camera and Other Devices'][len(cam):]
    ear = [[n.replace('Earbuds Clear - Full Body', 'Earbuds · Clear, full body').replace('Smart Ring - ', 'Smart ring · '), s_, l, r]
           for n, s_, l, r in other if not n.startswith('Infotainment')]
    car = [[n.replace('Infotainment - ', 'Car screen · '), s_, l, r] for n, s_, l, r in other if n.startswith('Infotainment')]
    rh, fs, hh = 5.95, 9.0, (5.4, 4.9)
    T = lambda t, ico: tab_title(t, ico, 11.5)
    pt = lambda rows, t, ico, a='1 Side': pivot_table(rows, rh, fs, a, name_w=40, tab=T(t, ico), head_h=hh)
    html = header_compact(title, 'Official price list&nbsp;&nbsp;·&nbsp;&nbsp;Pakistan') + f"""
<div class="abs col" style="left:{x0}mm;width:{w}mm;top:{BL + 33}mm;height:{297 - 33 - 10}mm;justify-content:space-between">
  {legend(7.4)}
  {pt(pivot(SEC['Tablet / iPad']), 'Tablet / iPad', 'tablet')}
  {pt(pivot(SEC['Laptop']), 'Laptop', 'laptop')}
  {pt(pivot(SEC['Smart Watch'], 'Screen'), 'Smart watch', 'watch', 'Screen')}
  {pt(pivot(cam, 'Screen'), 'Camera', 'camera', 'Screen')}
  <div>{T('More devices', 'earbuds')}<div style="height:2mm"></div><div class="flex" style="gap:4mm">
     <div style="flex:1.2">{list_table(ear, rh, fs * 0.9, label='Earbuds &amp; smart ring')}</div>
     <div style="flex:1">{list_table(car, rh, fs * 0.9, label='Car infotainment')}</div></div></div>
  {disclosure(7.2)}
</div>"""
    return W, H, page(W, H, '', html), save_tex('r-acrylic1-back', P), 0.14


# ---- protection types ------------------------------------------------------------------
TYPES = [
    # name, short description, features (clear look, anti-glare, impact, privacy)
    ('Clear', 'Crystal-clear film that keeps your device looking brand new.', (1, 0, 0, 0)),
    ('Matte', 'Smooth matte finish that cuts glare and hides fingerprints.', (0, 1, 0, 0)),
    ('Tuff', 'Thicker, impact-resistant clear film for scratches, scuffs and rough daily use.', (1, 0, 1, 0)),
    ('Tuff Matte', 'All the strength of Tuff with a smooth, no-glare matte finish.', (0, 1, 1, 0)),
    ('Privacy', 'Your screen looks dark from the side, so only you can see it.', (0, 0, 0, 1)),
    ('Tuff Privacy', 'Privacy plus the strength of Tuff. Our most protective film.', (0, 0, 1, 1)),
]
FEATURES = [('diamond', 'Crystal-clear<br>look'), ('sun', 'Anti-glare &amp;<br>anti-fingerprint'),
            ('shield', 'Extra impact<br>strength'), ('eyeoff', 'Privacy from<br>the side')]


def swatch(kind, size_mm, uid):
    """A phone corner under the film, with the film peeling back. The film shows the finish:
    gloss streak (clear), frosted (matte), thick edge (tuff), louvres (privacy)."""
    matte = 'Matte' in kind
    tuff = kind.startswith('Tuff')
    priv = 'Privacy' in kind
    d = [f'<clipPath id="c{uid}"><rect width="100" height="100" rx="14"/></clipPath>',
         f'<linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/>'
         f'<stop offset=".42" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".55"/>'
         f'<stop offset=".6" stop-color="#fff" stop-opacity="0"/></linearGradient>',
         f'<linearGradient id="k{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#ffffff"/>'
         f'<stop offset="1" stop-color="#9a9aa2"/></linearGradient>',
         f'<linearGradient id="p{uid}" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#000" stop-opacity=".85"/>'
         f'<stop offset=".55" stop-color="#000" stop-opacity=".35"/><stop offset="1" stop-color="#000" stop-opacity=".8"/></linearGradient>',
         f'<clipPath id="f{uid}"><path d="M44 12H86a12 12 0 0 1 12 12V130H20V36z"/></clipPath>']
    g = [f'<rect width="100" height="100" rx="14" fill="{ROW2}"/>',
         f'<g clip-path="url(#c{uid})">',
         # phone body + screen
         f'<rect x="18" y="10" width="92" height="120" rx="14" fill="#2C2C31"/>',
         f'<rect x="24" y="16" width="80" height="110" rx="9" fill="#0E0E11"/>',
         f'<circle cx="64" cy="24" r="2.2" fill="#2C2C31"/>',
         # film (minus the peeled corner)
         f'<g clip-path="url(#f{uid})">',
         f'<rect x="20" y="12" width="88" height="118" rx="12" fill="#fff" opacity="{0.34 if matte else 0.05}"/>']
    if priv:
        g.append(f'<rect x="20" y="12" width="88" height="118" fill="url(#p{uid})"/>')
        g += [f'<line x1="{x}" y1="12" x2="{x}" y2="130" stroke="#000" stroke-width="1.1" opacity=".35"/>' for x in range(26, 108, 4)]
    if not matte:
        g.append(f'<rect x="20" y="12" width="88" height="118" fill="url(#g{uid})"/>')
    g.append(f'<rect x="20.8" y="12.8" width="86.4" height="116.4" rx="11.2" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="{2.6 if tuff else 0.9}"/>')
    if tuff:
        g.append('<rect x="24.2" y="16.2" width="79.6" height="109.6" rx="8.2" fill="none" stroke="#fff" stroke-opacity=".28" stroke-width=".8"/>')
    g.append('</g>')
    # the peeled corner, curling back
    g.append(f'<path d="M20 38 C27 30 36 20 44 12 C40 26 34 34 20 38z" fill="url(#k{uid})" stroke="#fff" stroke-width="{1.6 if tuff else 0.6}" stroke-linejoin="round"/>')
    g.append('</g>')
    return (f'<svg style="width:{size_mm}mm;height:{size_mm}mm;flex:none" viewBox="0 0 100 100">'
            f'<defs>{"".join(d)}</defs>{"".join(g)}</svg>')


def check_cell(on, size):
    if on:
        return (f'<div class="flex" style="width:{size}mm;height:{size}mm;border-radius:50%;background:{YEL};align-items:center;justify-content:center">'
                f'{icon("check", size * 0.62, INK, 3)}</div>')
    return f'<div style="width:{size * 0.42}mm;height:.5mm;background:{C["Rule Dark"]}"></div>'


DEVICES = [('phone', 'Smartphones'), ('tablet', 'Tablets / iPads'), ('laptop', 'Laptops'), ('watch', 'Smart watches'),
           ('camera', 'Cameras'), ('earbuds', 'Earbuds &amp; more')]


def device_row(size, fs, color=WHITE, ic=YEL):
    return '<div class="flex" style="justify-content:space-between">' + ''.join(
        f'<div class="col" style="align-items:center;gap:1.6mm;flex:1">{icon(i, size, ic, 1.7)}'
        f'<div style="font-size:{fs}pt;font-weight:600;color:{color};text-align:center;line-height:1.15">{t}</div></div>' for i, t in DEVICES) + '</div>'


TERMS = [
    ('Original device only', 'Replacement is valid only for the device the WrapShap protection was installed on.'),
    ('A fee on every replacement', 'The replacement fee shown on the price list is charged every time, including the first replacement.'),
    ('Full Body = both sides', 'The Full Body replacement fee is the normal charge when both sides are replaced together.'),
    ('Not a free replacement plan', 'Lifetime Care does not mean free replacements. A replacement charge applies every time.'),
    ('What is covered', 'Normal wear and tear, scratches and everyday use. Not covered: lost, stolen or physically damaged devices.'),
    ('WrapShap-installed only', 'Replacement is provided only for WrapShap-installed products. Third-party film or modification may void eligibility.'),
    ('Right to modify', 'WrapShap may update pricing, terms and conditions at any time without prior notice.'),
]


def terms_list(fs, gap, num=6.2, items=TERMS):
    return '<div class="col" style="gap:%smm">' % gap + ''.join(f"""<div class="flex" style="gap:3mm;align-items:flex-start">
  <div class="flex an" style="flex:none;width:{num}mm;height:{num}mm;border-radius:50%;background:{YEL};color:{INK};align-items:center;justify-content:center;font-size:{num * 1.75:.1f}pt;line-height:1">{i + 1}</div>
  <div style="font-size:{fs}pt;line-height:1.32;color:{WHITE}"><b style="font-weight:700;color:{YEL}">{t}.</b> {b}</div></div>""" for i, (t, b) in enumerate(items)) + '</div>'


def lifetime_steps(fs, ic=9):
    steps = [('infinity', 'Choose Lifetime Care', 'when your protection is installed.'),
             ('refresh', 'Come back any time', 'with the same device, as often as you need.'),
             ('receipt', 'Pay the replacement fee', 'shown on the price list. New film, fitted.')]
    return '<div class="flex" style="gap:3mm">' + ''.join(f"""<div class="col" style="flex:1;gap:2mm;background:{ROW};border-radius:2mm;padding:3mm">
  <div class="flex" style="align-items:center;gap:2mm">{icon(i, ic, YEL, 1.8)}<div class="an" style="font-size:{fs * 1.9:.1f}pt;color:{C['Rule Dark']}">0{n + 1}</div></div>
  <div style="font-size:{fs}pt;line-height:1.3;color:{WHITE}"><b style="font-weight:700">{t}</b> {b}</div></div>""" for n, (i, t, b) in enumerate(steps)) + '</div>'


# ---- ACRYLIC 2: product education ---------------------------------------------------------
def acrylic2_front():
    W, H = 210 + 2 * BL, 297 + 2 * BL
    P = Paint(W, H, 0.14, 721)
    grunge_a4(P, W, H, 721)
    x0, w = BL + 10, 190
    title = f'<div class="an" style="font-size:42pt;color:{WHITE}">Choose your <span style="color:{YEL}">protection</span></div>'
    head = (f'<div class="flex" style="align-items:flex-end;gap:0;padding-left:{30 + 62}mm">' + ''.join(
        f'<div class="col" style="flex:1;align-items:center;gap:1.4mm">{icon(i, 6.4, YEL, 1.7)}'
        f'<div style="font-size:6.6pt;font-weight:700;letter-spacing:.04em;text-transform:uppercase;color:{GREY};text-align:center;line-height:1.2">{t}</div></div>'
        for i, t in FEATURES) + '</div>')
    rows = ''.join(f"""<div class="flex" style="align-items:center;background:{ROW if k % 2 == 0 else ROW2};border-radius:2.4mm;padding:2.6mm;gap:4mm">
  {swatch(n, 24, k)}
  <div style="width:58mm"><div class="an" style="font-size:20pt;color:{YEL}">{n}</div>
    <div style="font-size:8.6pt;line-height:1.3;color:{WHITE};margin-top:1.6mm">{d}</div></div>
  <div class="flex" style="flex:1">{''.join(f'<div class="flex" style="flex:1;justify-content:center;align-items:center">{check_cell(f, 7)}</div>' for f in feats)}</div>
</div>""" for k, (n, d, feats) in enumerate(TYPES))
    html = header_a4(W, title, 'How to choose&nbsp;&nbsp;·&nbsp;&nbsp;Pakistan', note='Premium device protection<br>Ask us for a sample of any film') + f"""
<div class="abs mk" style="right:{BL + 12}mm;top:{BL + 40}mm;font-size:13pt;color:{YEL};transform:rotate(-6deg);text-align:right;line-height:1.05">Stay wrapped.<br>Stay protected.</div>
<div class="abs col" style="left:{x0}mm;width:{w}mm;top:{BL + 60}mm;height:{297 - 60 - 10}mm;justify-content:space-between">
  {head}
  <div class="col" style="gap:2.2mm">{rows}</div>
  <div class="flex" style="align-items:center;gap:4mm;border-top:.3mm solid {C['Rule Dark']};padding-top:3.4mm">
    <div style="font-size:7.6pt;color:{GREY};width:30mm;line-height:1.3">Available for</div>
    <div style="flex:1">{device_row(6.2, 6.4)}</div></div>
</div>"""
    return W, H, page(W, H, '', html), save_tex('r-acrylic2-front', P), 0.14


def acrylic2_back():
    W, H = 210 + 2 * BL, 297 + 2 * BL
    P = Paint(W, H, 0.14, 731)
    grunge_a4(P, W, H, 731)
    x0, w = BL + 10, 190
    title = f'<div class="an" style="font-size:36pt;color:{WHITE}"><span style="color:{YEL}">Lifetime Care</span> &amp; terms</div>'
    cmp = lambda ico, t, lines, hl: f"""<div class="col" style="flex:1;gap:2mm;border:{'.5mm solid ' + YEL if hl else '.3mm solid ' + C['Rule Dark']};border-radius:2.4mm;padding:3.4mm">
  <div class="flex" style="align-items:center;gap:2.4mm">{icon(ico, 7, YEL, 1.8)}<div class="an" style="font-size:18pt;color:{YEL if hl else WHITE}">{t}</div></div>
  {''.join(f'<div class="flex" style="gap:2mm;font-size:9.6pt;line-height:1.3;color:{WHITE}">{icon(i, 4, YEL if i == "check" else MUTED, 2.6, "margin-top:.4mm")}<span>{x}</span></div>' for i, x in lines)}</div>"""
    html = header_a4(W, title, 'Replacement policy&nbsp;&nbsp;·&nbsp;&nbsp;Pakistan', note='Premium device protection<br>Please read before you buy') + f"""
<div class="abs col" style="left:{x0}mm;width:{w}mm;top:{BL + 56}mm;height:{297 - 56 - 10}mm;justify-content:space-between">
  <div class="flex" style="gap:4mm">
    {cmp('tag', 'Standard', [('check', 'One-time protection, installed by WrapShap.'), ('x', 'No replacement included.')], False)}
    {cmp('infinity', 'Lifetime Care', [('check', 'Replacement for as long as you use the device.'), ('check', 'A clearly stated fee on every replacement, including the first.')], True)}
  </div>
  <div>{tab_title('How Lifetime Care works', 'refresh', 14)}<div style="height:3.4mm"></div>{lifetime_steps(9.4, 10)}</div>
  <div>{tab_title('Key terms &amp; conditions', 'receipt', 14)}<div style="height:4mm"></div>{terms_list(9.6, 3.6, 7)}</div>
  {disclosure(8.4)}
</div>"""
    return W, H, page(W, H, '', html), save_tex('r-acrylic2-back', P), 0.14


# ---- hero visual: a phone (back) wrapped in film, one corner peeling ----------------------
def hero_phone(cx, cy, w, rot, uid):
    """Vector phone, back side, 3-lens camera, glossy film with the bottom-right corner lifting.
    Drawn in a 100 x 210 box, scaled to width w (mm) and centred on (cx, cy)."""
    k = w / 100
    d = f"""<defs>
<linearGradient id="hb{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#3B3B42"/><stop offset=".45" stop-color="#141417"/><stop offset="1" stop-color="#232328"/></linearGradient>
<linearGradient id="hr{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#9C9CA6"/><stop offset=".5" stop-color="#2A2A30"/><stop offset="1" stop-color="#6E6E78"/></linearGradient>
<radialGradient id="hl{uid}" cx=".38" cy=".36" r=".7"><stop offset="0" stop-color="#2D4C8C"/><stop offset=".45" stop-color="#101A33"/><stop offset="1" stop-color="#030305"/></radialGradient>
<linearGradient id="hs{uid}" x1="0" y1="0" x2="1" y2=".55"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".3" stop-color="#fff" stop-opacity="0"/>
 <stop offset=".37" stop-color="#fff" stop-opacity=".28"/><stop offset=".43" stop-color="#fff" stop-opacity="0"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/>
 <stop offset=".6" stop-color="#fff" stop-opacity=".12"/><stop offset=".66" stop-color="#fff" stop-opacity="0"/></linearGradient>
<linearGradient id="hc{uid}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#FFFFFF" stop-opacity=".95"/><stop offset=".6" stop-color="#C9C9D0" stop-opacity=".9"/><stop offset="1" stop-color="#7C7C86" stop-opacity=".9"/></linearGradient>
<radialGradient id="hg{uid}" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="{YEL}" stop-opacity=".55"/><stop offset=".6" stop-color="{YEL}" stop-opacity=".14"/><stop offset="1" stop-color="{YEL}" stop-opacity="0"/></radialGradient>
<clipPath id="hf{uid}"><path d="M0 0H100V160L58 210H0z"/></clipPath>
</defs>"""

    def lens(x, y):
        return (f'<circle cx="{x}" cy="{y}" r="9.6" fill="#0A0A0C" stroke="#4A4A54" stroke-width="1.6"/>'
                f'<circle cx="{x}" cy="{y}" r="6.4" fill="url(#hl{uid})"/>'
                f'<circle cx="{x}" cy="{y}" r="2.4" fill="#06060A"/>'
                f'<circle cx="{x - 2.4}" cy="{y - 2.6}" r="1.3" fill="#fff" opacity=".7"/>')
    g = [f'<ellipse cx="50" cy="105" rx="95" ry="140" fill="url(#hg{uid})"/>',
         f'<rect x="0" y="0" width="100" height="210" rx="17" fill="url(#hb{uid})" stroke="url(#hr{uid})" stroke-width="1.8"/>',
         '<rect x="7" y="7" width="48" height="48" rx="12" fill="#1C1C21" stroke="#45454E" stroke-width=".9"/>',
         lens(20, 20), lens(20, 43), lens(42, 31.5),
         '<circle cx="42" cy="15.5" r="3.1" fill="#F4EBCF"/><circle cx="42" cy="47" r="1.4" fill="#0A0A0C"/>',
         # film over the whole back, except the lifted corner
         f'<g clip-path="url(#hf{uid})"><rect x="1.4" y="1.4" width="97.2" height="207.2" rx="15.8" fill="#fff" opacity=".05"/>'
         f'<rect x="1.4" y="1.4" width="97.2" height="207.2" rx="15.8" fill="url(#hs{uid})"/>'
         '<rect x="1.9" y="1.9" width="96.2" height="206.2" rx="15.3" fill="none" stroke="#fff" stroke-opacity=".55" stroke-width=".7"/></g>',
         # the lifted corner (with its shadow on the phone)
         '<path d="M100 160 L58 210 C70 196 86 184 100 160z" fill="#000" opacity=".35" transform="translate(-3 -2)"/>',
         f'<path d="M100 160 C92 182 80 196 58 210 C66 186 70 172 100 160z" fill="url(#hc{uid})" stroke="#fff" stroke-width=".6"/>']
    return f'<g transform="translate({cx} {cy}) rotate({rot}) scale({k}) translate(-50 -105)">{d}{"".join(g)}</g>'


def type_chip(ico, label, fs):
    return (f'<div class="flex" style="align-items:center;gap:1.4mm;border:.3mm solid {C["Rule Dark"]};border-radius:5mm;padding:.9mm 2.4mm .9mm 1.6mm">'
            f'{icon(ico, fs * 0.5, YEL, 2)}<span style="font-size:{fs * 0.82:.1f}pt;font-weight:600;color:{WHITE}">{label}</span></div>')


# ---- TRI-FOLD FLYERS (A4 landscape, roll fold) --------------------------------------------
FW, FH = 297 + 2 * BL, 210 + 2 * BL
OUT_PANELS = [(BL, 97), (BL + 97, 100), (BL + 197, 100)]           # flap (folds in) | back | cover
IN_PANELS = [(BL, 100), (BL + 100, 100), (BL + 200, 97)]
PAD = 7


def panel(x, w, inner, top=BL + 8, bottom=BL + 202, justify='space-between'):
    return (f'<div class="abs col" style="left:{x + PAD}mm;width:{w - 2 * PAD}mm;top:{top}mm;height:{bottom - top}mm;'
            f'justify-content:{justify}">{inner}</div>')


def flyer_grunge(P, seed, cover=None):
    P.dry_brush('yellow', (-6, FH - 3), (FW * 0.3, FH + 3), 10, bristles=90, dryness=0.55, solid=0.3, bend=-0.6)
    P.dry_brush('yellow', (FW * 0.72, FH + 3), (FW + 6, FH - 5), 10, bristles=90, dryness=0.55, solid=0.4, bend=0.6)
    P.dry_brush('yellow', (FW * 0.62, -3), (FW + 6, 3.5), 8, bristles=90, dryness=0.5, solid=0.35, bend=0.6)
    if cover:
        cx, cy, rad = cover
        P.dry_brush('yellow', (cx - rad, cy + rad * 0.5), (cx + rad, cy - rad * 0.7), rad * 0.9, bristles=150, dryness=0.5,
                    solid=0.5, bend=rad * 0.1)
        P.spatter('yellow', cx + rad * 0.4, cy - rad * 0.4, rad * 0.9, 70, 0.12, 0.9)


def fl_rows(name):
    return [[n.replace(' - ', ' · '), a, b, c] for n, a, b, c in SEC[name]]


def fl_block(title, ico, rows, rh=6.15, fs=8, label='Protection'):
    return f'<div>{tab_title(title, ico, 11)}<div style="height:2.2mm"></div>{list_table(rows, rh, fs, label=label)}</div>'


def contact(fs=7.4):
    def line(i, t):
        return (f'<div class="flex" style="align-items:center;gap:2.2mm;font-size:{fs}pt;color:{WHITE};line-height:1.25">'
                f'{icon(i, fs * 0.62, YEL, 2)}<span>{t}</span></div>')
    return f'<div class="col" style="gap:1.8mm">{line("pin", OFFICE["address"])}{line("globe", OFFICE["web"])}{line("mail", OFFICE["email"])}</div>'


def sub_label(i, t, fs=10):
    return (f'<div class="flex" style="align-items:center;gap:1.8mm;margin-bottom:1.6mm">{icon(i, fs * 0.36, YEL, 2)}'
            f'<span class="an" style="font-size:{fs}pt;color:{WHITE}">{t}</span></div>')


def flyer_cover(x, w, kicker, title_html, sub):
    cx = x + w / 2
    return A.logo_slot(cx, BL + 24, 62) + f"""
<div class="abs" style="left:{x + PAD}mm;width:{w - 2 * PAD}mm;top:{BL + 40}mm;text-align:center">
  <div class="mono" style="font-size:6pt;color:{YEL};line-height:1">{kicker}</div>
  <div style="margin-top:3.4mm">{title_html}</div></div>
<div class="abs" style="left:{x + PAD}mm;width:{w - 2 * PAD}mm;top:{BL + 180}mm">{sub}</div>"""


def legend_stack(fs):
    return ''.join(
        f'<div class="flex" style="gap:2mm;align-items:flex-start">{icon(i, fs * 0.6, YEL, 2)}'
        f'<div style="font-size:{fs}pt;line-height:1.3;color:{WHITE}"><b style="color:{YEL}">{t}</b> {b}</div></div>'
        for i, t, b in (('tag', 'Standard:', 'one-time protection, no replacement.'),
                        ('infinity', 'Lifetime Care:', 'replace whenever you need, for the replacement fee shown, every time, including the first.')))


def flyer1_outside():
    P = Paint(FW, FH, 0.14, 801)
    (fx, fw), (bx, bw), (cx_, cw) = OUT_PANELS
    flyer_grunge(P, 801, cover=(cx_ + cw / 2, BL + 128, 40))
    flap = panel(fx, fw, f"""
  <div class="col" style="gap:2mm;margin-bottom:-6mm">{tab_title('Full body combos', 'swap', 11)}
    <div style="font-size:7.2pt;line-height:1.3;color:{GREY}">A different film on the front and the back. Prices are for both sides.</div></div>
  <div>{sub_label('phone', 'Mobile')}{list_table(SEC['Mobile Full Body Combos'], 5.85, 7.6, label='Front + back')}</div>
  <div>{sub_label('laptop', 'Laptop')}{list_table(SEC['Laptop Full Body Combos'], 5.85, 7.6, label='Front + back')}</div>""")
    back = panel(bx, bw, f"""
  <div>{sub_label('tablet', 'Tablet combos')}{list_table(SEC['Tablet Full Body Combos'], 5.85, 7.6, label='Front + back')}</div>
  <div class="col" style="gap:2.2mm">{tab_title('How pricing works', 'tag', 11)}{legend_stack(7.4)}</div>
  <div style="border-top:.3mm solid {C['Rule Dark']};padding-top:3mm">{contact()}</div>""")
    title = f'<div class="an" style="font-size:30pt;color:{WHITE}">Official<br><span style="color:{YEL}">price list</span></div>'
    sub = (f'<div class="col" style="gap:3mm;align-items:center"><div class="mk" style="font-size:11pt;color:{WHITE};transform:rotate(-3deg)">'
           f'Stay wrapped. Stay protected.</div>{device_row(4.6, 5)}</div>')
    svg = hero_phone(cx_ + cw / 2, BL + 128, 34, -12, 'f1')
    html = flap + back + flyer_cover(cx_, cw, 'Premium device protection&nbsp;&nbsp;·&nbsp;&nbsp;Pakistan', title, sub)
    return FW, FH, page(FW, FH, svg, html), save_tex('r-flyer1-outside', P), 0.14


def flyer1_inside():
    P = Paint(FW, FH, 0.14, 811)
    flyer_grunge(P, 811)
    (x1, w1), (x2, w2), (x3, w3) = IN_PANELS
    allc = SEC['Camera and Other Devices']
    cam = [[n.replace('Camera ', '').replace(' - ', ' · '), a, b, c] for n, a, b, c in allc if n.startswith('Camera')]
    oth = [[n.replace('Earbuds Clear - Full Body', 'Earbuds · Clear, full body').replace('Infotainment - ', 'Car screen · ').replace('Smart Ring - ', 'Smart ring · '), a, b, c]
           for n, a, b, c in allc if not n.startswith('Camera')]
    p1 = panel(x1, w1, fl_block('Smartphone', 'phone', fl_rows('Smartphone')) + fl_block('Tablet / iPad', 'tablet', fl_rows('Tablet / iPad')))
    p2 = panel(x2, w2, fl_block('Laptop', 'laptop', fl_rows('Laptop')) + fl_block('Smart watch', 'watch', fl_rows('Smart Watch')))
    p3 = panel(x3, w3, fl_block('Camera', 'camera', cam, rh=5.7, fs=7.6)
               + fl_block('More devices', 'earbuds', oth, rh=5.7, fs=7.6, label='Device · protection') + disclosure(6.6))
    return FW, FH, page(FW, FH, '', p1 + p2 + p3), save_tex('r-flyer1-inside', P), 0.14


def type_card(k, n, d, feats, sw=21, fs=8.2):
    chips = ''.join(type_chip(FEATURES[i][0], FEATURES[i][1].replace('<br>', ' '), fs) for i, f in enumerate(feats) if f)
    return f"""<div class="flex" style="gap:3mm;background:{ROW if k % 2 == 0 else ROW2};border-radius:2.4mm;padding:2.6mm;align-items:center">
  {swatch(n, sw, 'c%d' % k)}
  <div class="col" style="gap:1.4mm;flex:1"><div class="an" style="font-size:17pt;color:{YEL}">{n}</div>
    <div style="font-size:{fs}pt;line-height:1.3;color:{WHITE}">{d}</div>
    <div class="flex" style="gap:1.4mm;flex-wrap:wrap">{chips}</div></div></div>"""


WHY = [('diamond', 'Premium film', 'High-clarity film made for everyday wear.'),
       ('cut', 'Cut for your exact model', 'Precision-cut on our machine in under 60 seconds.'),
       ('bubbles', 'Bubble-free finish', 'Fitted by our team, edge to edge.'),
       ('infinity', 'Lifetime Care option', 'Replace whenever you need, for a fixed fee.')]


def why_item(i, t, b):
    return f"""<div class="flex" style="gap:3mm;align-items:flex-start">
  <div class="flex" style="flex:none;width:16mm;height:16mm;border-radius:3mm;background:{ROW2};align-items:center;justify-content:center">{icon(i, 9, YEL, 1.6)}</div>
  <div><div class="an" style="font-size:15pt;color:{WHITE}">{t}</div><div style="font-size:8.6pt;line-height:1.3;color:{GREY};margin-top:1.4mm">{b}</div></div></div>"""


def device_grid(size, fs):
    cells = ''.join(f'<div class="col" style="align-items:center;gap:2mm">{icon(i, size, YEL, 1.6)}'
                    f'<div style="font-size:{fs}pt;font-weight:600;color:{WHITE};text-align:center">{t}</div></div>' for i, t in DEVICES)
    return f'<div style="display:grid;grid-template-columns:1fr 1fr 1fr;row-gap:6mm">{cells}</div>'


def flyer2_outside():
    P = Paint(FW, FH, 0.14, 821)
    (fx, fw), (bx, bw), (cx_, cw) = OUT_PANELS
    flyer_grunge(P, 821, cover=(cx_ + cw / 2, BL + 128, 40))
    flap = panel(fx, fw, f"""
  <div>{tab_title('Why WrapShap', 'shield', 12)}</div>
  {''.join(why_item(*x) for x in WHY)}
  <div class="mk" style="font-size:12pt;color:{YEL};transform:rotate(-3deg);text-align:center">Stay wrapped. Stay protected.</div>""")
    back = panel(bx, bw, f"""
  <div>{tab_title('We protect', 'device', 12)}<div style="height:8mm"></div>{device_grid(12, 8.2)}</div>
  <div class="col" style="gap:2.4mm;background:{YEL};border-radius:2.4mm;padding:4mm">
    <div class="an" style="font-size:15pt;color:{INK}">Visit us</div>
    <div style="font-size:8.6pt;line-height:1.35;color:{C['Ink Text']}">Ask for the price list and a sample of any film.</div></div>
  <div>{contact(7.6)}</div>""")
    title = f'<div class="an" style="font-size:24pt;color:{WHITE}">Complete protection<br><span style="color:{YEL}">for all your devices</span></div>'
    names = f'<span style="color:{YEL}">&nbsp;/&nbsp;</span>'.join(n for n, _, _ in TYPES)
    sub = f'<div class="an" style="text-align:center;font-size:9pt;color:{WHITE};line-height:1.4">{names}</div>'
    svg = hero_phone(cx_ + cw / 2, BL + 128, 33, 10, 'f2')
    html = flap + back + flyer_cover(cx_, cw, 'Premium device protection&nbsp;&nbsp;·&nbsp;&nbsp;Pakistan', title, sub)
    return FW, FH, page(FW, FH, svg, html), save_tex('r-flyer2-outside', P), 0.14


def flyer2_inside():
    P = Paint(FW, FH, 0.14, 831)
    flyer_grunge(P, 831)
    (x1, w1), (x2, w2), (x3, w3) = IN_PANELS
    p1 = panel(x1, w1, f'<div>{tab_title("Choose your protection", "layers", 11)}</div>' + ''.join(type_card(k, *TYPES[k]) for k in range(3)))
    p2 = panel(x2, w2, ''.join(type_card(k, *TYPES[k]) for k in range(3, 6))
               + f'<div style="font-size:7pt;color:{GREY};line-height:1.35">Every film comes as 1 side or full body. See the price list for prices.</div>')
    p3 = panel(x3, w3, f"""<div class="col" style="gap:2mm">{tab_title('Lifetime Care', 'infinity', 11)}
    <div style="font-size:7.4pt;line-height:1.35;color:{WHITE}">Your protection can be replaced for as long as you use the device, with a clearly stated fee on every replacement, including the first.</div></div>
  <div class="col" style="gap:2.6mm">{tab_title('Key terms', 'receipt', 11)}{terms_list(7.3, 2.3, 4.8)}</div>
  {disclosure(6.6)}""")
    return FW, FH, page(FW, FH, '', p1 + p2 + p3), save_tex('r-flyer2-inside', P), 0.14


# ---- ROLL-UP STANDEE (850 x 2000 mm) -----------------------------------------------------
def standee():
    TW, TH = 850, 2000
    W, H = TW + 2 * BL, TH + 2 * BL
    cell = 0.6
    P = Paint(W, H, cell, 901, k=5)
    P.dry_brush('yellow', (-20, 1240), (W + 20, 760), 330, bristles=260, dryness=0.5, solid=0.55, bend=40)
    P.spatter('yellow', W * 0.72, 820, 240, 180, 0.6, 5)
    P.spatter('yellow', W * 0.2, 1260, 200, 120, 0.6, 4)
    P.dry_brush('yellow', (-30, 1885), (W + 30, 1860), 150, bristles=260, dryness=0.35, solid=0.85, bend=-8)
    P.stroke('yellow', [(-40, 1925), (W * 0.5, 1905), (W + 40, 1915)], 110, pressure=1)
    P.stroke('yellow', [(-40, 1960), (W + 40, 1960)], 160, pressure=1)
    cx = W / 2
    svg = hero_phone(cx + 130, 1075, 300, -11, 'st')
    types = ''.join(f"""<div class="col" style="align-items:center;gap:9mm;flex:1">{swatch(n, 104, 's%d' % k)}
      <div class="an" style="font-size:50pt;color:{WHITE};text-align:center">{n}</div></div>""" for k, (n, d, f) in enumerate(TYPES))
    html = A.logo_slot(cx, BL + 205, 640) + f"""
<div class="abs mono" style="left:0;width:{W}mm;top:{BL + 360}mm;text-align:center;font-size:42pt;letter-spacing:.32em;color:{YEL}">Premium device protection</div>
<div class="abs an" style="left:{BL + 60}mm;top:{BL + 430}mm;font-size:250pt;line-height:.92;color:{WHITE}">Stay<br>wrapped.<br><span style="color:{YEL}">Stay<br>protected.</span></div>
<div class="abs" style="left:{BL + 40}mm;width:{TW - 80}mm;top:{BL + 1430}mm"><div class="flex" style="gap:12mm">{types}</div></div>
<div class="abs" style="left:{BL + 40}mm;width:{TW - 80}mm;top:{BL + 1610}mm">{device_row(78, 40)}</div>
<div class="abs" style="left:0;width:{W}mm;top:{BL + 1828}mm;text-align:center">
  <div class="an" style="font-size:110pt;color:{INK}">{OFFICE['web']}</div></div>"""
    return W, H, page(W, H, svg, html), save_tex('r-standee', P), cell


def build(only=None):
    os.makedirs(os.path.join(HERE, 'html'), exist_ok=True)
    jobs = []

    def add(name, spec, trim):
        W, H, doc, tex, cell = spec
        p = os.path.join(HERE, 'html', name + '.html')
        open(p, 'w').write(doc)
        jobs.append(dict(name=name, html=p, w=W, h=H, trim=trim, cmyk=True, tex=tex, cell=cell, layers=LAYERS, bg='Wrap Black'))
        print('built', name)

    add('r-acrylic1-front', acrylic1_front(), (210, 297))
    add('r-acrylic1-back', acrylic1_back(), (210, 297))
    add('r-acrylic2-front', acrylic2_front(), (210, 297))
    add('r-acrylic2-back', acrylic2_back(), (210, 297))
    add('r-flyer1-outside', flyer1_outside(), (297, 210))
    add('r-flyer1-inside', flyer1_inside(), (297, 210))
    add('r-flyer2-outside', flyer2_outside(), (297, 210))
    add('r-flyer2-inside', flyer2_inside(), (297, 210))
    add('r-standee', standee(), (850, 2000))
    json.dump(jobs, open(os.path.join(HERE, 'jobs_retail.json'), 'w'), indent=1)
    json.dump(TOKENS_R, open(os.path.join(HERE, 'tokens.json'), 'w'), indent=1)


if __name__ == '__main__':
    build()
