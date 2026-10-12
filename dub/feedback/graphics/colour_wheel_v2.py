"""Full-screen colour-wheel card in the reference style (blue blueprint grid, PURPLE TINT / INSTANT GLOW title,
12-hue wheel with 3 tint rings, purple at top, yellow at bottom, markers joined by a line through the centre).

usage: colour_wheel_v2.py <out.mp4> [--dur 4.5]
Timeline: title slides in · wheel spins in · purple marker pops · line draws down · yellow marker pops · soft pulse.
Opaque 1080x1920 30 fps clip (used as the whole shot; the assembler time-fits it to the shot length).
"""
import argparse
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageFont

FONTS = Path(__file__).resolve().parents[2] / "post" / "fonts"
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
W, H, FPS = 1080, 1920, 30
CX, CY = W // 2, int(H * 0.50)          # reference (Sunscream-1 T): wheel ~91% of width, centred mid-frame
R_RIM, R_OUT, R_HUB = 490, 458, 196
# clockwise from the top: violet (top) ... yellow (bottom, index 6 = directly opposite)
HUES = ["#6E2BB5", "#9A2FB5", "#C83AAE", "#DC3A6E", "#D7302F", "#E86A2A",
        "#F3C531", "#9BC53D", "#3C9B4B", "#2BA4B4", "#2C6DC1", "#3F43B2"]
BG_TOP, BG_BOT, GRID = (34, 84, 178), (24, 64, 150), (255, 255, 255, 34)


def ease(t):
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def back(t):
    t = max(0.0, min(1.0, t))
    c = 1.4
    return 1 + (c + 1) * (t - 1) ** 3 + c * (t - 1) ** 2


def mix(hex_, w):
    r, g, b = (int(hex_[i:i + 2], 16) for i in (1, 3, 5))
    return (int(r + (255 - r) * w), int(g + (255 - g) * w), int(b + (255 - b) * w), 255)


def background():
    bg = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(bg)
    for y in range(H):
        k = y / H
        d.line([(0, y), (W, y)], fill=tuple(int(BG_TOP[i] + (BG_BOT[i] - BG_TOP[i]) * k) for i in range(3)))
    grid = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    g = ImageDraw.Draw(grid)
    for x in range(0, W, 45):
        g.line([(x, 0), (x, H)], fill=GRID, width=2 if x % 225 == 0 else 1)
    for y in range(0, H, 45):
        g.line([(0, y), (W, y)], fill=GRID, width=2 if y % 225 == 0 else 1)
    bg = bg.convert("RGBA")
    bg.alpha_composite(grid)
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))   # soft light behind the wheel
    ImageDraw.Draw(glow).ellipse([CX - 560, CY - 560, CX + 560, CY + 560], fill=(150, 170, 255, 70))
    bg.alpha_composite(glow.filter(ImageFilter.GaussianBlur(80)))
    return bg


def wheel(ss=2):
    S = (R_RIM + 40) * 2 * ss
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    c = S / 2
    rim = Image.new("RGBA", (S, S), (0, 0, 0, 0))   # glowing white rim
    ImageDraw.Draw(rim).ellipse([c - R_RIM * ss, c - R_RIM * ss, c + R_RIM * ss, c + R_RIM * ss], fill=(255, 255, 255, 255))
    halo = rim.filter(ImageFilter.GaussianBlur(18 * ss))
    im.alpha_composite(halo)
    im.alpha_composite(rim)
    step = (R_OUT - R_HUB) / 5
    bands = [(R_OUT - k * step, w) for k, w in enumerate((0.0, 0.18, 0.36, 0.54, 0.70))]   # 5 tint rings, saturated outside
    for i, hx in enumerate(HUES):
        a0 = -90 - 15 + i * 30
        for r, w in bands:
            rr = r * ss
            d.pieslice([c - rr, c - rr, c + rr, c + rr], a0, a0 + 30, fill=mix(hx, w))
    for r, _ in bands[1:]:   # thin white ring lines
        rr = r * ss
        d.ellipse([c - rr, c - rr, c + rr, c + rr], outline=(255, 255, 255, 150), width=2 * ss)
    for i in range(12):      # thin white spokes
        a = math.radians(-90 - 15 + i * 30)
        d.line([(c + R_HUB * ss * math.cos(a), c + R_HUB * ss * math.sin(a)),
                (c + R_OUT * ss * math.cos(a), c + R_OUT * ss * math.sin(a))], fill=(255, 255, 255, 170), width=2 * ss)
    hr = R_HUB * ss
    d.ellipse([c - hr, c - hr, c + hr, c + hr], fill=(255, 255, 255, 255))
    return im.resize((S // ss, S // ss), Image.LANCZOS)


def marker(color, r=30):
    """Hollow white ring with a tinted centre (as in the reference)."""
    S = r * 2 + 40
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r], fill=color[:3] + (235,), outline=(255, 255, 255, 255), width=7)
    return im


