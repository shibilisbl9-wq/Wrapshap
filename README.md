# Wrapshap: envelope redesign, mat pads, polo shirt and stationery

This repo has two design options. Each one is a set of an envelope, four mat pads and a design-system sheet.
The polo shirt and the stationery (letterheads and business cards for Pakistan and the UAE) are in Option A,
because they use A's Wrap Halo design.
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
| `03-polo-shirt/` (Option A only) | Black polo with orange collar and cuffs. Front: logo only, 85 mm, left chest. Back: Wrap Halo, logo and tagline, 282 × 236 mm | `.ai`, `-print.pdf` (page 1 back, page 2 front), transparent 300 dpi `.png` per print, `wrapshap-polo-mockup.jpg` |
| `04-stationery/pakistan/` and `04-stationery/uae/` (Option A only) | A4 letterhead and 90 × 50 mm business card for each office, with that office's address, web and email | `.ai` (the card has front and back on one canvas), `-print.pdf` (CMYK, 3 mm bleed; card page 1 is the front, page 2 the back), `.jpg` previews |

**Send the `-print.pdf` files to the printer.** They have exact trim and bleed boxes and are in CMYK. The polo files are
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
- **Polo: print.** The artwork is RGB on a transparent background, which suits DTG or DTF printing. The rings fade out
  as they move away from the logo, but that fade uses solid ink colours rather than transparency, which prints badly on
  fabric. The rings also get thinner, from 1.2 mm to 0.6 mm. In the `.ai`, the dark panel behind the artwork only shows
  the shirt colour and is not printed.
- **Polo: collar and cuffs are part of the garment, not the print.** Order black polos with an orange knit collar and cuffs.
  Ask the supplier for the colour closest to the brand Orange `#F39200` (roughly Pantone 144 C) and check a physical swatch.
- **Polo: embroidery.** Polos are often embroidered. The logo's gradient can't be stitched as it is: an embroidery digitiser
  will turn it into 2–3 thread colours for the chest logo. The thin back rings are too fine to embroider, so print the back
  (DTF or DTG) even if you embroider the front. For screen printing, the logo gradient needs a halftone separation.

## Decisions I made that you may want to change

- **Mat pad sizes** weren't specified. I chose 250 and 350 mm for 1:1, and 400 × 225 and 800 × 450 mm for 16:9.
- **Copy** is unchanged from your envelope, including the "This device belongs to" Name and Number fields. I did **not** add a
  website or social handles because I don't know them.
- **Option B's spray is generated from a fixed seed.** Every stroke, swash and brush is built by code (`source/spray.py`)
  from a seed number. Change the seed in `source/design_b.py` to get a different spray in the same style.
- **Business cards have placeholders.** The name ("Full Name"), job title ("Designation") and phone number
  (`+92 3XX XXX XXXX` / `+971 5X XXX XXXX`) are placeholders because they weren't supplied. Replace them in the `.ai`
  file for each person before printing. The address, web and email are exactly as supplied. On the UAE address,
  "UAE" was added after "Dubai".
- **Letterhead.** It is designed for pre-printed paper (offset or digital print). The body area is left white for typing or
  printing letters. If you also want a Word template with the same header and footer for typing letters, ask.
- **Shirts.** At your request, the t-shirts from both options were replaced by the single polo. The old t-shirt files
  are still in the git history.
- **Option B changed direction.** The first version used cartoon paint splats. It was replaced with spray-can textures
  after your references. The old version is still in the git history if you want it back.

## Rebuilding (optional)

`source/` holds the generator. Layouts are written as HTML/SVG in millimetres, Chromium prints them to vector PDF,
then the original logo is placed and the colour is converted to CMYK. Option B's textures are generated in
`spray.py` and placed under the vector artwork as 1-bit masks. You need Python 3 (PyMuPDF, Pillow, NumPy, SciPy),
Node with Playwright, and the font TTFs in a `fonts/` folder next to `source/`.

- Option A: `design.py` → `render.mjs` → `post.py` → `export.py <repo> a`
- Option B: `design_b.py` → `JOBS=jobs_b.json SLOTS=slots_b.json node render.mjs` → the same env vars with `post.py` → `export.py <repo> b`
- Stationery: `stationery.py` → `JOBS=jobs_stat.json SLOTS=slots_stat.json node render.mjs` → the same env vars with `post.py` → `export.py <repo> stationery`
- Polo: `polo.py` → `JOBS=jobs_polo.json SLOTS=slots_polo.json node render.mjs` → the same env vars with `post.py` → `polo_mockup.py` → `export.py <repo> polo`
