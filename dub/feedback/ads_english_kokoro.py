"""Indian-English voice-over for the 10 General Ads with Kokoro (free, local) — replaces the Indic-Mio English take.

usage: .venv/bin/python feedback/ads_english_kokoro.py <voice> <lang> [<id> ...]   e.g. hf_alpha h
Per line: text from plan.json lines[*].en (brand terms respelled for the TTS), synthesised at speed 1.0, sped up (max
1.2x) only if it would overrun its slot (next line's start - 0.1 s). Lines are written to out/<id>_en/line_<n>.wav and
laid onto the ad timeline by assemble.main (same as the dubs), then the rebuilt picture is remuxed in.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from kokoro import KPipeline

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "feedback"))
import assemble  # noqa: E402
from general_ads_vo import speak_h  # noqa: E402

ADS = "4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1".split()
SR = 24000
SAY = [(r"SPF 50 PA\+\+\+", "S P F fifty, P A triple plus"), (r"SPF 50", "S P F fifty"), (r"PA\+\+\+", "P A triple plus"),
       (r"\bDERMDOC\b", "[Dermdoc](/dˈɜɹmdˌɔk/)"), (r"\bKojic\b", "[Kojic](/kˈOʤɪk/)"), (r"\b2%", "two percent"), (r"\b4%", "four percent"), (r"\bUVA and UVB\b", "U V A and U V B")]


def speak(t):
    for a, b in SAY:
        t = re.sub(a, b, t)
    return t


# broadcast finish: low cut, a little warmth and presence, softer sibilance, gentle compression, peak -1 dB
ENHANCE = ("highpass=f=80,equalizer=f=220:t=q:w=1:g=2,equalizer=f=3800:t=q:w=1.2:g=3,highshelf=f=9000:g=2,"
           "deesser=i=0.4,acompressor=threshold=-20dB:ratio=3:attack=5:release=80:makeup=3,alimiter=limit=0.89")


def enhance(path):
    tmp = path.with_suffix(".raw.wav")
    path.rename(tmp)
    subprocess.run(["/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg", "-v", "error", "-y", "-i", str(tmp), "-af", ENHANCE,
                    "-ar", "48000", str(path)], check=True)
    tmp.unlink()


def synth(pipe, voice, text, speed):
    parts = [np.asarray(a.numpy() if hasattr(a, "numpy") else a, dtype=np.float32) for _, _, a in pipe(text, voice=voice, speed=speed)]
    wav = np.concatenate(parts) if parts else np.zeros(1, np.float32)
    nz = np.nonzero(np.abs(wav) > 0.01)[0]   # trim leading/trailing silence
    return wav[max(0, nz[0] - 240): nz[-1] + 1200] if len(nz) else wav


def main(voice, lang, ids):
    pipe = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")
    import assemble_fix
    for v in ids:
        wd = ROOT / "work" / v
        plan = json.loads((wd / "plan.json").read_text())
        lines = plan["lines"]
        clips = ROOT / "out" / f"{v}_en"
        clips.mkdir(parents=True, exist_ok=True)
        for i, l in enumerate(lines):
            slot = (lines[i + 1]["start"] - 0.1 if i + 1 < len(lines) else plan["duration"] - 0.2) - l["start"]
            if "window_end" in l:   # shot-locked line: must finish inside the shot(s) it talks about
                slot = l["window_end"] - l["start"]
            say = speak_h(l["en"]) if lang == "h" else speak(l["en"])
            base, top = (1.1, 1.3) if lang == "h" else (1.0, 1.2)   # the Indian-English G2P speaks slower
            wav = synth(pipe, voice, say, base)
            if len(wav) / SR > slot:
                sp = min(top, base * len(wav) / SR / slot + 0.02)
                wav = synth(pipe, voice, say, sp)
            sf.write(clips / f"line_{l['id']}.wav", wav, SR)
            enhance(clips / f"line_{l['id']}.wav")
            print(f"  {v} L{l['id']}: {len(wav) / SR:.2f}s / slot {slot:.2f}s", flush=True)
        (clips / "script.json").write_text(json.dumps({"language": "en", "lines": lines}, ensure_ascii=False))
        stems = wd / "stems"
        assemble.main(clips / "script.json", clips, str(ROOT / "out" / f"{v}_en.mp4"), wd / "source.mp4",
                      stems / "no_vocals.wav", stems / "vocals.wav")
        assemble_fix.remux(v)
        print(f"{v}: voiced ({voice}/{lang})", flush=True)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:] or ADS)
