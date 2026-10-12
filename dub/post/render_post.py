#!/usr/bin/env python3
"""render_post.py — final-delivery renderer for the DERMDOC dubbed ads.

Turns every dubbed video out/<id>_<lang>.mp4 into a client-ready 1080x1920 ad:
lanczos upscale -> on-screen text from work/<id>/graphics.json -> word-synced dub-language captions with the
brand-blue active-word box -> DERMDOC logo (top-left) -> 5 s product outro (silent).  See post/RENDER_SPEC.md.

USAGE  (run from anywhere; paths are resolved from this file)
  .venv/bin/python post/render_post.py                              # everything that is ready, 3 parallel renders
  .venv/bin/python post/render_post.py --ids 00b304b4 02bad3b3      # only these videos (all 5 languages)
  .venv/bin/python post/render_post.py --ids 00b304b4 --langs ta bn --force
  .venv/bin/python post/render_post.py --preview 00b304b4 ta        # 6 QA stills -> post/preview/
  .venv/bin/python post/render_post.py --preview 00b304b4 ta --times 1.0 8.2 20.5
  .venv/bin/python post/render_post.py --ads                        # the 10 original-language Hinglish ads
  .venv/bin/python post/render_post.py --preview ce52c347           # stills for an ad (no language needed)

OPTIONS
  --ids ID [ID ...]   video ids (dir names in work/, prefix match ok). Default: every dubbed id with a
                      work/<id>/graphics.json (with --ads: every ad).
  --langs L [L ...]   any of bn ta te ml or (default: all five). Ignored with --ads.
  --ads               render the original-language Hinglish ads (work/<id>/meta.json "kind": "ad") instead of dubs:
                      input work/<id>/source.mp4 (original audio), captions from work/<id>/captions.json word timings
                      (Poppins SemiBold, same 1-2 word chunks + blue active-word box); graphics/logo/outro identical.
  --jobs N            parallel renders (default 3, hard-capped at 3). Each ffmpeg runs `nice -n 10` with -threads 3,
                      starts only when `memory_pressure -Q` free >= 25 % and fewer than 3 renders run system-wide.
  --force             re-render outputs that already exist (default: skip them).
  --preview ID LANG   render 6 stills (PNG) at interesting times (hook / pill / claim / label / caption highlight /
                      outro) into post/preview/<id>_<lang>_<k>_<t>s.png instead of a video (ads: LANG optional).
  --times T [T ...]   with --preview: still times in seconds on the final timeline (outro starts at the dub's end).
  --dry-run           write the .ass and print the ffmpeg command, render nothing.

OUTPUT
  deliver/<Bengali|Tamil|Telugu|Malayalam|Odia>/<NN>_<title>_<id>.mp4 (NN + title exactly as organize.py names them),
  1080x1920 30 fps H.264 (h264_videotoolbox, 10M/14M max, high, yuv420p, faststart) + AAC 192k 48 kHz stereo,
  duration = dubbed video + 5 s outro.  Generated .ass files live in post/cache/, failure logs in post/logs/.
  Ads: deliver/Hinglish_Ads/<NN>_<PS|KNC>_<title>_<id>.mp4 (NN = createdAt order among the ads, title = slug of the
  opening voiceover sentence).
  (id, lang) pairs without out/<id>_<lang>/layout.json or work/<id>/graphics.json are skipped with a message.

LOOK NOTES
  * Sizes of on-screen text are visual em sizes in px (hook 84, pill 56, claim 96/sub 44, label 58, tag 40); they
    shrink automatically to fit the frame. Captions use ASS size 54 (Indic) / 44 px em Poppins (Hinglish).
  * All text is measured with uharfbuzz on the same font files libass uses (px/unit = fs / (winAscent+winDescent)),
    so the blue active-word box sits exactly behind the spoken word for every script.
  * Logo: per-video dark/white choice as in the spec, plus a legibility guard that swaps the variant (on the shot
    cut) for stretches >= 0.8 s where the chosen one would vanish (dark logo on luma < 100, white on luma > 200).
  * Garbled baked-in text: a pill "mask" box (or a {"type":"blur","box":{...}} element) gets a feathered frosted
    gaussian blur (box + 2 % pad, 48 px soft edge, sigma 26, 120 ms fades) inside the same filtergraph; the pill is
    then drawn at its natural size on the mask centre (or text_x/text_y). Empty "lines" -> blur only.
  * Cards (pills / name tags) are rounded, shadowed, <= 86 % of the frame wide; a newer card landing on an older one
    replaces it (never stacked). Text blocks are nudged off the logo and the caption band.
    JetBrains Mono ligatures (PA+++ etc.) are suppressed.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import subprocess
import threading
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

import uharfbuzz as hb
from fontTools.ttLib import TTFont

ROOT = Path(__file__).resolve().parent.parent
POST = ROOT / "post"
FONT_DIR = POST / "fonts"
ASSETS = POST / "assets"
CACHE = POST / "cache"
LOGS = POST / "logs"
PREVIEW_DIR = POST / "preview"
DELIVER = ROOT / "deliver"
FFMPEG = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FFPROBE = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"

W, H, FPS = 1080, 1920, 30
OUTRO_DUR = 5.0
MAX_JOBS = 3
MIN_FREE_PCT = 25

LANG_NAME = {"bn": "Bengali", "ta": "Tamil", "te": "Telugu", "ml": "Malayalam", "or": "Odia",
             "en": "English"}   # en: the General Ads only (client: general ads ship in English, no Indic dubs)
DUB_LANGS = [l for l in LANG_NAME if l != "en"]

# font key -> (file, name used inside the ASS; verified against the font's name table at startup)
FONTS = {
    "bn": ("NotoSansBengali-SemiBold.ttf", "Noto Sans Bengali SemiBold"),
    "ta": ("NotoSansTamil-SemiBold.ttf", "Noto Sans Tamil SemiBold"),
    "te": ("NotoSansTelugu-SemiBold.ttf", "Noto Sans Telugu SemiBold"),
    "ml": ("NotoSansMalayalam-SemiBold.ttf", "Noto Sans Malayalam SemiBold"),
    "or": ("NotoSansOriya-Bold.ttf", "Noto Sans Oriya Bold"),  # no SemiBold cut for Oriya
    # Brand fonts (client: "font is not Lato or Roboto Mono"): Lato for headlines/captions, Roboto Mono for labels.
    # Keys keep their old names (mono_*/pop_*) so the layout code is unchanged.
    "mono_xb": ("RobotoMono-Bold.ttf", "Roboto Mono Bold"),
    "mono_b": ("RobotoMono-Bold.ttf", "Roboto Mono Bold"),
    "pop_black": ("Lato-Black.ttf", "Lato Black"),
    "pop_xb": ("Lato-Black.ttf", "Lato Black"),
    "pop_sb": ("Lato-Bold.ttf", "Lato Bold"),
}

# ---- look constants (1080x1920 px) ----
LOGO_W, LOGO_X, LOGO_Y = 230, 44, 52
LOGO_SHADOW_PAD = 14
LOGO_BOX = (LOGO_X, LOGO_Y, LOGO_X + LOGO_W, LOGO_Y + 70)  # visible logo bbox (height = 230 * 266/873)
LOGO_KEEPOUT = 16  # min distance between logo bbox and any text block

CAPTION_FS = 54          # ASS font size of the captions (libass "real dimension" size)
CAPTION_MAX_W = 820      # caption line never wider than this (keeps clear of HUD brackets)
CAPTION_PAD_X, CAPTION_PAD_Y, CAPTION_RADIUS = 10, 6, 12
CAPTION_HOLD = 0.25
LONG_WORD = 11           # chars; longer words get a chunk of their own
AD_LANG = "hi"           # original-language Hinglish ads (Latin captions, Poppins SemiBold)
AD_CAPTION_EM = 44       # Latin caption em (x-height ~24 px = same body height as the Indic captions at fs 54)
BRAND_BLUE = "#2F4DB0"
NAVY = "#1C2B5E"
ACCENT = {"uv_sunscreen": "#7B4FD6", "kojic_night_cream": "#2F4DB0"}
HOOK_OUTLINE = {"uv_sunscreen": "#3B1A6E", "kojic_night_cream": "#1C2B5E"}
POS_Y = {"top": 0.16, "upper": 0.30, "center": 0.50, "lower": 0.68}
SAFE_X = 40              # min side margin for text blocks


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


# ----------------------------------------------------------------------------------------------------------------------
# fonts: harfbuzz measurement that reproduces libass layout exactly
# ----------------------------------------------------------------------------------------------------------------------
class FontM:
    """Font metrics + shaping. libass sizes fonts so that (usWinAscent + usWinDescent) == \\fs, i.e.
    px_per_unit = fs / (winA + winD); with \\an7 the line top is at pos.y and the baseline at pos.y + winA*ppu."""

    _cache: dict[str, "FontM"] = {}

    def __init__(self, key: str):
        file, name = FONTS[key]
        self.key, self.name, self.path = key, name, FONT_DIR / file
        tt = TTFont(self.path)
        names = {tt["name"].getDebugName(i) for i in (1, 4, 6)}
        if name not in names:
            raise SystemExit(f"font {file}: ASS name '{name}' not in name table {names}")
        self.upm = tt["head"].unitsPerEm
        os2 = tt["OS/2"]
        self.winA, self.winD = os2.usWinAscent, os2.usWinDescent
        self.cap = getattr(os2, "sCapHeight", 0) or int(0.7 * self.upm)
        self.cmap = set(tt.getBestCmap())
        self.hbf = hb.Font(hb.Face(hb.Blob.from_file_path(str(self.path))))
        self.hbf.scale = (self.upm, self.upm)
        self._shape_cache: dict[str, list] = {}

    @classmethod
    def get(cls, key: str) -> "FontM":
        if key not in cls._cache:
            cls._cache[key] = FontM(key)
        return cls._cache[key]

    # sizes
    def fs_for_em(self, em: float) -> float:
        return em * (self.winA + self.winD) / self.upm

    def em_for_fs(self, fs: float) -> float:
        return fs * self.upm / (self.winA + self.winD)

    def shape(self, text: str):
        """-> list of (cluster, pen_x, x_adv, x_off, y_off, extents|None) in font units."""
        if text in self._shape_cache:
            return self._shape_cache[text]
        buf = hb.Buffer()
        buf.add_codepoints([ord(c) for c in text])
        buf.guess_segment_properties()
        hb.shape(self.hbf, buf, {"kern": True})
        out, pen = [], 0
        for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
            ext = self.hbf.get_glyph_extents(info.codepoint)
            out.append((info.cluster, pen, pos.x_advance, pos.x_offset, pos.y_offset, ext))
            pen += pos.x_advance
        self._shape_cache[text] = out
        return out

    def width(self, text: str, em: float) -> float:
        g = self.shape(text)
        return sum(x[2] for x in g) * em / self.upm

    def ink(self, text: str, em: float, lo: int = 0, hi: int | None = None):
        """ink box of the glyphs whose cluster is in [lo, hi): (x0, x1, top, bottom, adv_x0, adv_x1) in px,
        x relative to the pen start of the whole string, top = px above baseline, bottom = px below baseline."""
        hi = len(text) if hi is None else hi
        s = em / self.upm
        x0 = y_top = 1e9
        x1 = y_bot = -1e9
        ax0, ax1 = 1e9, -1e9
        for cl, pen, adv, xo, yo, ext in self.shape(text):
            if not lo <= cl < hi:
                continue
            ax0, ax1 = min(ax0, pen), max(ax1, pen + adv)
            if ext and ext.width:
                gx = pen + xo + ext.x_bearing
                x0, x1 = min(x0, gx), max(x1, gx + ext.width)
                top = yo + ext.y_bearing
                bot = top + ext.height  # height is negative
                y_top, y_bot = min(y_top, -top), max(y_bot, -bot)
        if ax0 > ax1:
            return None
        if x0 > x1:
            x0, x1, y_top, y_bot = ax0, ax1, 0, 0
        return (x0 * s, x1 * s, -y_top * s, y_bot * s, ax0 * s, ax1 * s)

    def an5_y(self, cap_center_y: float, em: float, cap: float | None = None) -> float:
        """pos.y for \\an5 so that the (cap-height) centre of the line lands on cap_center_y."""
        ppu = em / self.upm
        cap = self.cap if cap is None else cap
        # libass \\an5: line box (winA+winD) centred on pos.y -> baseline = pos.y + (winA - winD)/2
        return cap_center_y + cap * ppu / 2 - (self.winA - self.winD) * ppu / 2


# ----------------------------------------------------------------------------------------------------------------------
# small ASS helpers
# ----------------------------------------------------------------------------------------------------------------------
def ass_color(hex_rgb: str) -> str:
    h = hex_rgb.lstrip("#")
    return f"&H{h[4:6]}{h[2:4]}{h[0:2]}&".upper()


def ass_alpha(opacity: float) -> str:
    return f"&H{int(round((1 - max(0.0, min(1.0, opacity))) * 255)):02X}&"


def ts(t: float) -> str:
    t = max(0.0, t)
    cs = int(round(t * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def f1(v: float) -> str:
    return f"{v:.1f}".rstrip("0").rstrip(".") if abs(v - round(v)) > 1e-6 else str(int(round(v)))


def rrect(x0, y0, x1, y1, r) -> str:
    r = max(0.0, min(r, (x1 - x0) / 2, (y1 - y0) / 2))
    k = 0.4477 * r  # control-point inset (1 - 0.5523) * r
    p = [f"m {f1(x0 + r)} {f1(y0)}", f"l {f1(x1 - r)} {f1(y0)}",
         f"b {f1(x1 - k)} {f1(y0)} {f1(x1)} {f1(y0 + k)} {f1(x1)} {f1(y0 + r)}",
         f"l {f1(x1)} {f1(y1 - r)}",
         f"b {f1(x1)} {f1(y1 - k)} {f1(x1 - k)} {f1(y1)} {f1(x1 - r)} {f1(y1)}",
         f"l {f1(x0 + r)} {f1(y1)}",
         f"b {f1(x0 + k)} {f1(y1)} {f1(x0)} {f1(y1 - k)} {f1(x0)} {f1(y1 - r)}",
         f"l {f1(x0)} {f1(y0 + r)}",
         f"b {f1(x0)} {f1(y0 + k)} {f1(x0 + k)} {f1(y0)} {f1(x0 + r)} {f1(y0)}"]
    return " ".join(p)


def rect(x0, y0, x1, y1) -> str:
    return f"m {f1(x0)} {f1(y0)} l {f1(x1)} {f1(y0)} {f1(x1)} {f1(y1)} {f1(x0)} {f1(y1)}"


def clean_text(s: str) -> str:
    return s.replace("{", "(").replace("}", ")").replace("\\", "/")


def mono_text(s: str) -> str:
    """JetBrains Mono turns '+++', '--', '..' etc. into programming ligatures (e.g. PA+++ -> joined pluses).
    libass offers no feature switch, so force a shaping-run break between adjacent symbols with an (invisible)
    0.01 px letter-spacing change; advances in a monospace font are unchanged."""
    s = clean_text(s)
    out, odd = [], False
    for i, ch in enumerate(s):
        if i and not ch.isalnum() and not ch.isspace() and not s[i - 1].isalnum() and not s[i - 1].isspace():
            odd = not odd
            out.append("{\\fsp0.01}" if odd else "{\\fsp0}")
        out.append(ch)
    return "".join(out)


class Ass:
    def __init__(self):
        self.events: list[tuple[int, float, float, str]] = []
        self.goff = 0  # graphics layer offset: each on-screen element gets its own layer band (later = on top)

    def add(self, layer: int, t0: float, t1: float, text: str):
        if 20 <= layer < 30:
            layer += self.goff
        if t1 - t0 >= 0.01:
            self.events.append((layer, t0, t1, text))

    def draw(self, layer, t0, t1, tags, path):
        self.add(layer, t0, t1, "{" + tags + "\\p1}" + path + "{\\p0}")

    def text(self, layer, t0, t1, tags, txt, mono=False):
        self.add(layer, t0, t1, "{" + tags + "}" + (mono_text(txt) if mono else clean_text(txt)))

    def dump(self) -> str:
        head = (
            "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n"
            "ScaledBorderAndShadow: yes\nKerning: yes\nYCbCr Matrix: TV.709\n\n"
            "[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
            "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding\n"
            "Style: D,Lato Bold,50,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,"
            "0,0,0,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n")
        rows = [f"Dialogue: {l},{ts(a)},{ts(b)},D,,0,0,0,,{t}" for l, a, b, t in
                sorted(self.events, key=lambda e: (e[1], e[0]))]
        return head + "\n".join(rows) + "\n"


# ----------------------------------------------------------------------------------------------------------------------
# captions: words -> timing -> chunks -> ASS
# ----------------------------------------------------------------------------------------------------------------------
STRIP = set(",.!;:।॥\"'“”‘’()[]{}…–—-*_/|~")
BREAK_PUNCT = set(",.!?;:।॥…–—")


@dataclass
class Word:
    text: str          # display text
    weight: float      # spoken-length proxy (letters + marks)
    pause_after: bool  # source token ended with punctuation
    t0: float = 0.0
    t1: float = 0.0


INDIC_BASE = {"bn": "ক", "ta": "க", "te": "క", "ml": "ക", "or": "କ"}


class CapText:
    """Caption typesetting for one language. Indic text uses the language's Noto Sans cut at ASS size 54; Latin runs
    inside it (ingredient / brand terms such as "4% Niacinamide-এ") use Poppins SemiBold at the em size whose
    x-height equals the Indic body height, so mixed lines look even. Each run is measured with uharfbuzz on the
    very font + size libass uses for it."""

    def __init__(self, lang: str):
        self.lang = lang
        self.lat = FontM.get("pop_sb")
        if lang in (AD_LANG, "en"):   # Latin-script captions
            self.ind, self.ind_em = self.lat, AD_CAPTION_EM
            self.lat_em = AD_CAPTION_EM
        else:
            self.ind = FontM.get(lang)
            self.ind_em = self.ind.em_for_fs(CAPTION_FS)
            body = self.ind.ink(INDIC_BASE[lang], self.ind_em)[2]
            xh = 1026 / 2000  # Lato Bold sxHeight / upm
            self.lat_em = min(48.0, max(40.0, body / xh))
        self.gap = self.ind.width(" ", self.ind_em) + 0.25 * self.ind_em  # one space + 0.25 em

    def is_latin(self, ch: str) -> bool:
        if self.ind is self.lat:
            return True
        if ch in "\u200c\u200d":
            return False
        o = ord(ch)
        return o < 0x0250 or 0x2000 <= o <= 0x206F or 0x20A0 <= o <= 0x20CF or o == 0x2122

    def drawable(self, ch: str) -> bool:
        if ch in "\u200c\u200d":
            return self.ind is not self.lat
        return ord(ch) in (self.lat.cmap if self.is_latin(ch) else self.ind.cmap)

    def runs(self, word: str):
        """[(text, font, em, x_offset)] for one word."""
        out, cur, lat = [], "", None
        for ch in word:
            l_ = self.is_latin(ch)
            if cur and l_ != lat:
                out.append((cur, lat))
                cur = ""
            cur += ch
            lat = l_
        if cur:
            out.append((cur, lat))
        res, x = [], 0.0
        for txt, l_ in out:
            f, em = (self.lat, self.lat_em) if l_ else (self.ind, self.ind_em)
            res.append((txt, f, em, x))
            x += f.width(txt, em)
        return res

    def measure(self, word: str):
        """(advance width, ink x0, ink x1, ink top, ink bottom, line ascender) in px, x from the word's pen start."""
        x0 = top = bot = 0.0
        x1 = None
        asc = 0.0
        adv = 0.0
        ink_any = False
        for txt, f, em, xo in self.runs(word):
            ink = f.ink(txt, em)
            adv = xo + f.width(txt, em)
            asc = max(asc, f.winA * em / f.upm)
            if ink:
                if not ink_any:
                    x0, x1 = xo + ink[0], xo + ink[1]
                    ink_any = True
                x0, x1 = min(x0, xo + ink[0]), max(x1, xo + ink[1])
                top, bot = max(top, ink[2]), max(bot, ink[3])
        return adv, min(x0, 0.0), max(x1 if x1 is not None else adv, adv), top, bot, asc

    def width(self, words: list[str]) -> float:
        return sum(self.measure(w)[0] for w in words) + self.gap * max(0, len(words) - 1)

    def ass(self, word: str) -> str:
        parts = []
        for txt, f, em, _ in self.runs(word):
            parts.append(f"{{\\fn{f.name}\\fs{f.fs_for_em(em):.2f}}}{clean_text(txt)}")
        return "".join(parts)


