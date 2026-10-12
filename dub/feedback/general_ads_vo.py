"""Shot-locked English VO for the user's General Ads (voice hf_alpha, Indian-English G2P "h").

Each line: (start, window_end, text) — window_end = end of the shot(s) the line talks about, so the words land on the
right frames. usage: .venv/bin/python feedback/general_ads_vo.py check   -> synth every line, report fit per window
                     .venv/bin/python feedback/general_ads_vo.py apply   -> write plan.json lines (window_end kept)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VO = {
    # KNC 1 — mirror 0-0.9 | jar opens 0.9-3.6 | scoop 3.6-5.9 | applying 6-8.9 | cells+tags 9-11.9 | jar orbs 12-13.9 |
    # cream 14-16.9 | asleep 17-17.9 | end card 18+
    "a9be56d9": [(0.15, 2.0, "Dark spots stealing your glow?"),
                 (2.05, 5.8, "Meet DERMDOC 2% Kojic Acid Night Cream."),
                 (6.0, 8.9, "Massage it in every night."),
                 (9.0, 12.0, "Kojic Acid, Niacinamide, Alpha Arbutin."),
                 (12.05, 14.0, "Fading the look of dark spots."),
                 (14.2, 16.9, "Rich, never heavy."),
                 (17.0, 18.6, "You sleep. It works."),
                 (18.7, 23.0, "Shop now at Purplle.com.")],
    # KNC 2 — face 0-1 | jar opens 1-3.5 | scoop+swirl 3.5-6.5 | ONE JAR 6.5-7.6 | bathrobe 7.6-8.9 | layers 9-9.9 |
    # jar orbs 10-11.9 | OVERNIGHT cell 12-14.4 | constellation 14.4-16.9 | cream/jar 16.9-18.9 | end card 19+
    "426b77bb": [(0.15, 3.4, "Night is when your skin does its best work."),
                 (3.5, 6.5, "DERMDOC 2% Kojic Acid Night Cream."),
                 (6.6, 7.7, "One jar. One step."),
                 (7.8, 9.0, "Apply before bed."),
                 (9.1, 12.0, "Glow Fusion Formula, on dark spots."),
                 (12.1, 14.4, "The overnight brightener."),
                 (14.5, 16.9, "Skin renews, the actives work."),
                 (17.0, 19.3, "Wake up brighter."),
                 (19.6, 24.0, "Shop now at Purplle.com.")],
    # KNC 3 — mirror 0-2 | jar blue 2-3.5 | lid+peak 3.5-6.2 | spatula 6.2-8 | swirl+ONE JAR 8-9.9 | applying 10-11.9 |
    # OVERNIGHT cell 12-14.2 | constellation 14.2-16.7 | layers+actives 16.7-19.9 | jar orbs 19.9-22.2 | B/A 22.25-24.4 |
    # cream 24.4-25.9 | end card 26+
    "eab38211": [(0.15, 2.1, "New dark spots again?"),
                 (2.2, 6.1, "Meet DERMDOC 2% Kojic Acid Night Cream."),
                 (6.25, 8.0, "Rich, yet light."),
                 (8.1, 9.9, "One jar. One step."),
                 (10.0, 12.0, "Massage it in at night."),
                 (12.1, 14.2, "The overnight brightener."),
                 (14.3, 16.7, "Skin renews while you sleep."),
                 (16.8, 19.9, "Kojic Acid, Niacinamide, Alpha Arbutin."),
                 (20.0, 22.2, "On the look of dark spots."),
                 (22.3, 24.4, "After two weeks: brighter."),
                 (24.5, 25.9, "Your overnight glow."),
                 (26.3, 31.0, "Shop now at Purplle.com.")],
    # KNC 4 — jar on milk 0-1.7 | jar blue 1.7-4.2 | lid+peak 4.2-6.9 | spatula 6.9-8.9 | swirl 9-9.9 | OVERNIGHT cell 10-12.3 |
    # bathrobe+fingers 12.3-13.9 | cream into cells 14-15.2 | streams 15.2-17.2 | constellation 17.2-19.7 |
    # jar orbs 19.7-21.9 | ribbon+jar 22-25.9 | end card 26+
    "e9528636": [(0.15, 1.75, "The overnight brightener."),
                 (1.8, 4.2, "DERMDOC Kojic Acid Night Cream."),
                 (4.3, 6.9, "Rich, whipped, light on skin."),
                 (7.0, 8.9, "One scoop at night."),
                 (10.0, 12.3, "It works while you sleep."),
                 (12.35, 13.95, "Smooth it on."),
                 (14.0, 15.2, "Three actives,"),
                 (15.25, 17.2, "Kojic, Niacinamide, Arbutin,"),
                 (17.25, 19.7, "on the look of dark spots."),
                 (19.75, 22.0, "Wake up brighter."),
                 (22.5, 25.9, "Rich, never heavy."),
                 (26.3, 30.9, "Shop now at Purplle.com.")],
    # KNC 5 — mirror 0-2 | jar on milk 2-4.6 | lid 4.6-5.9 | spatula 6-8.9 | swirl 9-10.9 | OVERNIGHT cell 11-12.9 |
    # applying 13-14.9 | cream into cells 15.9-16.9 | streams 17-19 | jar orbs 19-20.9 | in bed 21-22.6 |
    # B/A 24.75-26.6 | jar 27-28.9 | asleep 29-29.9 | end card 30+
    "b4c787e1": [(0.15, 2.0, "Those dark spots again?"),
                 (2.1, 4.6, "Meet the overnight brightener."),
                 (4.7, 8.9, "DERMDOC 2% Kojic Acid Night Cream."),
                 (9.0, 10.9, "Smooth and whipped."),
                 (11.0, 12.9, "It works while you sleep."),
                 (13.0, 15.0, "Massage it in at night."),
                 (15.9, 19.0, "Kojic Acid, Niacinamide, Alpha Arbutin,"),
                 (19.05, 20.9, "on the look of dark spots."),
                 (21.0, 22.6, "Wake up glowing."),
                 (24.8, 26.6, "After two weeks: brighter."),
                 (27.0, 28.9, "Rich, never heavy."),
                 (29.0, 30.1, "You sleep."),
                 (30.5, 35.3, "Shop now at Purplle.com.")],
    # PS 1 — face scan 0-2.5 | tube on cream 2.7-5.9 | shield 5.9-8.3 | city woman 8.3-11.3 | wheel 11.3-13.5 |
    # split face 13.5-15.8 | tube macro 15.8-17.6 | face 17.6-20.4 | end card 20.4+
    "c01adcce": [(0.15, 2.5, "Worried about sun damage?"),
                 (2.7, 5.9, "DERMDOC 4% Niacinamide sunscreen."),
                 (5.95, 8.3, "SPF 50 PA+++."),
                 (8.4, 11.3, "Step out protected, and glowing."),
                 (11.35, 13.5, "Purple cancels yellow dullness."),
                 (13.55, 15.8, "Non-greasy, fast-absorbing."),
                 (15.85, 17.6, "Instant glow."),
                 (17.65, 20.4, "Made for Indian skin."),
                 (20.6, 24.8, "Shop now at Purplle.com.")],
    # PS 2 — spots 0-2 | tube macro 2.2-4.7 | flash+shield 4.7-7.8 | city woman 7.8-10.7 | wheel 10.7-12.9 |
    # split face 12.9-15.2 | tube podium 15.2-17 | face 17-19.8 | end card 19.8+
    "fe7174d4": [(0.15, 2.1, "Stepping out unprotected?"),
                 (2.2, 4.7, "DERMDOC 4% Niacinamide sunscreen."),
                 (4.9, 7.8, "SPF 50 PA+++."),
                 (7.9, 10.7, "And the purple tint? Instant glow."),
                 (10.75, 12.9, "Purple cancels yellow dullness."),
                 (12.95, 15.2, "Non-greasy, fast-absorbing."),
                 (15.25, 17.0, "Balances skin tone."),
                 (17.05, 19.8, "Made for Indian skin."),
                 (20.0, 24.3, "Shop now at Purplle.com.")],
    # PS 4 — applying cheek 0-1.7 | tube on cream 1.7-5.5 | rays barrier 5.5-7.1 | swatch+woman 7.9-10.8 |
    # rubbing 10.8-13.1 | wheel 13.1-15.3 | tube podium 15.4-17 | woman smiling 17-19.9 | tube marble 20-21.2 |
    # B/A 21.25-23.6 | end card 24.5+
    "fb3fa838": [(0.15, 1.75, "Greasy sunscreen? Not this."),
                 (1.8, 5.45, "DERMDOC 4% Niacinamide sunscreen."),
                 (5.5, 7.85, "SPF 50 PA+++."),
                 (7.9, 10.8, "Niacinamide strengthens your barrier."),
                 (10.85, 13.1, "Non-greasy, absorbs fast."),
                 (13.15, 15.35, "Purple cancels yellow dullness."),
                 (15.4, 17.0, "For an even look."),
                 (17.1, 19.9, "Hello, instant glow."),
                 (21.3, 23.6, "One layer. Brighter."),
                 (24.6, 28.5, "Shop now at Purplle.com.")],
    # PS 5 — spots 0-2 | tube on cream 2.2-5.2 | rays barrier 5.2-7.6 | swatch+woman 7.6-10.5 | water drops 10.5-12.8 |
    # wheel 12.8-15 | tube podium 15.1-17.5 | spheres 17.5-20.2 | tube marble 20.2-22.1 | B/A 22.1-24.5 |
    # tube macro 25-27.4 | end card 28+
    "ce52c347": [(0.15, 2.1, "Stepping out unprotected?"),
                 (2.25, 5.2, "DERMDOC 4% Niacinamide sunscreen."),
                 (5.25, 7.6, "SPF 50 PA+++."),
                 (7.65, 10.5, "Niacinamide strengthens your barrier."),
                 (10.55, 12.8, "Water resistant. Sweat proof."),
                 (12.85, 15.0, "Purple cancels yellow dullness."),
                 (15.1, 17.5, "For an instantly even look."),
                 (17.55, 20.2, "Light, and never greasy."),
                 (22.15, 24.5, "One layer. Instant glow."),
                 (25.0, 27.4, "Made for Indian skin."),
                 (28.3, 32.0, "Shop now at Purplle.com.")],
    # PS 3 — spots 0-2.1 | tube on cream 2.1-5.3 | rays/shield on skin 5.3-7.75 | woman + shield 7.75-10.7 |
    # wheel 10.7-12.9 | cells 12.9-15.2 | tube podium 15.25-17 | water drops 17-19.3 | flash | end card 19.8+
    "4010f985": [(0.15, 2.05, "Tired of sun damage?"),
                 (2.15, 5.25, "DERMDOC 4% Niacinamide sunscreen."),
                 (5.35, 7.7, "SPF 50 PA+++."),
                 (7.8, 10.65, "It shields, and you glow."),
                 (10.75, 12.85, "Purple cancels yellow dullness."),
                 (12.95, 15.2, "Niacinamide strengthens your barrier."),
                 (15.3, 17.0, "Made for Indian skin."),
                 (17.05, 19.3, "Water resistant. Sweat proof."),
                 (19.9, 24.3, "Shop now at Purplle.com.")],
}
SAY_H = [(r"SPF 50 PA\+\+\+", "S P F fifty, P A triple plus"), (r"SPF 50", "S P F fifty"), (r"\bDERMDOC\b", "Dermdoc"),
         (r"\b2%", "two percent"), (r"\b4%", "four percent"), (r"\bPurplle\.com\b", "Purple dot com"), (r"\bPurplle\b", "Purple"), (r"\bUVA and UVB\b", "U V A and U V B"),
         (r"\bUVA\b", "U V A"), (r"\bUVB\b", "U V B")]


def speak_h(t):
    import re
    for a, b in SAY_H:
        t = re.sub(a, b, t)
    return t


def check():
    import numpy as np
    from kokoro import KPipeline
    pipe = KPipeline(lang_code="h", repo_id="hexgrad/Kokoro-82M")
    bad = 0
    for vid, lines in VO.items():
        for s, e, t in lines:
            a = np.concatenate([np.asarray(x.numpy() if hasattr(x, "numpy") else x, dtype=np.float32)
                                for _, _, x in pipe(speak_h(t), voice="hf_alpha", speed=1.1)])
            nz = np.nonzero(np.abs(a) > 0.01)[0]
            d = (nz[-1] - nz[0]) / 24000 if len(nz) else 0
            need = d / 1.3 * 1.1   # fastest allowed = 1.3x
            flag = "OK" if d <= e - s else ("FAST" if need <= e - s else "TOO LONG")
            bad += flag == "TOO LONG"
            print(f"{vid} {s:5.2f}-{e:5.2f} ({e - s:4.2f}s) speech {d:4.2f}s @1.1  {flag:8s} {t}", flush=True)
    print("TOO LONG:", bad)


def apply(ids=None):
    for vid, lines in VO.items():
        if ids and vid not in ids:
            continue
        wd = ROOT / "work" / vid
        p = json.loads((wd / "plan.json").read_text())
        p["lines"] = [{"id": i, "speaker": "narrator", "start": s, "end": e, "max_end": e, "window_end": e, "en": t,
                       "tag": None, "keep_original": False, "bn": "", "ta": "", "te": "", "ml": "", "or": ""}
                      for i, (s, e, t) in enumerate(lines, 1)]
        (wd / "plan.json").write_text(json.dumps(p, ensure_ascii=False, indent=1))
        g = json.loads((wd / "graphics.json").read_text())
        g["own_music"] = False   # client: only our VO + SFX + music, none of the footage's sound
        (wd / "graphics.json").write_text(json.dumps(g, indent=1, ensure_ascii=False))
        print(vid, len(lines), "lines")


if __name__ == "__main__":
    {"check": check, "apply": lambda: apply(sys.argv[2:])}[sys.argv[1]]()
