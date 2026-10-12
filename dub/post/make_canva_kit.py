"""Canva hand-off kit: every delivered ad split into layers a Canva editor can rebuild / change by hand.

Per ad -> Canva_Kit/<Category>/<Product>/<NN>_<title>_<id>/
  00_original_generation.mp4        the raw footage we started from (Higgsfield / user clip, before our edit)
  01_clean_video_no_text.mp4        edited picture, AI text erased, NO graphics / captions / logo / end slate, no audio
  02_video_with_text_and_endslate.mp4  same picture + our on-screen text + logo + company end slate (no captions, no audio)
  03_text_stickers/*.png            every on-screen text card as a transparent 1080x1920 PNG (drop full-size = exact spot)
  audio/voice_<Lang>.m4a            dialogue / VO (+ the clip's own ambience) on the final timeline (incl. end slate)
  audio/music_<Lang>.m4a            background music, already ducked under that language's voice
  audio/sfx.m4a                     whooshes / pops / dings, language independent
  captions/<Lang>.srt               the burned-in captions as text
  ON_SCREEN_TEXT.csv                every text card: start, end, type, text, position
  REFERENCE_final_<Lang>.mp4        one delivered final to match against
All audio files and video 02 have the same length, so stacking them at 0:00 in Canva reproduces the final.
usage: .venv/bin/python post/make_canva_kit.py [--jobs 5] [<id> ...]
"""
import csv
import json
import re
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import add_audio as AA  # noqa: E402
import build_folders as BF  # noqa: E402
import render_post as R  # noqa: E402

ROOT = R.ROOT
KIT = ROOT / "Canva_Kit"
FF, FP = R.FFMPEG, R.FFPROBE
LANGS = {"Bengali": "bn", "Tamil": "ta", "Telugu": "te", "Malayalam": "ml", "Odia": "or", "English": "en"}
CAT = {"personification": "1_Ingredient_Personified", "product_avatar": "2_Product_Avatar", "ugc": "3_UGC_Ads",
       "product_ad": "4_AI_General_Ads"}
PROD = {"uv_sunscreen": "Purple_Sunscreen_PS", "kojic_night_cream": "KNC"}


def ff(*args):
    r = subprocess.run([FF, "-v", "error", "-y", *map(str, args)], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(r.stderr[-400:])


def dur_of(p):
    return float(subprocess.run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                                capture_output=True, text=True).stdout)


def videos():
    """id -> {lang_name: deliver_music file} for everything that ships (same rules as build_folders.py)."""
    out = {}
    for f in sorted((ROOT / "deliver_music").glob("*/*.mp4")):
        lang, vid = f.parent.name, f.stem.split("_")[-1]
        if lang not in LANGS:
            continue
        style = json.loads((ROOT / "work" / vid / "plan.json").read_text())["style"]
        if (style == "product_ad") != (lang == "English"):
            continue
        out.setdefault(vid, {})[lang] = f
    return out


