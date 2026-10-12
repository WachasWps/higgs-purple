# Typo-fix brief — cover misspelled text that is baked into the AI footage

The source videos (AI-generated) sometimes contain on-screen titles/cards with typos ("Honeet Suience",
"Alpha Arbutie", "Halps even skin tone", "KOJIC ACIC"). We fix them with an opaque brand card carrying the
CORRECT text, placed exactly over the bad text for exactly as long as it is on screen.

Work dir: `/Users/wachas/Documents/higgs-purple/dub/`. For each assigned video:
1. Read `post/text_audit/<id>.json` (OCR text tracks: `text`, `variants`, `start`/`end` s, `box` = [x0,y0,x1,y1]
   fractions with top-left origin, `suspect_words`) and Read the crop PNG of each flagged track
   (`post/text_audit/<id>_<n>.png`, red box = the track). Also look at `post/sheets/<id>.png` for context.
2. Decide per flagged track:
   - **IGNORE** if the text is printed on the PRODUCT / PACKAGING (jar lid, jar label, tube label, box) OR is a
     REFLECTION / mirror image of the product or its label (mirror, glossy table, glass, water) — the client said the
     product and its reflections stay exactly as they are, typos included. Also ignore OCR noise (correct text misread on some frames — check the crop:
     if the visible text is actually spelled right, ignore), tiny illegible background text, and scene props.
   - **FIX** if it is floating on-screen text (title, ingredient card/caption under a character, tagline, end-slate
     line, "After 2 Weeks" card…) and the text in the crop is misspelled/garbled.
   Group stacked lines that belong to one card (e.g. "Alpha Arbutie" + "Halps even skin tone") into ONE cover card.
3. For each FIX write a cover card into `work/<id>/graphics.json` → `elements`:
   `{"type": "pill", "mask": {"x0","y0","x1","y1"}, "start", "end", "lines": [...], "anim": "fade"}`
   - mask = union box of the grouped tracks, padded by 0.012 horizontally and 0.006 vertically (clamped 0..1).
   - start = track start − 0.35 s (OCR samples at 3 fps, so the typo can appear up to 1/3 s earlier; never < 0);
     end = track end + 0.35 s (≤ duration from meta.json).
   - lines = the INTENDED text, correctly spelled, UPPERCASE, ≤ 5 words per line, ≤ 3 lines. Use the brand spelling:
     3XPERT (correct brand name of the night cream — never change it to EXPERT), DERMDOC, HONEST SCIENCE, 2% KOJIC ACID, NIACINAMIDE, ALPHA ARBUTIN, GLOW FUSION FORMULA, NIGHT CREAM,
     4% NIACINAMIDE, SPF 50 PA+++, ULTRA VIOLET, BRIGHTENING SUNSCREEN. Keep the same meaning (and hedges such as
     "helps", "even-looking"); never add claims, never fairness/whitening.
   - If an existing element in graphics.json already covers the same text/time (earlier estimated masks have a "mask"
     field), REPLACE it with your precise version instead of adding a duplicate. If a normal super would collide
     with a cover card (same area at the same time), move or retime that super.
4. Validate: `python3 post/validate_graphics.py work/<id>/graphics.json` until OK.

Write only `work/<id>/graphics.json`. No ffmpeg/ML. Final reply: per video → FIXED: "<bad>" → "<good>" (t, box) /
IGNORED: "<text>" (reason), one line each.
