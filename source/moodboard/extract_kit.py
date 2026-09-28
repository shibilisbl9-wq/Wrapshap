"""Cut the scanned brush / doodle / grunge sheets into single-colour alpha masks (kit/*.png).

Each mask is pure black with the ink as alpha, so the layout can recolour it with CSS
(mask-image) to any brand colour."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

RAW = 'photos_raw/'


def ink_alpha(path, lo=0.18, hi=0.62):
    L = np.asarray(Image.open(path).convert('L')).astype(np.float32) / 255
    # paper level: brightest nearby values, smoothed (removes the vignette)
    bg = ndi.gaussian_filter(ndi.maximum_filter(L, size=61), 25)
    r = 1 - np.clip(L / np.maximum(bg, 1e-3), 0, 1)          # 0 = paper, 1 = ink
    return np.clip((r - lo) / (hi - lo), 0, 1)


def save_mask(a, name, pad=12):
    ys, xs = np.nonzero(a > 0.02)
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, a.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, a.shape[1])
    a = a[y0:y1, x0:x1]
    rgba = np.zeros(a.shape + (4,), np.uint8)
    rgba[..., 3] = (a * 255).round().astype(np.uint8)
    Image.fromarray(rgba).save(f'kit/{name}.png')
    return a.shape


def components(a, grow=25, min_area=300):
    lab, n = ndi.label(ndi.binary_dilation(a > 0.3, iterations=grow))
    out = []
    for i, sl in enumerate(ndi.find_objects(lab), 1):
        m = (lab == i)
        area = (a * m).sum()
        if area < min_area:
            continue
        out.append((sl, a * m))
    return out


# names follow the sheets' left-to-right reading order
NAMES = {
    'brush': ['brush-swoosh', 'brush-zigzag-arrow', 'brush-m', 'brush-zigzag', 'brush-dab', 'brush-loop'],
    'doodle': ['doodle-crown', 'doodle-squiggle', 'doodle-star-smiley', 'doodle-smiley', 'doodle-star',
               'doodle-scribble', 'doodle-arrow'],
}

if __name__ == '__main__':
    for sheet, prefix, grow in [('sheet_brush.png', 'brush', 7), ('sheet_doodle.png', 'doodle', 4)]:
        a = ink_alpha(RAW + sheet)
        comps = components(a, grow)
        # a doodle drawn as separate strokes (a smiley's face inside its circle) is one piece
        inside = lambda s, o: (s[0].start >= o[0].start and s[0].stop <= o[0].stop
                               and s[1].start >= o[1].start and s[1].stop <= o[1].stop)
        merged = []
        for sl, m in comps:
            host = next((c for c in merged if inside(sl, c[0])), None)
            if host:
                host[1] += m
            else:
                merged.append([sl, m])
        comps = [c for c in merged if c[1].sum() > 4000]
        for k, (sl, m) in enumerate(sorted(comps, key=lambda c: (c[0][1].start // 400, c[0][0].start))):
            print(prefix, k, sl, save_mask(m, NAMES[prefix][k]))
    g = ink_alpha(RAW + 'sheet_grunge.png', lo=0.10, hi=0.55)
    h, w = g.shape
    save_mask(g[int(h*.06):int(h*.94), int(w*.28):int(w*.94)], 'texture-grunge', pad=0)
