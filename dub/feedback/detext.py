"""Erase baked-in AI text inside a box (instead of a frosted blur): per frame, mask bright text strokes (+ their dark
anti-alias rim) and inpaint them from the surrounding skin/background.  Writes work/<id>/source_fixed.mp4 in place
(original kept as source_fixed.pretext.mp4) and drops the matching "blur" elements from graphics.json.
usage: .venv/bin/python feedback/detext.py <id> [--preview]
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"


def text_mask(roi, thr=18):
    g = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY).astype(np.float32)
    bg = cv2.medianBlur(g.astype(np.uint8), 31).astype(np.float32)
    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB)
    sat = np.abs(lab[..., 1].astype(np.float32) - 128) + np.abs(lab[..., 2].astype(np.float32) - 128)
    m = ((g - bg > thr) & (sat < 40)).astype(np.uint8)          # light, low-saturation strokes brighter than local bg
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8))
    near = cv2.dilate(m, np.ones((15, 15), np.uint8))
    shadow = ((bg - g > 4) & (near > 0)).astype(np.uint8)          # the text's soft drop shadow next to the strokes
    m = cv2.dilate(m | shadow, np.ones((9, 9), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((15, 15), np.uint8))


def main(vid, preview=False):
    wd = ROOT / "work" / vid
    gp = wd / "graphics.json"
    g = json.loads(gp.read_text())
    boxes = [e for e in g["elements"] if e.get("type") == "blur"]
    src = wd / "source_fixed.pretext.mp4"
    if not src.exists():
        shutil.copy(wd / "source_fixed.mp4", src)
    cap = cv2.VideoCapture(str(src))
    fps = cap.get(cv2.CAP_PROP_FPS)
    W, H = int(cap.get(3)), int(cap.get(4))
    out = wd / ("detext_preview.mp4" if preview else "source_fixed.tmp.mp4")
    p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}",
                          "-i", "-", "-i", str(src), "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "15",
                          "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", str(out)], stdin=subprocess.PIPE)
    rng = np.random.default_rng(0)
    i = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        t = i / fps
        for e in boxes:
            if e["start"] - e.get("pre", 0.3) <= t <= e["end"] + e.get("post", 0.0):
                b = e["box"]
                x0, y0 = int(b["x0"] * W), int(b["y0"] * H)
                x1, y1 = int(b["x1"] * W), int(b["y1"] * H)
                pad = 12
                X0, Y0, X1, Y1 = max(0, x0 - pad), max(0, y0 - pad), min(W, x1 + pad), min(H, y1 + pad)
                roi = f[Y0:Y1, X0:X1].copy()
                m = text_mask(roi, e.get("thr", 18))
                m[: y0 - Y0], m[y1 - Y0:], m[:, : x0 - X0], m[:, x1 - X0:] = 0, 0, 0, 0
                if m.any():
                    fill = cv2.inpaint(roi, m, 9, cv2.INPAINT_TELEA)
                    fill = cv2.GaussianBlur(fill, (0, 0), 7).astype(np.float32)        # kill Telea streaks
                    hp = roi.astype(np.float32) - cv2.GaussianBlur(roi, (0, 0), 2).astype(np.float32)
                    sd = float(hp[m == 0].std()) if (m == 0).any() else 2.0
                    fill += rng.normal(0, sd, fill.shape[:2])[..., None]           # put the skin grain back
                    a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 3)[..., None]
                    f[Y0:Y1, X0:X1] = np.clip(roi * (1 - a) + fill * a, 0, 255).astype(np.uint8)
        p.stdin.write(f.tobytes())
        i += 1
    p.stdin.close()
    p.wait()
    if not preview:
        out.replace(wd / "source_fixed.mp4")
        g["elements"] = [e for e in g["elements"] if e.get("type") != "blur"]
        g.setdefault("notes", "")
        g["notes"] += " | baked AI text inside former blur boxes erased by inpainting (feedback/detext.py)"
        gp.write_text(json.dumps(g, indent=1, ensure_ascii=False))
    print(vid, "->", out.name, len(boxes), "boxes")


if __name__ == "__main__":
    main(sys.argv[1], "--preview" in sys.argv)
