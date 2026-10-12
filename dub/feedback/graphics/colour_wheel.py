"""Animated painter's (RYB) colour wheel — yellow at top, violet directly opposite — as a 1080x1920 overlay with alpha.

usage: colour_wheel.py <out.mov> [--cx 0.66] [--cy 0.40] [--r 250] [--dur 4.8] [--panel]
Timeline: 0-0.6 wheel spins in · 0.7 YELLOW segment lifts + label · 1.5 VIOLET lifts + label · 2.3 double arrow
"OPPOSITES CANCEL" · 3.1 claim card. --panel puts a frosted card behind everything (for busy backgrounds).
Output: ProRes 4444 with alpha (overlay it with ffmpeg `overlay`).
"""
import argparse
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

FONTS = Path(__file__).resolve().parents[2] / "post" / "fonts"
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
W, H, FPS = 1080, 1920, 30
# 12-step painter's wheel, clockwise from the top. Index 0 = yellow, index 6 = violet (opposite).
RYB = ["#FCE21B", "#FDB515", "#F7941D", "#F26522", "#E8262B", "#B8237E",
       "#7A2E9A", "#5641A0", "#2B59AA", "#1A9BA8", "#3DB04A", "#A5CD39"]
VIOLET_BRAND = "#8E6CD6"


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def back(t):
    t = max(0.0, min(1.0, t))
    c = 1.70158
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def font(name, size):
    return ImageFont.truetype(str(FONTS / name), size)


def mono(size, weight=700):
    f = font("RobotoMono[wght].ttf", size)
    try:
        f.set_variation_by_axes([weight])
    except Exception:
        pass
    return f


