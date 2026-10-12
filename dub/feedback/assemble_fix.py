"""Rebuild a video's picture from its EDL: keep good source shots, swap bad ones for library clips / graphics.

usage: assemble_fix.py <id> [<id> ...] [--remux]   (--remux: put the fixed picture into out/<id>_<lang>.mp4, keeping audio)
Inputs : work/<id>/source.mp4, feedback/edl/<id>.json, feedback/clips/<CLIP>.mp4 (Wan) or <CLIP>_kb.mp4 (Ken Burns
         fallback from the keyframe), feedback/graphics/cw_right.mov (colour wheel overlay).
Output : work/<id>/source_fixed.mp4 — same duration/fps as source, 1080x1920, no audio.
Timeline never changes (the dub is timed to it): every shot keeps its exact start/end.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
FP = "/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"
CLIPS = ROOT / "feedback" / "clips"
KEYS = ROOT / "feedback" / "codex" / "out"
GFX = ROOT / "feedback" / "graphics"
W, H = 1080, 1920   # full res so the colour-wheel graphic stays crisp; 480p clips are upscaled once here
FILL = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},setsar=1"
BA = {"ps": ("PS07_before_dull", "ADS_PS_AFTER"), "knc": ("KN08_before_day", "ADS_KNC_AFTER")}   # AFTERs edited from the BEFOREs: same pose/expression
CW_BASE = {"ps": "PSA2_avatar_point", "knc": "PSA2_avatar_point"}
HERO = {"ps": "PS01_hero_vanity", "knc": "KN01_hero_night"}
FALLBACK = {"CUSTOM_PS_INGR_MACRO": "PS10_texture_macro", "CUSTOM_KNC_INGR_MACRO": "KNA2_avatar_ingredients"}


def probe(p):
    o = json.loads(subprocess.run([FP, "-v", "error", "-print_format", "json", "-show_streams", "-show_format", str(p)],
                                  capture_output=True, text=True).stdout)
    v = next(s for s in o["streams"] if s["codec_type"] == "video")
    n, d = v["r_frame_rate"].split("/")
    return float(o["format"]["duration"]), float(n) / float(d)


def ken_burns(clip_id, secs=5.0, fps=30):
    """Free fallback: slow push-in on the Codex keyframe (used when no Wan clip exists yet)."""
    out = CLIPS / f"{clip_id}_kb.mp4"
    key = KEYS / f"{clip_id}.png"
    if not key.exists():
        return out if out.exists() else None
    if out.exists() and out.stat().st_mtime >= key.stat().st_mtime:   # rebuild when the keyframe was regenerated
        return out
    CLIPS.mkdir(parents=True, exist_ok=True)
    n = int(secs * fps)
    vf = (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=increase,crop={W * 2}:{H * 2},"
          f"zoompan=z='1+0.06*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={fps}")
    subprocess.run([FF, "-v", "error", "-y", "-loop", "1", "-i", str(key), "-vf", vf, "-frames:v", str(n),
                    "-c:v", "libx264", "-crf", "16", "-pix_fmt", "yuv420p", str(out)], check=True)
    return out


def clip_path(clip_id):
    if clip_id.startswith("CUSTOM:"):
        clip_id = clip_id.split(":", 1)[1]
    p = CLIPS / f"{clip_id}.mp4"
    if p.exists():
        return p
    kb = ken_burns(clip_id)
    if kb is None and clip_id in FALLBACK:   # custom clip not generated yet -> nearest library clip
        return clip_path(FALLBACK[clip_id])
    return kb


def fit(src, need, off=0.0):
    """Filter + input options so `src` (from `off`) covers exactly `need` seconds (slow down up to 1.6x, else loop)."""
    dur = probe(src)[0] - off
    if dur >= need:
        return [], f"trim=0:{need:.3f},setpts=PTS-STARTPTS"
    f = need / dur
    if f <= 1.6:
        return [], f"setpts={f:.4f}*(PTS-STARTPTS),trim=0:{need:.3f}"
    return ["-stream_loop", "-1"], f"trim=0:{need:.3f},setpts=PTS-STARTPTS"


# client: "what is the difference?" -> the BEFORE side has to read clearly dull/yellow-grey (the AFTER is never lightened)
DULL = "eq=saturation=0.78:contrast=0.94:gamma=0.95,colorbalance=bm=-0.05:bh=-0.03"
# sheen is blended on luma only — blending chroma too turned the skin orange/pink (and screen mode lightened it)
GLOW = ("bilateral=sigmaS=10:sigmaR=0.1,split[g0][g1];[g1]gblur=sigma=24[gb];[g0][gb]blend=c0_mode=softlight:"
        "c0_opacity=0.5:c1_mode=normal:c1_opacity=1:c2_mode=normal:c2_opacity=1,eq=contrast=1.02:saturation=1.02")
# KNC "after 2 weeks": a little more smoothing so flat dark spots fade (stronger looked blurred/fake)
GLOW_KNC = GLOW.replace("bilateral=sigmaS=10:sigmaR=0.1", "bilateral=sigmaS=14:sigmaR=0.13")


def split_grade(before="left", glow=GLOW):
    """Creator's own side-by-side before/after: dull the BEFORE half, give the AFTER half an instant-glow look
    (smoother skin + soft sheen, same skin tone — luminosity, never lightening)."""
    l, r = (DULL, glow) if before == "left" else (glow, DULL)
    return (f"{FILL},split[a][b];[a]crop={W // 2}:{H}:0:0,{l}[l];[b]crop={W // 2}:{H}:{W // 2}:0,{r}[r];"
            f"[l][r]hstack=2,setpts=PTS-STARTPTS")


def zoom_vf(z):
    """'zoom': [factor, cx, cy] — punch in on a kept shot (e.g. to lose a half-visible box at the frame edge)."""
    f, cx, cy = (float(v) for v in z)
    cw, ch = int(W / f) // 2 * 2, int(H / f) // 2 * 2
    x, y = min(max(0, int(cx * W - cw / 2)), W - cw), min(max(0, int(cy * H - ch / 2)), H - ch)
    return f"crop={cw}:{ch}:{x}:{y},scale={W}:{H}:flags=lanczos,setsar=1"


def seg(job, i, s, product, src, fps, tmp):
    a, b = float(s["start"]), float(s["end"])
    need = b - a
    out = tmp / f"s{i:02d}.mp4"
    act, rep = s.get("action", "keep"), s.get("replace_with")
    enc = ["-threads", "4", "-r", f"{fps:.3f}", "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-an", str(out)]
    if act == "keep" or (act != "keep" and not rep and act != "remove"):
        sa, sb = s.get("src") or (a, b)   # "src": play another stretch of the source (slowed to fit) — e.g. hold a
        k = need / (float(sb) - float(sa))   # creator shot over a removed packshot
        vf = f"{FILL},setpts={k:.4f}*(PTS-STARTPTS),trim=0:{need:.3f},setpts=PTS-STARTPTS"
        if s.get("zoom"):
            vf += "," + zoom_vf(s["zoom"])
        glow = GLOW_KNC if product == "knc" else GLOW
        if s.get("grade") == "glow":   # whole shot gets the after look (e.g. an 'after 2 weeks' talking shot)
            vf += f",{glow}"
        if s.get("split_grade"):
            vf = f"setpts={k:.4f}*(PTS-STARTPTS),trim=0:{need:.3f}," + split_grade(s["split_grade"], glow)
        subprocess.run([FF, "-v", "error", "-y", "-ss", f"{float(sa):.3f}", "-t", f"{float(sb) - float(sa):.3f}",
                        "-i", str(src), "-filter_complex", vf] + enc, check=True)
        return out
    if act == "remove" and not rep:
        rep = HERO[product]
    if rep == "GRAPHIC_BA_SPLIT" and s.get("ba_src") is not None:
        # the creator's OWN footage from ba_src: BEFORE (dulled) on top, the same moment with the instant-glow look
        # below — keeps the UGC creator instead of a stock model; labels/caption move come from graphics.json
        t0 = float(s["ba_src"])
        y0 = int(H * float(s.get("ba_face_y", 0.10)))
        z = float(s.get("ba_zoom", 1.0))   # punch in when the source is a medium shot (face too small in the band)
        bw, bh = int(W / z) // 2 * 2, int(H / 2 / z) // 2 * 2
        bx = min(max(0, int(float(s.get("ba_face_x", 0.5)) * W - bw / 2)), W - bw)
        band = f"crop={bw}:{bh}:{bx}:{y0},scale={W}:{H // 2}:flags=lanczos"
        fc = (f"[0:v]{FILL},setpts=PTS-STARTPTS,trim=0:{need:.3f},split[a][b];[a]{band},{DULL}[t];[b]{band},{GLOW_KNC if product == 'knc' else GLOW}[u];"
              f"[t][u]vstack=2,drawbox=x=0:y={H // 2 - 3}:w={W}:h=6:color=white@0.95:t=fill,setsar=1[v]")
        o = ["-stream_loop", "-1"] if probe(src)[0] - t0 < need else []
        subprocess.run([FF, "-v", "error", "-y"] + o + ["-ss", f"{t0:.3f}", "-i", str(src), "-filter_complex", fc,
                       "-map", "[v]"] + enc, check=True)
        return out
    if rep == "GRAPHIC_BA_SPLIT":
        # "ba_pair": [before_id, after_id] = Codex stills of the SAME creator (slow push-in on each keyframe)
        bp, ap_ = ((clip_path(s["ba_pair"][0]), clip_path(s["ba_pair"][1])) if s.get("ba_pair")   # Wan clip if any, else push-in
                   else (clip_path(BA[product][0]), clip_path(BA[product][1])))
        o1, f1 = fit(bp, need)
        o2, f2 = fit(ap_, need)
        # Client: "half and half … so the face close-up is visible and not cropped" -> BEFORE on top, AFTER below,
        # each a full face (keyframes put the face in the upper-middle; crop a 1080x960 band around it).
        y0 = int(H * float(s.get("ba_face_y", 0.10)))
        half = f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},crop={W}:{H // 2}:0:{y0}"
        fc = (f"[0:v]{f1},{half}[t];[1:v]{f2},{half}[b];[t][b]vstack=2,"
              f"drawbox=x=0:y={H // 2 - 3}:w={W}:h=6:color=white@0.95:t=fill,setsar=1[v]")
        subprocess.run([FF, "-v", "error", "-y"] + o1 + ["-i", str(bp)] + o2 + ["-i", str(ap_), "-filter_complex", fc,
                       "-map", "[v]"] + enc, check=True)
        return out
    if rep == "GRAPHIC_COLOUR_WHEEL":
        # full-screen reference-style card (Sunscream-1 T): animation completes by ~1.8 s, then holds
        cw = GFX / "cw_v2.mp4"
        k = min(1.0, need / 2.0)   # squeeze only if the shot is shorter than 2 s
        vf = (f"setpts={k:.4f}*(PTS-STARTPTS),tpad=stop_mode=clone:stop_duration={need:.3f},"
              f"trim=0:{need:.3f},setpts=PTS-STARTPTS,{FILL}")
        subprocess.run([FF, "-v", "error", "-y", "-i", str(cw), "-vf", vf] + enc, check=True)
        return out
    if rep.startswith("CUSTOM"):
        cid = (rep.split(":", 1)[1] if ":" in rep else rep if rep.startswith("CUSTOM_")
               else ((s.get("custom") or {}).get("shared_id") or f"C_{job}_{s['n']}"))
        p = clip_path(cid)
        if p is None:   # custom clip not generated yet -> keep source for now
            print(f"  {job} S{s['n']}: custom {cid} missing, keeping source")
            return seg(job, i, {**s, "action": "keep"}, product, src, fps, tmp)
    else:
        p = clip_path(rep)
        if p is None:
            print(f"  {job} S{s['n']}: clip {rep} missing, keeping source")
            return seg(job, i, {**s, "action": "keep"}, product, src, fps, tmp)
    off = float(s.get("clip_offset", 0))
    o, f = fit(p, need, off)
    pre = ["-ss", f"{off:.3f}"] if off else []
    subprocess.run([FF, "-v", "error", "-y"] + o + pre + ["-i", str(p), "-vf", f"{f},{FILL}"] + enc, check=True)
    return out


def job_cat(vid):
    p = ROOT / "work" / vid / "plan.json"
    if p.exists():
        return json.loads(p.read_text()).get("style", "")
    return json.loads((ROOT / "work" / vid / "meta.json").read_text()).get("kind", "")


def plan_shots(vid):
    """the final contiguous shot list (start/end on the output timeline) + output duration, fps and source path"""
    v2 = ROOT / "feedback" / "edl_v2" / f"{vid}.json"   # v2 = keep the original creators/story, fix only flagged shots
    edl = json.loads((v2 if v2.exists() else ROOT / "feedback" / "edl" / f"{vid}.json").read_text())
    product = edl.get("product", "ps")
    src = ROOT / "work" / vid / "source.mp4"
    dur, fps = probe(src)
    shots = []
    src_shots = edl["shots"]
    if edl.get("use_rebuild"):   # general ads: brand-new shot list, all library clips / graphics, new length
        rb = edl["rebuild"]
        dur, fps = float(rb["target_duration_s"]), 30.0
        src_shots = [{"n": r["n"], "start": r["start"], "end": r["end"], "action": "replace", "replace_with": r["source"],
                      **({"clip_offset": r["clip_offset"]} if "clip_offset" in r else {}),
                      **{k: r[k] for k in ("ba_pair", "ba_face_y", "split_grade") if k in r}} for r in rb["shots"]]
    for s_ in sorted(src_shots, key=lambda s: float(s["start"])):   # expand multi-clip shots (split / segments)
        parts = s_.get("segments") or [{"start": q["start"], "end": q["end"], "replace_with": q["clip"]}
                                       for q in (s_.get("split") or [])]
        if parts and s_.get("action") != "keep":
            for k, q in enumerate(sorted(parts, key=lambda q: float(q["start"]))):
                shots.append({**s_, "start": q["start"], "end": q["end"], "replace_with": q["replace_with"],
                              "segments": None, "split": None, "then": None, "action": "replace", "n": f"{s_['n']}{'abcd'[k]}"})
        else:
            shots.append(s_)
    shots[0]["start"] = 0.0
    shots[-1]["end"] = dur if edl.get("use_rebuild") else max(float(shots[-1]["end"]), dur)
    for j in range(1, len(shots)):   # make the shot list contiguous
        shots[j]["start"] = shots[j - 1]["end"]
    # a before/after split must hold long enough to read (>= 2 s): borrow time from a replaced neighbour
    for j, s_ in enumerate(shots):
        short = 2.0 - (float(s_["end"]) - float(s_["start"]))
        if s_.get("replace_with") != "GRAPHIC_BA_SPLIT" or short <= 0:
            continue
        for nb, edge in ((j - 1, "start"), (j + 1, "end")):
            if 0 <= nb < len(shots) and shots[nb].get("action") != "keep":
                give = min(short, float(shots[nb]["end"]) - float(shots[nb]["start"]) - 1.0)
                if give > 0:
                    if edge == "start":
                        s_["start"] = shots[nb]["end"] = round(float(s_["start"]) - give, 3)
                    else:
                        s_["end"] = shots[nb]["start"] = round(float(s_["end"]) + give, 3)
                    short -= give
            if short <= 0:
                break
    # "then": a second library clip for the back half of a shot (e.g. dots -> blend -> instant glow)
    split = []
    for s_ in shots:
        nxt = s_.get("then")
        if nxt and s_.get("action") != "keep" and float(s_["end"]) - float(s_["start"]) >= 2.0:
            mid = round((float(s_["start"]) + float(s_["end"])) / 2, 3)
            split += [{**s_, "end": mid, "then": None}, {**s_, "start": mid, "replace_with": nxt, "then": None,
                                               # play the END of the second clip (the payoff, e.g. the glow)
                                               "clip_offset": max(0.0, 5.0 - (float(s_["end"]) - mid))}]
        else:
            split.append(s_)
    shots = split
    # the same library clip on consecutive shots continues where it left off instead of restarting
    for prev, cur in zip(shots, shots[1:]):
        rep = cur.get("replace_with")
        if cur.get("action") != "keep" and rep and rep == prev.get("replace_with") and not rep.startswith(("GRAPHIC", "CUSTOM")):
            p = clip_path(rep)
            nxt = float(prev.get("clip_offset", 0)) + float(prev["end"]) - float(prev["start"])
            if p and "clip_offset" not in cur and probe(p)[0] - nxt >= 0.8:
                cur["clip_offset"] = nxt
    return shots, product, src, dur, fps


def build(vid):
    shots, product, src, dur, fps = plan_shots(vid)
    tmp = ROOT / "work" / vid / "fix_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir()
    parts = [seg(vid, i, s, product, src, fps, tmp) for i, s in enumerate(shots)]
    lst = tmp / "list.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    out = ROOT / "work" / vid / "source_fixed.mp4"
    part = out.with_name("source_fixed.part.mp4")   # atomic: a render must never read a half-written picture
    # re-encode the join: segments from different sources can carry different stream parameters, and a mid-stream
    # change made the caption renderer lose the picture after the switch (blank frames to the end)
    subprocess.run([FF, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-r", f"{fps:.3f}",
                    "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p", "-colorspace", "bt709",
                    "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv", "-an", str(part)], check=True)
    part.replace(out)
    shutil.rmtree(tmp)
    nd, _ = probe(out)
    print(f"{vid}: source_fixed.mp4 {nd:.2f}s (source {dur:.2f}s), "
          f"{sum(1 for s in shots if s.get('action') != 'keep')} shots replaced")
    return out


def remux(vid):
    fixed = ROOT / "work" / vid / "source_fixed.mp4"
    bak = ROOT / "out_prefix"
    for f in sorted((ROOT / "out").glob(f"{vid}_*.mp4")):
        bak.mkdir(exist_ok=True)
        if not (bak / f.name).exists():
            shutil.copy2(f, bak / f.name)
        tmp = f.with_suffix(".tmp.mp4")
        # audio from the CURRENT file (it may have been re-dubbed since the backup was taken)
        subprocess.run([FF, "-v", "error", "-y", "-i", str(fixed), "-i", str(f), "-map", "0:v", "-map", "1:a",
                        "-c", "copy", "-shortest", str(tmp)], check=True)
        tmp.replace(f)
        print(f"  remuxed {f.name}")


if __name__ == "__main__":
    ids = [a for a in sys.argv[1:] if not a.startswith("--")]
    for v in ids:
        build(v)
        if "--remux" in sys.argv:
            remux(v)
