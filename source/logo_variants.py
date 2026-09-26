"""One-colour versions of the original logo, made by recolouring its own vector paths.

Nothing is redrawn: the logo PDF's content stream is split into its drawing blocks, and each
block keeps its exact geometry. Only the paint changes (or a block is left out).

Blocks in the original, bottom to top:
  rim     - white silhouette behind the whole word (fill + 1 pt stroke)
  grad    - letter bodies, amber -> orange gradient (clip path + shading)
  outline - thin orange line around the silhouette
  edge    - thin amber edge on each letter

Variants (colours are RGB, for the garment files):
  full    - the original, untouched
  white   - letters only, white        (one-colour print on dark shirts)
  black   - letters only, black        (one-colour print on light shirts)
  inverse - white letters on a black silhouette (bubble letters with a black outline)
"""
import os, re
import pymupdf as fitz

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'logo.pdf')
FORM = 14                                  # xref of the form XObject holding the artwork
BLACK, WHITE = '#111111', '#FFFFFF'

VARIANTS = {
    'white':   dict(rim=None, outline=None, grad=WHITE, edge=WHITE),
    'black':   dict(rim=None, outline=None, grad=BLACK, edge=BLACK),
    'inverse': dict(rim=BLACK, outline=BLACK, grad=WHITE, edge=BLACK),
}
ROLE_BY_COLOUR = {'0 0 0 0': 'rim', '0.004 0.496 0.992 0': 'outline', '0.098 0.172 0.895 0': 'edge'}
_CACHE = {}


def blocks(stream):
    """Split the form's content into top-level q ... Q blocks."""
    out, cur, depth = [], [], 0
    for line in stream.split('\n'):
        if not line.strip():
            continue
        cur.append(line)
        depth += len(re.findall(r'(?:^|\s)q(?=\s|$)', line)) - len(re.findall(r'(?:^|\s)Q(?=\s|$)', line))
        if depth == 0:
            out.append(cur)
            cur = []
    assert not cur, 'unbalanced q/Q in logo stream'
    return out


def role(block):
    text = '\n'.join(block)
    if ' sh ' in text:
        return 'grad'
    m = re.search(r'^([\d. ]+) k$', text, re.M)
    return ROLE_BY_COLOUR[m.group(1).strip()]


def rgb(hexv):
    return ' '.join('%.4f' % (int(hexv[i:i + 2], 16) / 255) for i in (1, 3, 5))


def paint(block, r, colour):
    c = rgb(colour)
    text = '\n'.join(block)
    if r == 'grad':                       # fill the clip with a flat colour instead of the gradient
        return text.replace('BX /Sh0 sh EX', f'{c} rg -50 -50 100 100 re f')
    text = re.sub(r'^[\d. ]+ k$', f'{c} rg', text, flags=re.M)
    return re.sub(r'^[\d. ]+ K$', f'{c} RG', text, flags=re.M)


def logo(variant='full'):
    """fitz document of the logo in the given variant (same page size as the original)."""
    if variant not in _CACHE:
        doc = fitz.open(SRC)
        if variant != 'full':
            spec = VARIANTS[variant]
            parts = []
            for b in blocks(doc.xref_stream(FORM).decode('latin1')):
                r = role(b)
                if spec[r]:
                    parts.append(paint(b, r, spec[r]))
            doc.update_stream(FORM, '\n'.join(parts).encode('latin1'))
        _CACHE[variant] = doc
    return _CACHE[variant]


def parse_slot(sid):
    """Slot ids: 'logo', 'logo2' -> original; 'logo--<variant>[--r<deg>]' -> variant, rotated."""
    parts = sid.split('--')
    variant = parts[1] if len(parts) > 1 else 'full'
    rot = int(parts[2][1:]) if len(parts) > 2 else 0
    return variant, rot


if __name__ == '__main__':
    out = os.path.join(HERE, 'preview')
    os.makedirs(out, exist_ok=True)
    for v in ('full', *VARIANTS):
        logo(v)[0].get_pixmap(dpi=200, alpha=True).save(os.path.join(out, f'logo-{v}.png'))
        print(v, [role(b) for b in blocks(fitz.open(SRC).xref_stream(FORM).decode('latin1'))].count('grad') if v == 'full' else '')
