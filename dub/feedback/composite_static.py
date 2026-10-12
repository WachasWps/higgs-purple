"""Lock a region of a Wan clip to its (approved) Codex keyframe — e.g. a colour wheel Wan keeps rotating/morphing.

usage: composite_static.py <clip_id> <cx> <cy> <r> [--feather 12] [--hole cx cy rx ry] [--xmin X] [--until S] [--fit S]
Coordinates are in the clip's own pixels (480x854). Inside the soft circle the frame comes from
feedback/codex/out/<clip_id>.png (resized to the clip); --hole keeps a moving part (a pointing finger) from the clip;
--xmin never pastes left of X (moving hair); --until uses only the first S seconds of the clip, --fit stretches them to
S seconds (slow-mo) so a late glitch never appears. Writes feedback/clips/<clip_id>.mp4 (original kept as _raw.mp4).
"""
import argparse
import shutil
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip")
    ap.add_argument("cx", type=float)
    ap.add_argument("cy", type=float)
    ap.add_argument("r", type=float)
    ap.add_argument("--feather", type=float, default=12)
    ap.add_argument("--hole", type=float, nargs=4)
    ap.add_argument("--xmin", type=float)
    ap.add_argument("--until", type=float)
    ap.add_argument("--fit", type=float)
    a = ap.parse_args()
    clip = ROOT / "feedback" / "clips" / f"{a.clip}.mp4"
    raw = clip.with_name(f"{a.clip}_raw.mp4")
    if not raw.exists():
        shutil.copy2(clip, raw)
    W, H, fps = 480, 854, 30
    key = np.asarray(Image.open(ROOT / "feedback" / "codex" / "out" / f"{a.clip}.png").convert("RGB")
                     .resize((W, H), Image.LANCZOS)).astype(np.float32)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - a.cx) ** 2 + (yy - a.cy) ** 2)
    m = np.clip((a.r - d) / a.feather + 0.5, 0, 1)
    if a.hole:
        hx, hy, rx, ry = a.hole
        dh = np.sqrt(((xx - hx) / rx) ** 2 + ((yy - hy) / ry) ** 2)
        m *= np.clip((dh - 1) * 4 + 0.5, 0, 1)
    if a.xmin is not None:
        m *= np.clip((xx - a.xmin) / a.feather, 0, 1)
    m = m[..., None]
    vf = [f"scale={W}:{H}"]
    if a.until:
        vf = [f"trim=0:{a.until}", "setpts=PTS-STARTPTS"] + vf
        if a.fit:
            vf += [f"setpts={a.fit / a.until:.4f}*PTS", f"fps={fps}"]
    src = subprocess.run([FF, "-v", "error", "-i", str(raw), "-vf", ",".join(vf + [f"fps={fps}"]), "-f", "rawvideo",
                          "-pix_fmt", "rgb24", "-"], capture_output=True, check=True).stdout
    frames = np.frombuffer(src, np.uint8).reshape(-1, H, W, 3).astype(np.float32)
    out = (frames * (1 - m) + key * m).clip(0, 255).astype(np.uint8)
    subprocess.run([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps),
                    "-i", "-", "-c:v", "libx264", "-crf", "14", "-pix_fmt", "yuv420p", str(clip)],
                   input=out.tobytes(), check=True)
    print(f"{a.clip}: {len(out)} frames -> {clip.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
