"""Make ad captions spell exactly like the voiceover script while keeping Whisper's word timings.

Aligns work/<id>/captions.json words (Whisper) to transcript.json's vo_script (from the prompt): matched words take
the script's spelling; replaced spans get the script words spread over the same time; words only in the script are
dropped unless they sit between matched words (then they share the gap); Whisper-only words are kept unless garbage.
Usage: python3 post/fix_ad_captions.py id1 id2 ...
"""
import json
import re
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAND = [(re.compile(r"^derm\W*doc", re.I), "DERMDOC"), (re.compile(r"^pa\+*$", re.I), "PA+++")]


def norm(w):
    return re.sub(r"[^a-z0-9%+]", "", w.lower())


def brand(w):
    for rx, rep in BRAND:
        if rx.match(re.sub(r"[^\w+]", "", w)):
            return rx.sub(rep, re.sub(r"[^\w+]", "", w)) + re.sub(r"^[\w+]+", "", w)
    return w


def fix(vid):
    wd = ROOT / "work" / vid
    words = json.loads((wd / "captions.json").read_text())["words"]
    script = json.loads((wd / "transcript.json").read_text()).get("vo_script", "")
    sw = script.replace("—", " — ").split()
    sw = [w for w in sw if w != "—"]
    if not sw:
        out = words
    else:
        a, b = [norm(w["w"]) for w in words], [norm(w) for w in sw]
        out = []
        for op, i1, i2, j1, j2 in SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
            if op == "equal":
                out += [{"w": sw[j1 + k], "s": words[i1 + k]["s"], "e": words[i1 + k]["e"]} for k in range(i2 - i1)]
            elif op == "replace":
                s, e = words[i1]["s"], words[i2 - 1]["e"]
                lens = [max(len(norm(x)), 1) for x in sw[j1:j2]]
                t = s
                for x, n in zip(sw[j1:j2], lens):
                    d = (e - s) * n / sum(lens)
                    out.append({"w": x, "s": round(t, 2), "e": round(t + d, 2)})
                    t += d
            elif op == "insert" and out and i1 < len(words):
                s, e = out[-1]["e"], words[i1]["s"]
                if e - s >= 0.12:  # only fill a real gap between spoken words
                    step = (e - s) / (j2 - j1)
                    out += [{"w": sw[j1 + k], "s": round(s + k * step, 2), "e": round(s + (k + 1) * step, 2)}
                            for k in range(j2 - j1)]
            elif op == "delete":
                out += [w for w in words[i1:i2] if re.fullmatch(r"[\x20-\x7E’“”—–]+", w["w"])]  # drop non-Latin junk
    out = [{**w, "w": brand(w["w"])} for w in out if w["w"].strip()]
    data = json.loads((wd / "captions.json").read_text())
    data["words"], data["aligned_to_script"] = out, bool(sw)
    (wd / "captions.json").write_text(json.dumps(data, ensure_ascii=False, indent=1))
    print(f"{vid}: {len(out)} words | {' '.join(w['w'] for w in out)[:150]}")


if __name__ == "__main__":
    for v in sys.argv[1:]:
        fix(v)
