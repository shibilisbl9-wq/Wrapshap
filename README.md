# Wrapshap: envelope redesign, mat pads and t-shirt

This repo has two design options. Each one is a complete set: envelope, four mat pads, a t-shirt and a design-system sheet.
Both use the **original Wrapshap logo artwork unchanged**. It was taken as vector straight out of the supplied envelope file.

| | Option A: Wrap Halo | Option B: Graffiti |
|---|---|---|
| Folder | `option-a-wrap-halo/` | `option-b-graffiti/` |
| Mood | Clean, premium, tech | Loud, street, paint-splattered |
| Main graphic | Thin rounded "device" outlines around the logo, fading outward | A thrown paint splat behind the logo, paint dripping from the top edge |
| Headline type | Geist SemiBold | Big Shoulders Stencil (Black, all caps) |
| Ownership card | Minimal card, off-white | "HELLO MY NAME IS"-style slap sticker, tilted |
| Quick look | `option-a-wrap-halo/wrapshap-overview.jpg` | `option-b-graffiti/wrapshap-overview.jpg` |

## Colour

Both options share the same core palette. Option B adds two paint colours.

| Token | HEX | CMYK | Used in |
|---|---|---|---|
| Wrap Black (large solids) | `#0B0B0C` | 60/40/40/100 | A, B |
| Amber (logo top) | `#ECBF30` | 10/18/90/0 | A, B |
| Orange (logo bottom) | `#F39200` | 0/50/100/0 | A, B |
| Signal (accent type) | `#F0A616` | 5/36/96/0 | A, B |
| Paper (write-on card) | `#F4F2EE` | 2/2/4/0 | A |
| Burnt (base splat) | `#B8480A` | 10/78/100/8 | B |
| Chalk (off-white paint) | `#F2EFE8` | 3/3/7/0 | B |
| Small grey and black type | — | black ink only (K) | A, B |

## What's in each option folder

| Folder | What | Files |
|---|---|---|
| `00-design-system/` | One-page system sheet (A3), plus the logo on its own as a vector file | `.ai` `.pdf` `.jpg`, `wrapshap-logo-vector.ai/.pdf` |
| `01-envelope/` | 163 × 205 mm, front and back, 3 mm bleed | `.ai` (both sides on one canvas, with crop marks), `-print.pdf` (page 1 front, page 2 back), `.jpg` per side |
| `02-mat-pad/1x1/` | 250 × 250 mm and 350 × 350 mm, 3 mm bleed | `.ai` `-print.pdf` `.jpg` per size |
| `02-mat-pad/16x9/` | 400 × 225 mm and 800 × 450 mm, 3 mm bleed | `.ai` `-print.pdf` `.jpg` per size |
| `03-tshirt/` | Back print and left-chest print (sizes are on the mockup) | `.ai`, `-print.pdf`, transparent 300 dpi `.png` for DTG printing, `wrapshap-tee-mockup.jpg` |

**Send the `-print.pdf` files to the printer.** They have exact trim and bleed boxes and are in CMYK. The t-shirt files are
the exception, see below. The `.jpg` files are RGB previews cropped to the trim size.

## Read before printing or editing

- **About the `.ai` files.** They were built without Illustrator, so they are *PDF-based* `.ai` files. Illustrator
  opens them directly and every vector can be edited. They do not have Illustrator's own layers or multiple artboards:
  pieces with more than one side sit on one canvas with crop marks. The text is live, so install the fonts before editing it.
  Geist and Geist Mono are used in both options, and Big Shoulders Stencil Display is also used in B. All three are free
  on Google Fonts. Without them, Illustrator will substitute another font. The print PDFs already have the fonts embedded.
- **Everything is vector.** No PDF or AI file contains a raster image. That includes Option B's paint: every splat,
  drip and speck is a real vector shape, so it stays sharp at 800 mm.
- **Envelope construction.** These are flat front and back panels, like your original file. Flaps, glue areas and folds
  were not in the source, so get the printer's template and keep important content at least 5 mm inside the trim.
- **Rich black and small type.** Large black areas are 60/40/40/100. Small grey and black text is black ink only, which avoids
  colour fringing if the printing plates don't line up perfectly. The glow and fade effects use transparency. Modern print
  workflows (PDF/X-4) handle this, but ask for a hard proof if the printer flattens transparency.
- **Option B fine specks.** The smallest spray specks on the envelope are about 0.12 mm across. Offset printing may drop
  some of them, which is fine because they are texture. The t-shirt specks are at least about 0.9 mm across so they hold on fabric.
- **Mat pads.** These are usually dye-sublimation printed. If the printer wants RGB, give them the `.jpg`
  (150–200 dpi at full size) or let them convert the PDF. The printer cuts the corner radius and stitches the edges.
- **T-shirt.** The artwork is RGB on a transparent background, which suits DTG printing. It uses solid ink only.
  A's rings get thinner instead of fading, and B's paint is flat colour, because transparency prints badly on fabric.
  For screen printing, the logo's gradient needs a halftone or simulated-process separation, which screen printers handle routinely.

## Decisions I made that you may want to change

- **Mat pad sizes** weren't specified. I chose 250 and 350 mm for 1:1, and 400 × 225 and 800 × 450 mm for 16:9.
- **Copy** is unchanged from your envelope, including the "This device belongs to" Name and Number fields. I did **not** add a
  website or social handles because I don't know them.
- **Option B's paint is generated from a fixed seed.** Each splat is built from a seed number. Change the seed in
  `source/design_b.py` to get a different throw with the same style.

## Rebuilding (optional)

`source/` holds the generator. Layouts are written as HTML/SVG in millimetres, Chromium prints them to vector PDF,
then the original logo is placed and the colour is converted to CMYK. You need Python 3 (PyMuPDF, Pillow),
Node with Playwright, and the font TTFs in a `fonts/` folder next to `source/`.

- Option A: `design.py` → `render.mjs` → `post.py` → `mockup.py` → `export.py <repo> a`
- Option B: `design_b.py` → `JOBS=jobs_b.json SLOTS=slots_b.json node render.mjs` → the same env vars with `post.py` → `PREFIX=b- mockup.py` → `export.py <repo> b`
