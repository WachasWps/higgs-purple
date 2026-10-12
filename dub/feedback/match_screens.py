"""Match each client feedback screenshot to (deliverable, time) by ORB feature matching against Bengali deliverables."""
import json
import re
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FPS = 3
H = 480
orb = cv2.ORB_create(nfeatures=1500)
bf = cv2.BFMatcher(cv2.NORM_HAMMING)


def frames(path):
    w = 270
    raw = subprocess.run([FF, "-v", "error", "-i", str(path), "-vf", f"fps={FPS},scale={w}:{H},format=gray",
                          "-f", "rawvideo", "-"], capture_output=True).stdout
    arr = np.frombuffer(raw, np.uint8).reshape(-1, H, w)
    out = []
    for i, fr in enumerate(arr):
        kp, de = orb.detectAndCompute(fr, None)
        out.append((i / FPS, kp, de))
    return out


def score(sd, skp, kp, de):
    if de is None or sd is None or len(de) < 10:
        return 0
    m = bf.knnMatch(de, sd, k=2)
    good = [a for a, *b in m if b and a.distance < 0.75 * b[0].distance]
    if len(good) < 8:
        return len(good) // 2
    src = np.float32([kp[g.queryIdx].pt for g in good])
    dst = np.float32([skp[g.trainIdx].pt for g in good])
    _, mask = cv2.findHomography(src, dst, cv2.RANSAC, 6.0)
    return int(mask.sum()) if mask is not None else 0


def main():
    ocr = json.loads((ROOT / "feedback/screens_ocr.json").read_text())
    vids = sorted(ROOT.glob("Final_Deliverables/*/*/Bengali_WB/*.mp4"))
    cache = {}
    res = {}
    for key, o in ocr.items():
        shot = next((ROOT / "feedback/wa_raw").glob(key + "-PHOTO-*.jpg"))
        img = cv2.imread(str(shot), cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, None, fx=1.4, fy=1.4)
        skp, sd = orb.detectAndCompute(img, None)
        name = re.sub(r"\s*\(\d+\)", "", o["name"]).replace(".mp4", "").lstrip("_")
        cands = [v for v in vids if name and name != "?" and (v.stem == name or v.stem.endswith(name) or name.endswith(v.stem))] or vids
        best = (0, None, None)
        for v in cands:
            if v not in cache:
                cache[v] = frames(v)
            for t, kp, de in cache[v]:
                s = score(sd, skp, kp, de)
                if s > best[0]:
                    best = (s, v, t)
        s, v, t = best
        res[key] = {"file": v.name if v else None, "time": t, "score": s, "ocr_time": o["time"], "n_cands": len(cands)}
        print(key, res[key], flush=True)
    (ROOT / "feedback/screens_match.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
