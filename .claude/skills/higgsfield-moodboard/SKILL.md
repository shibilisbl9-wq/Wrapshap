---
name: higgsfield-moodboard
description: Build a full brand moodboard as a single responsive HTML artifact from a reference image (logo, Higgsfield-generated image, or brand sheet). Generates the photography, brush/graffiti kit, cut-outs and mockups on Higgsfield, then sets the posters, colour, type, logo colourways and house rules live in HTML. Use when the user hands over a reference image or logo and asks for a moodboard, brand direction, key visuals, "board", or "same as the Wrapshap moodboard".
---

# Higgsfield moodboard

Reproduces the "Wrapshap Loud & Exact" moodboard: one long, scrolling HTML page where
generated images carry the photography and mockups, and everything typographic is set
live in HTML/SVG (never baked into images).

## 0. Before generating anything
1. Read `anthropic-skills:higgsfield-pipeline` (upload sequence, model choice, cost preflight, failure modes).
2. Upload the user's reference image(s) first (`media_upload_widget` for attachments, `media_import_url` for links). Always pass the returned `media_id`, never raw URLs.
3. Extract from the reference: palette (hex), logo shape, vibe words, audience/market, and any plan or brief the user supplied. Pull the brand's own risk list (e.g. banned claims, logo defects) from the brief; it becomes the "Don't" rules.
4. Run a cost quote/preflight and tell the user the credit total. Confirm before a large batch.

## 1. Write the direction (before any image)
Settle, in plain words:
- **One-line idea** in the form "X outside. Y inside." (Wrapshap: "Loud outside. Exact inside.")
- **Three pillars** (energy / craft / roots), each with a one-word shout.
- **Palette**: 2 leading colours + black, with area ratios (Wrapshap: yellow 40 / white 35 / ink 20 / tint 5), flat, no gradients.
- **Type**: one variable family used at two widths (condensed italic "shout", wide upright "statement") plus a mono for specs/proof.
- **Hero device**: the one repeated gesture (Wrapshap: phone pushed at a 14mm lens).
- **Casting + wardrobe rule**: all ages, wardrobe limited to the palette on seamless white.

## 2. Generate on Higgsfield (batch tools, `jobs_wait`, then one `show_generation_by_ids`)
| Asset | Model | Notes |
|---|---|---|
| Photography, ~10-12 frames (hero pose, privacy gesture, macro detail, top-down, grid, kiosk/space) | `nano_banana_2`, 2K, 9:16 mostly | Reference image attached. Wardrobe locked to palette, white seamless, one hard shadow. Name the lens and angle in every prompt. |
| Brush / graffiti kit (crown, strike, circle, arrow, sparkle, burst, splatter, smiley) in black AND palette-colour | `gpt_image_2_5` | One sheet per colour on plain background, then `remove_background` so each mark is a transparent webp. |
| Hero cut-outs (one per poster) | `remove_background` on the chosen photos | Export webp with alpha. |
| Mockups (billboard, packaging, sticker sheet, space) | `gpt_image_2_5` | Pass the new logo colourway as reference so the mark is correct. |

Rules: use the model the user or skill names, do not let presets hijack; check each result with `show_generation_by_ids` before building on it; reroll only the failures; never reroll for a physics glitch more than once without changing the prompt. Download results into `assets/` (brush, logos) and `img/` (photos, cut-outs, mockups).

## 3. Logo colourways
Redraw or recolour the logo flat as SVG: primary on white, black on yellow (accent), on black, white on accent. Fix anything the brief flags as a defect (Wrapshap: six-point stars become four-point sparkles).

## 4. Build the page (single HTML, tokens on `:root`)
Section order, matching the Wrapshap board:
1. **Top bar**: logo + 3 meta labels.
2. **Hero artboard** (16:9, container-query units `cqw` so it scales as one picture; reflows to 4:5 under 700px): big statement with the key word struck out in brush, cut-out hero, spinning SVG sticker, kicker copy.
3. **Idea band** (accent background): big line with one word outlined, three pillars.
4. **The board**: 12-column bento of photo tiles with white mono "art director" notes pinned on each; two solid-colour text tiles; brush marks overlaid on tiles. Collapses to 2 columns under 760px.
5. **Six posters** (9:16 `cqw` artboards): one giant shout word, cut-out breaking in front of it, struck "almost"-style word, footer with promise left and logo right. Include 2 device posters built in JS/SVG (text-on-a-spiral, radial stopwatch of 60 bars with arched text) plus a notes row explaining each rule.
6. **Colour**: swatch strip with usage % and a ratio bar.
7. **Type**: four spec cards (shout / statement / mono proof / body).
8. **Kit**: four logo colourways + eight brush-mark cards, each with a one-line usage rule.
9. **Applications**: mockups grid.
10. **House rules**: black section, Do / Don't lists with mono labels.
11. **Credits**: state which models made what, and that people are AI references, not final talent.

Fonts via Google Fonts (e.g. Archivo variable with `wdth`, JetBrains Mono). Support dark/light only if the board needs it; the Wrapshap board is a fixed light page. Respect `prefers-reduced-motion` for the spinner. Mobile 16px gutters, no horizontal scroll.

## 5. Publish
Load `artifact-design`, write the HTML plus `assets/` and `img/` via the `files` map, publish with the Artifact tool, return the link. Ask before making it public.

## Checks before handing over
- No image contains baked-in type except the logo and mockups.
- Every brush mark has a job (points, strikes, circles, crowns); max two per layout.
- Banned claims and logo defects from the brief appear in the Don't list and are actually absent from the page.
- Layout verified at desktop and ~390px width.
