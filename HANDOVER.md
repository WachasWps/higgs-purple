# DERMDOC × Purplle AI ads: handover

You are taking over a finished but still-live client project: 40 short vertical skincare ads (160 video files) for the Indian brand **DERMDOC**, sold on **Purplle**. Everything has been delivered. Your job is to fix whatever the client flags next, without new AI video generation, because **Higgsfield credits are at 0**.

This doc covers:
- what the project is;
- how every video was made, step by step (what was done by hand and what the engine does);
- what the client asked for and what we did about it;
- the rules you must never break;
- how to fix things, in **Canva** (no code) or with the **code engine** (Mac + Claude Code);
- a ready-to-paste prompt so Claude Code can pick up where we left off.

Full detail (every instruction, every client point with its status, every script) is in [PROJECT_HISTORY.md](PROJECT_HISTORY.md).

---

## 0. What you received

| Thing | Where | What it is |
|---|---|---|
| **GitHub repo** | `github.com/WachasWps/higgs-purple` (private) | All the code, scripts, per-video plans, scripts in 5 languages, on-screen text, edit lists, fonts, logos, end slates, music beds and briefs. Media files are **not** in git (too big). |
| **Zip / Drive** | `DERMDOC_Handover_Kit.zip` | `Canva_Kit/` (every ad split into layers), `Final_Deliverables/` (the 160 delivered videos), this doc and the history. |
| **Full working folder** | Ask wachas (47 GB) | The repo **plus** all media: `work/` (source footage per ad), `out/` (dubbed audio), `feedback/clips` (fix clips), etc. You only need it to re-render with the engine. Copy it over the cloned repo and everything lines up. |

---

## 1. The project in one page

- **Client:** DERMDOC ("Honest Science"), via Dhruv (account contact, WhatsApp group "Crazy Kaam"). Feedback has come from the brand's marketing person through Dhruv, plus an internal QC review by Priyansh (Oct 11).
- **Products:**
  - **PS: Purple Sunscreen.** DERMDOC Ultra Violet, 4% Niacinamide, SPF 50 PA+++. Purple tint cancels yellow-looking dullness, gives an *Instant Glow* and leaves no white cast.
  - **KNC: Kojic Night Cream.** DERMDOC 2% Kojic Acid Night Cream, Glow Fusion Formula with Niacinamide & Alpha Arbutin. Fades the look of dark spots overnight; results show "after 2 weeks".
- **4 categories × 2 products:**

| Category | Ads | Languages | Files |
|---|---|---|---|
| 1. Ingredient Personified (cartoon ingredients / villains) | 5 KNC + 5 PS | 5 regional | 50 |
| 2. Product Avatar (talking product mascot) | 5 KNC + 5 PS | 5 regional | 50 |
| 3. UGC (creator-style selfie ads) | 5 KNC + 5 PS | 5 regional | 50 |
| 4. AI General Ads (premium commercials) | 5 KNC + 5 PS | **English only** | 10 |
| **Total** | **40 ads** | | **160 files** |

- **Regional languages:**

  | Language | Market | Folder |
  |---|---|---|
  | Bengali | West Bengal | `Bengali_WB` |
  | Tamil | Tamil Nadu | `Tamil_TN` |
  | Telugu | Andhra Pradesh / Telangana | `Telugu_APTS` |
  | Malayalam | Kerala | `Malayalam_KL` |
  | Odia | Odisha | `Odia_Od` |

  There is no Hindi or English for categories 1–3.
- **Format:** 1080×1920 vertical, 30 fps.
  - Ads in categories 1–2 run about 15–20 s, plus the 5 s company end slate.
  - The new PS UGCs run 30–37 s.
  - General Ads run 20–36 s.
- **Delivery naming:** `Final_Deliverables/<N_Category>/<Product>/<Lang_Region>/<PS|KNC>_<Category>_<title>_<Language>.mp4`. General Ads use `4_AI_General_Ads/<Product>/<PS|KNC>_General-Ad_<title>_English.mp4`.
- **Drive:** wachas uploads by hand to the client Drive folder "Final_Deliverables (1)", replacing the old files.