def split_words(text: str, cap: "CapText") -> list[Word]:
    words: list[Word] = []
    for tok in text.split():
        core = tok
        while core and core[0] in STRIP:
            core = core[1:]
        while core and (core[-1] in STRIP or (core[-1] == "?" and core[:-1] and core[-2] in STRIP)):
            core = core[:-1]
        # drop chars neither caption font can draw (a libass fallback font would break the box maths)
        core = "".join(c for c in core if cap.drawable(c))
        core = core.strip("\u200c\u200d")
        pause = bool(tok) and tok[-1] in BREAK_PUNCT
        if not core:
            if words and pause:
                words[-1].pause_after = True
            continue
        wt = sum(1 for c in core if unicodedata.category(c)[0] in "LMN")
        words.append(Word(core, max(1.0, float(wt)), pause))
    return words


def clean_bursts(bursts, t0, t1):
    b = sorted([float(s), float(e)] for s, e in (bursts or []) if e > s)
    if not b:
        return [[t0, t1]]
    merged = [b[0]]
    for s, e in b[1:]:
        if s - merged[-1][1] < 0.08:  # micro-gaps are not pauses
            merged[-1][1] = max(merged[-1][1], e)
        else:
            merged.append([s, e])
    # absorb tiny blips (< 70 ms) into their nearest neighbour
    changed = True
    while changed and len(merged) > 1:
        changed = False
        for i, (s, e) in enumerate(merged):
            if e - s < 0.07:
                if i == 0:
                    merged[1][0] = s
                elif i == len(merged) - 1:
                    merged[i - 1][1] = e
                elif merged[i][0] - merged[i - 1][1] <= merged[i + 1][0] - merged[i][1]:
                    merged[i - 1][1] = e
                else:
                    merged[i + 1][0] = s
                del merged[i]
                changed = True
                break
    return merged


