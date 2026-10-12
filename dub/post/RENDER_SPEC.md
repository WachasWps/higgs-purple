# Renderer spec — final delivery videos (captions + on-screen text + logo + outro)

Build `post/render_post.py` that turns each dubbed video into a client-ready ad matching the approved reference
(`post/assets/reference_final.mp4`, contact sheets in `post/ref/sheet_1.png`, `sheet_2.png` — LOOK at them).

Root: `/Users/wachas/Documents/higgs-purple/dub`. Python: `.venv/bin/python` (has uharfbuzz, fontTools, Pillow, librosa).
ffmpeg with libass + harfbuzz + videotoolbox: `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg` (use this one, NOT plain ffmpeg).

## Inputs per (id, lang) — 29 ids × langs bn ta te ml or
- `out/<id>_<lang>.mp4` — dubbed video (480×854 or similar, 30 fps, AAC). The picture is the original AI video.
- `out/<id>_<lang>/layout.json` — `{"rate", "lines":[{"id","speaker","start","end","speech":[[s,e],...]}]}`: exact
  final-timeline seconds of each dubbed line and its speech bursts.
- `out/<id>_<lang>/script.json` — `{"language", "lines":[{"id", <lang>: "<text in target script>", ...}]}`.
  (For lines with `keep_original: true` the text is empty → no caption.)
- `work/<id>/graphics.json` — on-screen text design (schema in `post/GRAPHICS_BRIEF.md`): `product`, `caption_y`,
  `elements[]` of type hook_mono | pill | claim_bold | label | hud, with start/end (s), lines, sub, position|x,y, anim.
- `work/<id>/meta.json` (duration), `work/<id>/prompt.txt`.
- Fonts (use `fontsdir=post/fonts` in the ass filter and family names inside the ASS):
  Poppins-Black/ExtraBold/SemiBold, JetBrainsMono-ExtraBold/Bold, NotoSans{Bengali,Tamil,Telugu,Malayalam}-SemiBold/Bold,
  NotoSansOriya-Bold (no SemiBold for Oriya). Verify each family name with fontTools before use.
- Logos: `post/assets/logo_dark.png` (black DERMDOC + blue "Honest Science" box), `post/assets/logo_white.png`
  (white DERMDOC + blue "Honest Science" text) — both RGBA.
- Outros (5 s, 576×1024, no audio): `post/assets/outro_uv_sunscreen.mp4`, `post/assets/outro_kojic_night_cream.mp4`
  — pick by graphics.json `product`.

## Output
`deliver/<Language>/<NN>_<title>_<id>.mp4` (Language = Bengali/Tamil/Telugu/Malayalam/Odia; NN + title exactly as
`organize.py`'s naming), 1080×1920, 30 fps, H.264 via `h264_videotoolbox` (-b:v 10M -maxrate 14M, high profile,
yuv420p, +faststart), AAC 192k 48 kHz stereo. Total = dubbed video + 5 s outro.

## Look (match the reference, then make it a touch more premium)
1. **Upscale** the dubbed picture to 1080×1920 (lanczos) before burning text so text is crisp.
2. **Logo** top-left on the whole main video (not on the outro, which has its own branding): width ≈ 230 px at
   x=44, y=52, fade in 0.3 s. Choose per video: sample the source's top-left region (x 0–320, y 0–180 at 1080 scale)
   on ~10 frames; mean luma > 140 → `logo_dark.png`, else `logo_white.png`; add a very soft shadow for legibility.
3. **Captions** (dub language, burned in): small, bottom center at y = caption_y × 1920 (default 0.90), max 2 words
   at a time (1 word if a word is long, > 11 chars), white SemiBold ~54 px with soft dark shadow (no heavy box);
   the CURRENTLY SPOKEN word sits on a brand-blue rounded rectangle (#2F4DB0, radius ~12, padding 10×6) — exactly
   the reference look. Word timing: split each line's text into words; map words onto that line's `speech` bursts
   proportionally to their character counts (graphemes/len without punctuation), so pauses fall between bursts.
   A chunk shows from its first word's start to its last word's end (+ hold up to 0.25 s, never overlapping the next).
   Measure word widths with uharfbuzz using the SAME font file + size as the ASS style to place the highlight box
   behind the right word (ASS vector drawing `\p1` on a lower layer; text on a higher layer). Indic shaping must be
   correct (libass+harfbuzz) — verify visually on a frame for every script.
4. **On-screen text** from graphics.json, ASS at PlayRes 1080×1920, positions: top .16, upper .30, center .50,
   lower .68 (block centre), or explicit x,y (0..1):
   - `hook_mono`: JetBrains Mono ExtraBold ~84 px, white, outline 5 px #3B1A6E, shadow 3; anim slide_up (\move
     +40 px over 250 ms + \fad(150,150)) or type (typewriter reveal ~35 ms/char).
   - `pill`: white rounded pill (92 % opacity, radius 22, padding 28×16) + navy #1C2B5E JetBrains Mono Bold ~56 px,
     1–2 lines; anim pop (scale 85→104→100 % over 220 ms + fade).
   - `claim_bold`: Poppins Black ~96 px white with soft purple glow (\bord 6 #7B4FD6 + \blur 6) and light shadow;
     optional `sub` Poppins SemiBold ~44 px white with small glow under it; anim fade (250 ms in/out).
   - `label`: "BEFORE"/"AFTER" → Poppins ExtraBold ~58 px white with dark shadow, at x,y. Any other label = character
     name tag: brand-blue pill (#2F4DB0) with white Poppins ExtraBold ~40 px, pop anim.
   - `hud` corners: four thin white L-brackets (3 px, 70 px arms, 60 px margin, 55 % opacity); `scan`: thin inset
     frame (90 px) + 2–3 tiny mono tech labels (e.g. "ID AX-4021", "10X", "1X01") at 45 % opacity, like reference.
   Product colour accent: uv_sunscreen → lavender/purple glow (#7B4FD6); kojic_night_cream → deep blue glow (#2F4DB0).
5. **Outro**: scale to 1080×1920 30 fps, append after the main video; audio: fade the main audio out over its last
   0.25 s, then 5 s of silence under the outro.

## Engineering
- One ffmpeg-full invocation per output (filter_complex: scale → ass → overlay logo → concat with outro).
- `--ids`, `--langs`, `--jobs N` (default 3 parallel renders, each `-threads 3`, run under `nice -n 10`), skip outputs
  that exist unless `--force`, write a per-output log on failure and continue.
- `--preview <id> <lang>`: render 6 stills (PNG) at interesting times into `post/preview/` for visual QA.
- If `layout.json` is missing for an (id, lang), skip it with a clear message (it will be provided later).
- Keep the Mac safe: never more than 3 concurrent renders; check `memory_pressure -Q` free % ≥ 25 before starting
  each render (wait otherwise).
- Deliver a short README section at the top of render_post.py: usage + what each option does.