Every ad has an 8-character **id** (e.g. `bd3b8af7`). The engine works by id. The table of all 40 ids → titles is in PROJECT_HISTORY.md §7, and each Canva kit folder name ends with its id.

---

## 2. How the videos were made (end-to-end)

```
 (A) BY HAND (wachas + Bhxdxx)                       (B) CLAUDE CODE ENGINE (this repo, runs on a Mac)
 ─────────────────────────────                       ─────────────────────────────────────────────────
 Concept + Hinglish script per ad                     1. prep.py      Demucs voice/music split, Whisper transcript, frames
        │                                             2. plan.json    cast + every line translated to bn/ta/te/ml/or
 ChatGPT / Codex image gen → keyframes &                              (written by Claude "director" agents, DIRECTOR_BRIEF.md)
 5-panel frame sheet + product photos                 3. dubplan.py   Indic-Mio TTS cloning each character's voice
        │                                                             → out/<id>_<lang>.mp4   (Kaggle T4 GPU helped)
 Higgsfield  Wan 3.0  (480p, 20 s, audio on)          4. feedback/…   picture fixes from client notes: Codex redraws +
 shot-by-shot prompt + refs → raw ad video                            Wan 5 s clips, colour wheel, before/after split,
        │                                                             text erase, watermark removal  → source_fixed.mp4
 Downloaded → given to Claude ───────────────────►    5. post/render_post.py  on-screen text, captions in the language,
                                                                      logo, company end slate         → deliver/
 Oct 11: wachas also made the 10 General Ads           6. post/add_audio.py   music bed + SFX, ducked → deliver_music/
 footage himself + downloaded 5 new sunlight          7. tools/pack.sh       folders + loudness -16 LUFS → Final_Deliverables/
 UGC creator videos → given to Claude                  8. post/make_canva_kit.py  → Canva_Kit/ (layers for hand editing)
```

### 2a. Done by hand

1. **Scripts and concepts** per ad, written in Hinglish with speaker labels.
2. **Keyframes** in ChatGPT/Codex image gen, attaching the real product photos (`dub/feedback/product_refs/`).
3. **Video generation** on **Higgsfield, model Wan 3.0**.
   - Original ads: 480p, 20 s, `generate_audio` on.
   - References: 2 product photos plus a 5-panel frame sheet.
   - Prompt: shot by shot, with character dialogue.
   - The Hinglish voices came from the generation itself.
4. **Reference material** for the engine:
   - a finished reference ad for the text and caption style (`post/assets/reference_final.mp4`);
   - a colour-wheel style reference;
   - DERMDOC logos;
   - the **company end-slate videos** (`post/assets/outro_*.mp4`);
   - product photos.
5. **Oct 11:**
   - Made the **10 General Ads** footage (KNC 1–5, PS 1–5; Grok/Gemini/Higgsfield) → `feedback/user_knc_ads`, `feedback/user_ps_ads`.
   - Downloaded **5 new PS UGC creator clips shot in sunlight** → `feedback/user_ugc*`. These replaced all 5 old PS UGCs.
6. **Drive uploads and client messages.**

### 2b. Done by Claude Code (the engine)

The steps below follow the diagram above. Prompts wachas gave are quoted in PROJECT_HISTORY.md §1.

1. **Dubbing** into 5 languages for 30 ads, with character voices: villains menacing, memes squeaky, creators natural, and **female voices only** (client rule).
   - Text is transcreated, not translated. English terms (Niacinamide, SPF 50, Kojic Acid) stay as spoken English.
2. **Post-production:**
   - English on-screen supers (Lato / Roboto Mono, brand blue `#2F4DB0`);
   - word-by-word captions in each language (1–2 words, blue highlight box);
   - DERMDOC logo top-left;
   - the company end slate appended.