def time_words(words: list[Word], bursts, line_t0, line_t1):
    """Assign each word [t0, t1] inside the line's speech bursts. Words are grouped onto bursts by a small DP
    (burst share of speech time ~ group share of characters, punctuation prefers a burst end), so pauses always fall
    between words; inside a burst the time is split proportionally to character weight."""
    if not words:
        return
    b = clean_bursts(bursts, line_t0, line_t1)
    while len(b) > len(words):  # more pauses than words: close the smallest gap
        gi = min(range(len(b) - 1), key=lambda i: b[i + 1][0] - b[i][1])
        b[gi] = [b[gi][0], b[gi + 1][1]]
        del b[gi + 1]
    K, N = len(b), len(words)
    T = sum(e - s for s, e in b)
    Wt = sum(w.weight for w in words)
    cum = [0.0]
    for w in words:
        cum.append(cum[-1] + w.weight)
    INF = float("inf")
    best = [[INF] * (N + 1) for _ in range(K + 1)]
    back = [[0] * (N + 1) for _ in range(K + 1)]
    best[0][0] = 0.0
    for k in range(1, K + 1):
        dk = (b[k - 1][1] - b[k - 1][0]) / T
        for j in range(k, N - (K - k) + 1):
            for i in range(k - 1, j):
                if best[k - 1][i] == INF:
                    continue
                share = (cum[j] - cum[i]) / Wt
                c = (dk - share) ** 2 + 0.02 * (math.log(max(dk, 1e-3) / max(share, 1e-3))) ** 2
                if k < K and not words[j - 1].pause_after:
                    c += 0.004  # a pause after a word without punctuation is less likely
                if k < K and words[j - 1].pause_after:
                    c -= 0.002
                v = best[k - 1][i] + c
                if v < best[k][j]:
                    best[k][j], back[k][j] = v, i
    j, groups = N, []
    for k in range(K, 0, -1):
        i = back[k][j]
        groups.append((i, j))
        j = i
    groups.reverse()
    for (i, j), (s, e) in zip(groups, b):
        tot = cum[j] - cum[i]
        t = s
        for w in words[i:j]:
            d = (e - s) * w.weight / tot
            w.t0, w.t1 = t, t + d
            t += d
        words[j - 1].t1 = e


@dataclass
class Chunk:
    words: list[Word]
    t0: float
    t1: float
    y: float = 0.0
    fade_in: bool = False
    fade_out: bool = False


def caption_y_at(g: dict, t: float) -> float:
    for mv in g.get("caption_moves") or []:
        try:
            if float(mv["start"]) <= t < float(mv["end"]):
                return float(mv["y"])
        except (KeyError, TypeError, ValueError):
            continue
    return float(g.get("caption_y") or 0.90)


def dub_word_lines(layout: dict, script: dict, lang: str, cap: CapText,
                   cap_lines: dict | None = None) -> list[list[Word]]:
    """dubbed videos: words of each line timed onto that line's speech bursts (layout.json). Caption text comes
    from work/<id>/captions_<lang>.json ("lines": {"<line id>": text}) when it has the line, else from script.json."""
    texts = {ln.get("id"): ln for ln in script.get("lines", [])}
    cap_lines = {str(k): v for k, v in (cap_lines or {}).items()}
    out = []
    for L in sorted(layout.get("lines", []), key=lambda x: x["start"]):
        s = texts.get(L.get("id")) or {}
        txt = cap_lines.get(str(L.get("id")))
        if not (isinstance(txt, str) and txt.strip()):
            if s.get("keep_original"):
                continue
            txt = s.get(lang) or ""
        if not txt.strip():
            continue
        words = split_words(txt, cap)
        if words:
            time_words(words, L.get("speech"), float(L["start"]), float(L["end"]))
            out.append(words)
    return out


def ad_word_lines(captions: dict, cap: CapText) -> list[list[Word]]:
    """original-language ads: captions.json already carries exact per-word timings."""
    words = []
    for it in captions.get("words", []):
        try:
            s, e = float(it["s"]), float(it["e"])
        except (KeyError, TypeError, ValueError):
            continue
        ws = split_words(str(it.get("w", "")), cap)
        if not ws:
            if words and str(it.get("w", ""))[-1:] in BREAK_PUNCT:
                words[-1].pause_after = True
            continue
        for w in ws:  # (a token never splits further; loop keeps it robust)
            w.t0, w.t1 = s, max(e, s + 0.04)
            words.append(w)
    return [words] if words else []


def build_chunks(word_lines: list[list[Word]], cap: CapText, g: dict) -> list[Chunk]:
    chunks: list[Chunk] = []
    for words in word_lines:
        groups: list[list[Word]] = []
        cur: list[Word] = []
        for w in words:
            if cur:
                prev = cur[-1]
                if (len(cur) >= 2 or len(w.text) > LONG_WORD or len(prev.text) > LONG_WORD or prev.pause_after
                        or w.t0 - prev.t1 > 0.30 or cap.width([x.text for x in cur + [w]]) > CAPTION_MAX_W):
                    groups.append(cur)
                    cur = []
            cur.append(w)
        if cur:
            groups.append(cur)
        # a lone word spoken in < 0.25 s would only flash: pair it with a single-word neighbour if the pair fits
        i = 0
        while i < len(groups):
            gr = groups[i]
            if len(gr) == 1 and gr[0].t1 - gr[0].t0 < 0.25:
                for j in (i + 1, i - 1):
                    if 0 <= j < len(groups) and len(groups[j]) == 1:
                        pair = [groups[min(i, j)][0], groups[max(i, j)][0]]
                        if (cap.width([x.text for x in pair]) <= CAPTION_MAX_W
                                and pair[1].t0 - pair[0].t1 <= 0.30):
                            groups[min(i, j)] = pair
                            del groups[max(i, j)]
                            i = min(i, j)
                            break
            i += 1
        chunks += [Chunk(gr, gr[0].t0, gr[-1].t1) for gr in groups]
    chunks.sort(key=lambda c: c.t0)
    for i, c in enumerate(chunks):
        nxt = chunks[i + 1].t0 if i + 1 < len(chunks) else None
        end = max(c.words[-1].t1 + CAPTION_HOLD, c.t0 + 0.12)
        c.t1 = max(c.t0 + 0.02, min(end, nxt)) if nxt is not None else end
        c.y = caption_y_at(g, c.t0) * H
    for i, c in enumerate(chunks):
        c.fade_in = i == 0 or c.t0 - chunks[i - 1].t1 > 0.04
        c.fade_out = i == len(chunks) - 1 or chunks[i + 1].t0 - c.t1 > 0.04
    return chunks


_BOX_METRICS: dict[str, tuple[float, float]] = {}


def caption_box_metrics(cap: CapText) -> tuple[float, float]:
    """(ink above baseline, ink below baseline) in px covering ~90 % of the caption words of this language (dub
    scripts + captions_<lang>.json files, or the ads' captions.json) — one constant box height per language, so the
    highlight never jumps in height."""
    lang = cap.lang
    if lang in _BOX_METRICS:
        return _BOX_METRICS[lang]
    tops, bots = [], []
    texts = []
    if lang == AD_LANG:
        for f in sorted(ROOT.glob("work/*/captions.json"))[:60]:
            try:
                texts += [str(w.get("w", "")) for w in json.loads(f.read_text()).get("words", [])]
            except Exception:
                continue
    else:
        for f in sorted(ROOT.glob(f"out/*_{lang}/script.json"))[:60]:
            try:
                texts += [ln.get(lang) or "" for ln in json.loads(f.read_text()).get("lines", [])]
            except Exception:
                continue
        for f in sorted(ROOT.glob(f"work/*/captions_{lang}.json"))[:60]:
            try:
                texts += [str(v) for v in (json.loads(f.read_text()).get("lines") or {}).values()]
            except Exception:
                continue
    for t in texts:
        for w in split_words(t, cap):
            m = cap.measure(w.text)
            tops.append(m[3])
            bots.append(m[4])
    if not tops:
        r = (0.62 * cap.ind_em, 0.18 * cap.ind_em)
    else:
        tops.sort()
        bots.sort()
        r = (tops[int(0.9 * (len(tops) - 1))], max(0.0, bots[int(0.9 * (len(bots) - 1))]))
    _BOX_METRICS[lang] = r
    return r


def add_captions(ass: Ass, chunks: list[Chunk], cap: CapText):
    """each word is its own \\an7 event at a harfbuzz-computed x (one space + 0.25 em between words), all words of a
    chunk on one shared baseline; the blue box (L201) sits behind the active word's measured extent."""
    top_ext, bot_ext = caption_box_metrics(cap)
    blue = ass_color(BRAND_BLUE)
    for c in chunks:
        ms = [cap.measure(w.text) for w in c.words]
        width = sum(m[0] for m in ms) + cap.gap * (len(ms) - 1)
        scale = min(1.0, (W - 2 * SAFE_X) / width) if width > 0 else 1.0
        left = W / 2 - width * scale / 2
        baseline = c.y - (bot_ext - top_ext) / 2  # box (top_ext .. bot_ext around baseline) centred on c.y
        fi = 70 if c.fade_in else 0
        fo = 90 if c.fade_out else 0
        fad = f"\\fad({fi},{fo})" if fi or fo else ""
        sc = f"\\fscx{scale * 100:.1f}\\fscy{scale * 100:.1f}" if scale < 0.999 else ""
        x = left
        for k, (w, m) in enumerate(zip(c.words, ms)):
            adv, ix0, ix1, _, _, asc = m
            top = baseline - asc * scale
            base = f"\\an7\\pos({f1(x)},{f1(top)}){sc}"
            body = cap.ass(w.text)
            # L200: soft dark shadow (fill invisible, blurred transparent border -> soft drop shadow only)
            ass.add(200, c.t0, c.t1, "{" + base + f"\\1a&HFF&\\3c&H000000&\\3a&HFF&\\bord3\\blur5\\shad2.5"
                                             f"\\4c&H000000&\\4a&H60&{fad}" + "}" + body)
            # L202: crisp white text
            ass.add(202, c.t0, c.t1, "{" + base + f"\\1c&HFFFFFF&\\bord0\\shad0{fad}" + "}" + body)
            # L201: brand-blue box behind the active word
            a = c.t0 if k == 0 else w.t0
            b = c.words[k + 1].t0 if k + 1 < len(c.words) else c.t1
            if b - a >= 0.01:
                bx0 = x + ix0 * scale - CAPTION_PAD_X
                bx1 = x + ix1 * scale + CAPTION_PAD_X
                by0 = baseline - top_ext * scale - CAPTION_PAD_Y
                by1 = baseline + bot_ext * scale + CAPTION_PAD_Y
                bf = f"\\fad({fi if k == 0 else 0},{fo if k == len(c.words) - 1 else 0})" if (fi or fo) else ""
                ass.draw(201, a, b, f"\\an7\\pos(0,0)\\bord0\\shad0\\1c{blue}\\1a&H00&{bf}",
                         rrect(bx0, by0, bx1, by1, CAPTION_RADIUS))
            x += (adv + cap.gap) * scale


