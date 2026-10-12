"""TEXT_BRIEF step 3: rebuild work/<id>/graphics.json from the EDL supers + fixed KNC rules."""
import json, os
root = '/Users/wachas/Documents/higgs-purple/dub/work'

def BA(s, e):  # GRAPHIC_BA_SPLIT: BEFORE top half, AFTER bottom half, divider y=0.5
    return [{"type": "label", "start": s, "end": e, "lines": ["BEFORE"], "x": 0.5, "y": 0.455, "anim": "pop"},
            {"type": "label", "start": s, "end": e, "lines": ["AFTER 2 WEEKS"], "x": 0.5, "y": 0.955, "anim": "pop"}]

def MORNING(s, e):  # KN06_morning_wake
    return {"type": "claim_bold", "start": s, "end": e, "lines": ["BRIGHTER, CLEARER-LOOKING", "SKIN BY MORNING"],
            "position": "top", "anim": "fade"}

def KOJIC(s, e):
    return {"type": "pill", "start": s, "end": e, "lines": ["2% KOJIC ACID"], "x": 0.5, "y": 0.17, "anim": "pop"}
def NIA(s, e):
    return {"type": "pill", "start": s, "end": e, "lines": ["NIACINAMIDE"], "x": 0.3, "y": 0.27, "anim": "pop"}
def AA(s, e):
    return {"type": "pill", "start": s, "end": e, "lines": ["ALPHA ARBUTIN"], "x": 0.7, "y": 0.27, "anim": "pop"}

def TAG(text, s, e, x, y):
    return {"type": "label", "start": s, "end": e, "lines": text if isinstance(text, list) else [text], "x": x, "y": y, "anim": "pop"}

KN03_TAG = (0.84, 0.62)  # beside her cheek, over hair, clear of the face on KN03_before_night

