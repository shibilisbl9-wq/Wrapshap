"""Render the brand board, hero banner and 1080x1920 stories into option-f-campaign/.

    python3 build.py && python3 export.py
"""
import os
import shutil
import subprocess
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', '..', 'option-f-campaign')
STORIES = ['clear', 'privacy', 'tuff', 'matte', '60-sec']


def shot(page, png, w, h, scale, transparent=False):
    args = ['node', 'shot.mjs', page, png, str(w), str(h), str(scale)] + (['1'] if transparent else [])
    subprocess.run(args, cwd=HERE, check=True)


def to_jpg(png, jpg, q=92):
    Image.open(png).convert('RGB').save(jpg, quality=q, optimize=True, progressive=True)
    os.remove(png)
    print(os.path.relpath(jpg, HERE), Image.open(jpg).size)


if __name__ == '__main__':
    for d in ('01-hero', '02-stories', '03-logo', '04-kit', '05-stickers'):
        os.makedirs(os.path.join(OUT, d), exist_ok=True)
    tmp = os.path.join(HERE, 'tmp.png')

    shot('board.html', tmp, 1024, 1536, 3)
    to_jpg(tmp, os.path.join(OUT, 'wrapshap-brand-board.jpg'))
    shot('hero.html', tmp, 1024, 420, 3)
    to_jpg(tmp, os.path.join(OUT, '01-hero', 'wrapshap-hero-banner.jpg'))
    for i, name in enumerate(STORIES, 1):
        shot(f'poster-{i}.html', tmp, 1080, 1920, 1)
        to_jpg(tmp, os.path.join(OUT, '02-stories', f'wrapshap-story-{i:02d}-{name}-1080x1920.jpg'))

    # one-colour logo (vector, cut from the original artwork) and the full-colour original
    for src, dst in [('logo-mono-black.svg', 'wrapshap-logo-black.svg'),
                     ('logo-mono-white.svg', 'wrapshap-logo-white.svg'),
                     ('logo-mono-black-rim.svg', 'wrapshap-logo-black-white-rim.svg'),
                     ('logo-colour.svg', 'wrapshap-logo-full-colour.svg')]:
        shutil.copy(os.path.join(HERE, src), os.path.join(OUT, '03-logo', dst))
    for f in sorted(os.listdir(os.path.join(HERE, 'kit'))):
        if f.endswith('.png'):
            shutil.copy(os.path.join(HERE, 'kit', f), os.path.join(OUT, '04-kit', f))
    shot('pattern.html', os.path.join(OUT, '04-kit', 'doodle-pattern-1080.png'), 1080, 1080, 1, transparent=True)
    for f in sorted(os.listdir(os.path.join(HERE, 'stickers'))):
        if f.endswith('.webp'):
            shutil.copy(os.path.join(HERE, 'stickers', f), os.path.join(OUT, '05-stickers', 'wrapshap-sticker-' + f[3:]))