# ----------------------------------------------------------------------------------------------------------------------
# on-screen graphics
# ----------------------------------------------------------------------------------------------------------------------
@dataclass
class TLine:
    text: str
    font: FontM
    em: float
    gap_before: float = 0.0  # px between previous line's cap-bottom and this line's cap-top

    @property
    def w(self):
        return self.font.width(self.text, self.em)

    @property
    def cap(self):
        return self.font.cap * self.em / self.font.upm


def fit_em(lines: list[str], font: FontM, em: float, max_w: float, min_em: float) -> float:
    widest = max((font.width(t, em) for t in lines), default=0)
    if widest > max_w:
        em = max(min_em, em * max_w / widest)
    return em


def block_size(lines: list[TLine]) -> tuple[float, float]:
    w = max(l.w for l in lines)
    h = sum(l.cap + l.gap_before for l in lines)
    return w, h


def line_centers(lines: list[TLine], cy: float) -> list[float]:
    _, h = block_size(lines)
    y = cy - h / 2
    out = []
    for l in lines:
        y += l.gap_before
        out.append(y + l.cap / 2)
        y += l.cap
    return out


class Placer:
    """Keeps text blocks inside the frame, out of the logo and off the captions."""

    def __init__(self, g: dict, cap_half: float):
        self.g = g
        self.cap_half = cap_half

    def caption_band(self, t0, t1):
        ys = {float(self.g.get("caption_y") or 0.90)}
        for mv in self.g.get("caption_moves") or []:
            try:
                if float(mv["start"]) < t1 and float(mv["end"]) > t0:
                    ys.add(float(mv["y"]))
            except (KeyError, TypeError, ValueError):
                pass
        return [(y * H - self.cap_half, y * H + self.cap_half) for y in ys]

    def place(self, cx, cy, w, h, t0, t1, margin=SAFE_X):
        cx = min(max(cx, margin + w / 2), W - margin - w / 2) if w < W - 2 * margin else W / 2
        # captions: never overlap the caption band(s) active during the element
        for top, bot in self.caption_band(t0, t1):
            if cy + h / 2 > top - 24 and cy - h / 2 < bot + 24:
                if cy <= (top + bot) / 2:
                    cy = top - 24 - h / 2
                else:
                    cy = bot + 24 + h / 2
        # logo: nudge down just enough
        lx0, ly0, lx1, ly1 = LOGO_BOX
        if cx - w / 2 < lx1 + LOGO_KEEPOUT and cy - h / 2 < ly1 + LOGO_KEEPOUT:
            cy = ly1 + LOGO_KEEPOUT + h / 2
        cy = min(max(cy, 40 + h / 2), H - 40 - h / 2)
        return cx, cy


def elem_center(e: dict) -> tuple[float, float]:
    x = e.get("x")
    y = e.get("y")
    cx = float(x) * W if isinstance(x, (int, float)) else W / 2
    if isinstance(y, (int, float)):
        cy = float(y) * H
    else:
        cy = POS_Y.get(e.get("position") or "center", 0.5) * H
    return cx, cy


POP = "\\fscx85\\fscy85\\t(0,140,\\fscx104\\fscy104)\\t(140,220,\\fscx100\\fscy100)"


def pop_move(cx, ly, cy):
    """per-line \\move so that separately positioned lines follow the block's 85 -> 100 % scale about its centre."""
    return f"\\move({f1(cx)},{f1(cy + (ly - cy) * 0.85)},{f1(cx)},{f1(ly)},0,220)"


def add_hook(ass: Ass, e, product, placer: Placer):
    f = FontM.get("mono_xb")
    bord = 5
    lines_t = [str(t) for t in e.get("lines") or []]
    em = fit_em(lines_t, f, 84, W - 2 * 60 - 2 * bord, 52)
    lines = [TLine(t, f, em, 0 if i == 0 else 0.42 * em) for i, t in enumerate(lines_t)]
    bw, bh = block_size(lines)
    t0, t1 = float(e["start"]), float(e["end"])
    cx, cy = placer.place(*elem_center(e), bw + 2 * bord, bh + 2 * bord + 8, t0, t1)
    outline = ass_color(HOOK_OUTLINE.get(product, "#3B1A6E"))
    style = (f"\\fn{f.name}\\fs{f.fs_for_em(em):.2f}\\1c&HFFFFFF&\\bord{bord}\\3c{outline}\\shad3\\4c{outline}")
    anim = e.get("anim") or "slide_up"
    char_i = 0
    for ln, ly in zip(lines, line_centers(lines, cy)):
        py = f.an5_y(ly, em)
        if anim == "type":
            parts = []
            for ch in ln.text:
                if ch == " ":
                    parts.append(" ")
                    continue
                ms = 60 + char_i * 35
                parts.append(f"{{\\1a&HFF&\\3a&HFF&\\4a&HFF&\\t({ms},{ms + 1},\\1a&H00&\\3a&H00&\\4a&H60&)}}{clean_text(ch)}")
                char_i += 1
            ass.add(22, t0, t1, "{" + f"\\an5\\pos({f1(cx)},{f1(py)}){style}\\fad(0,160)" + "}" + "".join(parts))
        else:
            ass.text(22, t0, t1, f"\\an5\\move({f1(cx)},{f1(py + 40)},{f1(cx)},{f1(py)},0,250){style}\\4a&H60&"
                                 f"\\fad(150,150)", ln.text, mono=True)


PILL_PAD_X, PILL_PAD_Y, PILL_RADIUS = 28, 18, 22
CARD_MAX_W = 0.86 * W  # no card (pill / name tag) wider than 86 % of the frame


def pill_layout(e):
    f = FontM.get("mono_b")
    texts = [str(t) for t in e.get("lines") or [] if str(t).strip()]
    em = fit_em(texts, f, 56, CARD_MAX_W - 2 * PILL_PAD_X, 34) if texts else 56
    lines = [TLine(t, f, em, 0 if i == 0 else 0.5 * em) for i, t in enumerate(texts)]
    bw, bh = block_size(lines) if lines else (0, 0)
    return f, em, lines, bw + 2 * PILL_PAD_X, bh + 2 * PILL_PAD_Y


def pill_geometry(e, placer: Placer):
    """(cx, cy, pw, ph) of a pill at its natural size. Pills that cover a mask sit on the mask centre unless the
    element gives text_x/text_y; every pill is kept in frame, off the logo and off the captions."""
    _, _, _, pw, ph = pill_layout(e)
    t0, t1 = float(e["start"]), float(e["end"])
    m = e.get("mask") if isinstance(e.get("mask"), dict) else None
    if isinstance(e.get("text_x"), (int, float)) and isinstance(e.get("text_y"), (int, float)):
        c = (float(e["text_x"]) * W, float(e["text_y"]) * H)
    elif m:
        c = ((float(m["x0"]) + float(m["x1"])) / 2 * W, (float(m["y0"]) + float(m["y1"])) / 2 * H)
    else:
        c = elem_center(e)
    cx, cy = placer.place(c[0], c[1], pw, ph + 8, t0, t1, margin=24)
    return cx, cy, pw, ph


def add_pill(ass: Ass, e, product, placer: Placer, geom: tuple, end_: float | None = None):
    """white 92 % card, navy mono text, soft drop shadow; end_ = earlier end when a newer card takes this spot."""
    f, em, lines, _, _ = pill_layout(e)
    if not lines:
        return  # blur-only mask
    cx, cy, pw, ph = geom
    t0, t1 = float(e["start"]), float(e["end"])
    if end_ is not None:
        t1 = min(t1, end_)
    navy = ass_color(NAVY)
    shape = rrect(-pw / 2, -ph / 2, pw / 2, ph / 2, PILL_RADIUS)
    shadow = rrect(-pw / 2 + 4, -ph / 2 + 10, pw / 2 - 4, ph / 2 + 10, PILL_RADIUS)
    if (e.get("anim") or "pop") == "pop":
        fad, sc = "\\fad(110,150)", POP
    else:
        fad, sc = "\\fad(120,120)", "\\fscx96\\fscy96\\t(0,200,\\fscx100\\fscy100)"
    ass.draw(20, t0, t1, f"\\an7\\pos({f1(cx)},{f1(cy)})\\bord0\\shad0\\blur10\\1c&H000000&\\1a&HB0&{sc}{fad}", shadow)
    ass.draw(21, t0, t1, f"\\an7\\pos({f1(cx)},{f1(cy)})\\bord0\\shad0\\1c&HFFFFFF&\\1a{ass_alpha(0.92)}{sc}{fad}",
             shape)
    k = 0.85 if sc == POP else 0.96
    for ln, ly in zip(lines, line_centers(lines, cy)):
        py = f.an5_y(ly, em)
        mv = f"\\move({f1(cx)},{f1(cy + (py - cy) * k)},{f1(cx)},{f1(py)},0,{220 if k < 0.9 else 200})"
        ass.text(22, t0, t1, f"\\an5{mv}\\fn{f.name}\\fs{f.fs_for_em(em):.2f}\\1c{navy}"
                             f"\\bord0\\shad0{sc}{fad}", ln.text, mono=True)


# ---- frosted blur over garbled baked-in text (pill "mask" boxes and "blur" elements) ----
BLUR_PAD_X, BLUR_PAD_Y = 0.02 * W, 0.015 * H
BLUR_FEATHER = 48     # px soft alpha falloff outside the padded box
BLUR_SIGMA = 26
BLUR_FADE = 0.12


@dataclass
class BlurRegion:
    t0: float
    t1: float
    x: int
    y: int
    w: int
    h: int
    mask: Path


