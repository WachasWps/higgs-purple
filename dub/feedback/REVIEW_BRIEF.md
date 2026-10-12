# Shot review brief — map every shot to keep / replace, per client feedback

Work dir: /Users/wachas/Documents/higgs-purple/dub. You are reviewing DERMDOC vertical ads (Purple Sunscreen "PS" =
uv_sunscreen, Kojic Night Cream "KNC" = kojic_night_cream). The client (Dhruv's client) rejected many shots. We will
fix them by replacing bad shots with NEW 5-second AI clips (Wan 480p on Higgsfield, ~300-400 credits total — so be
frugal) generated from corrected keyframes. Most replacements must come from a shared LIBRARY of clips; a
"CUSTOM" new clip only when nothing in the library fits AND the shot is essential.

## Inputs
- `feedback/shots/video_info.json` → per video: `sheet` (contact sheet image: one tile per shot, labelled
  "S<n> start-end" = seconds), `shots`, `lines` (VO script with start/end seconds, English `en`), `cast`, `our_supers`
  (text overlays WE add in post — fixable for free).
- Product truth: `feedback/product_refs/sheet.jpg` and `feedback/product_refs/knc_tub_open.png`.
  PS tube: white squeeze tube, lavender ULTRA VIOLET band, WIDE flat translucent lavender CAP, NO NOZZLE/spout ever,
  stands on its cap; cream is pale lavender and must blend invisibly (no residue/cast). KNC: blue-base jar, white lid,
  white label "2% KOJIC ACID / GLOW FUSION FORMULA with Niacinamide & Alpha Arbutin / NIGHT CREAM", thick white cream.
- Flagged client screenshots with comments: `feedback/issues_screens.json` (file, time, comment) + frames in
  `feedback/issue_frames/<key>.jpg`.
- Library catalog: `feedback/codex/library.json` ("clips": id → prompt = what the clip shows, motion). Models in
  library clips are DUSKY Indian women (MEERA for PS, ANANYA for KNC).

## Client feedback (all must be satisfied)
GLOBAL: models must be duskier (relatable Indian skin); female VO only; BG music too slow (handled elsewhere);
DERMDOC logo throughout + endslate (already done); no hair on skin close-ups; skin must look like skin, not a mountain
(start & end on a face); product packaging must be exact in EVERY frame (nozzle/cap/tub/label).
PS: no nozzle — wide cap always; colour wheel shown by AI is WRONG in every video (yellow must be opposite purple, not
blue) and unexplained → every AI colour-wheel shot must be REPLACED (we will overlay a correct animated wheel in post
on library shot PSA2_avatar_point or full-screen graphic — mark it as replace_with "GRAPHIC_COLOUR_WHEEL"); explain
WHY purple tint: purple sits opposite yellow on the colour wheel → cancels yellow-looking dullness → made for Indian
skin tones → instant glow, no white cast (VO + text); wherever "glow" is said → "Instant Glow"; instant glow after
application must be clearly shown (application → fully blended → visibly glowy smooth skin) — missing in all videos;
before/after must show a real difference (before dull, no glow; after very glowy/smooth), label under after =
"INSTANT GLOW"; product must be fully blended — no residue, no cast; no mask/ubtan-like thick application; no
"dull in sunlight" nonsense; never two products in a frame; product avatar = exact tube with eyes + hands.
KNC: say full product name, never "KNC"; night cream → application only at night, results next morning in daylight;
before/after SPLIT-SCREEN frame (vertical half/half, face not cropped) is missing → add one, with "AFTER 2 WEEKS"
under the after image; the morning wake-up frame text must be "Brighter, clearer-looking skin by morning" style,
NOT "2 weeks"; dark spots must look realistic (soft brown patches, not chicken-pox dots); NO dark spots after
application / in morning / after shots; label the THREE ingredients separately and consistently: "2% Kojic Acid",
"Niacinamide", "Alpha Arbutin" (AI-baked labels with misspellings like "ARBUTM" or duplicated "Kojic Acid" must be
replaced or covered); don't call the product "dark-spot leader"; cream must blend fully then show transformation;
after = spotless, glowing, smooth, same skin tone; jar must be exact.
UGC: before dull (no glow), after much glowier and spotless; transformation shot missing in some; B/A frame missing in
some; VO too animated (handled in dub); lip-sync not matching → prefer shots where the model is NOT talking to camera
while VO plays (B-roll), or keep talking shots short.
GENERAL ADS (product_ad, Hinglish VO): client: "not at all up to the mark, not a high-end commercial" (ref: L'Oréal
Glycolic Bright short), ingredients must be labelled (3 drops not enough), B/A rework (before realistic, after glowy),
dark spots realistic, colour wheel explained, PS "yellow dullness" concept is LIKED, random fancy shots before the
endslate serve no purpose → remove.

## What to output — one file per video: `feedback/edl/<video_id>.json`
```json
{"video_id": "...", "product": "ps|knc", "category": "...",
 "shots": [{"n": 1, "start": 0.0, "end": 2.6, "content": "<what the shot shows>", "issues": ["nozzle", ...],
            "action": "keep|replace|remove", "replace_with": "<library id>|GRAPHIC_COLOUR_WHEEL|GRAPHIC_BA_SPLIT|CUSTOM|null",
            "custom": {"keyframe": "<full description of the corrected first frame>", "motion": "<5s motion>",
                       "base_frame_time": 1.3} ,
            "note": "<why / how it lines up with the VO line>"}],
 "script_changes": [{"line_id": 3, "old_en": "...", "new_en": "...", "reason": "Instant Glow / full product name / ..."}],
 "new_lines": [{"after_line_id": 4, "en": "...", "speaker": "<cast id or narrator_female>", "purpose": "..."}],
 "supers": [{"action": "remove|add|change", "match": "<existing super text or null>", "text": "...", "start": 0, "end": 0, "why": "..."}],
 "voice_changes": [{"speaker": "<cast id>", "to": "female", "why": "male/scary"}],
 "summary": "<2 lines>"}
```
Rules: keep shots that are genuinely fine (cartoon villains/ingredient characters without product/skin problems are
fine to keep) — every replacement costs credits. If a video's woman is replaced in some shots, replace ALL her
shots in that video (continuity — the library model must be the only woman). A replacement must match the VO line
playing during that shot (e.g. a line about blending → PS05_blend_glow). Shots longer than 5 s may be covered by two
library clips or one slowed clip (say which in note). Use CUSTOM sparingly (target ≤ 1 per video; 0 is better) and
describe its keyframe so an image model can draw it exactly. Script changes: English only (translations are done
later), keep lines about the same length as the old ones (timing), keep claims hedged ("helps", "looking"), no
fairness/whitening. Only write files under feedback/edl/. Look at each sheet image (Read tool) — they are small.
Final reply: one line per video: id, #replace, #custom, key changes.
