"""Local clean-up of the generated photos (no paid tools). Writes into photos_raw/.

  t1_cut2.png   hand + phone cut-out. The paid remover dropped most of the hand, so its alpha is
                kept only for the phone and the hand is keyed against the plain studio background.
  t1_final.png  ...with the Apple logo filled in (a fitted surface of the surrounding metal + grain).
  t3_cut.png    face close-up keyed off its flat yellow background.
  p3_clean.png  'tuff' model: Nike swoosh removed from the left sneaker.
  p4_clean.png  'matte' model: the crossed stripes on both sneakers painted out.
  hero_clean.png hero: the garbled AI lettering on the upturned sole filled in.
  hw_cut.png    wide-pose hero (straddle jump), cut out locally and free with rembg/BiRefNet.
"""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

R = 'photos_raw/'


def load(name):
    return np.asarray(Image.open(R + name).convert('RGBA')).astype(np.float32)


def save(arr, name):
    Image.fromarray(arr.clip(0, 255).astype(np.uint8)).save(R + name)


def biggest(mask):
    lab, n = ndi.label(mask)
    if n == 0:
        return mask
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    return ndi.binary_fill_holes(lab == (np.argmax(sizes) + 1))


def refine(soft, core, band=4):
    """Solid inside `core`, soft edge values in a thin band around it, empty elsewhere."""
    inner = ndi.binary_erosion(core, iterations=band)
    outer = ndi.binary_dilation(core, iterations=band)
    return np.where(inner, 1, np.where(outer, soft, 0))


def surface_fill(rgb, mask, ring, grain_seed=3, grain=0.9):
    """Replace `mask` with a quadratic surface fitted on `ring`, plus matching grain."""
    Y, X = np.mgrid[0:rgb.shape[0], 0:rgb.shape[1]]
    A = np.stack([np.ones_like(X), X, Y, X * X, Y * Y, X * Y], -1).reshape(-1, 6).astype(np.float64)
    noise = ndi.gaussian_filter(np.random.default_rng(grain_seed).normal(0, 1, rgb.shape[:2]), 0.7)
    out = rgb.copy()
    r = ring.reshape(-1)
    for c in range(3):
        v = rgb[..., c].reshape(-1)
        coef, *_ = np.linalg.lstsq(A[r], v[r], rcond=None)
        fit = (A @ coef).reshape(rgb.shape[:2])
        sd = np.std(rgb[..., c][ring] - fit[ring])
        out[..., c] = fit + noise * sd * grain
    return out


def blend(base, patch, mask, feather):
    f = ndi.gaussian_filter(mask.astype(np.float32), feather)[..., None]
    return base * (1 - f) + patch * f


def phone():
    im = load('t1_b.png')[..., :3]
    paid = load('t1_cut.png')[..., 3] / 255
    lum, sat = im.mean(-1), im.max(-1) - im.min(-1)
    bg = (sat < 14) & (lum > 150) & (paid < 0.05)
    w = bg.astype(np.float32)
    est = np.stack([ndi.gaussian_filter(im[..., c] * w, 40) for c in range(3)], -1)
    est /= np.maximum(ndi.gaussian_filter(w, 40), 1e-4)[..., None]
    key = np.clip((np.sqrt(((im - est) ** 2).sum(-1)) - 10) / 28, 0, 1)
    fg = np.maximum(key, paid)
    core = biggest(ndi.binary_opening(fg > 0.5, iterations=2))
    a = ndi.gaussian_filter(refine(fg, core), 0.8)
    save(np.dstack([im, a * 255]), 't1_cut2.png')
    # Apple logo: an ellipse over the logo and leaf, filled from the metal around it
    x0, x1, y0, y1 = 540, 900, 700, 1080
    reg = im[y0:y1, x0:x1]
    Y, X = np.mgrid[0:reg.shape[0], 0:reg.shape[1]]
    cx, cy = 708 - x0, 880 - y0
    mask = ((X - cx) / 100) ** 2 + ((Y - cy) / 122) ** 2 <= 1
    ring = (((X - cx) / 150) ** 2 + ((Y - cy) / 172) ** 2 <= 1) & ~mask
    im[y0:y1, x0:x1] = blend(reg, surface_fill(reg, mask, ring), mask, 6)
    save(np.dstack([im, a * 255]), 't1_final.png')


