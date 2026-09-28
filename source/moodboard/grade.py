"""One bright, high-key grade for every photo, closer to the MÜLER look than the generator's
muted editorial grade: lifted shadows, a touch more exposure, cleaner whites, richer clothing
colour (vibrance) with skin protected, and a little crispness."""
import numpy as np
from PIL import Image
from scipy import ndimage as ndi


def _hsv(rgb):
    mx, mn = rgb.max(-1), rgb.min(-1)
    d = mx - mn
    s = np.where(mx > 0, d / np.maximum(mx, 1e-6), 0)
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    h = np.zeros_like(mx)
    m = d > 1e-6
    rc = np.where(m, (mx - r) / np.maximum(d, 1e-6), 0)
    gc = np.where(m, (mx - g) / np.maximum(d, 1e-6), 0)
    bc = np.where(m, (mx - b) / np.maximum(d, 1e-6), 0)
    h = np.where(r == mx, bc - gc, np.where(g == mx, 2 + rc - bc, 4 + gc - rc))
    h = (h / 6) % 1
    return h, s, mx


def _rgb(h, s, v):
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    out = np.stack([
        np.choose(i, [v, q, p, p, t, v]),
        np.choose(i, [t, v, v, q, p, p]),
        np.choose(i, [p, p, t, v, v, q])], -1)
    return out


def grade(im, exposure=1.08, lift=0.5, vibrance=0.55, whites=0.7, sharpen=0.4):
    a = np.asarray(im.convert('RGBA')).astype(np.float32) / 255
    rgb, alpha = a[..., :3], a[..., 3:]

    # exposure, then lift the shadows and lower mids through a luminance curve (keeps hue)
    rgb = np.clip(rgb * exposure, 0, 1)
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    curved = lum + lift * lum * (1 - lum) ** 2
    rgb = np.clip(rgb * (curved / np.maximum(lum, 1e-4))[..., None], 0, 1)

    # vibrance: push low-saturation colour more than already-strong colour; spare skin tones
    h, s, v = _hsv(rgb)
    skin = np.exp(-((h - 0.07) / 0.05) ** 2) * (s > 0.15) * (s < 0.65)
    s = np.clip(s * (1 + vibrance * (1 - s) * (1 - 0.9 * skin)), 0, 1)
    rgb = _rgb(h, s, v)

    # neutral, clean whites: near-white, low-saturation pixels drift toward pure neutral
    lum = rgb @ np.array([0.2126, 0.7152, 0.0722], np.float32)
    wmask = np.clip((lum - 0.72) / 0.2, 0, 1) * np.clip(1 - s / 0.18, 0, 1) * whites
    rgb = rgb * (1 - wmask[..., None]) + np.minimum(lum[..., None] * 1.03, 1) * wmask[..., None]

    # a little crispness (unsharp mask on the colour, not the edges of the cut-out)
    blur = np.stack([ndi.gaussian_filter(rgb[..., c], 1.4) for c in range(3)], -1)
    rgb = np.clip(rgb + sharpen * (rgb - blur), 0, 1)

    return Image.fromarray((np.concatenate([rgb, alpha], -1) * 255).round().astype(np.uint8), 'RGBA')
