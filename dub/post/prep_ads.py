"""Prep original-language (Hinglish) ads for post-production: no dubbing, captions from the original voice.

Usage: nice -n 10 .venv/bin/python post/prep_ads.py gens_last10.json
Per video writes work/<id8>/: source.mp4, prompt.txt, meta.json (kind=ad), transcript.json, plan.json (lines for the
graphics directors; no plan.ok so the dubbing engine ignores it), captions.json (word timings), and post/sheets/<id>.png.
"""
import json
import re
import subprocess
import sys
import urllib.request
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import mlx_whisper

ROOT = Path(__file__).resolve().parent.parent
WHISPER = "mlx-community/whisper-large-v3-turbo"


def vo_script(prompt):
    """The quoted voiceover script inside the prompt (steers Whisper's Hinglish spelling)."""
    m = re.search(r"VOICE ?OVER[^:]*:\s*[“\"]([^”\"]+)[”\"]", prompt, re.I)
    if m:
        return m.group(1)
    quotes = re.findall(r"[“\"]([^”\"]{12,})[”\"]", prompt)
    return " ".join(quotes)[:600]


def main(gens_path):
    for g in json.loads(Path(gens_path).read_text()):
        vid = g["id"][:8]
        wd = ROOT / "work" / vid
        wd.mkdir(parents=True, exist_ok=True)
        src = wd / "source.mp4"
        if not src.exists():
            urllib.request.urlretrieve(g["results"]["rawUrl"], src)
        prompt = g["params"].get("prompt") or ""
        (wd / "prompt.txt").write_text(prompt)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", src],
                                   capture_output=True, text=True, check=True).stdout)
        (wd / "meta.json").write_text(json.dumps({"id": g["id"], "createdAt": g["createdAt"], "duration": dur,
                                                  "kind": "ad", "language": "hinglish"}))
        sheet = ROOT / "post" / "sheets" / f"{vid}.png"
        if not sheet.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-vf", "fps=1,scale=216:-1,tile=5x4",
                            "-frames:v", "1", sheet], check=True)
        hint = vo_script(prompt)
        r = mlx_whisper.transcribe(str(src), path_or_hf_repo=WHISPER, language="en", word_timestamps=True,
                                   initial_prompt=hint or None, condition_on_previous_text=False)
        segs = [{"seg": i, "start": round(s["start"], 2), "end": round(s["end"], 2), "text": s["text"].strip(),
                 "words": [[w["word"].strip(), round(w["start"], 2), round(w["end"], 2)] for w in s.get("words", [])]}
                for i, s in enumerate(r["segments"])]
        (wd / "transcript.json").write_text(json.dumps({"language": "hinglish", "vo_script": hint, "segments": segs},
                                                       ensure_ascii=False, indent=1))
        words = [{"w": w, "s": s, "e": e} for seg in segs for w, s, e in seg["words"] if w]
        (wd / "captions.json").write_text(json.dumps({"language": "hinglish", "script": "latin", "words": words},
                                                     ensure_ascii=False, indent=1))
        lines = [{"id": i + 1, "speaker": "narrator", "start": s["start"], "end": s["end"], "en": s["text"]}
                 for i, s in enumerate(segs)]
        (wd / "plan.json").write_text(json.dumps({"video_id": vid, "kind": "ad", "style": "product_ad", "duration": dur,
                                                  "cast": [{"id": "narrator", "name": "Voiceover", "role": "narrator"}],
                                                  "lines": lines}, ensure_ascii=False, indent=1))
        print(f"{vid}: {len(words)} words, {len(segs)} lines | {' '.join(w['w'] for w in words)[:110]}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1])