def blur_regions(g: dict) -> list[BlurRegion]:
    out = []
    for e in g.get("elements", []):
        if not isinstance(e, dict):
            continue
        box = e.get("mask") if e.get("type") == "pill" else e.get("box") if e.get("type") == "blur" else None
        if not isinstance(box, dict):
            continue
        try:
            t0, t1 = float(e["start"]), float(e["end"])
            bx0, by0 = float(box["x0"]) * W, float(box["y0"]) * H
            bx1, by1 = float(box["x1"]) * W, float(box["y1"]) * H
        except (KeyError, TypeError, ValueError):
            continue
        if t1 <= t0 or bx1 <= bx0 or by1 <= by0:
            continue
        core = (max(0.0, bx0 - BLUR_PAD_X), max(0.0, by0 - BLUR_PAD_Y), min(W, bx1 + BLUR_PAD_X), min(H, by1 + BLUR_PAD_Y))
        x = max(0, int(core[0] - BLUR_FEATHER) // 2 * 2)
        y = max(0, int(core[1] - BLUR_FEATHER) // 2 * 2)
        x1 = min(W, (int(math.ceil(core[2] + BLUR_FEATHER)) + 1) // 2 * 2)
        y1 = min(H, (int(math.ceil(core[3] + BLUR_FEATHER)) + 1) // 2 * 2)
        out.append(BlurRegion(t0, t1, x, y, x1 - x, y1 - y,
                              blur_mask_png(x1 - x, y1 - y, (core[0] - x, core[1] - y, core[2] - x, core[3] - y))))
    return out


def blur_mask_png(w: int, h: int, core: tuple) -> Path:
    """grey alpha mask: 255 inside the padded box (rounded corners), smoothstep falloff over BLUR_FEATHER px."""
    key = f"{w}x{h}_" + "_".join(f"{v:.0f}" for v in core)
    out = CACHE / f"blurmask_{key}.png"
    if out.exists():
        return out
    import numpy as np
    from PIL import Image
    r = 28.0
    xs = np.arange(w, dtype=np.float32) + 0.5
    ys = np.arange(h, dtype=np.float32) + 0.5
    X, Y = np.meshgrid(xs, ys)
    # signed distance to the rounded core rect (open where the core touches the frame edge)
    ex0 = -1e6 if core[0] <= 0.5 else core[0] + r
    ey0 = -1e6 if core[1] <= 0.5 else core[1] + r
    ex1 = 1e6 if core[2] >= w - 0.5 else core[2] - r
    ey1 = 1e6 if core[3] >= h - 0.5 else core[3] - r
    dx = np.maximum(np.maximum(ex0 - X, X - ex1), 0)
    dy = np.maximum(np.maximum(ey0 - Y, Y - ey1), 0)
    d = np.sqrt(dx * dx + dy * dy) - r
    tt = np.clip(d / BLUR_FEATHER, 0, 1)
    a = 1 - tt * tt * (3 - 2 * tt)
    CACHE.mkdir(parents=True, exist_ok=True)
    Image.fromarray((a * 255 + 0.5).astype(np.uint8), "L").save(out)
    return out


def add_claim(ass: Ass, e, product, placer: Placer):
    fb, fs_ = FontM.get("pop_black"), FontM.get("pop_sb")
    accent = ass_color(ACCENT.get(product, "#7B4FD6"))
    texts = [str(t) for t in e.get("lines") or []]
    t0, t1 = float(e["start"]), float(e["end"])
    max_w = W - 2 * SAFE_X - 24
    em = fit_em(texts, fb, 96, max_w, 56)
    lines = [TLine(t, fb, em, 0 if i == 0 else 0.30 * em) for i, t in enumerate(texts)]
    sub = str(e.get("sub") or "").strip()
    sub_lines = []
    if sub:
        sem = 44
        if fs_.width(sub, sem) > max_w:
            sem2 = sem * max_w / fs_.width(sub, sem)
            if sem2 >= 34:
                sem = sem2
                sub_lines = [sub]
            else:  # wrap into two balanced lines
                ws = sub.split()
                best = min(range(1, len(ws)), key=lambda k: abs(fs_.width(" ".join(ws[:k]), sem)
                                                                 - fs_.width(" ".join(ws[k:]), sem))) if len(ws) > 1 else 1
                sub_lines = [" ".join(ws[:best]), " ".join(ws[best:])] if len(ws) > 1 else [sub]
                sem = fit_em(sub_lines, fs_, sem, max_w, 30)
        else:
            sub_lines = [sub]
        for i, s in enumerate(sub_lines):
            lines.append(TLine(s, fs_, sem, (0.36 * em) if i == 0 else 0.42 * sem))
    bw, bh = block_size(lines)
    cx, cy = placer.place(*elem_center(e), bw + 30, bh + 30, t0, t1)
    fad = "\\fad(250,250)"
    for ln, ly in zip(lines, line_centers(lines, cy)):
        py = ln.font.an5_y(ly, ln.em)
        if ln.font is fb:
            tags = (f"\\an5\\pos({f1(cx)},{f1(py)})\\fn{fb.name}\\fs{fb.fs_for_em(ln.em):.2f}\\1c&HFFFFFF&"
                    f"\\bord6\\3c{accent}\\blur6\\shad3\\4c&H000000&\\4a&HA0&{fad}")
        else:
            tags = (f"\\an5\\pos({f1(cx)},{f1(py)})\\fn{fs_.name}\\fs{fs_.fs_for_em(ln.em):.2f}\\1c&HFFFFFF&"
                    f"\\bord3\\3c{accent}\\blur4\\shad2\\4c&H000000&\\4a&HB0&{fad}")
        ass.text(23, t0, t1, tags, ln.text)


def add_label(ass: Ass, e, product, placer: Placer):
    texts = [str(t) for t in e.get("lines") or []]
    if not texts:
        return
    t0, t1 = float(e["start"]), float(e["end"])
    f = FontM.get("pop_xb")
    fad = "\\fad(110,150)"
    # before/after split labels ("BEFORE", "AFTER", "AFTER 2 WEEKS", "INSTANT GLOW") share one white headline style
    if len(texts) == 1 and texts[0].strip().upper().startswith(("BEFORE", "AFTER", "INSTANT GLOW")):
        em = 58 if len(texts[0].strip()) <= 6 else 50
        ln = TLine(texts[0], f, em)
        cx, cy = placer.place(*elem_center(e), ln.w + 12, ln.cap + 12, t0, t1, margin=24)
        py = f.an5_y(cy, em)
        ass.text(24, t0, t1, f"\\an5\\pos({f1(cx)},{f1(py)})\\fn{f.name}\\fs{f.fs_for_em(em):.2f}\\1c&HFFFFFF&"
                             f"\\bord3\\3c&H000000&\\3a&HFF&\\blur4\\shad3\\4c&H000000&\\4a&H58&{POP}{fad}", ln.text)
        return
    # ingredient on a glowing halo in the footage: bold white text with a glow in the halo's colour (no box), pinned
    # exactly at x/y — every ingredient gets the same face/size so they read as one set
    if e.get("style") == "glow":
        em = float(e.get("em", 40))
        glow = ass_color(e.get("glow", "#FFC94D"))
        cx, cy = elem_center(e)
        for ln, ly in zip([TLine(t, f, em) for t in texts], line_centers([TLine(t, f, em) for t in texts], cy)):
            py = f.an5_y(ly, em)
            ass.text(24, t0, t1, f"\\an5\\pos({f1(cx)},{f1(py)})\\fn{f.name}\\fs{f.fs_for_em(em):.2f}\\1c{glow}\\1a&H30&"
                                 f"\\bord7\\3c{glow}\\3a&H40&\\blur9\\shad0{POP}{fad}", ln.text)
            ass.text(25, t0, t1, f"\\an5\\pos({f1(cx)},{f1(py)})\\fn{f.name}\\fs{f.fs_for_em(em):.2f}\\1c&HFFFFFF&"
                                 f"\\bord1.5\\3c&H202020&\\3a&H90&\\shad0{POP}{fad}", ln.text)
        return
    # character name tag: brand-blue pill
    pad_x, pad_y = 26, 15
    em = fit_em(texts, f, 40, CARD_MAX_W - 2 * pad_x, 28)
    lines = [TLine(t, f, em, 0 if i == 0 else 0.45 * em) for i, t in enumerate(texts)]
    bw, bh = block_size(lines)
    pw, ph = bw + 2 * pad_x, bh + 2 * pad_y
    cx, cy = placer.place(*elem_center(e), pw, ph + 8, t0, t1, margin=24)
    radius = min(ph / 2, 30)
    blue = ass_color(BRAND_BLUE)
    ass.draw(20, t0, t1, f"\\an7\\pos({f1(cx)},{f1(cy)})\\bord0\\shad0\\blur8\\1c&H000000&\\1a&HA8&{POP}{fad}",
             rrect(-pw / 2 + 3, -ph / 2 + 7, pw / 2 - 3, ph / 2 + 7, radius))
    ass.draw(21, t0, t1, f"\\an7\\pos({f1(cx)},{f1(cy)})\\bord0\\shad0\\1c{blue}\\1a&H00&{POP}{fad}",
             rrect(-pw / 2, -ph / 2, pw / 2, ph / 2, radius))
    for ln, ly in zip(lines, line_centers(lines, cy)):
        py = f.an5_y(ly, em)
        ass.text(22, t0, t1, f"\\an5{pop_move(cx, py, cy)}\\fn{f.name}\\fs{f.fs_for_em(em):.2f}\\1c&HFFFFFF&"
                             f"\\bord0\\shad0{POP}{fad}", ln.text)


def add_hud(ass: Ass, e, product, placer: Placer):
    t0, t1 = float(e["start"]), float(e["end"])
    fad = "\\fad(200,200)"
    white = "\\1c&HFFFFFF&\\bord0\\shad0"
    if (e.get("variant") or "corners") == "corners":
        th, arm = 3, 70
        x0, x1 = 60, W - 60
        y0 = LOGO_BOX[3] + 28        # below the logo
        y1 = H - 110
        p = []
        for (cx, cy, sx, sy) in ((x0, y0, 1, 1), (x1, y0, -1, 1), (x0, y1, 1, -1), (x1, y1, -1, -1)):
            hx = sorted((cx, cx + sx * arm))
            hy = sorted((cy, cy + sy * th))
            p.append(rect(hx[0], hy[0], hx[1], hy[1]))
            vx = sorted((cx, cx + sx * th))
            vy = sorted((cy + sy * th, cy + sy * arm))
            p.append(rect(vx[0], vy[0], vx[1], vy[1]))
        ass.draw(10, t0, t1, f"\\an7\\pos(0,0){white}\\1a{ass_alpha(0.55)}{fad}", " ".join(p))
        return
    # scan: thin inset frame + corner accents + crosshair + sweep line + tiny mono tech labels
    cap_top = min(t for t, _ in placer.caption_band(t0, t1))
    x0, x1 = 90, W - 90
    y0 = LOGO_BOX[3] + 48
    y1 = min(H - 90, cap_top - 70)
    th = 2
    frame = " ".join([rect(x0, y0, x1, y0 + th), rect(x0, y1 - th, x1, y1),
                      rect(x0, y0 + th, x0 + th, y1 - th), rect(x1 - th, y0 + th, x1, y1 - th)])
    ass.draw(10, t0, t1, f"\\an7\\pos(0,0){white}\\1a{ass_alpha(0.45)}{fad}", frame)
    acc, a3, off = 40, 4, 14
    p = []
    for (cx, cy, sx, sy) in ((x0 - off, y0 - off, 1, 1), (x1 + off, y0 - off, -1, 1),
                             (x0 - off, y1 + off, 1, -1), (x1 + off, y1 + off, -1, -1)):
        hx = sorted((cx, cx + sx * acc))
        hy = sorted((cy, cy + sy * a3))
        p.append(rect(hx[0], hy[0], hx[1], hy[1]))
        vx = sorted((cx, cx + sx * a3))
        vy = sorted((cy + sy * a3, cy + sy * acc))
        p.append(rect(vx[0], vy[0], vx[1], vy[1]))
    # crosshair (top-right inside the frame) + side ticks at the frame's 42 % line
    chx, chy, r = x1 - 70, y0 + 70, 18
    p += [rect(chx - r, chy - 1, chx - 5, chy + 1), rect(chx + 5, chy - 1, chx + r, chy + 1),
          rect(chx - 1, chy - r, chx + 1, chy - 5), rect(chx - 1, chy + 5, chx + 1, chy + r)]
    my = y0 + 0.42 * (y1 - y0)
    p += [rect(20, my - 1, 62, my + 1), rect(W - 62, my - 1, W - 20, my + 1)]
    ass.draw(11, t0, t1, f"\\an7\\pos(0,0){white}\\1a{ass_alpha(0.6)}{fad}", " ".join(p))
    ass.draw(11, t0, t1, f"\\an7\\pos(0,0){white}\\1a{ass_alpha(0.22)}{fad}", rect(x0 + th, my, x1 - th, my + 2))
    # slow sweep line
    ass.draw(11, t0, t1, f"\\an7\\move(0,{f1(y0 + 6)},0,{f1(y1 - 8)})\\bord0\\shad0\\1c&HFFFFFF&"
                         f"\\1a{ass_alpha(0.35)}\\blur2{fad}", rect(x0 + 6, 0, x1 - 6, 2))
    f = FontM.get("mono_b")
    em = 22
    fs = f.fs_for_em(em)
    la = ass_alpha(0.45)
    lab = f"\\fn{f.name}\\fs{fs:.2f}{white}\\1a{la}{fad}"
    # "ID AX-4021" box top-right above the frame
    tw = f.width("ID AX-4021", em)
    bx1, by1 = x1, y0 - 18
    bx0, by0 = bx1 - tw - 24, by1 - 40
    ass.draw(11, t0, t1, f"\\an7\\pos(0,0){white}\\1a{la}{fad}",
             " ".join([rect(bx0, by0, bx1, by0 + 2), rect(bx0, by1 - 2, bx1, by1),
                       rect(bx0, by0 + 2, bx0 + 2, by1 - 2), rect(bx1 - 2, by0 + 2, bx1, by1 - 2)]))
    ass.text(12, t0, t1, f"\\an5\\pos({f1((bx0 + bx1) / 2)},{f1(f.an5_y((by0 + by1) / 2, em))}){lab}", "ID AX-4021")
    # rotated side labels on the left margin
    for txt, yy in (("10X", y0 + 0.45 * (y1 - y0)), ("1X01", y0 + 0.70 * (y1 - y0))):
        ass.text(12, t0, t1, f"\\an5\\pos(56,{f1(yy)})\\frz90{lab}", txt)
    # bottom-right code under the frame
    ass.text(12, t0, t1, f"\\an9\\pos({f1(x1)},{f1(y1 + 16)}){lab}", "038921")


def add_graphics(ass: Ass, g: dict, placer: Placer):
    product = g.get("product") or "uv_sunscreen"
    els = sorted((e for e in g.get("elements", []) if isinstance(e, dict) and "start" in e and "end" in e),
                 key=lambda e: (e.get("type") != "hud", float(e["start"])))
    # cards at their natural size; a newer card that lands on an older one (time + space overlap) replaces it
    pills = [e for e in els if e.get("type") == "pill"]
    geom, cut = {}, {}
    for e in pills:
        try:
            geom[id(e)] = pill_geometry(e, placer)
        except (KeyError, TypeError, ValueError) as ex:
            log(f"  ! pill {e} skipped: {ex!r}")
    for i, a in enumerate(pills):
        for b in pills[i + 1:]:
            if id(a) not in geom or id(b) not in geom or not pill_layout(b)[2]:
                continue
            if not float(a["start"]) < float(b["start"]) < float(a["end"]):
                continue
            (ax, ay, aw, ah), (bx, by, bw, bh) = geom[id(a)], geom[id(b)]
            if abs(ax - bx) < (aw + bw) / 2 + 20 and abs(ay - by) < (ah + bh) / 2 + 20:
                cut[id(a)] = min(cut.get(id(a), 1e9), float(b["start"]))
    k = 0
    for e in els:
        try:
            t = e.get("type")
            if t not in ("hud", "blur"):
                ass.goff = 10 * k
                k += 1
            if t == "hook_mono":
                add_hook(ass, e, product, placer)
            elif t == "pill":
                if id(e) in geom:
                    add_pill(ass, e, product, placer, geom[id(e)], cut.get(id(e)))
            elif t == "claim_bold":
                add_claim(ass, e, product, placer)
            elif t == "label":
                add_label(ass, e, product, placer)
            elif t == "hud":
                add_hud(ass, e, product, placer)
        except Exception as ex:  # one bad element must not kill the render
            log(f"  ! graphics element {e} skipped: {ex!r}")
    ass.goff = 0


# ----------------------------------------------------------------------------------------------------------------------
# naming (identical to organize.py)
# ----------------------------------------------------------------------------------------------------------------------
def title(wd: Path) -> str:
    p = (wd / "prompt.txt").read_text() if (wd / "prompt.txt").exists() else ""
    m = re.search(r'(?:TITLE:|titled|—)\s*[“"]([^”"]{3,60})[”"]', p) or re.search(r'[“"]([^”"]{4,40})[”"]', p)
    t = m.group(1) if m else ""
    plan = json.loads((wd / "plan.json").read_text()) if (wd / "plan.json").exists() else {}
    style = plan.get("style", "ad")
    product = "kojic-night-cream" if "KOJIC" in p.upper() else "uv-sunscreen" if "VIOLET" in p.upper() else "dermdoc"
    slug = re.sub(r"[^a-z0-9]+", "-", (t or style).lower()).strip("-")[:40]
    return f"{product}_{style}_{slug}"


_ORDER: dict[str, int] | None = None


def order_of(vid: str) -> int:
    global _ORDER
    if _ORDER is None:
        ids = sorted(p.parent for p in (ROOT / "work").glob("*/plan.json"))
        meta = {wd.name: json.loads((wd / "meta.json").read_text())["createdAt"] if (wd / "meta.json").exists() else 0
                for wd in ids}
        _ORDER = {v: i + 1 for i, v in enumerate(sorted(meta, key=meta.get))}
    return _ORDER[vid]


def video_kind(vid: str) -> str:
    """'ad' for the original-language Hinglish ads (meta.json kind == "ad"), else 'dub'."""
    mf = ROOT / "work" / vid / "meta.json"
    try:
        return "ad" if json.loads(mf.read_text()).get("kind") == "ad" else "dub"
    except Exception:
        return "dub"


_AD_ORDER: dict[str, int] | None = None


def ad_order_of(vid: str) -> int:
    global _AD_ORDER
    if _AD_ORDER is None:
        meta = {}
        for mf in (ROOT / "work").glob("*/meta.json"):
            try:
                m = json.loads(mf.read_text())
            except Exception:
                continue
            if m.get("kind") in ("ad", "ad_dub"):   # ad_dub = the rebuilt general ads
                meta[mf.parent.name] = m.get("createdAt", 0)
        _AD_ORDER = {v: i + 1 for i, v in enumerate(sorted(meta, key=lambda k: (meta[k], k)))}
    return _AD_ORDER[vid]


def ad_title(wd: Path) -> str:
    """slug of the ad's opening voiceover sentence (captions.json), e.g. 'dark-spots-scattered-hain'."""
    words = []
    try:
        words = [str(w.get("w", "")) for w in json.loads((wd / "captions.json").read_text()).get("words", [])]
    except Exception:
        pass
    first = []
    for w in words:
        first.append(w)
        if w[-1:] in ".?!" or len(first) >= 7:
            break
    slug = re.sub(r"[^a-z0-9]+", "-", " ".join(first).lower()).strip("-")
    if len(slug) > 40:
        slug = slug[:41].rsplit("-", 1)[0]
    return slug or "ad"


def out_path(vid: str, lang: str) -> Path:
    wd = ROOT / "work" / vid
    if lang in (AD_LANG, "en"):   # general ads keep their ad numbering/titles (English = the rebuilt cut)
        prod = "ad"
        try:
            prod = json.loads((wd / "graphics.json").read_text()).get("product") or ""
        except Exception:
            prompt = (wd / "prompt.txt").read_text() if (wd / "prompt.txt").exists() else ""
            prod = "kojic_night_cream" if "KOJIC" in prompt.upper() else "uv_sunscreen"
        code = {"uv_sunscreen": "PS", "kojic_night_cream": "KNC"}.get(prod, "AD")
        return DELIVER / ("Hinglish_Ads" if lang == AD_LANG else "English") / f"{ad_order_of(vid):02d}_{code}_{ad_title(wd)}_{vid}.mp4"
    return DELIVER / LANG_NAME[lang] / f"{order_of(vid):02d}_{title(wd)}_{vid}.mp4"


# ----------------------------------------------------------------------------------------------------------------------
# media helpers
# ----------------------------------------------------------------------------------------------------------------------
def probe(path: Path) -> dict:
    r = subprocess.run([FFPROBE, "-v", "error", "-show_entries",
                        "stream=codec_type,width,height,nb_frames,duration,r_frame_rate:format=duration",
                        "-of", "json", str(path)], capture_output=True, text=True)
    d = json.loads(r.stdout or "{}")
    v = next((s for s in d.get("streams", []) if s.get("codec_type") == "video"), {})
    a = next((s for s in d.get("streams", []) if s.get("codec_type") == "audio"), None)
    vdur = float(v.get("duration") or d.get("format", {}).get("duration") or 0)
    return {"w": v.get("width"), "h": v.get("height"), "vdur": vdur, "has_audio": a is not None}


_LOGO_LOCK = threading.Lock()


def choose_logo(vid: str, src: Path, dur: float) -> list[tuple[int, int, str]]:
    """Logo plan [(first_frame, end_frame, 'dark'|'white')].
    Base choice per video (spec): mean luma of the top-left region (x 0-320, y 0-180 @1080) on 10 evenly spaced
    frames > 140 -> 'dark' logo, else 'white'. Legibility guard: where the region stays clearly wrong for the base logo
    for >= 0.8 s (dark logo over luma < 100, white logo over luma > 200), that stretch switches to the other logo,
    cutting exactly on the frame where the luma jumps (normally a shot cut).
    Cached per video id in post/cache/<id>_logo.json (identical picture in every language)."""
    cf = CACHE / f"{vid}_logo.json"
    with _LOGO_LOCK:
        if cf.exists():
            try:
                d = json.loads(cf.read_text())
                if d.get("v") == 2:
                    return [tuple(x) for x in d["plan"]]
            except Exception:
                pass
    # top-left 320x180 of the 1080x1920 frame, measured directly on the (near-9:16) source picture
    vf = "crop=trunc(iw*320/1080):trunc(ih*180/1920):0:0,scale=32:18,format=gray"
    r = subprocess.run(["nice", "-n", "10", FFMPEG, "-v", "error", "-threads", "2", "-i", str(src), "-vf", vf,
                        "-fps_mode", "passthrough", "-f", "rawvideo", "-"], capture_output=True)
    d, px = r.stdout, 32 * 18
    lum = [sum(d[i * px:(i + 1) * px]) / px for i in range(len(d) // px)]
    nf = max(1, int(round(dur * FPS)))
    if not lum:
        return [(0, nf, "white")]
    lum = (lum + [lum[-1]] * nf)[:nf]
    samples = [lum[min(nf - 1, int((k + 0.5) * nf / 10))] for k in range(10)]
    base_l = sum(samples) / len(samples)
    base = "dark" if base_l > 140 else "white"
    other = "white" if base == "dark" else "dark"
    sm = [sorted(lum[max(0, i - 2):i + 3])[len(lum[max(0, i - 2):i + 3]) // 2] for i in range(nf)]  # median-5
    bad = [(v < 100) if base == "dark" else (v > 200) for v in sm]
    runs, i = [], 0
    while i < nf:
        if bad[i]:
            j = i
            while j < nf and bad[j]:
                j += 1
            runs.append([i, j])
            i = j
        else:
            i += 1
    merged = []
    for a, b in runs:  # close tiny gaps
        if merged and a - merged[-1][1] <= 6:
            merged[-1][1] = b
        else:
            merged.append([a, b])
    runs = [(a, b) for a, b in merged if b - a >= int(0.8 * FPS)]

    def snap(f):  # move a boundary onto the biggest luma jump within +-6 frames
        lo, hi = max(1, f - 6), min(nf - 1, f + 6)
        if lo >= hi:
            return f
        return max(range(lo, hi + 1), key=lambda k: abs(lum[k] - lum[k - 1]))

    plan, cur = [], 0
    for a, b in runs:
        a = 0 if a <= 6 else snap(a)
        b = nf if b >= nf - 6 else snap(b)
        if a > cur:
            plan.append((cur, a, base))
        if b > a:
            plan.append((a, b, other))
        cur = max(cur, b)
    if cur < nf:
        plan.append((cur, nf, base))
    with _LOGO_LOCK:
        cf.write_text(json.dumps({"v": 2, "base": base, "base_luma": round(base_l, 1), "plan": plan}))
    return plan


def logo_png(variant: str) -> Path:
    """logo resized to LOGO_W with a very soft drop shadow, padded by LOGO_SHADOW_PAD on every side."""
    out = CACHE / f"logo_{variant}_{LOGO_W}.png"
    with _LOGO_LOCK:
        if out.exists():
            return out
        from PIL import Image, ImageFilter
        src = Image.open(ASSETS / f"logo_{variant}.png").convert("RGBA")
        h = round(src.height * LOGO_W / src.width)
        logo = src.resize((LOGO_W, h), Image.LANCZOS)
        pad = LOGO_SHADOW_PAD
        canvas = Image.new("RGBA", (LOGO_W + 2 * pad, h + 2 * pad), (0, 0, 0, 0))
        a = logo.split()[3]
        strength = 0.68 if variant == "white" else 0.28
        sh_a = Image.new("L", canvas.size, 0)
        sh_a.paste(a.point(lambda v: int(v * strength)), (pad, pad + 2))
        sh_a = sh_a.filter(ImageFilter.GaussianBlur(4.5))
        shadow = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        shadow.putalpha(sh_a)
        canvas = Image.alpha_composite(canvas, shadow)
        canvas.alpha_composite(logo, (pad, pad))
        canvas.save(out)
        return out


def outro_for(product: str) -> Path:
    p = ASSETS / f"outro_{product}.mp4"
    return p if p.exists() else ASSETS / "outro_uv_sunscreen.mp4"


# ----------------------------------------------------------------------------------------------------------------------
# job assembly
# ----------------------------------------------------------------------------------------------------------------------
@dataclass
class Job:
    vid: str
    lang: str
    src: Path
    g: dict
    dur: float
    has_audio: bool
    ass_path: Path
    logo_plan: list  # [(f0, f1, variant)]
    blurs: list      # [BlurRegion]
    outro: Path
    out: Path
    chunks: list = field(default_factory=list)


def prepare(vid: str, lang: str) -> tuple[Job | None, str]:
    """lang = bn/ta/te/ml/or for dubbed videos, AD_LANG ('hi') for the original-language ads."""
    wd = ROOT / "work" / vid
    if not (wd / "graphics.json").exists():
        return None, "graphics.json missing (will be provided later)"
    cap = CapText(lang)
    if lang == AD_LANG:
        src = wd / "source.mp4"
        if not src.exists():
            return None, "work/<id>/source.mp4 missing"
        if not (wd / "captions.json").exists():
            return None, "captions.json missing (will be provided later)"
        word_lines = ad_word_lines(json.loads((wd / "captions.json").read_text()), cap)
    else:
        od = ROOT / "out" / f"{vid}_{lang}"
        src = ROOT / "out" / f"{vid}_{lang}.mp4"
        if not (od / "layout.json").exists():
            return None, "layout.json missing (will be provided later)"
        if not src.exists():
            return None, "dubbed video missing"
        if not (od / "script.json").exists():
            return None, "script.json missing"
        cf = wd / f"captions_{lang}.json"
        cap_lines = None
        if cf.exists():
            try:
                cap_lines = json.loads(cf.read_text()).get("lines")
            except Exception as ex:
                log(f"  ! {cf.relative_to(ROOT)} unreadable ({ex!r}); using script.json text")
        word_lines = dub_word_lines(json.loads((od / "layout.json").read_text()),
                                    json.loads((od / "script.json").read_text()), lang, cap, cap_lines)
    g = json.loads((wd / "graphics.json").read_text())
    info = probe(src)
    if not info["vdur"] or info["vdur"] < 3:
        return None, f"input video unreadable/short ({info['vdur']})"
    dur = round(info["vdur"] * FPS) / FPS

    chunks = build_chunks(word_lines, cap, g)
    ass = Ass()
    top_ext, bot_ext = caption_box_metrics(cap)
    placer = Placer(g, (top_ext + bot_ext) / 2 + CAPTION_PAD_Y + 6)
    add_graphics(ass, g, placer)
    add_captions(ass, chunks, cap)
    # clip everything to the main video (the outro carries its own branding)
    ass.events = [(l, a, min(b, dur), t) for l, a, b, t in ass.events if a < dur - 0.01]
    CACHE.mkdir(parents=True, exist_ok=True)
    ass_path = CACHE / f"{vid}_{lang}.ass"
    ass_path.write_text(ass.dump(), encoding="utf-8")
    nf = int(round(dur * FPS))
    if g.get("no_logo"):  # footage already carries its own logo
        plan = []
    else:
        plan = choose_logo(vid, src, dur)
        plan = [(a, min(b, nf), v) for a, b, v in plan if a < nf] or [(0, nf, "white")]
        plan[-1] = (plan[-1][0], nf, plan[-1][2])
    if g.get("logo_until"):  # footage ends on the company end slate, which carries its own logo
        lu = int(round(g["logo_until"] * FPS))
        plan = [(a, min(b, lu), v) for a, b, v in plan if a < lu]
    blurs = [b for b in blur_regions(g) if b.t0 < dur - 0.02]
    for b in blurs:
        b.t1 = min(b.t1, dur)
    job = Job(vid, lang, src, g, dur, info["has_audio"], ass_path, plan, blurs,
              outro_for(g.get("product") or "uv_sunscreen"), out_path(vid, lang), chunks)
    return job, ""


def esc(p: Path) -> str:
    return str(p).replace("\\", "\\").replace(":", "\\:").replace("'", "\\'")


def logo_variants(job: Job) -> list[str]:
    return sorted({v for _, _, v in job.logo_plan}, key=lambda v: min(a for a, _, x in job.logo_plan if x == v))


def filter_graph(job: Job, with_audio: bool) -> str:
    """inputs: 0 = picture (+audio), 1 = outro, 2.. = logo PNGs (one per variant used in the logo plan)."""
    d = job.dur
    lx, ly = LOGO_X - LOGO_SHADOW_PAD, LOGO_Y - LOGO_SHADOW_PAD
    variants = logo_variants(job)
    nb = len(job.blurs)
    v = (f"[0:v]setpts=PTS-STARTPTS,scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
         f"crop={W}:{H},setsar=1,fps={FPS},trim=duration={d:.4f},unsharp=5:5:0.35:5:5:0")
    if nb:
        # frosted blur patches: crop -> gaussian blur -> feathered alpha (PNG) -> overlay during [t0, t1]
        v += f",split={nb + 1}[b0]" + "".join(f"[bs{i}]" for i in range(nb)) + ";"
        for i, b in enumerate(job.blurs):
            mi = 2 + len(variants) + i
            win = f"between(t,{b.t0:.3f},{b.t1:.3f})"
            fo = max(b.t0, b.t1 - BLUR_FADE)
            fade_out = f",fade=t=out:st={fo:.3f}:d={BLUR_FADE}:alpha=1" if b.t1 < d - 0.05 else ""  # no fade into outro
            v += (f"[bs{i}]crop={b.w}:{b.h}:{b.x}:{b.y},"
                  f"gblur=sigma={BLUR_SIGMA}:steps=3:enable='between(t,{b.t0 - 0.1:.3f},{b.t1 + 0.1:.3f})',"
                  f"format=yuva420p[bb{i}];[{mi}:v]format=gray[bm{i}];"
                  f"[bb{i}][bm{i}]alphamerge,fade=t=in:st={b.t0:.3f}:d={BLUR_FADE}:alpha=1{fade_out}[bp{i}];"
                  f"[b{i}][bp{i}]overlay=x={b.x}:y={b.y}:format=auto:enable='{win}'[b{i + 1}];")
        v += f"[b{nb}]"
    else:
        v += ","
    v += f"ass=filename='{esc(job.ass_path)}':fontsdir='{esc(FONT_DIR)}':shaping=complex[l0];"
    for k, var in enumerate(variants):
        wins = [(a, b) for a, b, x in job.logo_plan if x == var]
        en = "+".join(f"between(t,{a / FPS - 0.004:.4f},{(b - 1) / FPS + 0.004:.4f})" for a, b in wins)
        fade = ",fade=t=in:st=0:d=0.3:alpha=1" if wins[0][0] == 0 else ""
        v += (f"[{2 + k}:v]format=rgba{fade}[lg{k}];"
              f"[l{k}][lg{k}]overlay=x={lx}:y={ly}:eof_action=pass:format=auto:enable='{en}'[l{k + 1}];")
    v += (f"[l{len(variants)}]format=yuv420p[mv];"
          f"[1:v]setpts=PTS-STARTPTS,scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},"
          f"setsar=1,fps={FPS},trim=duration={OUTRO_DUR},format=yuv420p[ov];")
    no_outro = bool(job.g.get("no_outro"))
    es = job.g.get("endslate_from")   # footage ends on its own (old) end card: put our end slate over it from here
    if no_outro and es is not None and es < d - 0.2:
        v = v.replace("[l%d]format=yuv420p[mv];" % len(variants), "[l%d]format=yuv420p[mv0];" % len(variants))
        v = v.replace(f"trim=duration={OUTRO_DUR},format=yuv420p[ov];",
                      f"trim=duration={OUTRO_DUR},format=yuv420p,split[ov][oe];"
                      f"[oe]trim=duration={d - es:.4f},setpts=PTS-STARTPTS+{es:.4f}/TB,fade=t=in:st={es:.4f}:d=0.2[oe2];"
                      f"[mv0][oe2]overlay=eof_action=pass:enable='gte(t,{es:.4f})'[mv];")
    if no_outro and not with_audio:
        return v + "[ov]nullsink;[mv]null[v]"
    if not with_audio:
        return v + "[mv][ov]concat=n=2:v=1:a=0[v]"
    if job.has_audio:
        a = (f"[0:a]asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,"
             f"apad,atrim=duration={d:.4f},afade=t=out:st={max(0, d - 0.25):.4f}:d=0.25[ma];")
    else:
        a = f"anullsrc=r=48000:cl=stereo,atrim=duration={d:.4f}[ma];"
    if no_outro:
        return v + a + "[ov]nullsink;[mv]null[v];[ma]anull[a]"
    a += f"anullsrc=r=48000:cl=stereo,atrim=duration={OUTRO_DUR}[oa];"
    return v + a + "[mv][ma][ov][oa]concat=n=2:v=1:a=1[v][a]"


def inputs(job: Job) -> list[str]:
    args = ["-threads", "3", "-i", str(job.src), "-threads", "3", "-i", str(job.outro)]
    for var in logo_variants(job):
        args += ["-loop", "1", "-framerate", str(FPS), "-t", f"{job.dur:.4f}", "-i", str(logo_png(var))]
    for b in job.blurs:
        args += ["-loop", "1", "-framerate", str(FPS), "-t", f"{job.dur:.4f}", "-i", str(b.mask)]
    return args


def render_cmd(job: Job, tmp: Path) -> list[str]:
    return (["nice", "-n", "10", FFMPEG, "-hide_banner", "-nostdin", "-y", "-loglevel", "warning", "-stats_period", "5"]
            + inputs(job)
            + ["-filter_complex_threads", "3", "-filter_complex", filter_graph(job, True),
               "-map", "[v]", "-map", "[a]",
               "-c:v", "h264_videotoolbox", "-b:v", "10M", "-maxrate", "14M", "-bufsize", "20M",
               "-profile:v", "high", "-pix_fmt", "yuv420p", "-g", "60", "-allow_sw", "1",
               "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", "-color_range", "tv",
               "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
               "-threads", "3", "-movflags", "+faststart", "-f", "mp4", str(tmp)])


def renders_running() -> int:
    r = subprocess.run(["pgrep", "-f", "h264_videotoolbox"], capture_output=True, text=True)
    return len([x for x in r.stdout.split() if x.strip()])


def mem_free_pct() -> int:
    r = subprocess.run(["memory_pressure", "-Q"], capture_output=True, text=True)
    m = re.search(r"free percentage:\s*(\d+)%", r.stdout)
    return int(m.group(1)) if m else 100


_START_LOCK = threading.Lock()


def wait_for_slot(tag: str):
    waited = 0
    while True:
        free, running = mem_free_pct(), renders_running()
        if free >= MIN_FREE_PCT and running < MAX_JOBS:
            return
        if waited % 60 == 0:
            log(f"  {tag}: waiting (memory free {free}% / renders running {running})")
        time.sleep(5)
        waited += 5


def run_render(job: Job, force: bool, dry: bool) -> tuple[str, float]:
    tag = f"{job.vid}_{job.lang}"
    if job.out.exists() and not force:
        return "exists", 0.0
    job.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = job.out.with_suffix(".part")
    cmd = render_cmd(job, tmp)
    if dry:
        print(" ".join(f"'{c}'" if " " in c or ";" in c else c for c in cmd))
        return "dry", 0.0
    with _START_LOCK:  # serialise the slot check + process start
        wait_for_slot(tag)
        t0 = time.time()
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        time.sleep(1.0)  # let pgrep see it before the next job checks
    out, err = proc.communicate()
    dt = time.time() - t0
    ok = proc.returncode == 0 and tmp.exists() and tmp.stat().st_size > 100_000
    if ok:
        exp = job.dur + (0 if job.g.get("no_outro") else OUTRO_DUR)
        got = probe(tmp)["vdur"]
        if abs(got - exp) > 0.25:
            ok, err = False, (err or "") + f"\nduration check failed: got {got:.2f}s expected {exp:.2f}s"
    if not ok:
        LOGS.mkdir(parents=True, exist_ok=True)
        lp = LOGS / f"{tag}.log"
        lp.write_text("CMD: " + " ".join(cmd) + f"\nRC: {proc.returncode}\n\nSTDERR:\n{err}\n\nSTDOUT:\n{out}\n")
        tmp.unlink(missing_ok=True)
        return f"FAILED (log: {lp.relative_to(ROOT)})", dt
    tmp.replace(job.out)
    return "ok", dt


# ----------------------------------------------------------------------------------------------------------------------
# preview stills
# ----------------------------------------------------------------------------------------------------------------------
def preview_times(job: Job) -> list[float]:
    picks: list[tuple[float, str]] = []
    els = [e for e in job.g.get("elements", []) if e.get("type") != "hud"]
    seen = set()
    huds = [e for e in job.g.get("elements", []) if e.get("type") == "hud"]
    for e in sorted(els, key=lambda e: e["start"]):
        key = e["type"] + ("_tag" if e["type"] == "label" and str((e.get("lines") or [""])[0]).upper()
                           not in ("BEFORE", "AFTER") else "")
        if key in seen:
            continue
        seen.add(key)
        s, en = float(e["start"]), float(e["end"])
        picks.append((min(s + 0.8, (s + en) / 2 + 0.3), key))
    for h in huds:
        if len(picks) >= 4:
            break
        picks.append(((float(h["start"]) + float(h["end"])) / 2, "hud"))
    picks = picks[:4]
    # a caption with the highlight on the 2nd word of a 2-word chunk, far from already picked times
    two = [c for c in job.chunks if len(c.words) == 2]
    cands = [(c.words[1].t0 + c.words[1].t1) / 2 for c in two] or [(c.t0 + c.t1) / 2 for c in job.chunks]
    cands = [t for t in cands if all(abs(t - p) > 1.0 for p, _ in picks)] or cands
    if cands:
        picks.append((cands[len(cands) // 2], "caption"))
    while len(picks) < 5 and job.chunks:
        c = job.chunks[(len(picks) * 7) % len(job.chunks)]
        picks.append(((c.t0 + c.t1) / 2, "caption"))
    picks = [(min(max(0.05, t), job.dur - 0.05), k) for t, k in picks][:5]
    # top up with caption moments until there are 5 distinct frames before the outro
    extra = sorted(((c.words[-1].t0 + c.words[-1].t1) / 2 for c in job.chunks), key=lambda t: -min(
        [abs(t - p) for p, _ in picks] or [99]))
    for t in extra:
        if len({int(round(p * FPS)) for p, _ in picks}) >= 5:
            break
        picks.append((t, "caption"))
    picks.append((job.dur + OUTRO_DUR / 2, "outro"))
    return sorted(t for t, _ in picks)


def run_preview(vid: str, lang: str | None, times: list[float] | None):
    vid = resolve_ids([vid], kind=None)[0]
    if video_kind(vid) == "ad":
        lang = AD_LANG
    elif lang not in LANG_NAME:
        raise SystemExit(f"{vid} is a dubbed video: give a language, one of {list(LANG_NAME)}")
    job, why = prepare(vid, lang)
    if not job:
        raise SystemExit(f"{vid}_{lang}: {why}")
    ts_ = times or preview_times(job)
    frames = sorted({min(int(round(t * FPS)), int(round((job.dur + OUTRO_DUR) * FPS)) - 1) for t in ts_})
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    for old in PREVIEW_DIR.glob(f"{vid}_{lang}_*.png"):
        old.unlink()
    sel = "+".join(f"eq(n\\,{n})" for n in frames)
    tmpl = PREVIEW_DIR / f"{vid}_{lang}_%02d.png"
    cmd = (["nice", "-n", "10", FFMPEG, "-hide_banner", "-nostdin", "-y", "-loglevel", "error"] + inputs(job)
           + ["-filter_complex_threads", "3", "-filter_complex", filter_graph(job, False) + f";[v]select='{sel}'[s]",
              "-map", "[s]", "-fps_mode", "passthrough", str(tmpl)])
    t0 = time.time()
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"preview failed:\n{r.stderr[-3000:]}")
    outs = []
    for k, n in enumerate(frames, 1):
        p = PREVIEW_DIR / f"{vid}_{lang}_{k:02d}.png"
        if p.exists():
            q = PREVIEW_DIR / f"{vid}_{lang}_{k:02d}_{n / FPS:.2f}s.png"
            p.replace(q)
            outs.append(q)
    log(f"preview {vid}_{lang}: {len(outs)} stills in {time.time() - t0:.1f}s  (logo plan={job.logo_plan}, "
        f"{len(job.chunks)} caption chunks, dur {job.dur:.2f}s + {OUTRO_DUR:.0f}s outro)")
    for q in outs:
        print("  ", q)


# ----------------------------------------------------------------------------------------------------------------------
def resolve_ids(ids: list[str] | None, kind: str | None = "dub") -> list[str]:
    """ids given -> resolved dir names (prefix match); none -> every id of `kind` that has graphics.json
    (ads without graphics.json yet are listed too so they get a clear skip message)."""
    every = sorted(p.name for p in (ROOT / "work").iterdir() if p.is_dir() and (p / "meta.json").exists())
    if not ids:
        if kind == "ad":
            return [v for v in every if video_kind(v) == "ad"]
        return [v for v in every if (ROOT / "work" / v / "graphics.json").exists() and video_kind(v) == "dub"]
    out = []
    for i in ids:
        m = [x for x in every if x.startswith(i)]
        if not m:
            raise SystemExit(f"unknown id {i}")
        if kind and video_kind(m[0]) != kind:
            raise SystemExit(f"{m[0]} is a{'n ad' if video_kind(m[0]) == 'ad' else ' dubbed video'}: "
                             f"{'add' if kind == 'dub' else 'drop'} --ads")
        out.append(m[0])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ids", nargs="+")
    ap.add_argument("--langs", nargs="+", default=DUB_LANGS, choices=list(LANG_NAME))
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--ads", action="store_true", help="render the original-language Hinglish ads instead of dubs")
    ap.add_argument("--preview", nargs="+", metavar="ID [LANG]")
    ap.add_argument("--times", nargs="+", type=float)
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    for k in FONTS:  # verify every font/family name up front
        FontM.get(k)
    if a.preview:
        run_preview(a.preview[0], a.preview[1] if len(a.preview) > 1 else None, a.times)
        return
    jobs_n = max(1, min(MAX_JOBS, a.jobs))
    todo: list[Job] = []
    for vid in resolve_ids(a.ids, "ad" if a.ads else "dub"):
        for lang in ([AD_LANG] if a.ads else a.langs):
            try:
                if not a.force and (ROOT / "work" / vid / "graphics.json").exists() and out_path(vid, lang).exists():
                    log(f"skip {vid}_{lang}: exists ({out_path(vid, lang).relative_to(ROOT)})")
                    continue
                job, why = prepare(vid, lang)
            except Exception as ex:
                job, why = None, f"prepare failed: {ex!r}"
            if job:
                todo.append(job)
            else:
                log(f"skip {vid}_{lang}: {why}")
    log(f"{len(todo)} render(s) queued, {jobs_n} in parallel")
    results = []

    def work(job: Job):
        tag = f"{job.vid}_{job.lang}"
        log(f"start {tag} ({job.dur:.2f}s + outro) -> {job.out.relative_to(ROOT)}")
        st, dt = run_render(job, a.force, a.dry_run)
        log(f"{st:6s} {tag}  {dt:.1f}s")
        results.append((tag, st, dt))

    with ThreadPoolExecutor(max_workers=jobs_n) as ex:
        list(ex.map(work, todo))
    ok = [r for r in results if r[1] == "ok"]
    bad = [r for r in results if r[1].startswith("FAILED")]
    log(f"done: {len(ok)} ok, {len(bad)} failed" + (f"; avg {sum(r[2] for r in ok) / len(ok):.1f}s/render" if ok else ""))
    for r in bad:
        log("  ", r[0], r[1])


if __name__ == "__main__":
    main()
