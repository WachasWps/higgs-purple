"""Find text baked into the source videos and flag typos (Apple Vision OCR, on-device).

For each video: sample frames, OCR them, link detections across frames into text "tracks" (same place, similar text),
spell-check each track against the brand lexicon + /usr/share/dict/words, and save:
  post/text_audit/<id>.json  — every track: text, time window, union box (top-left origin, fractions), typo words
  post/text_audit/<id>_<n>.png — crop of each flagged track's middle frame with the box drawn (for review)
Usage: nice -n 10 .venv/bin/python post/detect_text.py [id ...]   (default: all work/*/)
"""
import json
import re
import subprocess
import sys
import tempfile
from difflib import SequenceMatcher
from pathlib import Path

from ocrmac import ocrmac
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "post" / "text_audit"
FPS = 3
LEXICON = {w.lower() for w in """dermdoc honest science niacinamide kojic acid alpha arbutin spf pa uva uvb glow fusion
formula night cream ultra violet brightening sunscreen purple tint knc xpert 3xpert dullness greasiness villain
before after weeks week indian skin tone even looking dark spots spot white cast protection protected shield
for fair medium all types""".split()}
try:
    LEXICON |= {w.strip().lower() for w in open("/usr/share/dict/words")}
except OSError:
    pass


def words_bad(text):
    bad = []
    for w in re.findall(r"[A-Za-z][A-Za-z'’-]*", text):
        lw = w.lower().strip("'’-")
        if len(lw) <= 2 or lw in LEXICON or lw.rstrip("s") in LEXICON:
            continue
        bad.append(w)
    return bad


def frames(video, tmp):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vf", f"fps={FPS}", f"{tmp}/f_%04d.png"],
                   check=True)
    return sorted(Path(tmp).glob("f_*.png"))


def ocr(png):
    out = []
    for text, conf, (x, y, w, h) in ocrmac.OCR(str(png), recognition_level="accurate").recognize():
        if conf < 0.3 or len(text.strip()) < 2:
            continue
        out.append({"text": text.strip(), "conf": conf, "box": [x, 1 - (y + h), x + w, 1 - y]})  # top-left origin
    return out


def iou(a, b):
    ix = max(0, min(a[2], b[2]) - max(a[0], b[0]))
    iy = max(0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = ix * iy
    ua = (a[2] - a[0]) * (a[3] - a[1]) + (b[2] - b[0]) * (b[3] - b[1]) - inter
    return inter / ua if ua else 0


def audit(vid):
    video = ROOT / "work" / vid / "source.mp4"
    with tempfile.TemporaryDirectory() as tmp:
        pngs = frames(video, tmp)
        tracks = []
        for i, png in enumerate(pngs):
            t = i / FPS
            for d in ocr(png):
                best = None
                for tr in tracks:
                    if t - tr["last"] > 0.75:
                        continue
                    sim = SequenceMatcher(None, d["text"].lower(), tr["texts"][-1].lower()).ratio()
                    if iou(d["box"], tr["box_last"]) > 0.3 and sim > 0.5:
                        best = tr
                        break
                if best is None:
                    best = {"texts": [], "first": t, "box": d["box"][:], "frames": []}
                    tracks.append(best)
                best["texts"].append(d["text"])
                best["last"] = t
                best["box_last"] = d["box"]
                best["box"] = [min(best["box"][0], d["box"][0]), min(best["box"][1], d["box"][1]),
                               max(best["box"][2], d["box"][2]), max(best["box"][3], d["box"][3])]
                best["frames"].append((t, png.name))
        result = []
        for n, tr in enumerate(tracks):
            if len(tr["texts"]) < 2:  # single-frame flickers are OCR noise
                continue
            text = max(set(tr["texts"]), key=tr["texts"].count)
            bad = sorted({w for s in tr["texts"] for w in words_bad(s)})
            item = {"n": n, "text": text, "variants": sorted(set(tr["texts"]))[:6], "start": round(tr["first"], 2),
                    "end": round(tr["last"] + 1 / FPS, 2), "box": [round(v, 4) for v in tr["box"]],
                    "height": round(tr["box"][3] - tr["box"][1], 4), "suspect_words": bad}
            if bad:
                mid_t, mid_png = tr["frames"][len(tr["frames"]) // 2]
                img = Image.open(Path(tmp) / mid_png).convert("RGB")
                W, H = img.size
                x0, y0, x1, y1 = tr["box"]
                d = ImageDraw.Draw(img)
                d.rectangle([x0 * W - 3, y0 * H - 3, x1 * W + 3, y1 * H + 3], outline=(255, 0, 0), width=3)
                img.save(OUT / f"{vid}_{n}.png")
                item["crop"] = f"post/text_audit/{vid}_{n}.png"
            result.append(item)
    (OUT / f"{vid}.json").write_text(json.dumps(result, indent=1, ensure_ascii=False))
    flagged = [r for r in result if r["suspect_words"]]
    print(f"{vid}: {len(result)} text tracks, {len(flagged)} flagged: "
          + "; ".join(f"'{r['text']}' {r['start']}-{r['end']}s" for r in flagged), flush=True)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    ids = sys.argv[1:] or sorted(p.parent.name for p in (ROOT / "work").glob("*/source.mp4"))
    for vid in ids:
        try:
            audit(vid)
        except Exception as e:
            print(f"{vid}: FAILED {e!r}", flush=True)
