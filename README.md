# Wrapshap: envelope redesign, mat pads, polo shirt, graffiti t-shirt and stationery

This repo has five envelope design directions. Options A and B are each a full set of an envelope, four
mat pads and a design-system sheet. The polo shirt and the stationery (letterheads and business cards for
Pakistan and the UAE) are in Option A, because they use A's Wrap Halo design. The graffiti t-shirt is in
Option B. Options C, D and E are a trio built to match the three columns of your reference image exactly
(icon pattern / vibrant gradient / graffiti street) so you can pick one — they're envelope-only concept
mockups, not full production sets. See "What's in each option folder" for what that means in practice.
All five use the **original Wrapshap logo artwork unchanged**. It was taken as vector straight out of the
supplied envelope file.

| | Option A: Wrap Halo | Option B: Graffiti | Option C: Icon Pattern | Option D: Vibrant/Modern | Option E: Street Pop |
|---|---|---|---|---|---|
| Folder | `option-a-wrap-halo/` | `option-b-graffiti/` | `option-c-icon-pattern/` | `option-d-vibrant-modern/` | `option-e-street-pop/` |
| Mood | Clean, premium, tech | Street, spray-painted | Fun, scattered, youthful | Premium, fluid, modern | Loose, playful, hand-drawn |
| Main graphic | Thin rounded "device" outlines around the logo, fading outward | Spray-can textures: grainy airbrush strokes, an off-white sprayed swash with drips behind the logo, and an orange dry-brush stripe under the headline | A seeded scatter of hand-drawn device icons (phone, laptop, bolt, "W" mark, crown, smiley, sparkle) — solid black on Amber for the front, tone-on-tone on Wrap Black for the back | Soft organic "lava lamp" blobs in a warm Amber → Orange → Rose gradient, bleeding from the corners on Wrap Black | A loose scatter of hand-drawn doodles (crown, smiley, sparkle, bolt, X marks, arrow) plus rough Amber paint smears bleeding off two corners, on Wrap Black |
| Headline type | Geist SemiBold | Big Shoulders Stencil (Black, all caps), set in black on the dry-brush stripe | Geist ExtraBold, all caps, straight on the Amber ground | Geist SemiBold, top-right, white | Geist ExtraBold, top-left, white |
| Ownership card | Minimal card, off-white | "HELLO MY NAME IS"-style slap sticker, tilted | Minimal card, white | Minimal card, off-white | Minimal card, off-white |
| Quick look | `option-a-wrap-halo/wrapshap-overview.jpg` | `option-b-graffiti/wrapshap-overview.jpg` | `option-c-icon-pattern/wrapshap-overview.jpg` | `option-d-vibrant-modern/wrapshap-overview.jpg` | `option-e-street-pop/wrapshap-overview.jpg` |

Options C and E are both "street/graffiti" in mood but come from different references: B was built earlier
from spray-can texture references (airbrush, dry brush); E was built fresh to match this reference image's
own graffiti column (loose scattered doodles, plain bold headline, corner paint smears). They're deliberately
different executions of a similar mood — compare both if that's the direction you want.

## Colour

All five options share the same core palette. Option B adds one paint colour, Chalk; Option D adds one
accent, Rose (see its row below — a warm colour chosen to extend the logo's own amber-to-orange gradient,
see "Decisions" for why). Option C and E use only tokens already in this table — nothing new — so they
aren't listed in the "Used in" column.

| Token | HEX | CMYK | Used in |
|---|---|---|---|
| Wrap Black (large solids) | `#0B0B0C` | 60/40/40/100 | A, B, C, D, E |
| Amber (logo top) | `#ECBF30` | 10/18/90/0 | A, B, C, D, E |
| Orange (logo bottom) | `#F39200` | 0/50/100/0 | A, B, C, D, E |
| Signal (accent type) | `#F0A616` | 5/36/96/0 | A |
| Paper (write-on card) | `#F4F2EE` | 2/2/4/0 | A |
| Chalk (off-white spray paint) | `#F2EFE8` | 3/3/7/0 | B |
| Rose (gradient accent) | `#F2545B` | 0/74/54/0 | D |
| Small grey and black type | — | black ink only (K) | A, B, C, D, E |

## What's in each option folder