3. **Music and SFX:** synthesized by code (copyright-free). PS is 124 BPM dance-pop, KNC is 118 BPM chill-house. Whooshes, pops and dings land on every text card and cut; music ducks under the voice.
4. **Fix rounds** after client feedback (§3):
   - redrew bad frames (Codex) and re-animated them (Wan 3.0, 5 s, 480p, 5 credits each);
   - new colour-wheel graphic;
   - before/after split screens;
   - female recast;
   - frame-by-frame rescript (52 line changes);
   - General Ads rebuilt on wachas' footage with Indian-English VO;
   - PS UGC rebuilt with product B-roll cutaways, dialogue placed on her lip movement ("lipfit");
   - baked AI text erased (inpainting);
   - Grok watermarks removed.

### 2c. Models and tools

| Job | Model / tool |
|---|---|
| Source videos and fix clips | **Higgsfield Wan 3.0** (480p, 5 s fix clips = 5 credits). **Credits now 0.** |
| Keyframe and before/after images | **Codex CLI** → gpt-image (ChatGPT plan). Brief: `dub/feedback/codex/CODEX_BRIEF.md`. Higgsfield nano_banana_pro a few times. |
| Regional voices (bn/ta/te/ml/or) | **Indic-Mio** (SPRINGLab, open source) + **MioCodec** voice cloning, on the Mac (MLX) plus Kaggle T4 |
| English VO (General Ads) | **Kokoro-82M**, voice `hf_alpha`, Indian English (`h`). **Not ElevenLabs**: the free plan can't use library voices via the API. |
| Voice/music split | **Demucs** htdemucs |
| Transcription and QA | **mlx-whisper** large-v3-turbo |
| Lip-sync | LatentSync 1.5 tested on Kaggle; **not shipped**. "lipfit" places lines on mouth movement instead. |
| Render | **ffmpeg-full 9** (libass, harfbuzz) |
| Text erase | OpenCV inpaint (`feedback/detext.py`) |
| Music / SFX | numpy/scipy synthesis (`post/add_audio.py`) |

---

## 3. What the client asked for, and what we did

The client gave three big rounds of feedback. Each point and its status is in PROJECT_HISTORY.md §4. The essentials:

### Round 0 (Oct 7, before dubbing)

- Logo throughout, and an end slate on every ad.
- Start and end on the face; no weird shots.
- Exact packaging: **PS tube with cap, never a nozzle**; correct KNC jar.
- Realistic dark spots, not dots.
- Full absorption, then glow; no glow in the "before".
- PS: sell the **purple tint** (colour wheel, made for Indian skin, Instant Glow, no white cast).
- KNC UGC: "After 2 weeks", half/half before/after split, duskier models.
- Fonts Lato / Roboto Mono.

### Round 1 (Oct 9, Dhruv's WhatsApp + 39 screenshots)

| Ask | Done how |
|---|---|
| General Ads in **English**, much better quality | Rebuilt twice. Final: wachas' own footage, longer shots, Indian-English female VO timed per shot, only our VO, music and SFX, ending "Shop now at Purplle.com" |
| Label all 3 KNC ingredients (2% Kojic Acid, Niacinamide, Alpha Arbutin) | On-screen cards, separate and spelled right |
| Correct colour wheel (purple **opposite yellow**) and explain it | New wheel graphic in every PS ad. VO and captions explain "purple cancels yellow-looking dullness, made for Indian skin tones" |
| PS tube with cap, no nozzle | Bad shots redrawn and replaced |
| "Instant Glow" wherever glow is said | Text and VO pass |
| **Female VO only**, natural | Recast of 31 lines in 18 ads |
| Before/after on every ad | Split screens with new Codex images: PS "AFTER / INSTANT GLOW", KNC "AFTER 2 WEEKS" (only on the split) |
| Morning text only on morning shots | Night shots now say "WORKS WHILE YOU SLEEP" |
| Faster music | New upbeat beds plus more SFX |
| Never say "KNC" | Full product name everywhere |
| UGC must look real | All 5 PS UGCs replaced with new sunlight creator footage, 30–35 s, product B-roll ≥ 2 s, wheel, before/after |

