"""Swap the user's own General Ads (feedback/user_knc_ads, feedback/user_ps_ads) into our General-Ad slots.

usage: python3 feedback/setup_user_general_ads.py
Per slot: backs up work/<id> to post/superseded/general_ours/<id> (once), puts the user's video in as source.mp4 /
source_fixed.mp4, uses its own soundtrack (-6 dB) as the bed, writes the shot-by-shot English VO (plan.json),
the on-screen text (graphics.json: own end card, own music) and captions.json (title slug).
Then: .venv/bin/python feedback/ads_english_kokoro.py hf_beta a <ids>; render_post --langs en; add_audio; build_folders.
"""
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FP = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"
BACKUP = ROOT / "post" / "superseded" / "general_ours"


def lab(t, s, e, y):
    return {"type": "label", "start": s, "end": e, "lines": [t], "x": 0.5, "y": y, "anim": "pop"}


def hook(lines, s, e):
    return {"type": "hook_mono", "start": s, "end": e, "lines": lines, "position": "lower", "anim": "slide_up"}


def pill(lines, s, e, y=0.12):
    return {"type": "pill", "start": s, "end": e, "lines": lines, "x": 0.5, "y": y, "anim": "pop"}


def claim(lines, sub, s, e, y=0.76):
    return {"type": "claim_bold", "start": s, "end": e, "lines": lines, "sub": sub, "x": 0.5, "y": y, "anim": "fade"}


