# Wrapshap: visual system v1.0

This is a redesign of the Wrapshap device envelope, plus mat pads and a t-shirt built on the same system.
For a quick look at everything, open `wrapshap-overview.jpg`.

## The idea

The old envelope used low-contrast paint splatters that looked busy and a bit cheap. The new system keeps
the **original logo artwork exactly as supplied** and the black base. Everything around the logo is rebuilt:

- **Wrap Halo** is the main graphic. It is a set of rounded "device" outlines that step out from the logo like
  layers of protection. The colour runs amber to orange and fades as the rings get further from the logo.
- **Frame**: precision corner ticks and four labels in Geist Mono: *Stay wrapped · Stay protected ·
  Invisible protection · Made for your device*.
- **Type**: Geist (display and body) and Geist Mono (labels). Both are free from Google Fonts.
- **Colour** (full specs are in `00-design-system/`):

| Token | HEX | CMYK |
|---|---|---|
| Wrap Black (large solids) | `#0B0B0C` | 60/40/40/100 |
| Amber (logo top) | `#ECBF30` | 10/18/90/0 |
| Orange (logo bottom) | `#F39200` | 0/50/100/0 |
| Signal (accent type) | `#F0A616` | 5/36/96/0 |
| Paper (write-on card) | `#F4F2EE` | 2/2/4/0 |
| Small grey/black type | — | K-only |

## Files

| Folder | What | Files |
|---|---|---|
| `00-design-system/` | One-page system sheet (A3). Also the logo on its own as a clean vector file | `.ai` `.pdf` `.jpg`, `wrapshap-logo-vector.ai/.pdf` |
| `01-envelope/` | 163 × 205 mm, front + back, 3 mm bleed | `.ai` (both sides on one canvas, with crop marks), `-print.pdf` (page 1 front, page 2 back), `.jpg` per side |
| `02-mat-pad/1x1/` | 250 × 250 mm and 350 × 350 mm, 3 mm bleed | `.ai` `-print.pdf` `.jpg` per size |
| `02-mat-pad/16x9/` | 400 × 225 mm and 800 × 450 mm, 3 mm bleed | `.ai` `-print.pdf` `.jpg` per size |
| `03-tshirt/` | Back print 300 × 268 mm and left-chest logo 90 mm | `.ai`, `-print.pdf`, transparent 300 dpi `.png` for DTG, `wrapshap-tee-mockup.jpg` |

**Send the `-print.pdf` files to the printer.** Each one has an exact TrimBox and BleedBox and is CMYK
(the t-shirt files are the exception, see below). The `.jpg` files are RGB previews cropped to trim size.

## Read before printing or editing

- **About the `.ai` files.** They were built without Illustrator, so they are *PDF-based* `.ai` files. Illustrator
  opens them directly and every vector can be edited. They do not have Illustrator's own layers or multiple
  artboards. Multi-piece items sit on one canvas with crop marks. The text is live, so install **Geist** and
  **Geist Mono** before you edit it, or Illustrator will substitute another font. The print PDFs have the fonts embedded.
- **Everything is vector.** There are no raster images in any PDF or AI file, and the logo is the original
  CMYK artwork from your file.
- **Envelope construction.** Like the original file, these are flat front and back panels. Flaps, glue areas and
  folds were not in the source file, so ask the printer for their dieline and keep important content 5 mm or more inside the trim.
- **Rich black.** Large black areas are 60/40/40/100. Small grey and black text is black ink only, which avoids
  colour fringing when the plates don't line up perfectly. The rings and glow use transparency. Any modern
  print workflow (PDF/X-4) handles this, but ask for a hard proof if the printer flattens transparency.
- **Mat pads.** Mouse pads are usually dye-sublimation printed. If your printer asks for RGB, they can use the
  `.jpg` files (150 to 200 dpi at full size) or convert the PDF. Corner radius and stitched edges are cut by the printer.
- **T-shirt.** The artwork is RGB with a transparent background, which suits DTG printing. The rings use solid
  ink with lines that thin from 1.3 mm to 0.55 mm instead of fading, because fades print badly on fabric.
  If you screen print, the logo's gradient needs a halftone or simulated-process separation. That is normal for screen printers.

## Decisions I made that you may want to change

- **Mat pad sizes** weren't specified. I chose 250 and 350 mm for 1:1, and 400 × 225 and 800 × 450 mm for 16:9. The layouts
  are generated from the short side, so other sizes can be regenerated easily.
- **Copy** is unchanged from your envelope. I kept the "This device belongs to" card with Name and Number.
  I did **not** add a website, social handles or contact details because I don't know them. Add them if you want them.
- **Paper card** is a very light warm tint (2/2/4/0). For plain paper white, set it to 0/0/0/0.

## Rebuilding (optional)

The `source/` folder contains the generator: HTML/SVG laid out in millimetres, printed to vector PDF by
Chromium, then the original logo is placed and colours are converted to CMYK. It needs Python 3 (PyMuPDF,
Pillow), Node with Playwright, and the Geist TTFs in a `fonts/` folder next to `source/`. The run order is
`design.py` → `render.mjs` → `post.py` → `mockup.py` → `export.py <output dir>`.