### Round 2 (Oct 11 review)

| Ask | Done how |
|---|---|
| Blur patches | Removed by text inpainting |
| Alpha Arbutin / Kojic mismatch | Fixed |
| Duplicate Niacinamide | Fixed |
| Orb labels not following | Replaced with one card |
| Captions over the after-face | Moved to the divider |
| "2 weeks" on the sleep shot | Erased |
| Grok watermarks | Removed |
| Logo on top of the end slate's logo | Our logo now stops where the slate starts |
| Duplicate filename | Renamed |
| Redundant "Dark Spots" headline | Removed |

### Not fixed (internal only; never list these to the client)

These are the known gaps, so you know what's likely to come back. Most need **new generation**, which is impossible at 0 credits.

1. **Application → fully blended → glow is not shown** in most ads. This is the client's #1 repeated ask; most KNC ads show only the scoop from the jar.
2. Some before/afters are weak (the difference reads as exposure or blur).
3. Dark spots still look like dots in spot-meeting-cancelled (`f7ce58d4`) and the hooks of `715b1b5c` / `7558fbf1`.
4. Packaging leftovers:
   - a nozzle tube in one shot of `c51221b6`;
   - a clear cap in `e7e42eaf`;
   - a carton beside the tube in `655a1328` and `00b304b4`;
   - the animated jar in shhh-she-s-sleeping (`390113f1`).
5. No true lip-sync.
6. General Ads leftovers. wachas said "General Ads are done", so leave them unless the client asks.
7. `715b1b5c` keeps a soft frosted disc at 4.75–6.25 s (the erase left ghost text).

---

## 4. Rules you must never break

1. **Company end slate: never change it**, and it must be on **every** video.
   - Most ads get the 5 s `post/assets/outro_*.mp4` appended.
   - 6 UGCs end on a baked company card.
   - Our DERMDOC logo stops where the slate starts.
2. **CTA:** our text and VO say **"Shop at Purplle.com"** / "Shop now at Purplle.com", never "Available on Purplle". The slate itself is the company's; leave it.
3. **PS tube:** white tube, lavender "ULTRA VIOLET" band, wide flat lavender **cap always on, never a nozzle**. The cream is pale lavender and blends invisibly.
4. **KNC jar:** royal-blue base, white lid, white label (2% KOJIC ACID / GLOW FUSION FORMULA…). Thick white cream, **night use only**.
5. **Female voices only**, natural (not over-animated).
6. **General Ads: English only** (Indian English). Categories 1–3: the 5 regional languages only.
7. Say **"Instant Glow"** for PS. **"AFTER 2 WEEKS"** for KNC, only on the before/after split. Morning wording only on morning shots.
8. Never say "KNC" aloud or on screen; use the full product name. Label the 3 ingredients separately, in the same font.
9. **"3XPERT"** is the correct spelling (product name), not EXPERT.
10. **The colour-wheel graphic is final.** Don't edit it; explain it in VO and text.
11. Use hedged claims only ("helps", "the look of", "visibly"). **Never fairness or whitening**, and never lighten skin tone between before and after.
12. Don't change an ad's storyline or characters when fixing a shot; redraw the same composition.
13. **Before spending any credits** (Higgsfield, ElevenLabs…), show wachas the plan and the cost and get a yes.
14. Client messages list **only what was fixed**.

---

## 5. Fixing things: path A, Canva (no code)

`Canva_Kit/` mirrors the delivery folders. One folder per ad: `<Category>/<Product>/<title>_<id>/`:

| File | Use |
|---|---|
| `00_original_generation.mp4` | Raw footage before our edit (reference / extra shots) |
| `01_clean_video_no_text.mp4` | Our edited picture, **no** text, captions, logo or end slate. Use it when you need to change text. |
| `02_video_with_text_and_endslate.mp4` | Picture + our on-screen text + logo + company end slate, **no captions, no audio**. Use it when the text is fine. |
| `03_text_stickers/NN_<start>s_<TEXT>.png` | Every on-screen text card as a **transparent 1080×1920 PNG**. Drop it full-size on the video and it sits exactly where it was. The name tells you the start time. |
| `ON_SCREEN_TEXT.csv` | All text cards: start, end, type, words, position, matching sticker |
| `audio/voice_<Language>.m4a` | The voice (dub / VO) for that language, already on the final timeline |
| `audio/music_<Language>.m4a` | Background music, already ducked under that language's voice |
| `audio/sfx.m4a` | Sound effects (same for all languages) |
| `captions/<Language>.srt` | The captions that are burned into the finals (timed text) |
| `EDIT_NOTES.txt` | Length, where the end slate starts, the English meaning of every line |
| `REFERENCE_final_<Language>.mp4` | One delivered final, to compare against |

Video 02 and every audio file have the **same length and all start at 0:00**, so stacking them rebuilds the final exactly (captions aside).

### Rebuild an ad in Canva