# slot id -> (product, user file, VO lines [(start, text)], text elements, caption moves)
ADS = {
    "a9be56d9": ("kojic_night_cream", "user_knc_ads/knc1.mp4", [
        (0.2, "Dark spots that just won't fade?"), (2.1, "Meet DERMDOC 2% Kojic Acid Night Cream."),
        (4.6, "One scoop at night, massaged in before bed."), (7.5, "It melts right in."),
        (9.0, "Inside the Glow Fusion Formula, Kojic Acid, Niacinamide and Alpha Arbutin work together"),
        (14.1, "to help reduce the look of dark spots."), (16.5, "You sleep. It works."), (18.3, "Available on Purplle.")],
        [hook(["DARK SPOTS?"], 0.2, 1.4), pill(["ONE SCOOP", "EVERY NIGHT"], 4.0, 6.0), lab("MELTS RIGHT IN", 6.5, 8.5, 0.80),
         claim(["GLOW FUSION", "FORMULA"], "KOJIC · NIACINAMIDE · ARBUTIN", 12.0, 14.0, 0.30), pill(["ALL SKIN TYPES"], 14.5, 16.5),
         pill(["YOU SLEEP.", "IT WORKS."], 16.6, 17.9, 0.30)], []),
    "426b77bb": ("kojic_night_cream", "user_knc_ads/knc2.mp4", [
        (0.2, "Your skin does its best work at night."), (2.6, "So give it DERMDOC 2% Kojic Acid Night Cream."),
        (6.4, "One jar. One step."), (8.0, "Apply it before bed."),
        (9.4, "Its Glow Fusion Formula works on the look of dark spots."), (12.6, "The overnight brightener."),
        (14.1, "While your skin renews, the actives keep working."), (16.9, "Wake up to brighter, more even-looking skin."),
        (19.6, "Available on Purplle.")],
        [hook(["NIGHT SHIFT", "FOR SKIN"], 0.2, 1.8), lab("APPLY AT NIGHT", 8.0, 9.2, 0.30),
         claim(["GLOW FUSION", "FORMULA"], "KOJIC · NIACINAMIDE · ARBUTIN", 9.4, 11.9, 0.30),
         claim(["WAKE UP", "BRIGHTER"], "MORE EVEN-LOOKING SKIN", 16.8, 18.9, 0.30)], []),
    "eab38211": ("kojic_night_cream", "user_knc_ads/knc3.mp4", [
        (0.2, "Spotted new dark spots in the mirror?"), (2.4, "Meet DERMDOC 2% Kojic Acid Night Cream."),
        (5.2, "Rich and creamy, yet light on skin."), (7.9, "One jar. One step."), (10.0, "Massage it in every night."),
        (12.1, "The overnight brightener."), (14.0, "Skin renews while you sleep,"),
        (16.0, "and Kojic Acid, Niacinamide and Alpha Arbutin work on the look of dark spots."),
        (22.3, "After two weeks: brighter, more even-looking skin."), (24.7, "Your overnight glow."),
        (26.4, "Available on Purplle.")],
        [hook(["NEW DARK", "SPOTS?"], 0.2, 1.9), lab("RICH. NEVER HEAVY.", 5.0, 7.0, 0.80), lab("EVERY NIGHT", 10.0, 11.8, 0.80),
         claim(["GLOW FUSION", "FORMULA"], "KOJIC · NIACINAMIDE · ARBUTIN", 16.2, 18.9, 0.20), pill(["3 ACTIVES", "1 JAR"], 19.2, 21.6),
         lab("BEFORE", 22.4, 24.3, 0.455), lab("AFTER 2 WEEKS", 22.4, 24.3, 0.895)], [(22.3, 24.4)]),
    "e9528636": ("kojic_night_cream", "user_knc_ads/knc4.mp4", [
        (0.3, "The overnight brightener is here."), (2.3, "DERMDOC 2% Kojic Acid Night Cream."),
        (4.7, "A rich cream that's light on skin."), (7.0, "Just one scoop at night."), (9.0, "Smooth and whipped."),
        (10.3, "It works while you sleep."), (12.2, "Smooth it on before bed."),
        (14.1, "Its three actives, Kojic Acid, Niacinamide and Alpha Arbutin,"),
        (17.5, "help reduce the look of dark spots, night after night."),
        (20.6, "Wake up to brighter, more even-looking skin."), (23.4, "Rich, never heavy."), (26.4, "Available on Purplle.")],
        [pill(["ONE SCOOP", "EACH NIGHT"], 6.2, 8.6), lab("APPLY BEFORE BED", 12.2, 13.8, 0.30),
         claim(["3 ACTIVES", "1 FORMULA"], "KOJIC · NIACINAMIDE · ARBUTIN", 14.3, 16.9, 0.20),
         claim(["WAKE UP", "BRIGHTER"], "MORE EVEN-LOOKING SKIN", 20.6, 23.0, 0.30), pill(["NEVER HEAVY"], 23.4, 25.6)], []),
    "b4c787e1": ("kojic_night_cream", "user_knc_ads/knc5.mp4", [
        (0.2, "Those dark spots again?"), (1.9, "Meet the overnight brightener: DERMDOC 2% Kojic Acid Night Cream."),
        (6.0, "A rich cream. One scoop is all you need."), (8.8, "Smooth, whipped, and light on skin."),
        (11.0, "It works while you sleep."), (13.0, "Massage it in before bed."),
        (15.4, "Its Glow Fusion Formula, Kojic Acid, Niacinamide and Alpha Arbutin,"),
        (19.2, "helps reduce the look of dark spots."), (21.3, "Wake up glowing."),
        (24.8, "After two weeks: brighter, more even-looking skin."), (27.7, "Rich, never heavy. Made for all skin types."),
        (30.8, "Available on Purplle.")],
        [hook(["DARK SPOTS", "AGAIN?"], 0.2, 1.8), pill(["ONE SCOOP"], 6.2, 8.4), lab("BEFORE BED", 13.0, 14.6, 0.80),
         claim(["GLOW FUSION", "FORMULA"], "KOJIC · NIACINAMIDE · ARBUTIN", 16.0, 18.9, 0.20),
         lab("BEFORE", 24.9, 26.5, 0.455), lab("AFTER 2 WEEKS", 24.9, 26.5, 0.895), pill(["ALL SKIN TYPES"], 27.7, 29.4)],
        [(24.8, 26.6)]),
    "c01adcce": ("uv_sunscreen", "user_ps_ads/ps1.mp4", [
        (0.2, "Worried about sun damage?"), (1.9, "DERMDOC 4% Niacinamide Brightening Sunscreen, with a purple tint."),
        (5.3, "SPF 50 PA+++ shields your skin from UVA and UVB rays,"), (8.6, "so you can step out protected and glowing."),
        (10.9, "Why purple? It sits opposite yellow on the colour wheel,"),
        (13.6, "so it cancels dull, yellow tones. Non-greasy and fast-absorbing."),
        (17.2, "Made for Indian skin: protected, even, glowing."), (20.2, "Available on Purplle.")],
        [claim(["SPF 50 PA+++"], "UVA + UVB", 5.3, 7.9, 0.30), lab("STEP OUT GLOWING", 8.6, 10.4, 0.80)], []),
    "fe7174d4": ("uv_sunscreen", "user_ps_ads/ps2.mp4", [
        (0.2, "Stepping out without sunscreen?"), (2.0, "Meet DERMDOC 4% Niacinamide Brightening Sunscreen."),
        (4.9, "SPF 50 PA+++ guards against UVA and UVB rays."), (7.8, "And its purple tint gives an instant glow."),
        (10.0, "On the colour wheel, purple cancels yellow,"),
        (12.3, "so it's instantly even. Non-greasy and fast-absorbing."),
        (15.2, "4% Niacinamide balances uneven skin tone."), (17.4, "Made for Indian skin: protected, even, glowing."),
        (20.2, "Available on Purplle.")],
        [claim(["SPF 50 PA+++"], "UVA + UVB", 4.9, 7.4, 0.30), lab("INSTANT GLOW", 7.8, 9.6, 0.80),
         pill(["BALANCES", "SKIN TONE"], 15.0, 16.9)], []),
    "fb3fa838": ("uv_sunscreen", "user_ps_ads/ps4.mp4", [
        (0.2, "Greasy sunscreen? Not this one."), (2.1, "DERMDOC 4% Niacinamide Brightening Sunscreen."),
        (4.7, "SPF 50 PA+++ against UVA and UVB,"), (7.2, "and 4% Niacinamide to strengthen your skin barrier."),
        (10.0, "It's non-greasy and absorbs fast."), (12.6, "The purple tint? Purple cancels yellow on the colour wheel,"),
        (15.5, "so dull, yellow tones look balanced, instantly."), (17.8, "Hello, instant glow."),
        (21.4, "One layer: brighter, more even-looking skin."), (24.8, "Available on Purplle.")],
        [claim(["SPF 50 PA+++"], "UVA + UVB", 4.8, 6.9, 0.30), pill(["CANCELS", "YELLOW TONES"], 15.4, 17.2),
         lab("INSTANT GLOW", 17.6, 19.4, 0.80), lab("BEFORE", 21.4, 23.5, 0.455), lab("AFTER", 21.4, 23.5, 0.895),
         lab("INSTANT GLOW", 21.4, 23.5, 0.955)], [(21.3, 23.6)]),
    "ce52c347": ("uv_sunscreen", "user_ps_ads/ps5.mp4", [
        (0.2, "Stepping out unprotected?"), (1.9, "DERMDOC 4% Niacinamide Brightening Sunscreen."),
        (4.6, "SPF 50 PA+++ shields from UVA and UVB,"), (7.2, "while Niacinamide strengthens your skin barrier."),
        (10.0, "Water resistant. Sweat proof."), (12.0, "And the purple tint? Purple cancels yellow on the colour wheel,"),
        (15.1, "so dull, yellow tones look even, instantly."), (17.4, "Light and fast-absorbing, never greasy."),
        (22.1, "One layer, and your glow shows instantly."), (24.7, "Made for Indian skin."), (28.4, "Available on Purplle.")],
        [claim(["SPF 50 PA+++"], "UVA + UVB", 4.7, 6.9, 0.30), pill(["CANCELS", "YELLOW TONES"], 15.0, 16.9),
         lab("NEVER GREASY", 17.4, 19.4, 0.80), lab("BEFORE", 22.15, 24.45, 0.455), lab("AFTER", 22.15, 24.45, 0.895),
         lab("INSTANT GLOW", 22.15, 24.45, 0.955), claim(["MADE FOR", "INDIAN SKIN"], None, 24.6, 26.8, 0.30)], [(22.05, 24.5)]),
    # GENERAL SS 3 (re-downloaded): every shot carries its own text, so VO only
    "4010f985": ("uv_sunscreen", "user_ps_ads/ps3.mp4", [(0.15, "Tired of sun damage?")], [], []),
}