def ts(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def slug(s, n=40):
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")[:n] or "text"


def graphics_ass(g, lang):
    cap = R.CapText(lang)
    top, bot = R.caption_box_metrics(cap)
    ass = R.Ass()
    R.add_graphics(ass, g, R.Placer(g, (top + bot) / 2 + R.CAPTION_PAD_Y + 6))
    return ass


def stickers(vid, g, ass, dur, dst):
    """one transparent PNG per on-screen element (each element owns a 10-layer band in the ASS)."""
    dst.mkdir(parents=True, exist_ok=True)
    els = sorted((e for e in g.get("elements", []) if "start" in e and e.get("type") not in ("hud", "blur")),
                 key=lambda e: float(e["start"]))
    bands = {}
    for ev in ass.events:
        bands.setdefault(max(0, (ev[0] - 20) // 10), []).append(ev)
    rows = []
    for k, evs in sorted(bands.items()):
        evs = [e for e in evs if e[1] < dur]
        if not evs:
            continue
        a, b = max(e[1] for e in evs), min(e[2] for e in evs)
        t = min(a + 0.45, (a + b) / 2) if b > a else (min(e[1] for e in evs) + max(e[2] for e in evs)) / 2
        e = els[k] if k < len(els) else {}
        txt = " / ".join(e.get("lines") or []) + (f" ({e['sub']})" if e.get("sub") else "")
        one = R.Ass()
        one.events = evs
        ap = dst / f"_{k}.ass"
        ap.write_text(one.dump(), encoding="utf-8")
        png = dst / f"{k + 1:02d}_{e.get('start', t):05.2f}s_{slug(txt)}.png"
        ff("-f", "lavfi", "-i", f"color=c=black@0.0:s={R.W}x{R.H}:r={R.FPS}:d={t + 0.2:.3f},format=rgba",
           "-vf", f"ass=filename='{R.esc(ap)}':fontsdir='{R.esc(R.FONT_DIR)}':shaping=complex:alpha=1,"
                  f"trim=start={t:.3f}", "-frames:v", "1", png)
        ap.unlink()
        rows.append([f"{k + 1:02d}", e.get("start", ""), e.get("end", ""), e.get("type", ""), txt,
                     e.get("position") or (f"x={e.get('x')} y={e.get('y')}" if "y" in e else ""), png.name])
    return rows


def build(vid, files):
    wd = ROOT / "work" / vid
    g = json.loads((wd / "graphics.json").read_text())
    plan = json.loads((wd / "plan.json").read_text())
    langs = [l for l in LANGS if l in files]
    title = files[langs[0]].stem[: -len(vid) - 1]
    d = KIT / CAT[plan["style"]] / PROD[g["product"]] / f"{title}_{vid}"
    if d.exists():
        shutil.rmtree(d)
    (d / "audio").mkdir(parents=True)
    (d / "captions").mkdir()
    job, why = R.prepare(vid, LANGS[langs[0]])
    if not job:
        return f"FAIL {vid}: {why}"
    no_outro = bool(g.get("no_outro"))
    total = job.dur + (0 if no_outro else R.OUTRO_DUR)
    # 00 raw footage, 01 clean edited picture
    orig = wd / "source.orig.mp4" if (wd / "source.orig.mp4").exists() else wd / "source.mp4"
    shutil.copy2(orig, d / "00_original_generation.mp4")
    ff("-i", job.src, "-map", "0:v", "-t", f"{job.dur:.3f}", "-c:v", "copy", "-an", d / "01_clean_video_no_text.mp4")
    # 02 picture + graphics + logo + end slate, no captions
    ass = graphics_ass(g, LANGS[langs[0]])
    ga = d / "_graphics.ass"
    ga.write_text(ass.dump(), encoding="utf-8")
    job.ass_path = ga
    ff(*R.inputs(job), "-filter_complex", R.filter_graph(job, False), "-map", "[v]", "-an", "-c:v", "libx264",
       "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-threads", "3", "-movflags", "+faststart",
       d / "02_video_with_text_and_endslate.mp4")
    ga.unlink()
    # 03 stickers + text sheet
    rows = stickers(vid, g, ass, job.dur, d / "03_text_stickers")
    with open(d / "ON_SCREEN_TEXT.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["#", "start_s", "end_s", "type", "text", "position", "sticker_png"])
        w.writerows(rows)
    # audio: sfx (shared), per language voice + ducked music, captions
    _, sfx = AA.build(vid, total, BANK)
    AA.write_wav(d / "audio" / "_sfx.wav", sfx)
    ff("-i", d / "audio" / "_sfx.wav", "-c:a", "aac", "-b:a", "192k", d / "audio" / "sfx.m4a")
    bed = BEDS[g["product"]][: int(total * AA.SR)].copy()
    fi, fo = int(0.8 * AA.SR), int(1.8 * AA.SR)
    bed[:fi] *= np.linspace(0, 1, fi)[:, None]
    bed[-fo:] *= np.linspace(1, 0, fo)[:, None]
    own_music = bool(g.get("own_music"))
    if not own_music:
        AA.write_wav(d / "audio" / "_bed.wav", bed)
    for lang in langs:
        code = LANGS[lang]
        lj, _ = R.prepare(vid, code) if lang != langs[0] else (job, "")
        voice = d / "audio" / f"voice_{lang}.m4a"
        pad = "" if no_outro else f",apad=whole_dur={total:.3f}"
        ff("-i", lj.src, "-map", "0:a", "-af", f"atrim=duration={job.dur:.3f},aresample=48000{pad}",
           "-ac", "2", "-c:a", "aac", "-b:a", "192k", voice)
        if not own_music:
            ff("-i", voice, "-i", d / "audio" / "_bed.wav", "-filter_complex",
               f"[0:a]aresample=48000[sc];[1:a][sc]sidechaincompress=threshold=0.03:ratio=3:attack=30:release=600:makeup=1,apad,atrim=duration={total:.3f}[m]",
               "-map", "[m]", "-c:a", "aac", "-b:a", "192k", d / "audio" / f"music_{lang}.m4a")
        with open(d / "captions" / f"{lang}.srt", "w", encoding="utf-8") as fh:
            for i, c in enumerate(lj.chunks, 1):
                fh.write(f"{i}\n{ts(c.t0)} --> {ts(c.t1)}\n{' '.join(w.text for w in c.words)}\n\n")
    for f in ("_sfx.wav", "_bed.wav"):
        (d / "audio" / f).unlink(missing_ok=True)
    ref = final_of(files[langs[0]])
    if ref:
        shutil.copy2(ref, d / f"REFERENCE_final_{langs[0]}.mp4")
    (d / "EDIT_NOTES.txt").write_text(
        f"Ad id {vid} | {CAT[plan['style']]} | {PROD[g['product']]} | languages: {', '.join(langs)}\n"
        f"Picture length {job.dur:.2f}s" + ("" if no_outro else f" + {R.OUTRO_DUR:.0f}s company end slate") +
        f" = {total:.2f}s total.\n"
        + ("The footage itself ends on the company end card (no separate end slate appended).\n" if no_outro else
           f"End slate starts at {job.dur:.2f}s (file: _shared/end_slates/).\n")
        + ("Music: the footage carries its own soundtrack (inside voice_*.m4a); no separate music file.\n" if own_music else "")
        + f"\nCanva stack (bottom -> top), everything starts at 0:00:\n"
          f"  video : 02_video_with_text_and_endslate.mp4  (or 01 clean + end slate + stickers if you change text)\n"
          f"  audio : voice_<Lang>.m4a 100%, music_<Lang>.m4a 100%, sfx.m4a 100%\n"
          f"  text  : burn captions from captions/<Lang>.srt if the client wants subtitles\n\n"
          f"Story / VO lines (English meaning):\n"
        + "".join(f"  {l['start']:6.2f}s  {l.get('en', '')}\n" for l in plan.get("lines", [])), encoding="utf-8")
    return f"ok   {vid} {len(langs)} langs, {len(rows)} stickers -> {d.relative_to(KIT)}"


def final_of(f):
    """deliver_music file -> the delivered (loudness-normalised) file in Final_Deliverables."""
    dst = BF.dest(f)
    if dst is None:
        return None
    alt = dst.with_name(dst.stem + f"_{f.stem.split('_')[-1]}.mp4")
    return alt if alt.exists() else dst if dst.exists() else None


def main():
    args = sys.argv[1:]
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else 5
    ids = [a for a in args if re.fullmatch(r"[0-9a-f]{8}", a)]
    vids = videos()
    if ids:
        vids = {k: v for k, v in vids.items() if k in ids}
    with ThreadPoolExecutor(jobs) as ex:
        for msg in ex.map(lambda kv: safe(*kv), vids.items()):
            print(msg, flush=True)
    print(f"KIT DONE {len(vids)} ads -> {KIT}")


def safe(vid, files):
    try:
        return build(vid, files)
    except Exception as ex:
        return f"FAIL {vid}: {ex!r}"[:600]


BEDS = {k: np.load(AA.CACHE / f"bed_{k}.npy") for k in ("uv_sunscreen", "kojic_night_cream")}
BANK = AA.sfx_bank()

if __name__ == "__main__":
    main()
