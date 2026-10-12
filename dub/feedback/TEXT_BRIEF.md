# Text pass brief — apply each video's EDL script/super changes in all 5 languages

Work dir: /Users/wachas/Documents/higgs-purple/dub. Read first: `DIRECTOR_BRIEF.md` (dub script conventions — how
English terms are spelled phonetically in each regional script for the TTS, per-language CPS budgets) and
`post/CAPTIONS_BRIEF.md` + `post/GRAPHICS_BRIEF.md` (caption / on-screen text formats). Source of changes:
`feedback/edl/<id>.json` (fields script_changes, new_lines, supers, summary; shot list tells you WHEN each picture
plays). The picture is being rebuilt from the EDL (library clips); the VO timeline does NOT move.

For each assigned video:

## 1. work/<id>/plan.json (keep a valid plan — validate_plan.py must pass)
- `script_changes`: set the line's `en` to `new_en` and write fresh, natural translations for bn, ta, te, ml, or
  (Bengali, Tamil, Telugu, Malayalam, Odia) — same register/character as the rest of that video, female speaker
  voice, colloquial ad tone. Keep length within the line's slot (validate_plan.py checks chars/second).
- `new_lines`: only if there is a real silent gap ≥ 1.2 s in the timeline where it fits; give it `id` = max id + 1,
  `start`/`end`/`max_end` inside the gap, `speaker` (an existing cast id; female), `tag` null, translations as above.
  Otherwise merge its meaning into the neighbouring changed line instead.
- Client wording rules: PS — say "Instant Glow" wherever glow is promised; explain purple tint via the colour wheel
  (purple sits opposite yellow → helps cancel yellow-looking dullness → made for Indian skin tones → no white cast).
  KNC — never say "KNC": use "Kojic Acid Night Cream" (or "DERMDOC Kojic Acid Night Cream" if it fits); it's a night
  cream (applied at night, results seen in the morning / after 2 weeks). Hedged claims only ("helps", "looking",
  "visibly"), no fairness/whitening/skin-lightening, no "dark-spot leader".
- UGC videos (style "ugc"): the client said the VO is "very animated" → set `tag` to null on every line of the video
  (no emotion tags) so delivery is calm and natural.
- Do NOT touch `cast` (voices were already recast to female by another step).
- Append every changed/new line id to `work/<id>/redub.json` (`{"lines":[...]}` — merge with what is there).
- Validate: `.venv/bin/python validate_plan.py work/<id>` (fix until it passes; it writes plan.ok).

## 2. work/<id>/captions_<lang>.json (bn, ta, te, ml, or)
For every changed/new line, write the caption text per `post/CAPTIONS_BRIEF.md` (regional script, with the English
terms in Latin: DERMDOC, Niacinamide, Kojic Acid, Alpha Arbutin, SPF 50 PA+++, Ultra Violet, Night Cream, and the claim
"Instant Glow" in Latin too). Validate: `python3 post/validate_captions.py work/<id>/captions_<lang>.json`.

## 3. work/<id>/graphics.json (on-screen English text, brand style)
Apply the EDL `supers` (remove / add / change) and these fixed rules:
- Remove any super that no longer matches the new picture (e.g. masks/pills placed for old baked-in text that the
  library clip no longer has; supers about removed concepts like "dull in sunlight", "DARK-SPOT LEADER").
  Any `blur`/pill `mask` element tied to a REPLACED shot must be deleted (the garbled text is gone).
- Before/after split shots (EDL replace_with GRAPHIC_BA_SPLIT): picture = BEFORE face in the top half, AFTER face in
  the bottom half, white divider at y=0.5. Add labels: `{"type":"label","lines":["BEFORE"],"x":0.5,"y":0.455}` and
  under the after image `{"type":"label","lines":["INSTANT GLOW"],"x":0.5,"y":0.955}` (PS) or
  `["AFTER 2 WEEKS"]` (KNC), both spanning the split's time window; add a `caption_moves` entry
  `{"start":..,"end":..,"y":0.58}` for that window so captions sit just under the divider.
- KNC morning wake-up shots (KN06_morning_wake): text = "BRIGHTER, CLEARER-LOOKING SKIN BY MORNING" style
  (claim_bold, position top) — never "2 weeks" on a morning frame.
- KNC ingredient shots (KNA2_avatar_ingredients): three SEPARATE labels in the SAME style, staggered
  near the top: "2% KOJIC ACID" (x .50 y .17), "NIACINAMIDE" (x .30 y .27), "ALPHA ARBUTIN" (x .70 y .27) — spelled
  exactly so, never "ARBUTIN" alone, never Kojic Acid twice.
- PS colour wheel shots (GRAPHIC_COLOUR_WHEEL): the graphic already carries its own text ("YELLOW DULLNESS",
  "PURPLE TINT", "OPPOSITES CANCEL", "PURPLE CANCELS YELLOW DULLNESS") — add NO supers in that window.
- Keep supers few, short, English, hedged. Validate: `python3 post/validate_graphics.py work/<id>/graphics.json`.

Do not run renders or any ML. Only edit files under work/<assigned ids>/. Final reply: per video — lines changed,
new lines, supers added/removed, validators OK.