G = {
 "23850d94": dict(
  elements=[
   TAG("PROFESSOR JAR", 0.3, 2.0, 0.5, 0.3),
   KOJIC(5.98, 8.1),
   NIA(8.34, 9.4),
   AA(9.4, 10.66),
   *BA(13.6, 15.17),
   {"type": "hud", "variant": "corners", "start": 13.6, "end": 15.12},
  ],
  caption_moves=[{"start": 13.6, "end": 15.17, "y": 0.58}],
  notes="Text pass (client EDL): PROFESSOR JAR tag above the KNA1 jar mascot; the three actives as separate same-style "
        "ingredient pills with no cover masks (KN03/KNA2 have no baked text): 2% KOJIC ACID on lesson one (KN03), then "
        "NIACINAMIDE (x.30) and ALPHA ARBUTIN (x.70) staggered over the KNA2 orbs on the new L4; Kojic is not repeated. "
        "B/A split: BEFORE over the top half, AFTER 2 WEEKS under the after half, captions lifted to 0.58 under the divider. "
        "Old blur boxes removed."),
 "390113f1": dict(
  elements=[
   {"type": "hook_mono", "start": 0.15, "end": 1.6, "lines": ["WHAT HAPPENS", "WHILE YOU SLEEP?"], "position": "top", "anim": "slide_up"},
   TAG("THE NIGHT TEAM", 5.2, 6.9, 0.68, 0.14),
   KOJIC(7.0, 8.5),
   NIA(8.5, 9.95),
   AA(9.95, 11.35),
   MORNING(11.45, 12.9),
   *BA(12.9, 14.57),
  ],
  caption_moves=[{"start": 12.9, "end": 14.57, "y": 0.58}],
  notes="Text pass (client EDL): bedtime hook on KN05 and THE NIGHT TEAM tag on the kept jar/team shot; DARK SPOT GANG, "
        "the face-scan HUD and the 'AFTER 2 WEEKS' cover card are removed with the replaced footage. KNA2 orbs get three "
        "separate same-style pills staggered near the top (2% KOJIC ACID x.50 y.17, NIACINAMIDE x.30 y.27, ALPHA ARBUTIN "
        "x.70 y.27), the KN06 morning wake gets the 'by morning' claim (no '2 weeks'), then the B/A split labels with "
        "captions lifted to 0.58."),
 "595689d8": dict(
  elements=[
   TAG("DULLNESS", 0.6, 2.4, *KN03_TAG),
   {"type": "claim_bold", "start": 10.25, "end": 11.55, "lines": ["GLOW FUSION", "FORMULA"], "sub": "WITH NIACINAMIDE & ALPHA ARBUTIN", "position": "top", "anim": "fade"},
   MORNING(14.35, 15.7),
   *BA(15.7, 17.43),
   {"type": "hud", "variant": "corners", "start": 17.45, "end": 20.0},
  ],
  caption_moves=[{"start": 4.2, "end": 6.1, "y": 0.72}, {"start": 15.7, "end": 17.43, "y": 0.58},
                 {"start": 17.43, "end": 20.0, "y": 0.93}],
  notes="Text pass (client EDL): DULLNESS tag beside her dull cheek on KN03 (the mirror ghost is gone); GLOW FUSION "
        "FORMULA kept on the kept beam shot; OVERNIGHT BRIGHTENING replaced by the 'by morning' claim on the KN06 wake; "
        "B/A split labels with captions lifted to 0.58; captions stay at 0.93 under the baked end slate."),
 "715b1b5c": dict(
  elements=[
   {"type": "hook_mono", "start": 0.15, "end": 1.85, "lines": ["DARK SPOTS", "TAKING OVER?"], "position": "top", "anim": "slide_up"},
   TAG("NIGHT PATROL CAPTAIN", 2.6, 3.95, 0.5, 0.14),
   {"type": "pill", "start": 4.5, "end": 6.27, "lines": ["2% KOJIC ACID"], "x": 0.4835, "y": 0.221, "anim": "pop",
    "mask": {"x0": 0.275, "y0": 0.145, "x1": 0.692, "y1": 0.297}},
   NIA(6.42, 8.75),
   AA(9.0, 11.0),
   *BA(14.97, 17.17),
   {"type": "claim_bold", "start": 17.3, "end": 18.95, "lines": ["THE OVERNIGHT", "BRIGHTENER"], "position": "top", "anim": "fade"},
  ],
  caption_moves=[{"start": 14.97, "end": 17.17, "y": 0.58}],
  notes="Text pass (client EDL): hook and jar-captain tag kept; on the kept golden-ring shot a 2% KOJIC ACID cover pill "
        "hides the baked ring text (OCR box 0.29-0.68 x 0.15-0.29, padded) so Kojic appears once and in the same pill "
        "style as NIACINAMIDE (x.30) and ALPHA ARBUTIN (x.70), which land on L4/L5 over the KNA2 orbs. B/A split labels "
        "with captions at 0.58. THE OVERNIGHT BRIGHTENER on the packshot ends at 18.95, before the baked end title "
        "appears at 19.0 in the same top area. The 3 ACTIVES claim is dropped (it repeated L6 word for word, straddled "
        "the KN02/KN04 cut, and the validator allows at most 8 text elements)."),
 "71e0977a": dict(
  elements=[
   TAG("DARK SPOTS", 0.15, 1.65, *KN03_TAG),
   {"type": "pill", "start": 3.0, "end": 5.87, "lines": ["THE NIGHT TEAM"], "x": 0.4935, "y": 0.8175, "anim": "pop",
    "mask": {"x0": 0.205, "y0": 0.787, "x1": 0.782, "y1": 0.848}},
   KOJIC(5.95, 7.15),
   NIA(7.15, 8.35),
   AA(8.35, 9.55),
   {"type": "claim_bold", "start": 9.7, "end": 12.45, "lines": ["3 BRIGHTENING", "ACTIVES"], "position": "top", "anim": "fade"},
   *BA(12.57, 14.3),
  ],
  caption_moves=[{"start": 12.57, "end": 14.3, "y": 0.58}],
  notes="Text pass (client EDL): DARK SPOTS tag beside her cheek on KN03; THE NIGHT TEAM cover card over the baked "
        "'The KNC Team' on the kept jar/team shot (OCR box 0.22-0.77 x 0.80-0.84, padded); three separate same-style "
        "ingredient pills over the KNA2 orbs (2% KOJIC ACID x.50 y.17, NIACINAMIDE x.30 y.27, ALPHA ARBUTIN x.70 y.27); "
        "3 BRIGHTENING ACTIVES moved to the top over KN04; B/A split labels with captions at 0.58. The face-off hook "
        "(2.95-4.15) is dropped: it straddled the 3.0 cut, sat on top of the cover card, and the validator allows at "
        "most 8 text elements."),
 "7558fbf1": dict(
  elements=[
   {"type": "hook_mono", "start": 0.1, "end": 1.75, "lines": ["DARK SPOTS", "MOVING IN?"], "position": "top", "anim": "slide_up"},
   KOJIC(4.4, 5.9),
   NIA(5.9, 7.1),
   AA(7.1, 8.3),
   {"type": "claim_bold", "start": 11.4, "end": 12.9, "lines": ["OVERNIGHT", "BRIGHTENER"], "position": "top", "anim": "fade"},
   MORNING(13.2, 14.85),
   *BA(14.9, 16.93),
  ],
  caption_moves=[{"start": 14.9, "end": 16.93, "y": 0.58}],
  notes="Text pass (client EDL): eviction hook kept on KN03; DARK-SPOT LEADER tag and the macro scan HUD removed; the "
        "three actives as separate same-style pills on their spoken names over the KNA2 orbs; OVERNIGHT BRIGHTENER kept "
        "on the night application; 'by morning' claim on the KN06 wake; B/A split labels with captions at 0.58. The "
        "requested GLOW FUSION FORMULA claim on KN01 is not added: the exact jar label in that shot already prints "
        "'GLOW FUSION FORMULA with Niacinamide & Alpha Arbutin', and a 9th text element would exceed the validator's 8."),
 "89697c77": dict(
  elements=[
   {"type": "hook_mono", "start": 0.15, "end": 1.75, "lines": ["TOO TIRED FOR", "SKINCARE?"], "position": "top", "anim": "slide_up"},
   {"type": "claim_bold", "start": 2.95, "end": 6.4, "lines": ["2% KOJIC ACID", "NIGHT CREAM"], "sub": "THE OVERNIGHT BRIGHTENER", "position": "top", "anim": "fade"},
   {"type": "pill", "start": 6.6, "end": 8.95, "lines": ["2% KOJIC ACID"], "x": 0.256, "y": 0.218, "anim": "pop",
    "mask": {"x0": 0.071, "y0": 0.165, "x1": 0.441, "y1": 0.271}},
   {"type": "pill", "start": 6.6, "end": 8.95, "lines": ["NIACINAMIDE"], "x": 0.725, "y": 0.248, "anim": "pop",
    "mask": {"x0": 0.48, "y0": 0.226, "x1": 0.97, "y1": 0.27}, "text_x": 0.725, "text_y": 0.232},
   {"type": "pill", "start": 6.6, "end": 8.95, "lines": ["ALPHA ARBUTIN"], "x": 0.725, "y": 0.2925, "anim": "pop",
    "mask": {"x0": 0.48, "y0": 0.27, "x1": 0.97, "y1": 0.315}, "text_x": 0.725, "text_y": 0.305},
   {"type": "hud", "variant": "corners", "start": 9.0, "end": 10.65},
   MORNING(15.5, 17.37),
   *BA(17.37, 20.04),
  ],
  caption_moves=[{"start": 17.37, "end": 20.04, "y": 0.58}],
  notes="Text pass (client EDL): hook kept on KN03; on the KNA1 jar a single hero card '2% KOJIC ACID NIGHT CREAM' + "
        "'THE OVERNIGHT BRIGHTENER' (merges the requested jar name tag and the OVERNIGHT BRIGHTENER super that was baked "
        "into the replaced shot); on the kept moon-jar shot three same-style cover pills over the baked callouts: 2% KOJIC "
        "ACID on the left (OCR 0.08-0.43 x 0.17-0.26), NIACINAMIDE and ALPHA ARBUTIN as two separate pills on the right "
        "(OCR 0.49-0.96 x 0.23-0.31); 'by morning' claim on the KN06 wake; B/A split labels with captions at 0.58. The "
        "RICH TEXTURE claim is dropped to stay within the validator's 8 text elements (the HUD on the macro stays)."),
 "906fbf3c": dict(
  elements=[
   TAG("DARK SPOTS", 0.3, 1.75, *KN03_TAG),
   {"type": "pill", "start": 5.65, "end": 8.27, "lines": ["NIACINAMIDE"], "x": 0.2334, "y": 0.3525, "anim": "fade",
    "mask": {"x0": 0.1086, "y0": 0.3055, "x1": 0.3581, "y1": 0.3994}, "text_x": 0.215, "text_y": 0.3525},
   {"type": "claim_bold", "start": 9.6, "end": 10.85, "lines": ["RICH & CREAMY"], "sub": "OVERNIGHT BRIGHTENER", "position": "top", "anim": "fade"},
   {"type": "hud", "variant": "corners", "start": 11.32, "end": 12.9},
   MORNING(13.3, 14.9),
   *BA(14.9, 16.6),
   {"type": "claim_bold", "start": 16.9, "end": 18.15, "lines": ["3XPERT FORMULA", "2% KOJIC ACID"], "sub": "WITH NIACINAMIDE & ALPHA ARBUTIN", "position": "top", "anim": "fade"},
  ],
  caption_moves=[{"start": 14.9, "end": 16.6, "y": 0.58}, {"start": 16.6, "end": 20.0, "y": 0.93}],
  notes="Text pass (client EDL): DARK SPOTS tag beside her cheek on KN03; the NIACINAMIDE cover over the faint icy hex "
        "stays (EDL asks for it as a glowing icy-blue hex badge in the white bold sans of the baked hexes; the renderer "
        "has no hex-badge element yet, so it is still a pill); the duplicate KOJIC ACID / FOR DARK SPOTS pill is removed "
        "(the baked gold hex already names 2% KOJIC ACID); 'by morning' claim on the KN06 wake; B/A split labels with "
        "captions at 0.58; the end claim names all three actives as '2% KOJIC ACID with Niacinamide & Alpha Arbutin'."),
 "bd3b8af7": dict(
  elements=[
   {"type": "hook_mono", "start": 0.2, "end": 2.2, "lines": ["THE NIGHT TEAM", "CLOCKS IN"], "position": "top", "anim": "slide_up"},
   KOJIC(4.0, 6.2),
   NIA(6.35, 8.4),
   AA(8.5, 9.95),
   *BA(12.0, 13.6),
   {"type": "claim_bold", "start": 13.65, "end": 14.95, "lines": ["GLOW FUSION FORMULA", "2% KOJIC ACID"], "sub": "WITH NIACINAMIDE & ALPHA ARBUTIN", "position": "top", "anim": "fade"},
  ],
  caption_moves=[{"start": 12.0, "end": 13.6, "y": 0.58}],
  notes="Text pass (client EDL): hook kept on KN05; the three actives as separate same-style ingredient pills: 2% KOJIC "
        "ACID on the Kojic line over KN03 (top, clear of her face), NIACINAMIDE (x.30) and ALPHA ARBUTIN (x.70) over the "
        "icy and pink KNA2 orbs on L3/L4; new B/A split labels with captions at 0.58; the end claim now names all three "
        "actives in full ('ARBUTIN' alone is gone) and starts after the B/A."),
 "f7ce58d4": dict(
  elements=[
   {"type": "hook_mono", "start": 0.15, "end": 2.2, "lines": ["DARK SPOTS", "AGAIN?"], "position": "top", "anim": "slide_up"},
   KOJIC(5.07, 6.7),
   NIA(6.7, 8.3),
   AA(8.3, 9.9),
   *BA(12.1, 13.77),
   {"type": "blur", "start": 15.55, "end": 17.02, "box": {"x0": 0.1963, "y0": 0.7364, "x1": 0.8037, "y1": 0.7812}, "anim": None},
  ],
  caption_moves=[{"start": 12.1, "end": 13.77, "y": 0.58}],
  notes="Text pass (client EDL): the 'Dark spots again?' hook that was baked into the replaced opening returns as our "
        "hook on KN03; the three ingredient cards become plain same-style pills (no cover masks, KNA2 has no baked text) "
        "staggered over the gold, icy and pink orbs on L3/L4/L5; the corners HUD gives way to the new B/A split labels "
        "(captions at 0.58); the blur over the garbled '- Honeet Suience' tagline on the kept packshot stays."),
}

for vid, spec in G.items():
    path = f'{root}/{vid}/graphics.json'
    old = json.load(open(path, encoding='utf-8'))
    raw = open(path, encoding='utf-8').read()
    new = {"video_id": vid, "product": old["product"], "caption_y": old.get("caption_y", 0.9),
           "caption_moves": spec["caption_moves"], "elements": spec["elements"], "notes": spec["notes"]}
    tmp = path + '.tmp_textpass'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(new, f, ensure_ascii=False, indent=1)
        if raw.endswith('\n'):
            f.write('\n')
    os.replace(tmp, path)
    print(vid, len(spec["elements"]), 'elements')
