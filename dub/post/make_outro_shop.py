"""End slates with 'SHOP AT PURPLLE.COM' instead of 'Available on purplle' (client rule: CTA always Shop at Purplle.com).
Erases the old line (inpaint) on every frame of post/assets/outro_<product>.mp4 and draws the new line.
Originals kept as outro_<product>.orig.mp4.   usage: .venv/bin/python post/make_outro_shop.py
"""
import shutil
import subprocess
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "feedback"))
from detext import text_mask  # noqa: E402

FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
ASSETS = ROOT / "post" / "assets"
FONT = ROOT / "post" / "fonts" / "Lato-Black.ttf"
BOX = (0.10, 0.115, 0.90, 0.215)   # x0, y0, x1, y1 of the 'Available on purplle' line
TEXT = "SHOP AT PURPLLE.COM"


def line_rgba(W, H):
    S = 3                                    # supersample for crisp edges
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    size = int(0.062 * W * S)
    f = ImageFont.truetype(str(FONT), size)
    tw = d.textlength(TEXT, font=f)
    cy = (BOX[1] + BOX[3]) / 2 * H * S
    x, y = (W * S - tw) / 2, cy - size * 0.62
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((x, y + 4 * S), TEXT, font=f, fill=(20, 30, 60, 150))
    img = Image.alpha_composite(img, sh.filter(ImageFilter.GaussianBlur(4 * S)))
    ImageDraw.Draw(img).text((x, y), TEXT, font=f, fill=(255, 255, 255, 255))
    return np.asarray(img.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255


def main():
    for prod in ("uv_sunscreen", "kojic_night_cream"):
        src = ASSETS / f"outro_{prod}.orig.mp4"
        if not src.exists():
            shutil.copy(ASSETS / f"outro_{prod}.mp4", src)
        cap = cv2.VideoCapture(str(src))
        fps, W, H = cap.get(cv2.CAP_PROP_FPS), int(cap.get(3)), int(cap.get(4))
        txt = line_rgba(W, H)
        x0, y0, x1, y1 = int(BOX[0] * W), int(BOX[1] * H), int(BOX[2] * W), int(BOX[3] * H)
        tmp = ASSETS / f"outro_{prod}.tmp.mp4"
        p = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "bgr24", "-s", f"{W}x{H}", "-r", f"{fps}",
                              "-i", "-", "-i", str(src), "-map", "0:v", "-map", "1:a?", "-c:v", "libx264", "-crf", "14",
                              "-pix_fmt", "yuv420p", "-c:a", "copy", str(tmp)], stdin=subprocess.PIPE)
        i = 0
        while True:
            ok, f = cap.read()
            if not ok:
                break
            roi = f[y0:y1, x0:x1].copy()
            m = text_mask(roi)
            if m.any():
                fill = cv2.GaussianBlur(cv2.inpaint(roi, m, 9, cv2.INPAINT_TELEA), (0, 0), 6).astype(np.float32)
                a = cv2.GaussianBlur(m.astype(np.float32), (0, 0), 3)[..., None]
                f[y0:y1, x0:x1] = np.clip(roi * (1 - a) + fill * a, 0, 255).astype(np.uint8)
            k = min(1.0, max(0.0, (i / fps - 0.15) / 0.45))          # fade in like the original line
            al = txt[..., 3:4] * k
            f[:] = np.clip(f * (1 - al) + txt[..., 2::-1][..., :3] * 255 * al, 0, 255).astype(np.uint8)
            p.stdin.write(f.tobytes())
            i += 1
        p.stdin.close()
        p.wait()
        tmp.replace(ASSETS / f"outro_{prod}.mp4")
        print(prod, "done", i, "frames")


if __name__ == "__main__":
    main()