| Folder | What | Files |
|---|---|---|
| `00-design-system/` | One-page system sheet (A3), plus the logo on its own as a vector file | `.ai` `.pdf` `.jpg`, `wrapshap-logo-vector.ai/.pdf` |
| `01-envelope/` | 163 × 205 mm, front and back, 3 mm bleed | `.ai` (both sides on one canvas, with crop marks), `-print.pdf` (page 1 front, page 2 back), `.jpg` per side |
| `02-mat-pad/1x1/` | 250 × 250 mm and 350 × 350 mm, 3 mm bleed | `.ai` `-print.pdf` `.jpg` per size |
| `02-mat-pad/16x9/` | 400 × 225 mm and 800 × 450 mm, 3 mm bleed | `.ai` `-print.pdf` `.jpg` per size |
| `03-polo-shirt/` (Option A only) | Black polo with orange collar and cuffs. Front: logo only, 85 mm, left chest. Back: Wrap Halo, logo and tagline, 282 × 236 mm | `.ai`, `-print.pdf` (page 1 back, page 2 front), transparent 300 dpi `.png` per print, `wrapshap-polo-mockup.jpg` |
| `03-t-shirt/` (Option B only) | Graffiti tee in black and white. Back: the logo with an outline and drips, a crown, a smiley, sparkles, a handwritten tagline and an orange swoosh, 320 × 279 mm. Front: a small version of the logo piece on the left chest, 108 × 60 mm. Inside neck: crown and tagline, 56 × 30 mm. Woven sleeve/hem label, 20 × 32 mm | `.ai` and `-print.pdf` per shirt colour (pages: back, chest, neck, label), transparent 300 dpi `.png` per print, `wrapshap-tee-mockup.jpg` |
| `04-stationery/pakistan/` and `04-stationery/uae/` (Option A only) | A4 letterhead, 90 × 50 mm business card and A5 landscape receipt voucher (210 × 148 mm) for each office, with that office's address, web and email. The voucher has the same fields as the supplied reference voucher, in rupees (Pakistan) or dirhams (UAE) | `.ai` (the card has front and back on one canvas), `-print.pdf` (CMYK, 3 mm bleed; card page 1 is the front, page 2 the back), `.jpg` previews |

**Send the `-print.pdf` files to the printer.** They have exact trim and bleed boxes and are in CMYK. The polo files are
the exception, see below. The `.jpg` files are RGB previews cropped to the trim size.

**Options C, D and E are envelope-only, and mockup-only.** Each is a `01-envelope/` with just
`wrapshap-envelope-front.jpg` and `wrapshap-envelope-back.jpg` (300 dpi, RGB, cropped to the 163 × 205 mm
trim), plus the same `wrapshap-overview.jpg` quick-look as A and B. There's no mat pad, design system, `.ai`,
or `-print.pdf` for any of the three — they were built to let you pick a direction, the way your reference
image did, not to send to a printer. Whichever of C, D or E you pick, say so and I'll take it through the
same production pass as A and B: CMYK `-print.pdf`, `.ai`, a design-system sheet, mat pads, and the rest of
the deliverable set.

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
- **Graffiti tee: print.** The artwork is RGB, 100% vector, and all type is converted to outlines, so no fonts are needed.
  The logo is the original, unchanged. The outline and drips around it are an exact offset of the logo's shape. On the black tee,
  the thin dark line between the logo and the white outline is left unprinted, so the shirt shows through. The finest lines are
  about 0.9 mm (the neck print), which DTF and DTG handle. For screen printing, the logo gradient needs a halftone separation.
- **Graffiti tee: label.** The orange crown label is drawn as a woven label (folded loop, crown on both halves). Give it to
  the label maker as a reference, not as a print file.
- **Polo: collar and cuffs are part of the garment, not the print.** Order black polos with an orange knit collar and cuffs.
  Ask the supplier for the colour closest to the brand Orange `#F39200` (roughly Pantone 144 C) and check a physical swatch.
- **Polo: embroidery.** Polos are often embroidered. The logo's gradient can't be stitched as it is: an embroidery digitiser
  will turn it into 2–3 thread colours for the chest logo. The thin back rings are too fine to embroider, so print the back
  (DTF or DTG) even if you embroider the front. For screen printing, the logo gradient needs a halftone separation.
- **Option C, D and E files are RGB screen mockups, not print files.** No CMYK conversion, no trim/bleed `.ai`, no
  fonts-embedded PDF — just the placed logo and a JPG export, so nothing here is ready for a printer yet.

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
- **Receipt voucher.** It keeps every field of the reference voucher you sent. I changed four things. (1) The unlabelled
  box next to the amount is now labelled "Being payment for". (2) The reference's real-estate note (deposit not refundable
  after a deal is cancelled) doesn't apply to Wrapshap, so it was replaced with a neutral line: "valid only when signed by an
  authorised Wrapshap representative; cheques are subject to realisation". Send your own terms if you want them there.
  (3) "Client / Agent Signature" became "Customer / Authorised Signature". (4) The phone line and social handles were left
  out because they weren't supplied. A5 landscape suits standard carbonless (NCR) receipt books. The printer adds the running
  number, perforation and binding stub.
- **Letterhead.** It is designed for pre-printed paper (offset or digital print). The body area is left white for typing or
  printing letters. If you also want a Word template with the same header and footer for typing letters, ask.
- **Graffiti tee.** It follows your references, but the wordmark is your real logo, not redrawn lettering. The crown,
  smiley and tagline handwriting (Kalam font) come from the references and are not part of your existing brand. Drop them
  if you don't want a crown as a brand mark.
