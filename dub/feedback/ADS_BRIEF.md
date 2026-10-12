# General-ad rebuild brief — new premium ads, female narrator, dubbed into 5 languages

Work dir: /Users/wachas/Documents/higgs-purple/dub. The client rejected the 10 general AI ads ("not at all up to the
mark", ref L'Oréal Glycolic-Bright short) and wants regional languages only (no English/Hindi in the final). Each
ad is rebuilt from `feedback/edl/<id>.json` → field `rebuild` (shots with start/end/source/super, `vo` English lines
with start/end, `target_duration_s`). Read first: `DIRECTOR_BRIEF.md` (dub-script conventions: English brand/
ingredient terms spelled phonetically in each regional script, per-language chars/second budgets),
`post/CAPTIONS_BRIEF.md`, `post/GRAPHICS_BRIEF.md`, and `feedback/TEXT_BRIEF.md` (the on-screen rules: B/A split
labels, 3 separate KNC ingredient labels, colour-wheel windows carry no supers, "Instant Glow", full product name).

For each assigned ad id write (back up nothing — I already backed up the originals):

1. `work/<id>/plan.json`:
```json
{"video_id": "<id>", "style": "product_ad", "duration": <target_duration_s>,
 "cast": [{"id": "narrator", "name": "Narrator", "role": "narrator",
           "description": "calm, premium female ad narrator",
           "ref_file": "work/71e0977a/stems/vocals.wav", "ref_ranges": [[9.32, 12.54], [13.68, 16.56]],
           "fx": "none", "pitch_semitones": 0}],
 "lines": [{"id": 1, "speaker": "narrator", "start": .., "end": .., "max_end": .., "en": "...", "tag": null,
            "keep_original": false, "bn": "...", "ta": "...", "te": "...", "ml": "...", "or": "..."}],
 "notes": "rebuilt general ad"}
```
   Lines = the rebuild `vo` lines (you may tighten wording). `max_end` = next line's start − 0.05 (last line:
   target_duration − 0.1). Natural, premium, colloquial translations (Bengali, Tamil, Telugu, Malayalam, Odia).
   Hedged claims only; PS says "Instant Glow"; KNC says "Kojic Acid Night Cream" (never "KNC"), night use, results
   "in 2 weeks"/"by morning" as the shot list implies. Validate: `.venv/bin/python validate_plan.py work/<id>/plan.json`
   and shorten until it passes (the rebuild scripts are known to be tight — trim the least important words first).
2. `work/<id>/captions_<lang>.json` for bn ta te ml or (CAPTIONS_BRIEF format; English terms incl. "Instant Glow" in
   Latin). Validate each with `python3 post/validate_captions.py`.
3. `work/<id>/graphics.json` — REPLACE its elements entirely (old ones belong to the old picture):
   `{"video_id": "<id>", "product": "<uv_sunscreen|kojic_night_cream>", "caption_y": 0.9, "elements": [...],
   "caption_moves": [...], "notes": "..."}` built from the rebuild shots' `super` fields + TEXT_BRIEF rules
   (B/A: BEFORE at x .5 y .455, INSTANT GLOW / AFTER 2 WEEKS at x .5 y .955, caption_moves y .58 for that window;
   ingredient macro shots: three separate labels in the same style; colour-wheel windows: no supers; few, short,
   English supers). Validate with `python3 post/validate_graphics.py work/<id>/graphics.json`.
4. `work/<id>/meta.json`: set `"kind": "ad_dub"` and `"duration": <target_duration_s>` (keep other fields).

Do not run renders or ML. Only edit files under work/<assigned ids>/. Final reply: per ad — lines, total English
chars, validators OK.