def glow(color, r=190):
    """Bright burst: wide coloured bloom + tight white-hot core (reference look)."""
    S = int(r * 2 + r * 2.6)   # room for the blur so the bloom never gets cut off (no hard edges)
    out = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    for rad, alpha, blur, col in ((r, 210, r * 0.35, color[:3]), (r * 0.55, 255, r * 0.18, color[:3]),
                                   (r * 0.22, 255, r * 0.08, (255, 255, 255))):
        g = Image.new("RGBA", (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(g).ellipse([S / 2 - rad, S / 2 - rad, S / 2 + rad, S / 2 + rad], fill=col + (alpha,))
        out.alpha_composite(g.filter(ImageFilter.GaussianBlur(blur)))
    return out


def text_img(txt, font, fill=(255, 255, 255, 255)):
    bb = font.getbbox(txt)
    im = Image.new("RGBA", (bb[2] + 40, bb[3] + 40), (0, 0, 0, 0))
    sh = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).text((20, 26), txt, font=font, fill=(10, 20, 70, 140))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(6)))
    ImageDraw.Draw(im).text((20, 20), txt, font=font, fill=fill)
    return im


def paste(base, im, cx, cy, alpha=1.0, scale=1.0, rot=0.0):
    if alpha <= 0.01 or scale <= 0.01:
        return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    if rot:
        im = im.rotate(rot, resample=Image.BICUBIC, expand=True)
    if alpha < 1.0:
        im = im.copy()
        im.putalpha(im.split()[3].point(lambda v: int(v * alpha)))
    base.alpha_composite(im, (int(cx - im.width / 2), int(cy - im.height / 2)))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--dur", type=float, default=5.0)   # animation completes by ~1.8 s, then holds
    a = ap.parse_args()
    bg, wh = background(), wheel()
    f1, f2 = ImageFont.truetype(str(FONTS / "Lato-Black.ttf"), 108), ImageFont.truetype(str(FONTS / "Lato-Bold.ttf"), 52)
    t1, t2, t3 = text_img("PURPLE TINT", f1), text_img("INSTANT GLOW", f1), text_img("FOR INDIAN SKIN TONE", f2)
    PURPLE, YELLOW = (122, 52, 190, 255), (246, 204, 52, 255)
    mp, my, gp, gy = marker(PURPLE), marker(YELLOW), glow(PURPLE), glow(YELLOW)
    flash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(flash).ellipse([CX - 520, CY - 520, CX + 520, CY + 520], fill=(255, 255, 255, 255))
    flash = flash.filter(ImageFilter.GaussianBlur(90))
    r_mark = R_OUT - 34
    top, bot = (CX, CY - r_mark), (CX, CY + r_mark)
    n = int(a.dur * FPS)
    proc = subprocess.Popen([FF, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(FPS),
                             "-i", "-", "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p", a.out], stdin=subprocess.PIPE)
    for k in range(n):
        t = k / FPS
        fr = bg.copy()
        for img, y in ((t1, 0.095), (t2, 0.153), (t3, 0.203)):
            paste(fr, img, W / 2, H * y, alpha=ease(t / 0.25))
        we = ease((t - 0.12) / 0.3)
        paste(fr, wh, CX, CY, alpha=we, scale=0.95 + 0.05 * we)
        fa = max(0.0, 1 - abs(t - 0.12) / 0.22)          # white flash as the wheel arrives
        paste(fr, flash, W / 2, H / 2, alpha=0.9 * fa)
        if t > 0.35:                                       # hollow markers
            paste(fr, mp, *top, alpha=ease((t - 0.35) / 0.2))
            paste(fr, my, *bot, alpha=ease((t - 0.35) / 0.2))
        if t > 0.6:                                        # line draws top -> bottom through the centre
            g = ease((t - 0.6) / 0.55)
            y1 = top[1] + 30 + (bot[1] - top[1] - 60) * g
            ImageDraw.Draw(fr).line([(CX, top[1] + 30), (CX, y1)], fill=(27, 46, 138, 255), width=6)
        if t > 1.05:                                       # purple glow burst, then a gentle pulse
            e = ease((t - 1.05) / 0.3)
            pulse = 1 + 0.08 * math.sin((t - 1.05) * 4)
            paste(fr, gp, *top, alpha=e, scale=(0.6 + 0.4 * e) * pulse)
        if t > 1.45:                                       # yellow glow burst
            e = ease((t - 1.45) / 0.3)
            pulse = 1 + 0.08 * math.sin((t - 1.45) * 4 + 1.2)
            paste(fr, gy, *bot, alpha=e, scale=(0.6 + 0.4 * e) * pulse)
        if t > 0.35:                                       # markers stay crisp on top of their glows
            paste(fr, mp, *top)
            paste(fr, my, *bot)
        proc.stdin.write(fr.tobytes())
    proc.stdin.close()
    proc.wait()
    print("wrote", a.out)


if __name__ == "__main__":
    main()