- **Shirts.** Earlier, the t-shirts from both options were replaced by the polo. The new graffiti tee (Option B,
  `03-t-shirt/`) was added after that. The polo is still in Option A, and the old t-shirts are in the git history.
- **Option B changed direction.** The first version used cartoon paint splats. It was replaced with spray-can textures
  after your references. The old version is still in the git history if you want it back.
- **Options C, D and E are a matched trio built from your reference image, and all three are envelope-only concept
  mockups.** Your reference showed three style columns (icon pattern, vibrant gradient, graffiti street); C, D and E
  each match one, so you can compare all three and pick. They're envelope-only because a background treatment
  (a pattern, a gradient, a paint smear) doesn't by itself tell me how to extend to a design-system sheet, mat pad,
  t-shirt or stationery — say which one you want taken further and I'll build the rest of the set the way A and B
  were built.
- **Option C (Icon Pattern) reuses B's crown/smiley/sparkle.** The reference's icon-pattern envelope put the wordmark
  on a flat yellow background; your real logo is amber-to-orange with a white-and-orange rim, so I kept it on Amber
  (a token you already had) rather than inventing a new yellow — the rim is what keeps it readable, not the background.
  The icon set (phone, laptop, bolt, a "W" mark, plus the crown/smiley/sparkle from Option B's references) is generated
  by seeded rejection-sampling in `source/handdrawn.py` + `source/design_c.py`, so it's reproducible and easy to
  re-seed for a different scatter. Like Option B's crown and smiley, treat these as optional: drop them if a plain
  device-icon set (phone/laptop/bolt/"W") reads more on-brand to you than the playful ones.
- **Option D (Vibrant/Modern) shifts the reference's gradient warm, and adds a new colour, Rose.** The reference's
  vibrant envelope uses a cool blue → purple → pink gradient; your logo is warm amber-to-orange, and a cool gradient
  behind it would fight the logo rather than frame it, the same reasoning as Option C's background. This keeps the
  reference's *shape* language (soft overlapping blob forms) but shifts the palette warm: Amber → Orange → Rose (a new
  coral-red token, `#F2545B`), so it reads as one family with the logo. If you'd rather have the literal cool gradient
  even though it clashes with the current logo colours, tell me — that's a genuine option, just a different one than
  what's built here.
- **Option E (Street Pop) is a new graffiti take, separate from Option B.** Both are "street" in mood, but B was built
  earlier from different, texture-heavy references (spray-can airbrush and dry-brush). E was built fresh to match
  *this* reference's own graffiti column: a plain bold headline top-left, loose hand-drawn doodles scattered around the
  logo, and rough paint smears bleeding off two corners, with no spray texture engine involved. Compare both if you
  want the street/graffiti mood but aren't sure which execution you prefer.

## Rebuilding (optional)

`source/` holds the generator. Layouts are written as HTML/SVG in millimetres, Chromium prints them to vector PDF,
then the original logo is placed and the colour is converted to CMYK. Option B's textures are generated in
`spray.py` and placed under the vector artwork as 1-bit masks. Options C, D and E's icon scatters, blobs and paint
smears are generated directly in `source/handdrawn.py` (numpy only, no image masks) and used by `design_c.py`,
`design_d.py` and `design_e.py`. You need Python 3 (PyMuPDF, Pillow, NumPy, SciPy), Node with Playwright, and the
font TTFs in a `fonts/` folder next to `source/`.

- Option A: `design.py` → `render.mjs` → `post.py` → `export.py <repo> a`
- Option B: `design_b.py` → `JOBS=jobs_b.json SLOTS=slots_b.json node render.mjs` → the same env vars with `post.py` → `export.py <repo> b`
- Options C, D, E (envelope mockups only, RGB): `design_c.py` / `design_d.py` / `design_e.py` → `JOBS=jobs_<c|d|e>.json SLOTS=slots_<c|d|e>.json node render.mjs` → the same env vars with `post_mockup.py` (places the logo and sets trim/bleed boxes, no CMYK step) → copy `source/preview/<c|d|e>-envelope-*.jpg` into the matching `option-*/01-envelope/`
- Stationery: `stationery.py` → `JOBS=jobs_stat.json SLOTS=slots_stat.json node render.mjs` → the same env vars with `post.py` → `export.py <repo> stationery`
- Graffiti tee: `tee.py` → `JOBS=jobs_tee.json SLOTS=slots_tee.json node render.mjs` → the same env vars with `post.py` → `tee_mockup.py` → `export.py <repo> tee` (needs Kalam 700 and Geist 600 TTFs)
- Receipt voucher: `voucher.py` → `JOBS=jobs_voucher.json SLOTS=slots_voucher.json node render.mjs` → the same env vars with `post.py` → `export.py <repo> voucher`
- Polo: `polo.py` → `JOBS=jobs_polo.json SLOTS=slots_polo.json node render.mjs` → the same env vars with `post.py` → `polo_mockup.py` → `export.py <repo> polo`
