# Wrapshap shoot guide: handover to the local (desktop) chat

Written 1 Oct 2026 from the cloud session. **Status: planning and prep done. The shoot guide itself is NOT built.**
No philosophy `.md`, no PDF, no storyboard frames exist yet. Do not assume otherwise.

## 1. What the user wants

A visual guide for executing the Wrapshap content plan shoot: storyboard frames, timings, shot setups, props, schedule,
"like everything". Use the **canvas-design** skill for the layout and a **generative image** tool for frames.
The user has said to use their Mac desktop, with **Google Flow** open in Chrome, and that Flow is the image tool.
**Desktop use only** means the work happens through the Mac and Flow, not through the cloud session.

## 2. The content plan already exists. Do not rebuild it.

`WrapShap_Launch_Plan_Yellow_Edition.pdf` (repo root, 42 pages) is the plan. Read it first. Page map:

| Pages | Content |
|---|---|
| 1-8 | Direction ("No more almost"), six rules, risks, phase map, all 15 posts + 4 series in order |
| 9-13 | Phase 1: A1 Spot your almost, A2 Every phone falls, A3 Worst protector in Pakistan, A5 Name a phone we can't cut |
| 14-20 | Phase 2: B1 Something's going up at [mall], B2 Meet the squad, B3 CLEAR, B4 PRIVACY, B5 MATTE, B6 TUFF |
| 21-26 | Phase 3: C1 Opening day, C4 From worst to cut, C2 W.R.A.P.S.H.A.P, C3 Almost vs exact, C5 Stump the machine |
| 27-30 | Phase 4: D1 Rate the fit, D2 "Is it glass?", D3 The sneaky neighbour |
| 31-42 | **Factory shoot, Day 1: scripts S1-S10 with second-by-second timings, cast, props, house rules** |

The factory shoot (S1-S10, pages 32-42) is the best base for the guide because it already has timecodes.
The A/B/C/D posts only have a format and length, with no beat-by-beat timings.
Any beats written for them are **proposals** and must be labelled that way.

Shoot facts (page 32): S1-S3, S9, S10 machine block; S4-S7 table block under lights; S8 window block last.
Dialogue is Roman Urdu with burned-in English subtitles. Dummy phones are used. Real timers on every cut. No speed-ramps.

## 3. Non-negotiable rules (from the plan, pages 4-6 and 32)

1. **Logo stars.** The original logo has six-point stars in both "a"s. Many in Pakistan read that as a Star of David.
   Use only the four-point **sparkle** version. It is saved at `shoot-guide/assets/wrapshap-logo-sparkle.png`
   (RGBA, 1948x705), extracted from the deck. **Never** use the original logo or show a close-up of it with the six-point stars.
   If the image tool draws its own logo, check the stars.
2. **Claims.** Say "scratch-resistant (3H-5H)". Never "scratch-proof", "unbreakable" or "shatterproof".
   Impact talk is for TUFF only. CLEAR is "99%+ light transmittance", written "99%+", not "%99+".
   Ranges are written "0.15-0.20 mm", not reversed.
3. **No faked proof.** Real timers, no speed-ramps. "Under 60 seconds" only goes out if the take really is under 60.
   Privacy blocking at 35 degrees must happen for real in camera. No broken phones for A2.
4. **Consent.** Written permission from anyone filmed (A3 winners, C4, D1, D3). Cast a friend as the "neighbour".
5. **Dummy screens do not light up.** Only the film's own behaviour is shown as proof. Skits play as comedy.
6. Every post points to the kiosk (location, hours, opening day or "will it fit mine?").
7. The name must not be explained with a Google-Translate-style card.

## 4. Brand look (from the three reference images the user sent)

- Palette: yellow `#FFD500`-ish, black, white, greys, plus the logo's orange-to-amber gradient.
  The reference sheets show a yellow-orange-pink-blue gradient chip. Treat it as accent only.
- Doodles: crown, smiley, asterisk, scribble underline, spray-paint swash, hand-drawn arrows, sticker tags.
- Type in the deck: **DM Sans** (headlines and body), **Anton** (sticker tags), **Permanent Marker** (hand-written notes).
  Downloadable from `raw.githubusercontent.com/google/fonts/main/ofl/dmsans/`, `.../ofl/anton/`,
  `.../apache/permanentmarker/`.
- One reference image (typography panel) shows the placeholder text "MULER!". That is a leftover from the image tool, not a brand font. Ignore it.
- Models in the references are Gen Z, yellow/pink/green/purple outfits, sunglasses, low-angle poses.
- Tagline and lines: "No more almost.", "Snip Snap Shap", "Exact fit only.", "Cut in under 60 sec.", "Don't worry, we got you."

