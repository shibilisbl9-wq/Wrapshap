"""Crop each cut-out photo to its subject and save a compact WebP (with alpha) into img/.

photos_raw/ holds the full-size Higgsfield generations and cut-outs; it is not committed.
Selected shots:  hero = hw_a (wide straddle jump),  poster 1-5 = p1_a, p2_b, p3_a, p4_b, p5_a (3 and 4 retouched, see retouch.py),
tile 1 (hand + phone) = t1_b, tile 2 (group) = t2_b, tile 3 (face) = t3_a."""
import json
import numpy as np
from PIL import Image

PICKS = {  # output name: (cut-out file, max height px)
    'hero': ('hw_cut.png', 1500),
    'p1': ('p1_cut.png', 1700), 'p2': ('p2_cut.png', 1700), 'p3': ('p3_clean.png', 1700),
    'p4': ('p4_clean.png', 1700), 'p5': ('p5_cut.png', 1700),
    'phone': ('t1_final.png', 1700), 'group': ('t2_cut.png', 1800), 'face': ('t3_cut.png', 2048),
}
info = {}
for name, (src, hmax) in PICKS.items():
    im = Image.open('photos_raw/' + src).convert('RGBA')
    a = np.asarray(im)[..., 3]
    ys, xs = np.nonzero(a > 8)
    box = (int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1)
    im = im.crop(box)
    if im.height > hmax:
        im = im.resize((round(im.width * hmax / im.height), hmax), Image.LANCZOS)
    im.save(f'img/{name}.webp', quality=90, method=6)
    info[name] = {'w': im.width, 'h': im.height, 'src_box': box}
    print(name, im.size)
json.dump(info, open('img/sizes.json', 'w'), indent=1)