def dur(p):
    return float(subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def main(ids=None):
    BACKUP.mkdir(parents=True, exist_ok=True)
    for vid, (product, src, vo, els, moves) in ADS.items():
        if ids and vid not in ids:
            continue
        wd = ROOT / "work" / vid
        if not (BACKUP / vid).exists():
            shutil.copytree(wd, BACKUP / vid)
            for f in ("edl_v2", "edl"):
                e = ROOT / "feedback" / f / f"{vid}.json"
                if e.exists():
                    shutil.move(str(e), str(BACKUP / vid / f"{f}.json"))
        s = ROOT / "feedback" / src
        D = round(dur(s), 3)
        shutil.copy(s, wd / "source.mp4")
        shutil.copy(s, wd / "source_fixed.mp4")
        subprocess.run([FF, "-v", "error", "-y", "-i", str(s), "-vn", "-af", "volume=0.5", "-ar", "44100", "-ac", "2",
                        str(wd / "stems" / "no_vocals.wav")], check=True)   # vocals.wav kept: loudness reference
        lines = []
        for i, (st, en) in enumerate(vo, 1):
            me = (vo[i][0] - 0.04) if i < len(vo) else D - 0.4
            lines.append({"id": i, "speaker": "narrator", "start": st, "end": round(me - 0.1, 2), "max_end": round(me, 2),
                          "en": en, "tag": None, "keep_original": False, "bn": "", "ta": "", "te": "", "ml": "", "or": ""})
        plan = json.loads((wd / "plan.json").read_text())
        plan.update({"duration": D, "lines": lines, "notes": f"user's own General Ad ({src}); English VO written shot by shot"})
        (wd / "plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1))
        g = {"video_id": vid, "product": product, "caption_y": 0.9, "no_outro": True, "own_music": True,
             "caption_moves": [{"start": a, "end": b, "y": 0.58} for a, b in moves],
             "elements": [{k: v for k, v in e.items() if v is not None} for e in els],
             "notes": "user's General Ad: text only where the footage has none baked in; own end card + music"}
        (wd / "graphics.json").write_text(json.dumps(g, indent=1, ensure_ascii=False))
        words = re.findall(r"[\w'%+]+[?.!,]?", vo[0][1])
        (wd / "captions.json").write_text(json.dumps({"language": "en", "script": "latin",
                                                      "words": [{"w": w, "s": 0, "e": 0} for w in words]}))
        m = json.loads((wd / "meta.json").read_text())
        m["duration"] = D
        (wd / "meta.json").write_text(json.dumps(m))
        print(f"{vid}: {src} {D:.1f}s, {len(lines)} lines, {len(els)} text elements")


if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