def face():
    im = load('t3_a.png')[..., :3]
    bgc = np.median(np.concatenate([im[:200, :300].reshape(-1, 3), im[:, :100].reshape(-1, 3)]), axis=0)
    soft = np.clip((np.sqrt(((im - bgc) ** 2).sum(-1)) - 18) / 37, 0, 1)
    core = biggest(ndi.binary_opening(soft > 0.5, iterations=3))
    a = ndi.gaussian_filter(refine(soft, core, 6), 1.2)
    save(np.dstack([im, a * 255]), 't3_cut.png')


def detail_mask(lum, size, thresh, dark=True):
    """Pixels that differ from their local median: printed/embossed marks on a plain panel."""
    d = ndi.median_filter(lum, size=size) - lum
    return (d if dark else -d) > thresh


def swoosh():
    im = load('p3_cut.png')
    x0, x1, y0, y1 = 330, 480, 1225, 1320          # side panel of the camera-left sneaker
    reg = im[y0:y1, x0:x1, :3]
    Y, X = np.mgrid[0:y1 - y0, 0:x1 - x0]
    # the swoosh sits in an ellipse centred ~(409, 1272); stay clear of the heel seam and collar
    mask = ((X - 79) / 50) ** 2 + ((Y - 47) / 30) ** 2 <= 1
    mask &= im[y0:y1, x0:x1, 3] > 250
    ring = (((X - 79) / 66) ** 2 + ((Y - 47) / 42) ** 2 <= 1) & ~mask & (im[y0:y1, x0:x1, 3] > 250)
    im[y0:y1, x0:x1, :3] = blend(reg, surface_fill(reg, mask, ring, grain=0.15), mask, 4)
    save(im, 'p3_clean.png')
    return mask.sum()


def stripes():
    im = load('p4_cut.png')
    rgb = im[..., :3]
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    green = (g - np.maximum(r, b) > 35) & (im[..., 3] > 200)
    lab, n = ndi.label(green)
    sizes = ndi.sum(green, lab, range(1, n + 1))
    cms = ndi.center_of_mass(green, lab, range(1, n + 1))
    # the stripes are small green islands on the shoes; the trousers are one huge region above
    # and the green sole trim sits below y 1900
    keep = [i + 1 for i, (sz, c) in enumerate(zip(sizes, cms)) if sz > 150 and 1600 < c[0] < 1900]
    mask = ndi.binary_dilation(np.isin(lab, keep), iterations=3)
    panel = ~mask & (rgb.mean(-1) > 165) & (np.abs(g - r) < 25) & (im[..., 3] > 250)   # cream leather
    out = rgb.copy()
    lab2, n2 = ndi.label(ndi.binary_dilation(mask, iterations=6))
    for i in range(1, n2 + 1):
        m = mask & (lab2 == i)
        ys, xs = np.nonzero(ndi.binary_dilation(m, iterations=24))
        sl = (slice(ys.min(), ys.max() + 1), slice(xs.min(), xs.max() + 1))
        ring = (ndi.binary_dilation(m, iterations=18) & panel)[sl]
        if ring.sum() < 50:
            continue
        out[sl] = blend(out[sl], surface_fill(out[sl], m[sl], ring, grain=0.5), m[sl], 1.5)
    im[..., :3] = out
    save(im, 'p4_clean.png')
    return mask.sum()


def hero_sole():
    im = load('hero_b_cut.png')
    x0, x1, y0, y1 = 480, 548, 1150, 1290
    reg = im[y0:y1, x0:x1, :3]
    mask = np.zeros(reg.shape[:2], bool)
    mask[20:120, 16:52] = True
    ring = np.zeros_like(mask)
    ring[6:134, 4:64] = True
    ring &= ~mask
    im[y0:y1, x0:x1, :3] = blend(reg, surface_fill(reg, mask, ring, grain=0.3), mask, 2)
    save(im, 'hero_clean.png')


def cutout_free(src, out, model='birefnet-portrait'):
    """Free local background removal (rembg + BiRefNet). Keeps hair strands and white sneakers
    on a light backdrop, which a colour key can't."""
    from rembg import remove, new_session
    remove(Image.open(R + src).convert('RGB'), session=new_session(model)).save(R + out)


if __name__ == '__main__':
    phone()
    face()
    print('swoosh px', swoosh())
    print('stripe px', stripes())
    hero_sole()
    cutout_free('hw_a.png', 'hw_cut.png')
