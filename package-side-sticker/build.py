"""Wrapshap package-side sticker: black + white versions, QR -> Instagram.
Change INSTAGRAM_URL below and re-run:  python3 build.py
"""
import re, segno, os

INSTAGRAM_URL = "https://www.instagram.com/wrapshap/"   # <-- CONFIRM HANDLE
HERE = os.path.dirname(os.path.abspath(__file__))
W, H = 496, 898
YEL = "#E8C53A"

# --- logo (exact vector from source/logo.pdf), inlined ---
svg = open(f"{HERE}/logo.svg").read()
inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1)
LOGO = f'<g transform="translate(66,128) scale(1.64)">{inner}</g>'   # 219x80pt -> ~360x131

# --- QR ---
q = segno.make(INSTAGRAM_URL, error="m", boost_error=False)
n = len(q.matrix); quiet = 0
px = 296 / n
qx0, qy0 = 100, 295
rects = "".join(f'<rect x="{qx0+c*px:.2f}" y="{qy0+r*px:.2f}" width="{px+.35:.2f}" height="{px+.35:.2f}"/>'
                for r, row in enumerate(q.matrix) for c, v in enumerate(row) if v)

def strokes(c):
    return f'''
<g fill="{c}">
 <polygon points="0,18 150,0 158,14 118,30 60,52 18,100 0,108"/>
 <polygon points="0,112 70,62 130,40 160,36 120,66 66,104 0,168"/>
 <polygon points="0,170 40,120 96,84 118,88 70,126 26,176 0,196"/>
</g>
<g fill="#000" opacity="0"/>
<g fill="{c}">
 <polygon points="496,898 496,812 440,822 388,850 330,880 306,898"/>
 <polygon points="496,800 496,770 450,790 400,812 430,810"/>
</g>
<g fill="{BG}">
 <circle cx="60" cy="40" r="1.6"/><circle cx="96" cy="22" r="1.2"/><circle cx="30" cy="70" r="1.5"/>
 <circle cx="430" cy="860" r="1.4"/><circle cx="470" cy="835" r="1.2"/><circle cx="400" cy="880" r="1.6"/>
</g>'''

def build(mode):
    global BG
    dark = mode == "black"
    BG = "#000000" if dark else "#FFFFFF"
    FG = "#FFFFFF" if dark else "#000000"
    URLC = YEL if dark else "#000000"
    panel_stroke = "" if dark else 'stroke="#000" stroke-width="3"'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<defs><style>
@font-face{{font-family:CB;src:url('CaveatBrush-Regular.ttf')}}
@font-face{{font-family:SM;src:url('SpaceMono-Regular.ttf')}}
.h{{font-family:CB,cursive;font-size:36px;fill:{FG};text-anchor:middle;font-style:italic}}
.u{{font-family:SM,monospace;font-size:27px;letter-spacing:3px;fill:{URLC};text-anchor:middle}}
.t{{font-family:SM,monospace;font-size:14.5px;letter-spacing:2.6px;fill:{FG};text-anchor:middle}}
</style></defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
{strokes(YEL)}
<!-- crown -->
<path d="M210,92 L214,60 L232,78 L250,54 L268,78 L286,60 L290,92 Z" fill="none" stroke="{YEL}" stroke-width="3.2" stroke-linejoin="round"/>
{LOGO}
<!-- slashes -->
<line x1="385" y1="246" x2="407" y2="236" stroke="{FG}" stroke-width="3" stroke-linecap="round"/>
<line x1="414" y1="268" x2="444" y2="258" stroke="{FG}" stroke-width="3" stroke-linecap="round"/>
<!-- QR panel -->
<polygon points="420,285 428,285 428,620 90,620 90,612 420,612" fill="{YEL}"/>
<rect x="80" y="275" width="335" height="335" fill="#fff" {panel_stroke}/>
<g fill="#000">{rects}</g>
<!-- zigzag -->
<polyline points="48,630 70,616 64,626 84,614" fill="none" stroke="{YEL}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
<!-- smiley -->
<g fill="none" stroke="{YEL}" stroke-width="3.2" stroke-linecap="round">
 <circle cx="48" cy="355" r="29"/><path d="M33,360 Q48,380 63,360"/>
 <line x1="40" y1="345" x2="40" y2="351"/><line x1="56" y1="345" x2="56" y2="351"/>
</g>
<!-- phone -->
<g transform="rotate(14 453 525)" fill="none" stroke="{FG}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
 <rect x="432" y="490" width="42" height="76" rx="7"/><line x1="445" y1="497" x2="461" y2="497"/>
 <line x1="443" y1="540" x2="462" y2="520"/><line x1="447" y1="548" x2="462" y2="532"/>
</g>
<g stroke="{YEL}" stroke-width="2.6" stroke-linecap="round"><line x1="455" y1="472" x2="458" y2="481"/><line x1="470" y1="483" x2="478" y2="487"/></g>
<text class="h" x="248" y="675">scan and checkout</text>
<text class="h" x="248" y="712">your life time</text>
<text class="h" x="248" y="749">screen protector</text>
<text class="u" x="248" y="800">WRAPSHAP.PR</text>
<text class="t" x="248" y="838">STAY WRAPPED. STAY PROTECTED.</text>
</svg>'''

for mode in ("black", "white"):
    open(f"{HERE}/wrapshap-sticker-{mode}.svg", "w").write(build(mode))
