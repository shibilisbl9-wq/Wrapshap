# Wrapshap: envelope redesign, mat pads, polo shirt, graffiti t-shirt and stationery

> **New visual direction: Option F (campaign board in the MÜLER style).** This is the direction you picked.
> It's a full brand board rebuilt from the MÜLER reference with the real Wrapshap logo, plus a hero banner and five
> 1080 × 1920 stories. See [Option F](#option-f-campaign-müler-style) below. Options A–E are the earlier
> envelope work and are unchanged.

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

## Option F: Campaign (MÜLER style)

Folder `option-f-campaign/`. Same structure as the MÜLER board: a hero with giant type behind a jumping model,
five posters, three tiles (product in hand, group selfie, face close-up), and a guideline strip (colour, type,
graphic elements, textures, mood). Two things were added on top of MÜLER: **your sticker set** is slapped onto
the hero, posters and tiles and shown in full on a blue sticker strip, and every background carries a faint
**tone-on-tone doodle pattern**. The logo is the **original Wrapshap artwork**, never redrawn, and always
**flat, with no texture or grunge**. The one-colour versions are the original letter shapes filled flat (see
`make_logos.py`).

| File | What |
|---|---|
| `wrapshap-brand-board.jpg` | The full board, 3072 × 4608 (2:3, same format as the reference) |
| `01-hero/wrapshap-hero-banner.jpg` | The hero on its own, 3072 × 1350 |
| `02-stories/wrapshap-story-0X-….jpg` | The five posters as 1080 × 1920 Instagram/WhatsApp stories: clear, privacy, tuff, matte, 60 sec |
| `03-logo/` | Logo SVGs: black, white, black with the white sticker rim, and the full-colour original |
| `04-kit/` | The hand-made graphic kit as transparent PNG masks (brushes, crown, smiley, stars, scribbles, arrow, grunge texture). Recolour them to any palette colour. `doodle-pattern-1080.png` is the background doodle pattern on its own (black on transparent). Use it at about 6–8% opacity on paper/white, or tinted darker yellow on yellow |
| `05-stickers/` | Your sticker set (crown, CUT IN 60 SEC, EXACT FIT, wrapshap logo, NO MORE ALMOST., smiley, sparkle, WE GOT YOU.) as transparent WebPs. Taken from your earlier board's assets, unchanged. The logo sticker uses the real logo |

### Colour

| Token | HEX | Role |
|---|---|---|
| Wrap Yellow | `#FFE014` | Lead colour: backgrounds, brush strokes |
| Paper | `#F7F7F2` | Main background |
| Ink | `#0E0E0E` | Logo, handwriting, doodles |
| Graphite | `#4B4B4B` | Secondary text |
| Mist | `#D5D5D0` | Grey brush, dividers |
| Pop Pink | `#FF3DA5` | Pop |
| Pop Cobalt | `#2350F0` | Pop, and the one non-yellow poster background |
| Pop Green | `#19B85B` | Pop |
| Pop Violet | `#7C4DFF` | Pop |
| Logo Orange | `#F39200` | Pop (from the logo) |

Type: the Wrapshap logo for display, **DM Sans** for small text, **Permanent Marker** for the handwritten lines.
Both are free on Google Fonts.

### Decisions I made that you may want to change

- **The big logo is one colour (black, or white on colour), not the orange full-colour logo.** This is the
  main reason MÜLER feels subtle and your first Wrapshap version (the orange logo everywhere) felt loud: an amber
  logo on yellow backgrounds is just more yellow. The full-colour logo stays for packaging, signage and anywhere it
  appears small. If you want the orange logo big anyway, it's a one-line change per placement in `build.py`.
- **More colour, with yellow still leading. Rule: "one pop per piece."** Every piece is yellow + black + paper, plus
  one pop colour taken from the model's outfit (the pink jacket gets pink doodles, the green tracksuit gets green).
  The **tuff** poster is on cobalt blue to break the all-yellow/white row. Swap it back to yellow or white if that's
  too far from MÜLER.
- **The hero uses a wide, low jump (legs split sideways), centred under the full-width logo.** With the earlier
  tall jumping pose, a centred model hid three letters. The wide pose keeps her body below the letters, so like
  MÜLER she hides about one ("p"), and the whole logo still reads. This photo was cut out with a free local
  model (rembg + BiRefNet), no credits.
- **Posters are 9:16** (MÜLER's are a bit taller), so each one is also a ready-to-post story.
- **Where the stickers went.** Hero: NO MORE ALMOST. Each poster carries exactly one sticker in the same corner
  (top right under the logo; top left on 60 sec so it doesn't cover his hand): sparkle (clear), WE GOT YOU.
  (privacy), smiley (tuff), EXACT FIT (matte), CUT IN 60 SEC (60 sec). The tiles have none, to keep them clean.
  The full set is on the blue strip.
- **Background doodles are sparse and faint**: only crowns, smileys, stars and asterisks, about 5% black on
  paper/white and darker yellow on yellow. An earlier denser version, with scribbles and arrows too, made the
  surfaces look dirty. Stronger or weaker is a one-line change (`BG_TONE` in `build.py`).
- **Cleanliness rules applied after a critique pass:** every poster uses one template (label, logo, one brush,
  a big model bleeding off the bottom, one handwritten line in the lower third, one pop doodle, one sticker).
  The handwriting is condensed like marker lettering, and all photos share one grade. The guide strip was thinned
  to the MÜLER layout (no hex labels on the board, 2 × 2 textures). The HEX codes are in the table above.
- **Copy comes from your earlier work, not invented.** The product names (clear, privacy, tuff, matte, 60 sec) and
  lines ("NO MORE ALMOST.", "EXACT FIT.", "LOUD OUTSIDE. EXACT INSIDE.", "EVERY PHONE FALLS.") come from your previous
  posters and stickers. **Check they match what you actually sell**, and the phone brand list (Apple, Samsung,
  Xiaomi, Oppo, Vivo) in the group tile.

### Read this before using the images publicly

- **The photography is AI-generated** (Higgsfield Soul 2.0). These are not real people. That's fine for a direction
  board and for pitching the look. For paid ads, the honest recommendation is a real shoot, with this board as the
  brief. AI images can hide small artefacts, and some platforms and markets expect AI imagery to be labelled.
- **Other brands' marks were removed by hand:** an Apple logo on the phone, a Nike swoosh on the tuff model's
  sneaker, Onitsuka Tiger-style stripes on the matte model's sneakers, and garbled lettering on the hero's sole.
  The phones are still recognisably iPhone-shaped, without logos. Look closely at anything before it runs as an ad.
- **These are RGB screen files, not print files.** For print (posters, kiosk wraps), say so and they'll go through
  the same CMYK/bleed pass as Options A and B.

### Rebuilding Option F

In `source/moodboard/`: `make_logos.py` → `retouch.py` → `prep_photos.py` → `extract_kit.py` → `build.py` →
`export.py`. The stickers the board uses are committed in `stickers/`. The full-size generations aren't in git (`photos_raw/` is ignored). Their Higgsfield job IDs are in
`higgsfield_jobs.json`, and the cropped photos the board actually uses are committed in `img/`, so `build.py` and
`export.py` work without them. Needs Python (PyMuPDF, Pillow, NumPy, SciPy), Node with Playwright, and DM Sans +
Permanent Marker TTFs in `fonts/` at the repo root. `retouch.py` also needs `rembg` (`pip install "rembg[cpu]"`),
which downloads the BiRefNet model (~1 GB) on first use.

## Colour (Options A–E)

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