## 5. What the user's Flow project already has (seen in the screenshot, not verified)

Project: `flow.google.com/project/34f2263d-c99b-4a5c-8f8c-0284a1922521`, Pro plan.
The right-hand "Untitled session" panel lists generated rows with a green check:

- C4 Worst to Cut (image 9:16), C2 How it Works (8 images 4:3), C3 Almost vs Exact (9:16), C5 Stump the Machine (9:16),
  D1 Rate the Fit (9:16), D2 Is it Glass? (5 images 4:3), D3 Sneaky Neighbor (9:16)
- **S1-10 Factory Storyboards: "Plan Ready"**, meaning a plan exists but frames are probably not generated yet.

So the Flow work covers the **post graphics** and has a storyboard **plan** for S1-S10.
The local chat should open that session and read the plan before generating anything.

Things visible in the Flow images that **must be checked before use**:
- A yellow card reads "MALL OF AMERICA - LEVEL 1 (BY NORDSTROM)". This looks like a placeholder or invented mall.
  The real mall and floor are not yet locked (the plan says date and mall must be locked before Phase 1).
- A card reads "Pull up to [KIOSK LOCATION]" (placeholder) and a TUFF card reads "Wrap Yellow" (not in the plan).
- Check the logo in every image for the six-point stars.
- Check every spec number against the plan: TUFF 0.25-0.35 mm, 4H-5H, EPU layer; CLEAR 99%+; PRIVACY 35 degrees.
- One card says "Not after TUFF? Meet the rest of the squad": check the wording is a claim the plan supports.

## 6. Cloud-session state

- Higgsfield MCP: balance **5.22 credits** (Creator plan). nano_banana costs 1 credit per image, nano_banana_2 costs 1.5.
  That is about 5 frames, so it cannot cover a 47-frame storyboard. This is why Flow was chosen.
  Nothing was generated or spent.
- Instagram research (earlier request) could not be done: Instagram blocked the fetch. Still waiting on screenshots or the exact SKW handle.
- Files saved: `shoot-guide/assets/wrapshap-logo-sparkle.png` and this file. Fonts were downloaded in the cloud container but are not committed.
- Earlier planning decision: draw storyboard frames in code in the brand's marker style (free, shows framing and arrows, does not invent a kiosk).
  The user then chose Flow instead. Either is fine. A hybrid works well: Flow for the hero looks, code-drawn overlays for timings and arrows.

## 7. Suggested structure for the guide (one PDF)

1. Cover and how to read the guide.
2. Day 1 run sheet: block order (Machine, Table, Window), time per script, kit list, crew roles, pre-roll checklist, rules from section 3.
3. One page per script S1-S10 (page 33-42 of the deck are the source): 4-7 frames, each with timecode, shot size, angle and move,
   action, dialogue (Roman Urdu with English), on-screen text, plus a small top-down floor plan, props, and the house rule.
4. Posts section: compact shoot cards for A1-D3, with proposed beats clearly marked as proposals.
5. Calendar page: W-4 to L+4 phase map with post ids.
6. Final QC page (the checklist in section 3 and the Flow checks in section 5).

The canvas-design skill asks for a design philosophy `.md` plus a single art-like canvas with minimal text.
This guide needs dense, readable text, so keep the philosophy but let function win over the "minimal text" rule, and say so.

## 8. Open questions for the user

- Mall name, floor, opening date (needed for B1, C1 and the end cards). Nothing in the repo has them.
- Real kiosk machine look: no photo exists in the repo. Frames show a generic kiosk until one is supplied.
- Real timer results for any "under 60 seconds" claim, and the real drop height for B6.
- Which cast is available for the factory day (S1-S10 need shopkeeper, customer, 3 staffers, an uncle, a nosy-uncle actor, one actor for four roles).

## 9. Paste-ready first message for the local chat

> Read `shoot-guide/HANDOVER.md` and `WrapShap_Launch_Plan_Yellow_Edition.pdf` in the Wrapshap repo (branch
> `claude/focused-mayer-jk3tke`). Open the Google Flow tab already open in Chrome, read the "S1-10 Factory Storyboards"
> plan, and build the shoot guide described in section 7, starting with the S1-S10 storyboard pages. Use only the sparkle
> logo. Check every generated image against sections 3 and 5 before putting it in the guide. Do not publish anything.