1. Create a design, **Video → Mobile video 1080×1920**.
2. Upload the ad's folder (drag the whole folder in).
3. Timeline, bottom to top:
   - **video:** `02_…mp4` (or `01_…mp4` followed by the end slate `_shared`/`outro_*.mp4` if you're re-doing text);
   - **audio:** `voice_<Lang>.m4a`, `music_<Lang>.m4a`, `sfx.m4a`, all at 100% and all starting at 0:00.
4. **Captions:** the finals have burned-in captions in the language. In Canva, add them from `captions/<Lang>.srt` as text boxes:
   - bottom area, around 90% down;
   - for the before/after split, at the middle divider;
   - font Noto Sans (Bengali/Tamil/…) with English words in Poppins/Lato;
   - highlight colour `#2F4DB0`.

   If the client only asked for a text change, the easier route is to leave captions out of Canva and re-render with the engine (§6).
5. **Export:** MP4, 1080p, then name it exactly like the file it replaces in `Final_Deliverables`.

### Common Canva fixes

| Client says | Do |
|---|---|
| "Change / remove this text" | Use `01_clean…` + stickers, minus the bad sticker. Add a new Canva text in **Lato Black** (headlines) / **Roboto Mono Bold** (labels). |
| "Text covers her face" | Move the sticker or text box |
| "Music too loud / soft" | Change the volume of `music_<Lang>.m4a` |
| "Remove this shot" | Split and delete on video 01/02, and cut the **same** span on all audio tracks. Speech will jump, so prefer covering the shot with another clip (overlay) of the same length. |
| "Use a better shot here" | Overlay a clip from `00_original_generation.mp4` (or another ad's 01) over the bad span. Keep the length the same so the voice stays in sync. |
| "Wrong word in the voice" | Can't be fixed in Canva. Needs a re-voice in the engine (§6). |

---

## 6. Fixing things: path B, the code engine (Mac)

### Setup (once)

1. Clone the repo:
   ```bash
   gh repo clone WachasWps/higgs-purple && cd higgs-purple/dub
   ```
2. Copy in the **media** from wachas' full folder: `work/`, `out/`, `feedback/clips`, `feedback/codex/out`, `feedback/user_*`, `feedback/graphics`, `post/cache`, `deliver/`, `deliver_music/`, `Final_Deliverables/`. Same relative paths.
3. Install ffmpeg-full:
   ```bash
   brew install ffmpeg-full    # scripts call /opt/homebrew/opt/ffmpeg-full/bin/ffmpeg (needs libass + harfbuzz)
   ```
4. Create the Python environment (Python 3.12):
   ```bash
   python3.12 -m venv .venv && .venv/bin/pip install -r requirements.txt
   ```
   Always run scripts with `.venv/bin/python`; the system python lacks librosa and other modules.
5. Apple Silicon is needed for the MLX voice models (dubbing). Rendering text and audio works on any Mac.
6. Mac limits: a 16 GB Mac overheats if you run several ML jobs at once.
   - Run one voice job at a time and at most 3–5 renders.
   - `guard.py` throttles automatically.

### Where things live (per ad id)

| File | What |
|---|---|
| `work/<id>/plan.json` | Cast + every spoken line: `en` meaning + `bn ta te ml or` text + timing |
| `work/<id>/graphics.json` | **All on-screen text** (type, start, end, lines, position), caption position moves, `no_outro`, `logo_until`, `own_music` |
| `work/<id>/captions_<lang>.json` | Caption text per language |
| `work/<id>/source_fixed.mp4` | Our edited picture (input to the render) |
| `feedback/edl_v2/<id>.json` | Shot list that builds `source_fixed.mp4` (keep / replace / wheel / before-after) |
| `out/<id>_<lang>.mp4` | Picture + dubbed voice (no text, no music) |
| `deliver/` → `deliver_music/` → `Final_Deliverables/` | Rendered → + music/SFX → delivered |

### Recipes

**Change or move on-screen text:**
```bash
# edit work/<id>/graphics.json (text, start/end, y position), then:
.venv/bin/python post/render_post.py --preview <id> bn --times 3.0 7.5     # stills in post/preview/ to check
.venv/bin/python post/render_post.py --ids <id> --langs bn ta te ml or --force --jobs 3
.venv/bin/python post/add_audio.py --ids <id> --force
zsh tools/pack.sh                                                           # rebuild Final_Deliverables + loudness
```
For General Ads use `--langs en`.

**Change a spoken line (regional):**
1. Edit the line's `bn/ta/te/ml/or` (and `en`) in `work/<id>/plan.json`. Respect the length budget; check with `validate_plan.py`.
2. Put the line ids in `work/<id>/redub.json`: `{"lines": [3]}`.
3. Run:
   ```bash
   .venv/bin/python validate_plan.py work/<id>/plan.json
   nice -n 10 .venv/bin/python redub.py <id>
   ```
4. Then render, add audio and pack as above.
5. For the new PS UGCs, run `feedback/lipfit/lipfit.py <id>` after the redub so lines land on her mouth.

**Change a General Ad VO line (English):**
1. Edit `feedback/general_ads_vo.py` (start, window end, text).
2. Run:
   ```bash
   .venv/bin/python feedback/general_ads_vo.py check && .venv/bin/python feedback/general_ads_vo.py apply
   .venv/bin/python feedback/ads_english_kokoro.py hf_alpha h <id>
   ```
3. Then render `--langs en`, add audio and pack.

**Erase text baked into the AI footage:**
1. Add `{"type":"blur","start":..,"end":..,"box":{"x0":..,"y0":..,"x1":..,"y1":..}}` to graphics.json. Coordinates are 0–1.
2. Run `.venv/bin/python feedback/detext.py <id> --preview` and check the result.
3. Run it again without `--preview`.
4. It always restarts from `source_fixed.pretext.mp4`, so **list every box each run**.
5. Then `feedback/assemble_fix.py <id> --remux` (puts the new picture into `out/`), render and pack.

**Swap / re-cut a shot (using existing clips only):**
1. Edit `feedback/edl_v2/<id>.json`.
2. Run `.venv/bin/python feedback/assemble_fix.py <id> --remux`.
3. Render and pack.

Never change shot timings in regional ads; the dub is timed to them.

**Rebuild the Canva kit after changes:** `.venv/bin/python post/make_canva_kit.py [<id> ...]`

**Re-render everything:** `zsh tools/final_all.sh` (about 30–40 min) renders all, then add_audio, then pack.

**QC after a render:**
- Check that `Final_Deliverables` has **160** files.
- Look at stills with `--preview`.
- Make sure the end slate is at the end of each video.

### If new generation is ever possible again (credits bought)

- **Images:** Codex CLI with `dub/feedback/codex/CODEX_BRIEF.md`, always attaching `feedback/product_refs/*`. Runner: `feedback/codex/gen.py`.
- **Video:**
  ```bash
  higgsfield generate create wan3_0 --prompt "<motion prompt>" --start-image <keyframe.png> \
      --resolution 480p --duration 5 --aspect_ratio 9:16 --generate_audio false --wait --json
  ```
  This costs 5 credits per clip. Jobs and prompts are in `feedback/wan_jobs.json`. Get wachas' approval for the plan and cost first.
- The #1 thing to generate: **the cream being applied and fully blended, then the glow.**

---

## 7. Prompt to paste into Claude Code

Open Claude Code in `higgs-purple/dub` and paste:

> You are continuing the DERMDOC × Purplle ad project in this repo. First read `../HANDOVER.md` (rules, pipeline, recipes) and `../PROJECT_HISTORY.md` (every client point and its status, all 40 ad ids, every script). Use `.venv/bin/python` for all scripts and ffmpeg at `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`. Respect Mac limits: one ML job at a time, at most 3–5 renders. Hard rules:
> - never change the company end slate, and it must end every video;
> - CTA is "Shop at Purplle.com";
> - PS tube always has its cap and never a nozzle;
> - female voices only;
> - General Ads are English only; regional ads are bn/ta/te/ml/or;
> - "Instant Glow" for PS, "AFTER 2 WEEKS" for KNC only on the before/after split;
> - never say KNC;
> - never edit the colour wheel graphic;
> - no new AI generation or paid credits without showing me the plan and cost first (Higgsfield credits are 0).
>
> Here is the client's new feedback: <paste>. For each point, find the ad id(s) and timestamp, say whether it can be fixed without generation and how (graphics.json / plan.json + redub / detext / edl re-cut / Canva), show me the plan, then do it. Re-render only the affected ids, run add_audio and tools/pack.sh, check Final_Deliverables still has 160 files, rebuild the Canva kit for those ids, and finally write me a short WhatsApp message to the client listing only what was fixed.

---

## 8. Repo map

```
HANDOVER.md, PROJECT_HISTORY.md     this doc + full history
dub/
  prep.py dubplan.py assemble.py redub.py repair.py validate_plan.py guard.py   dubbing engine
  DIRECTOR_BRIEF.md                 how plan.json (cast + 5-language script) is written
  work/<id>/                        per-ad plan.json, graphics.json, captions, transcript, prompt.txt (original gen prompt)
  out/<id>_<lang>/                  per-language line timing (script.json, layout.json)
  post/render_post.py               text, captions, logo, end slate (RENDER_SPEC.md, GRAPHICS_BRIEF.md, CAPTIONS_BRIEF.md)
  post/add_audio.py                 music + SFX
  post/build_folders.py             delivery folder names
  post/make_canva_kit.py            Canva kit builder
  post/assets/                      logos, company end slates (DO NOT CHANGE), reference ad
  post/fonts/                       Lato, Roboto Mono, Poppins, Noto Sans Indic
  feedback/                         client feedback (wa_raw/_chat.txt, CLIENT_REVIEW_OCT11.md, issues_screens.json),
                                    fix tools (assemble_fix, detext, codex/, wan_gen, build_ugc_timeline, lipfit/,
                                    general_ads_vo, ads_english_kokoro, setup_user_general_ads), edl_v2/, product_refs/
  tools/                            final_all.sh, final_fix4.sh, pack.sh, qc_all.py, degrok.py
  tools/session_scripts/            every one-off script used during the project (for reference)
  vm/, kaggle_jobs/                 GPU (Kaggle/Colab) versions of the dubbing engine
```

Questions about why something is the way it is: search PROJECT_HISTORY.md first. The answer is almost always there.
