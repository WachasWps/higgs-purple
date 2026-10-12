"""Re-voice only the lines listed in work/<id>/redub.json (changed text, new lines, or recast speakers), all 5 languages,
then re-assemble out/<id>_<lang>.mp4 over the fixed picture (work/<id>/source_fixed.mp4 if present).

redub.json: {"lines": [3, 5, 9]}   (ids from the current plan.json; new lines must already be in plan.json with timing)
usage: nice -n 10 .venv/bin/python redub.py <id> [<id> ...]      (one ML process at a time — Mac limits)
"""
import json
import sys
import time
from pathlib import Path

import soundfile as sf

import assemble
import guard
from dubplan import LANGS, TAKES, Engine

ROOT = Path(__file__).resolve().parent
WORK, OUT = ROOT / "work", ROOT / "out"


def redub(eng, vid):
    wd = WORK / vid
    spec = json.loads((wd / "redub.json").read_text())
    plan = json.loads((wd / "plan.json").read_text())
    lines = {l["id"]: l for l in plan["lines"]}
    ids = [i for i in spec["lines"] if i in lines and not lines[i].get("keep_original")]
    voices, vox = eng.voices(plan, wd / "stems" / "vocals.wav")
    pool = eng.sample([(lang, lines[i]) for lang in LANGS for i in ids], TAKES)
    video = wd / "source_fixed.mp4" if (wd / "source_fixed.mp4").exists() else wd / "source.mp4"
    for lang in LANGS:
        clips = OUT / f"{vid}_{lang}"
        qa = {r["id"]: r for r in json.loads((clips / "qa.json").read_text())} if (clips / "qa.json").exists() else {}
        for i in ids:
            l, best = lines[i], None
            for codes in pool.get((lang, i), []):
                wav = eng.render(codes, voices[l["speaker"]]["emb"])
                c, fit, heard = eng.check(wav, lang, l)
                if best is None or (round(c / 0.08), fit) < (round(best[0] / 0.08), best[1]):
                    best = (c, fit, heard, wav)
            if best is None:
                print(f"[{vid}] {lang} line {i}: no usable take", flush=True)
                continue
            sf.write(clips / f"line_{i}.wav", eng.finish(best[3], voices[l["speaker"]]), eng.sr)
            qa[i] = {"id": i, "speaker": l["speaker"], "cer": round(best[0], 2), "heard": best[2], "redub": True}
        (clips / "script.json").write_text(json.dumps({"language": lang, "lines": plan["lines"]}, ensure_ascii=False))
        (clips / "qa.json").write_text(json.dumps([qa[k] for k in sorted(qa)], ensure_ascii=False, indent=1))
        assemble.main(clips / "script.json", clips, str(OUT / f"{vid}_{lang}.mp4"), str(video),
                      wd / "stems" / "no_vocals.wav", wd / "stems" / "vocals.wav")
    (wd / "redub.ok").write_text(json.dumps({"lines": ids, "at": time.strftime("%H:%M")}))
    # drop only what was done: other steps may have queued more lines while this ran
    left = sorted(set(json.loads((wd / "redub.json").read_text())["lines"]) - set(ids))
    (wd / "redub.json").write_text(json.dumps({"lines": left}))


def main(ids):
    eng = Engine()
    for vid in ids:
        try:
            guard.wait_for_headroom(vid)
            t0 = time.time()
            redub(eng, vid)
            print(f"[{vid}] REDUB OK ({time.time() - t0:.0f}s)", flush=True)
        except Exception as e:  # one bad video must not stop the pass
            print(f"[{vid}] REDUB FAILED: {e!r}", flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