def segment_layer(i, R, ss=2, lift=0.0):
    """One wheel segment as RGBA (size 2.6R square), centred."""
    S = int(2.6 * R * ss)
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    a0 = -90 - 15 + i * 30 + 1.2
    a1 = a0 + 30 - 2.4
    mid = math.radians((a0 + a1) / 2)
    ox, oy = math.cos(mid) * lift * ss, math.sin(mid) * lift * ss
    ro, ri = R * ss, R * 0.42 * ss
    d.pieslice([c - ro + ox, c - ro + oy, c + ro + ox, c + ro + oy], a0, a1, fill=RYB[i])
    d.ellipse([c - ri, c - ri, c + ri, c + ri], fill=(0, 0, 0, 0))
    # re-cut the inner hole for lifted segments (hole stays centred on the lifted position)
    if lift:
        d.ellipse([c - ri + ox, c - ri + oy, c + ri + ox, c + ri + oy], fill=(0, 0, 0, 0))
    return im.resize((S // ss, S // ss), Image.LANCZOS)


def pill(text, f, fg, bg, pad=(22, 12)):
    tw, th = f.getbbox(text)[2], f.getbbox("Hg")[3]
    im = Image.new("RGBA", (tw + 2 * pad[0], th + 2 * pad[1]), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=im.height // 2, fill=bg)
    d.text((pad[0], pad[1] - f.getbbox("Hg")[1] // 2), text, font=f, fill=fg)
    return im


def shadowed(im, blur=14, alpha=110):
    sh = Image.new("RGBA", (im.width + 4 * blur, im.height + 4 * blur), (0, 0, 0, 0))
    a = im.split()[3].point(lambda v: v * alpha // 255)
    blk = Image.new("RGBA", im.size, (20, 10, 40, 255))
    blk.putalpha(a)
    sh.paste(blk, (2 * blur, 2 * blur + 6), blk)
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    sh.paste(im, (2 * blur, 2 * blur), im)
    return sh, 2 * blur


def paste_center(base, im, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        a = im.split()[3].point(lambda v: int(v * alpha))
        im = im.copy()
        im.putalpha(a)
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def arrow(L, th=10, head=34, color="#FFFFFF"):
    """Vertical double-headed arrow of length L (RGBA)."""
    im = Image.new("RGBA", (head * 2 + 8, L + 8), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    cx = im.width / 2
    d.rectangle([cx - th / 2, 4 + head * 0.8, cx + th / 2, L + 4 - head * 0.8], fill=color)
    d.polygon([(cx, 4), (cx - head, 4 + head * 1.2), (cx + head, 4 + head * 1.2)], fill=color)
    d.polygon([(cx, L + 4), (cx - head, L + 4 - head * 1.2), (cx + head, L + 4 - head * 1.2)], fill=color)
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--cx", type=float, default=0.66)
    ap.add_argument("--cy", type=float, default=0.40)
    ap.add_argument("--r", type=int, default=250)
    ap.add_argument("--dur", type=float, default=4.8)
    ap.add_argument("--panel", action="store_true")
    ap.add_argument("--card-x", type=float, default=0.5, help="closing card centre x (keep it off a mascot)")
    a = ap.parse_args()
    cx, cy, R = a.cx * W, a.cy * H, a.r
    segs = [segment_layer(i, R) for i in range(12)]
    lifted = {0: segment_layer(0, R, lift=R * 0.12), 6: segment_layer(6, R, lift=R * 0.12)}
    hub = Image.new("RGBA", (int(R * 0.84), int(R * 0.84)), (0, 0, 0, 0))
    ImageDraw.Draw(hub).ellipse([0, 0, hub.width - 1, hub.height - 1], fill=(255, 255, 255, 235))
    f_lab = mono(30)
    lab_y = pill("YELLOW DULLNESS", f_lab, "#3A2A00", "#FCE21BEE")
    lab_v = pill("PURPLE TINT", f_lab, "#FFFFFF", VIOLET_BRAND + "EE")
    lab_c = pill("OPPOSITES CANCEL", mono(26), "#2A1A4A", "#FFFFFFEE", pad=(18, 10))
    arr = arrow(int(R * 1.55))
    # claim card
    f1, f2 = font("Lato-Black.ttf", 66), mono(30)
    l1, l2, sub = "PURPLE CANCELS", "YELLOW DULLNESS", "FOR INDIAN SKIN TONES · INSTANT GLOW"
    cw = max(f1.getbbox(l1)[2], f1.getbbox(l2)[2], f2.getbbox(sub)[2]) + 80
    card = Image.new("RGBA", (cw, 250), (0, 0, 0, 0))
    d = ImageDraw.Draw(card)
    d.rounded_rectangle([0, 0, cw - 1, 249], radius=34, fill=(255, 255, 255, 236))
    for txt, f, y, col in ((l1, f1, 22, "#5B3FB0"), (l2, f1, 96, "#5B3FB0"), (sub, f2, 186, "#3B3355")):
        d.text(((cw - f.getbbox(txt)[2]) / 2, y), txt, font=f, fill=col)
    card, _ = shadowed(card)
    panel = None
    if a.panel:
        pw, ph = int(R * 2.9), int(R * 3.9)
        panel = Image.new("RGBA", (pw, ph), (0, 0, 0, 0))
        ImageDraw.Draw(panel).rounded_rectangle([0, 0, pw - 1, ph - 1], radius=48, fill=(255, 255, 255, 175))  # light frosted
    n = int(a.dur * FPS)
    tmp = Path(a.out).with_suffix(".frames")
    tmp.mkdir(exist_ok=True)
    for k in range(n):
        t = k / FPS
        fr = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        fade_out = 1 - ease((t - (a.dur - 0.35)) / 0.35)
        if panel is not None:
            paste_center(fr, panel, cx, cy + R * 0.55, alpha=0.9 * ease(t / 0.4) * fade_out)
        sp = back(t / 0.6)
        wheel = Image.new("RGBA", segs[0].size, (0, 0, 0, 0))
        hl_y, hl_v = ease((t - 0.7) / 0.3), ease((t - 1.5) / 0.3)
        for i, s in enumerate(segs):
            dim = 1.0
            if t > 2.3 and i not in (0, 6):
                dim = 1 - 0.55 * ease((t - 2.3) / 0.4)
            src = s
            if i == 0 and hl_y > 0.5:
                src = lifted[0]
            if i == 6 and hl_v > 0.5:
                src = lifted[6]
            if dim < 1:
                src = src.copy()
                src.putalpha(src.split()[3].point(lambda v, dd=dim: int(v * dd)))
            wheel.alpha_composite(src)
        wsh, _ = shadowed(wheel, blur=18, alpha=90)
        paste_center(fr, wsh, cx, cy, alpha=min(1.0, t / 0.3) * fade_out, scale=0.6 + 0.4 * sp, rot=(1 - sp) * 40)
        paste_center(fr, hub, cx, cy, alpha=min(1.0, t / 0.3) * fade_out, scale=0.6 + 0.4 * sp)
        if t > 0.7:
            paste_center(fr, lab_y, cx, cy - R - 58, alpha=ease((t - 0.7) / 0.25) * fade_out, scale=0.8 + 0.2 * back((t - 0.7) / 0.35))
        if t > 1.5:
            paste_center(fr, lab_v, cx, cy + R + 58, alpha=ease((t - 1.5) / 0.25) * fade_out, scale=0.8 + 0.2 * back((t - 1.5) / 0.35))
        if t > 2.3:
            g = ease((t - 2.3) / 0.45)
            ar = arr.crop((0, int(arr.height / 2 * (1 - g)), arr.width, int(arr.height / 2 * (1 + g)))) if g < 1 else arr
            if ar.height > 2:
                ash, _ = shadowed(ar, blur=8, alpha=120)
                paste_center(fr, ash, cx, cy, alpha=fade_out)
            paste_center(fr, lab_c, cx, cy, alpha=ease((t - 2.6) / 0.25) * fade_out)
        if t > 3.1:
            paste_center(fr, card, min(W - card.width / 2 - 24, max(card.width / 2 + 24, a.card_x * W)), min(H * 0.80, cy + R + 300), alpha=ease((t - 3.1) / 0.3) * fade_out,
                         scale=0.85 + 0.15 * back((t - 3.1) / 0.4))
        fr.save(tmp / f"{k:04d}.png")
    subprocess.run([FF, "-v", "error", "-y", "-framerate", str(FPS), "-i", str(tmp / "%04d.png"),
                    "-c:v", "prores_ks", "-profile:v", "4444", "-pix_fmt", "yuva444p10le", a.out], check=True)
    for p in tmp.iterdir():
        p.unlink()
    tmp.rmdir()
    print("wrote", a.out)


if __name__ == "__main__":
    main()
