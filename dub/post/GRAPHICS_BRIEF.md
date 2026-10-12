# Graphics Director Brief — on-screen text for DERMDOC dubbed ads

You design the on-screen text (supers) for short 9:16 DERMDOC ads (15–20 s). The SAME graphics are burned into all
5 language versions of a video (Bengali, Tamil, Telugu, Malayalam, Odia), so on-screen text is ENGLISH (brand style,
exactly like the client's approved reference). Spoken-word captions, the logo and the outro are added automatically
by the renderer — you do NOT design those. Write ONLY `work/<id>/graphics.json`, then validate it.

Work dir: `/Users/wachas/Documents/higgs-purple/dub/`

## Inputs per video
- `post/sheets/<id>.png` — contact sheet, 1 frame per second, 5 columns × 4 rows, row-major: tile k (0-based) = t = k s.
  LOOK AT IT (Read the image) to see shots, faces, product, empty areas.
- `work/<id>/plan.json` — cast + spoken lines with `start`/`end` (seconds) and `en` text = what is said. Use it to
  time supers to the moment a claim is SAID or SHOWN.
- `work/<id>/prompt.txt` — original creative intent (shots, hooks, claims). `work/<id>/meta.json` — duration.
- Product: "uv_sunscreen" (DERMDOC Ultra Violet Brightening Sunscreen: 4% Niacinamide, SPF 50 PA+++, purple tint,
  for Indian skin, no white cast) or "kojic_night_cream" (DERMDOC 2% Kojic Acid Night Cream: Glow Fusion Formula,
  Niacinamide + Alpha Arbutin, dark spots, overnight brightening).

## Reference style (client-approved final video) — reuse these looks
- `hook_mono`: big hook question/statement, monospace ExtraBold UPPERCASE, white with dark-purple outline + shadow.
  e.g. "STEPPING OUT / UNPROTECTED?" Opening seconds only, when the video opens with a problem/hook.
- `pill`: ingredient/benefit card — navy monospace UPPERCASE on a white rounded pill, 1–2 short lines.
  e.g. "4% NIACINAMIDE / REPAIRS & PROTECTS", "2% KOJIC ACID / TARGETS DARK SPOTS".
- `claim_bold`: hero claim, heavy rounded sans UPPERCASE, white with soft purple glow, optional smaller `sub` line.
  e.g. "PURPLE TINT / INSTANT GLOW" + sub "FOR INDIAN SKIN TONE"; "WATER RESISTANT" + sub "SWEAT PROOF".
- `label`: small bold labels e.g. "BEFORE" / "AFTER" over a split comparison (use explicit x,y), or a character
  name tag in personification videos (e.g. "UV VILLAIN", "SPF SHIELD", "KOJIC ACID") on first appearance.
- `hud`: decorative tech frame, `variant` "corners" (viewfinder corner brackets) or "scan" (thin scan frame + tiny
  tech labels). Use on macro skin shots / product hero shots / before-after, sparingly.

## Rules (quality bar = polished paid ad)
1. ONLY where it adds value: the hook, key ingredients/claims at the moment they are said or shown, before/after
   labels, character name tags. Typically 3–5 text elements per video (+ optional hud). Never caption speech
   word-for-word (captions already do that). No text in silent "breathing" shots unless it is a claim beat.
2. Claims must match what the video says (plan `en`) / the pack: 4% NIACINAMIDE, SPF 50 PA+++, NO WHITE CAST,
   PURPLE TINT COLOUR CORRECTION, FOR INDIAN SKIN, 2% KOJIC ACID, ALPHA ARBUTIN, GLOW FUSION FORMULA, etc.
   Never add new claims, never "whitening/fairness", keep "brighter-LOOKING" hedges where the script hedges.
3. Never cover faces, eyes, mouths, the product label, or the key action (application, swatch). Pick `position`
   from the free area in that shot: "top" (y≈0.16), "upper" (y≈0.30), "center" (y≈0.50), "lower" (y≈0.68).
   The top-left corner (logo) and the bottom 12% (captions) are reserved — never place text there.
4. Each element 1.2–3.5 s; time it to the shot (do not straddle a hard cut) and to the spoken beat.
   No two text elements on screen at once (hud may overlap a text element).
5. Keep text SHORT: ≤ 3 words per line, ≤ 2 lines (+ optional `sub` ≤ 5 words). UPPERCASE.
6. Animation: "pop" (default for pills/labels), "fade" (claims), "slide_up" (hooks), "type" (hook_mono only).
7b. `caption_moves` (optional): `[{"start": 16.0, "end": 20.0, "y": 0.74}]` lifts the captions to y during that
   window only — use it when the footage itself has text/end-slate at the bottom at that time.
7. `caption_y`: where the spoken captions sit, default 0.90 (fraction of height). Raise it (0.80–0.86) only if the
   bottom of the frame holds important content (e.g. product name, hands action) for most of the video.

## Output: `work/<id>/graphics.json`
```json
{"video_id": "<id>", "product": "uv_sunscreen|kojic_night_cream", "caption_y": 0.90,
 "elements": [
  {"type": "hook_mono", "start": 0.2, "end": 2.4, "lines": ["STEPPING OUT", "UNPROTECTED?"], "position": "center", "anim": "slide_up"},
  {"type": "pill", "start": 8.6, "end": 11.0, "lines": ["4% NIACINAMIDE", "REPAIRS & PROTECTS"], "position": "lower", "anim": "pop"},
  {"type": "claim_bold", "start": 12.0, "end": 14.6, "lines": ["PURPLE TINT", "INSTANT GLOW"], "sub": "FOR INDIAN SKIN TONE", "position": "top", "anim": "fade"},
  {"type": "label", "start": 14.8, "end": 17.0, "lines": ["BEFORE"], "x": 0.25, "y": 0.17, "anim": "pop"},
  {"type": "label", "start": 14.8, "end": 17.0, "lines": ["AFTER"], "x": 0.75, "y": 0.17, "anim": "pop"},
  {"type": "hud", "variant": "corners", "start": 0.0, "end": 3.0}
 ],
 "notes": "one line on intent"}
```
(Before/After labels are the one allowed exception to rule 4's "no two text elements at once".)

## Validate (mandatory)
`cd /Users/wachas/Documents/higgs-purple/dub && python3 post/validate_graphics.py work/<id>/graphics.json` — fix until it prints OK.
Final reply: one line per video: `<id>: <n> elements — <short list of texts>`.
Do NOT run ffmpeg/ML or edit anything outside work/<id>/graphics.json.
