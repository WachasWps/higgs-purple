"""Final repair pass on the GPU (CUDA port of repair.py): re-voice only the lines the QA flagged, then re-mix only the
affected languages. Every flagged line of every video is sampled in ONE vLLM pass (TAKES each) and all takes are
checked in batched Whisper rounds; finishing runs on the CPU process pool, re-mixing on the thread pool.

Usage: python vm/repair_cuda.py work/ out/ [cer_threshold=0.6] [--backend auto|vllm|transformers]
                                 [--only id1,id2,... | --ids-file ids.txt]
"""
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import soundfile as sf

import cudacfg
from dubplan_cuda import Engine, assemble, finish, fx_spec, opt

TAKES = 6


def fix(eng, wd, out_root, items, best, old, voices, t0):
    """CPU stage for one video: keep a new take only where it beats the old CER, then re-mix the touched languages."""
    vid = wd.name
    try:
        fx = {cid: fx_spec(v) for cid, v in voices.items()}
        wins = [(lang, l, best[(vid, lang, l["id"])]) for _, lang, l in items
                if best.get((vid, lang, l["id"])) and best[(vid, lang, l["id"])][0] < old[(vid, lang, l["id"])]]
        wavs = [eng.cpu.submit(finish, b[3], eng.sr, fx[l["speaker"]]) for lang, l, b in wins]
        touched = set()
        for (lang, l, b), wav in zip(wins, wavs):
            clips = out_root / f"{vid}_{lang}"
            sf.write(clips / f"line_{l['id']}.wav", wav.result(), eng.sr)
            qa = json.loads((clips / "qa.json").read_text())
            for r in qa:
                if r["id"] == l["id"]:
                    r.update(cer=round(b[0], 2), heard=b[2], repaired=True)
            (clips / "qa.json").write_text(json.dumps(qa, ensure_ascii=False, indent=1))
            touched.add(lang)
        stems = wd / "stems"
        for lang in touched:
            clips = out_root / f"{vid}_{lang}"
            assemble.main(clips / "script.json", clips, str(out_root / f"{vid}_{lang}.mp4"), wd / "source.mp4",
                          stems / "no_vocals.wav", stems / "vocals.wav")
        print(f"[{vid}] repaired {len(items)} flagged -> improved in {sorted(touched)} ({time.time() - t0:.0f}s)",
              flush=True)
        return len(wins)
    except Exception as e:
        print(f"[{vid}] FAILED: {e!r}", flush=True)
        return 0


def main(work, out_root, *args):
    work, out_root = Path(work), Path(out_root)
    threshold = float(args[0]) if args and not args[0].startswith("--") else 0.6
    only = cudacfg.ids_filter(args)
    flagged = defaultdict(list)  # vid -> [(lang, line_id, old_cer)]
    for qa in sorted(out_root.glob("*_*/qa.json")):
        vid, lang = qa.parent.name.rsplit("_", 1)
        if only is not None and vid not in only:
            continue
        for r in json.loads(qa.read_text()):
            if r["cer"] >= threshold:
                flagged[vid].append((lang, r["id"], r["cer"]))
    total = sum(map(len, flagged.values()))
    print(f"{total} flagged lines in {len(flagged)} videos", flush=True)
    if not total:
        return
    eng = Engine(backend=opt(list(args), "--backend", "auto"))
    t0 = time.time()
    items, old, voices = {}, {}, {}
    for vid, flags in flagged.items():
        try:
            plan = json.loads((work / vid / "plan.json").read_text())
            lines = {l["id"]: l for l in plan["lines"]}
            voices[vid], _ = eng.voices(plan, work / vid / "stems" / "vocals.wav")
            items[vid] = [(vid, lang, lines[i]) for lang, i, _ in flags]
            old.update({(vid, lang, i): c for lang, i, c in flags})
        except Exception as e:  # one bad video must not stop the repair
            print(f"[{vid}] FAILED: {e!r}", flush=True)
    every = [it for its in items.values() for it in its]
    best = eng.pick(every, eng.sample(every, TAKES), lambda vid, l: voices[vid][l["speaker"]]["emb"], lazy=False)
    print(f"re-voiced {len(every)} lines x {TAKES} takes in {time.time() - t0:.0f}s", flush=True)
    futs = [eng.io.submit(fix, eng, work / vid, out_root, its, best, old, voices[vid], t0) for vid, its in items.items()]
    fixed = sum(f.result() for f in futs)
    eng.close()
    print(f"REPAIR DONE: improved {fixed}/{total} lines", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
