"""Final repair pass: re-voice only the lines the QA flagged, then re-mix only the affected languages.

Usage: nice -n 10 .venv/bin/python repair.py work/ out/ [cer_threshold=0.6]
"""
import guard  # noqa: F401  (first: caps threads)

import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import soundfile as sf

import assemble
from dubplan import Engine

TAKES = 6


def robust_f0(y, sr):
    """Median pitch, taking pyin and yin together so a single octave error can't skew it."""
    import librosa
    import numpy as np
    if len(y) < sr // 5:
        return None
    p, _, _ = librosa.pyin(y, fmin=60, fmax=900, sr=sr)
    p = p[~np.isnan(p)]
    yi = float(np.median(librosa.yin(y, fmin=60, fmax=900, sr=sr)))
    if not len(p):
        return yi
    pm = float(np.median(p))
    return pm if abs(12 * np.log2(pm / yi)) < 3 else min(pm, yi)


def pitch_targets(plan, vocals):
    import librosa
    import numpy as np
    vox, sr = librosa.load(vocals, sr=16000)
    out = {}
    for c in plan["cast"]:
        ref = np.concatenate([vox[int(a * sr): int(b * sr)] for a, b in c["ref_ranges"]])
        f = robust_f0(ref, sr)
        if f:
            out[c["id"]] = f * 2 ** (c.get("pitch_semitones", 0) / 12)
    return out


def pitch_offset(clip, target):
    """Semitones between a finished line and its character's target pitch (0 if unknown)."""
    import librosa
    import numpy as np
    if not target or not clip.exists():
        return 0.0
    y, sr = librosa.load(clip, sr=16000)
    f = robust_f0(y, sr)
    return abs(12 * np.log2(f / target)) if f else 0.0


def main(work, out_root, threshold="0.6"):
    work, out_root, threshold = Path(work), Path(out_root), float(threshold)
    flagged = defaultdict(list)  # vid -> [(lang, line_id, old_cer)]
    for qa in sorted(out_root.glob("*_*/qa.json")):
        vid, lang = qa.parent.name.rsplit("_", 1)
        if not (work / vid / "plan.json").exists():  # legacy morning-glow_* folders from the first test
            continue
        if not (qa.parent / "script.json").exists():  # rendered elsewhere (Kaggle) without line clips here
            continue
        plan = json.loads((work / vid / "plan.json").read_text())
        targets = pitch_targets(plan, work / vid / "stems" / "vocals.wav")
        lines = {l["id"]: l for l in plan["lines"]}
        for r in json.loads(qa.read_text()):
            off = pitch_offset(qa.parent / f"line_{r['id']}.wav", targets.get(lines[r["id"]]["speaker"]))
            if r["cer"] >= threshold or off > 4:
                # a pitch outlier gets old score 1.0 so any clean re-take replaces it
                flagged[vid].append((lang, r["id"], 1.0 if off > 4 else r["cer"]))
    total = sum(map(len, flagged.values()))
    print(f"{total} flagged lines in {len(flagged)} videos", flush=True)
    if not total:
        return
    eng = Engine()
    fixed = 0
    for vid, items in flagged.items():
      try:
        guard.wait_for_headroom(vid)
        t0 = time.time()
        wd = work / vid
        plan = json.loads((wd / "plan.json").read_text())
        lines = {l["id"]: l for l in plan["lines"]}
        voices, _ = eng.voices(plan, wd / "stems" / "vocals.wav")
        pool = eng.sample([(lang, lines[i]) for lang, i, _ in items], TAKES)
        touched = set()
        for lang, i, old in items:
            l, best = lines[i], None
            for codes in pool.get((lang, i), []):
                wav = eng.render(codes, voices[l["speaker"]]["emb"])
                c, fit, heard = eng.check(wav, lang, l)
                if best is None or (round(c / 0.08), fit) < (round(best[0] / 0.08), best[1]):
                    best = (c, fit, heard, wav)
            if best and best[0] < old:
                clips = out_root / f"{vid}_{lang}"
                sf.write(clips / f"line_{i}.wav", eng.finish(best[3], voices[l["speaker"]]), eng.sr)
                qa = json.loads((clips / "qa.json").read_text())
                for r in qa:
                    if r["id"] == i:
                        r.update(cer=round(best[0], 2), heard=best[2], repaired=True)
                (clips / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=1))
                touched.add(lang)
                fixed += 1
        stems = wd / "stems"
        for lang in touched:
            clips = out_root / f"{vid}_{lang}"
            assemble.main(clips / "script.json", clips, str(out_root / f"{vid}_{lang}.mp4"), wd / "source.mp4",
                          stems / "no_vocals.wav", stems / "vocals.wav")
        print(f"[{vid}] repaired {sum(1 for x in items)} flagged -> improved in {sorted(touched)} "
              f"({time.time() - t0:.0f}s)", flush=True)
      except Exception as e:  # one bad video must not stop the pass
        print(f"[{vid}] REPAIR FAILED: {e!r}", flush=True)
    print(f"REPAIR DONE: improved {fixed}/{total} lines", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
