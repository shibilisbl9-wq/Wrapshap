# Wrapshap: envelope redesign, mat pads and t-shirt

This repo has two design options. Each one is a complete set: envelope, four mat pads, a t-shirt and a design-system sheet.
Both use the **original Wrapshap logo artwork unchanged**. It was taken as vector straight out of the supplied envelope file.

| | Option A: Wrap Halo | Option B: Graffiti |
|---|---|---|
| Folder | `option-a-wrap-halo/` | `option-b-graffiti/` |
| Mood | Clean, premium, tech | Street, spray-painted |
| Main graphic | Thin rounded "device" outlines around the logo, fading outward | Spray-can textures: grainy airbrush strokes, an off-white sprayed swash with drips behind the logo, and an orange dry-brush stripe under the headline |
| Headline type | Geist SemiBold | Big Shoulders Stencil (Black, all caps), set in black on the dry-brush stripe |
| Ownership card | Minimal card, off-white | "HELLO MY NAME IS"-style slap sticker, tilted |
| Quick look | `option-a-wrap-halo/wrapshap-overview.jpg` | `option-b-graffiti/wrapshap-overview.jpg` |

## Colour

Both options share the same core palette. Option B adds one paint colour, Chalk.

| Token | HEX | CMYK | Used in |
|---|---|---|---|
| Wrap Black (large solids) | `#0B0B0C` | 60/40/40/100 | A, B |
| Amber (logo top) | `#ECBF30` | 10/18/90/0 | A, B |
| Orange (logo bottom) | `#F39200` | 0/50/100/0 | A, B |
| Signal (accent type) | `#F0A616` | 5/36/96/0 | A |
| Paper (write-on card) | `#F4F2EE` | 2/2/4/0 | A |
| Chalk (off-white spray paint) | `#F2EFE8` | 3/3/7/0 | B |
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
- **What is vector and what is not.** Option A is 100% vector. In Option B the logo, type, drips and sticker card are
  vector. The spray textures (airbrush strokes, swash, dry brush) are grain by nature, so they are **1-bit texture masks**,
  like a scanned spray texture, each filled with one exact CMYK colour. They stay crisp at print size because there is no
  anti-aliasing to blur, and in Illustrator they appear as embedded 1-bit images you can recolour. The grain is 0.12 mm on the
  envelope and grows with the format, to about 0.33 mm on the 800 × 450 mat, so the spray texture is still visible.
- **Envelope construction.** These are flat front and back panels, like your original file. Flaps, glue areas and folds
  were not in the source, so get the printer's template and keep important content at least 5 mm inside the trim.
- **Rich black and small type.** Large black areas are 60/40/40/100. Small grey and black text is black ink only, which avoids
  colour fringing if the printing plates don't line up perfectly. That includes Option B's headline on the orange brush.
  Option A's glow and fade effects, and a scatter of fine amber specks in B, use transparency. Modern print workflows
  (PDF/X-4) handle this, but ask for a hard proof if the printer flattens transparency.
- **Option B spray grain.** Where the spray fades out, isolated grain dots are one grain cell across (0.12 mm on the
  envelope). Offset printing may drop some of them, which just reads as a softer spray falloff. Ask for a proof if the
  texture matters to you.
- **Mat pads.** These are usually dye-sublimation printed. If the printer wants RGB, give them the `.jpg`
  (150–200 dpi at full size) or let them convert the PDF. The printer cuts the corner radius and stitches the edges.
- **T-shirt.** The artwork is RGB on a transparent background, which suits DTG printing. It uses solid ink only.
  A's rings get thinner instead of fading, and B's spray is 1-bit grain in flat colour, because transparency prints badly on fabric.
  B's grain on the shirt is 0.30–0.35 mm, and the spray fades out before the edge of the print area so no hard cut-off shows.
  The finest isolated dots may not survive DTG on a black shirt, which again reads as natural spray falloff. B's headline is
  black ink on the orange stripe; a printer can knock it out to show the shirt instead.
  For screen printing, the logo's gradient needs a halftone or simulated-process separation, which screen printers handle routinely.

## Decisions I made that you may want to change

- **Mat pad sizes** weren't specified. I chose 250 and 350 mm for 1:1, and 400 × 225 and 800 × 450 mm for 16:9.
- **Copy** is unchanged from your envelope, including the "This device belongs to" Name and Number fields. I did **not** add a
  website or social handles because I don't know them.
- **Option B's spray is generated from a fixed seed.** Every stroke, swash and brush is built by code (`source/spray.py`)
  from a seed number. Change the seed in `source/design_b.py` to get a different spray in the same style.
- **Option B changed direction.** The first version used cartoon paint splats. It was replaced with spray-can textures
  after your references. The old version is still in the git history if you want it back.

## Rebuilding (optional)

`source/` holds the generator. Layouts are written as HTML/SVG in millimetres, Chromium prints them to vector PDF,
then the original logo is placed and the colour is converted to CMYK. Option B's textures are generated in
`spray.py` and placed under the vector artwork as 1-bit masks. You need Python 3 (PyMuPDF, Pillow, NumPy, SciPy),
Node with Playwright, and the font TTFs in a `fonts/` folder next to `source/`.

- Option A: `design.py` → `render.mjs` → `post.py` → `mockup.py` → `export.py <repo> a`
- Option B: `design_b.py` → `JOBS=jobs_b.json SLOTS=slots_b.json node render.mjs` → the same env vars with `post.py` → `PREFIX=b- mockup.py` → `export.py <repo> b`
