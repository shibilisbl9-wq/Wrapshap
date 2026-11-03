"""Wrapshap package-side sticker (black + white).

Built ON TOP of the original artwork (original-artwork.jpg) so the design is
identical. Only three things are replaced:
  1. QR code   -> re-generated, points to INSTAGRAM_URL (crisp vector-sharp)
  2. 'WRAPSHAP.AE' -> 'WRAPSHAP.PR' using the artwork's own P and R glyphs
  3. Logo      -> the vector logo from source/logo.pdf, laid exactly over the
                  original so it prints sharp
Run:  python3 build.py
"""
import os
import numpy as np, segno
from PIL import Image, ImageDraw

INSTAGRAM_URL = "https://www.instagram.com/wrapshappk/"
S = 4                                                   # upscale factor
HERE = os.path.dirname(os.path.abspath(__file__))

orig = Image.open(f"{HERE}/original-artwork.jpg").convert("RGB")
W, H = orig.size                                        # 496 x 898
base = np.asarray(orig.resize((W*S, H*S), Image.LANCZOS)).astype(float)

# ---- 2. domain text: AE -> PR, reusing the artwork's own mono glyphs --------
PITCH = 16.27                     # monospace cell width (orig px)
Y0, Y1 = 773, 800                 # text band
def cols(x0, x1): return slice(int(round(x0*S)), int(round(x1*S)))
rows = slice(Y0*S, Y1*S)
P_src = base[rows, cols(208.5, 208.5+PITCH)].copy()    # 'P' (cell 3)
R_src = base[rows, cols(175.5, 175.5+PITCH)].copy()    # 'R' (cell 1)
base[rows, cols(302, 340)] = base[Y0*S-8:Y0*S-4, cols(302, 340)].mean((0, 1))   # erase 'AE'
def paste(src, x):
    sl = cols(x, x+PITCH); w = sl.stop - sl.start
    base[rows, sl.start:sl.start+min(w, src.shape[1])] = src[:, :w]
paste(P_src, 208.5 + 6*PITCH)     # cell 9
paste(R_src, 175.5 + 9*PITCH)     # cell 10

# ---- white version: flip the neutral (black/white) parts, keep the yellow --
def to_white(arr):
    mx = arr.max(2); mn = arr.min(2)
    sat = (mx - mn) / np.maximum(mx, 1)
    w = (np.clip((sat - .25) / .35, 0, 1) * np.clip((mx - 40) / 60, 0, 1))[..., None]
    alpha = np.clip(mx / 228.0, 0, 1)[..., None]
    coloured = arr + (1 - alpha) * 255                  # same colour, on white
    lum = np.clip((arr.mean(2, keepdims=True) - 12) * 255 / 233, 0, 255)  # crush JPEG noise
    neutral = np.repeat(255 - lum, 3, 2)                 # black<->white
    out = w * coloured + (1 - w) * neutral
    # domain line: yellow on white is unreadable, so print it black
    band = arr[rows, cols(150, 345)]
    t = np.clip((band.max(2) - 30) / 170, 0, 1)[..., None]
    out[rows, cols(150, 345)] = 255 * (1 - t)
    return np.clip(out, 0, 255)

def finish(arr, dark):
    img = Image.fromarray(arr.astype(np.uint8))
    d = ImageDraw.Draw(img)
    # ---- 3. vector logo laid exactly over the original (bbox x68-427, y109-239)
    logo = Image.open(f"{HERE}/logo-hi.png").resize(((427-68+1)*S, (239-109+1)*S), Image.LANCZOS)
    img.paste(logo, (68*S, 109*S), logo)
    # ---- 1. QR panel + code (same position/size as the original QR)
    px0, py0, px1, py1 = 83.5*S, 278*S, 412.5*S, 607*S
    if not dark:   # panel needs an edge on a white background
        d.rectangle([px0-4*S, py0-4*S, px1+4*S, py1+4*S], fill="black")
    d.rectangle([px0, py0, px1, py1], fill="white")
    m = segno.make(INSTAGRAM_URL, error="m", boost_error=False).matrix
    n = len(m); size = 238*S; mod = size / n
    qx = (px0 + px1)/2 - size/2; qy = (py0 + py1)/2 - size/2
    for r, row in enumerate(m):
        for c, v in enumerate(row):
            if v:
                d.rectangle([qx+c*mod, qy+r*mod, qx+(c+1)*mod-1, qy+(r+1)*mod-1], fill="black")
    return img

for mode in ("black", "white"):
    arr = base.copy() if mode == "black" else to_white(base.copy())
    img = finish(arr, mode == "black")
    img.save(f"{HERE}/wrapshap-sticker-{mode}.png", dpi=(900, 900))
    img.save(f"{HERE}/wrapshap-sticker-{mode}.pdf", resolution=900)
    print(mode, img.size)
