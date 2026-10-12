"""English-only voice-over for the rebuilt General Ads (client: general ads ship in English, no Indic dubs).

usage: .venv/bin/python feedback/ads_english.py <id> [<id> ...]
Same engine as the Indic dubs (Indic-Mio + MioCodec, calm female narrator ref from the plan's cast), with English
plugged in as a language: text from plan.json lines[*].en. Brand terms are fed to the TTS phonetically ("Derm-doc",
"two percent", "Ko-jic") — captions keep the real text (script.json is written from the plan). Every take is checked
with Whisper against the spoken form (the Indic engine's "ASR heard English -> pass" shortcut is bypassed here).
Output: out/<id>_en.mp4 (+ out/<id>_en/ line wavs + qa.json); then assemble_fix.remux() puts the rebuilt picture in.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "feedback"))

import dubplan  # noqa: E402

PHON = [(r"SPF 50 PA\+\+\+", "S P F fifty, P A triple plus"), (r"SPF 50", "S P F fifty"), (r"PA\+\+\+", "P A triple plus"),
        (r"\bDERMDOC\b", "Derm-doc"), (r"\b2%", "two percent"), (r"\b4%", "four percent"), (r"\bKojic\b", "Ko-jic"),
        (r"\b3\b", "three"), (r"\b2\b", "two")]
NUM = {"2": "two", "3": "three", "4": "four", "50": "fifty"}


def phon(t):
    for a, b in PHON:
        t = re.sub(a, b, t, flags=re.I)
    return t


def spoken(t):
    """Comparable spoken form: lower-case letters only, numbers as words (Whisper writes '2%' or 'two percent')."""
    t = phon(t).lower().replace("%", " percent")
    t = re.sub(r"\d+", lambda m: NUM.get(m.group(), m.group()), t)
    return "".join(c for c in t if c.isalpha())


dubplan.LANGS[:] = ["en"]
dubplan.GOOD_CER["en"], dubplan.RETRY_CER["en"] = 0.12, 0.25
dubplan.ASR["en"] = ("en", "This is an English skincare ad for DERMDOC.")
_sample, _check, _cer = dubplan.Engine.sample, dubplan.Engine.check, dubplan.cer


def sample(self, items, takes):
    return _sample(self, [(lang, {**l, "en": phon(l["en"])}) for lang, l in items], takes)


def check(self, wav, lang, l):
    _, fit, heard = _check(self, wav, lang, l)
    return _cer(spoken(l["en"]), spoken(heard)), fit, heard


dubplan.Engine.sample, dubplan.Engine.check = sample, check


def main(ids):
    import assemble_fix
    eng = dubplan.Engine()
    for v in ids:
        (ROOT / "out" / f"{v}_en.mp4").unlink(missing_ok=True)   # process() skips languages that already exist
        eng.process(ROOT / "work" / v, ROOT / "out")
        assemble_fix.remux(v)
        print(Path(ROOT / "out" / f"{v}_en" / "qa.json").read_text(), flush=True)


if __name__ == "__main__":
    main(sys.argv[1:])
