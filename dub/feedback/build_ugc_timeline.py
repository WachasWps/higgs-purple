"""Re-cut a user-supplied UGC clip into a longer ad: the creator's own shots interleaved with product B-roll from the
user's General Ads (each >= 2 s), the colour-wheel graphic and a Codex before/after split.

usage: python3 feedback/build_ugc_timeline.py <id>
Writes feedback/clips/USR_<id>_<k>.mp4 (cut segments), feedback/edl_v2/<id>.json (use_rebuild), builds the picture
with assemble_fix, then muxes the creator's own audio under her shots (silence elsewhere) into work/<id>/source.mp4
(the original is kept as source.orig.mp4) — re-run prep.py afterwards so the stems match the new timeline.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "feedback"))
import assemble_fix as A  # noqa: E402

FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
PSAD = ROOT / "feedback" / "user_ps_ads"
# product B-roll from the user's Sunscreen General Ads (file, t0, t1)
BROLL = {   # (file, t0, t1, on-screen length): clean ranges only (no dissolves / white wipes); slowed when shorter
    "tube_purple_tint": ("ps1.mp4", 3.0, 5.7, 2.8),      # tube on purple cream, "Purple Tint = Instant Glow + Even Tone"
    "tube_repairs": ("ps4.mp4", 2.5, 5.4, 3.4),          # tube on purple cream, "Niacinamide = Repairs + Protects"
    "shield_rays": ("ps1.mp4", 6.0, 8.2, 2.2),           # purple shield deflects sun rays over skin cells
    "rays_barrier": ("ps4.mp4", 5.65, 7.1, 2.2),         # sun rays hit the skin barrier, "4% NIACINAMIDE"
    "tube_macro": ("ps5.mp4", 25.0, 27.3, 2.3),          # rotating tube macro (4% niacinamide, SPF 50 PA+++)
    "endcard_ps": ("ps1.mp4", 20.45, 25.33, 4.88),       # the user's Purplle end card
}
U3 = ROOT / "feedback" / "user_ugc3"
U4 = ROOT / "feedback" / "user_ugc4"
U5 = ROOT / "feedback" / "user_ugc5"
# shot lists: ("me", src_t0, src_t1[, source file]) = creator's own footage | ("b", broll key) | ("WHEEL", secs) | ("BA", secs)
PLANS = {
    "d6c1e78e": [("me", 0.0, 2.37), ("b", "tube_purple_tint"), ("WHEEL", 3.0), ("me", 6.1, 10.7),
                 ("b", "shield_rays"), ("me", 10.8, 14.2), ("b", "tube_macro"), ("BA", 2.5), ("me", 14.5, 17.1),
                 ("me", 19.4, 22.8), ("me", 22.95, 28.07)],
    "b876bd3c": [("me", 0.0, 3.9), ("b", "tube_repairs"), ("WHEEL", 3.0), ("me", 5.13, 11.0), ("b", "rays_barrier"),
                 ("b", "shield_rays"), ("me", 11.05, 14.9), ("BA", 2.5), ("b", "tube_macro"), ("me", 17.23, 20.5),
                 ("me", 20.53, 25.51)],
    # UGC 3 (32 s): her three clips back to back; wheel / shield / B-A are CUTAWAYS over her continuing voice
    # (last tuple item on a cutaway = (audio file, t0): her speech keeps running underneath)
    "a135c7dc": [("me", 0.0, 8.6, U3 / "c1_talking_clean.mp4"), ("me", 0.0, 4.45, U3 / "c3_applying_clean.mp4"),
                 ("WHEEL", 2.5, (U3 / "c3_applying_clean.mp4", 4.45)), ("me", 6.95, 8.95, U3 / "c3_applying_clean.mp4"),
                 ("me", 0.0, 2.75, U3 / "c2_showing_clean.mp4"), ("b", "shield_rays", (U3 / "c2_showing_clean.mp4", 2.75)),
                 ("BA", 2.5, (U3 / "c2_showing_clean.mp4", 4.95)), ("me", 7.45, 9.75, U3 / "c2_showing_clean.mp4"),
                 ("b", "endcard_ps")],
    # UGC 4 (33 s): same structure, second model
    "751fe1db": [("me", 0.0, 9.2, U4 / "d1_talking_clean.mp4"), ("me", 0.0, 3.35, U4 / "d2_applying_clean.mp4"),
                 ("me", 3.35, 5.1, U4 / "d2_applying_clean.mp4"), ("WHEEL", 2.5, (U4 / "d2_applying_clean.mp4", 5.1)),
                 ("me", 7.6, 8.9, U4 / "d2_applying_clean.mp4"), ("me", 0.0, 3.0, U4 / "d3_smiling_clean.mp4"),
                 ("b", "rays_barrier", (U4 / "d3_smiling_clean.mp4", 3.0)), ("BA", 2.5, (U4 / "d3_smiling_clean.mp4", 5.2)),
                 ("me", 7.7, 9.8, U4 / "d3_smiling_clean.mp4"), ("b", "endcard_ps")],
    # UGC 5 (34 s): e1 dull/struggle, e2 found it, e3 purple tint + blend (squeeze with the wrong tube skipped: starts 1.7),
    # e4 glow + claims + Purplle.com; wheel / shield / B-A as cutaways over her voice
    "010ea465": [("me", 1.9, 8.95, U5 / "e1_expressing_clean.mp4"), ("me", 1.9, 7.6, U5 / "e2_holding_clean.mp4"),
                 ("me", 1.7, 3.6, U5 / "e3_applying_clean.mp4"), ("WHEEL", 2.5, (U5 / "e3_applying_clean.mp4", 3.6)),
                 ("me", 6.1, 8.95, U5 / "e3_applying_clean.mp4"), ("me", 0.0, 1.9, U5 / "e4_smiling_clean.mp4"),
                 ("b", "shield_rays", (U5 / "e4_smiling_clean.mp4", 1.9)), ("BA", 2.5, (U5 / "e4_smiling_clean.mp4", 4.1)),
                 ("me", 6.6, 9.1, U5 / "e4_smiling_clean.mp4"), ("b", "endcard_ps")],
}


def run(cmd):
    subprocess.run([FF, "-v", "error", "-y", *cmd], check=True)


def cut(src, t0, t1, dst, out_len=None):
    k = (out_len or t1 - t0) / (t1 - t0)
    run(["-ss", f"{t0:.3f}", "-i", str(src), "-t", f"{t1 - t0:.3f}", "-vf",
         f"setpts={k:.4f}*(PTS-STARTPTS),scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,fps=30",
         "-an",
         "-c:v", "libx264", "-crf", "15", "-pix_fmt", "yuv420p", str(dst)])


def main(vid):
    wd = ROOT / "work" / vid
    orig = wd / "source.orig.mp4"
    if not orig.exists():
        shutil.copy(wd / "source.mp4", orig)
    src = wd / "source.clean.mp4" if (wd / "source.clean.mp4").exists() else orig   # watermark-free picture
    t, shots, audio = 0.0, [], []
    for k, s in enumerate(PLANS[vid], 1):
        if s[0] == "me":
            cid, d = f"USR_{vid}_{k:02d}", s[2] - s[1]
            f = s[3] if len(s) > 3 else src
            cut(f, s[1], s[2], A.CLIPS / f"{cid}.mp4")
            shots.append({"source": cid})
            audio.append(("me", s[1], d, f if len(s) > 3 else orig))
        elif s[0] == "b":
            f, a, b, d = BROLL[s[1]]
            cid = f"USR_PSAD_{s[1]}"
            cut(PSAD / f, a, b, A.CLIPS / f"{cid}.mp4", d)
            shots.append({"source": cid})
            audio.append(("me", s[2][1], d, s[2][0]) if len(s) > 2 else ("sil", 0, d, None))
        else:
            d = s[1]
            shots.append({"source": "GRAPHIC_COLOUR_WHEEL"} if s[0] == "WHEEL" else
                         {"source": "GRAPHIC_BA_SPLIT", "ba_pair": [f"BA2_{vid}_BEFORE", f"BA2_{vid}_AFTER"]})
            audio.append(("me", s[2][1], d, s[2][0]) if len(s) > 2 else ("sil", 0, d, None))
        shots[-1].update({"n": k, "start": round(t, 3), "end": round(t + d, 3)})
        t += d
    edl = {"video_id": vid, "product": "ps", "category": "ugc", "use_rebuild": True, "shots": [],
           "rebuild": {"target_duration_s": round(t, 3), "shots": shots}}
    (ROOT / "feedback" / "edl_v2" / f"{vid}.json").write_text(json.dumps(edl, indent=1))
    A.build(vid)
    # creator audio under her own shots, silence under B-roll / graphics
    parts, fc = [], []
    for i, (kind, a, d, af) in enumerate(audio):
        if kind == "me":
            parts += ["-ss", f"{a:.3f}", "-t", f"{d:.3f}", "-i", str(af)]
        else:
            parts += ["-f", "lavfi", "-t", f"{d:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
        fc.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=duration={d:.3f}[a{i}]")
    fc.append("".join(f"[a{i}]" for i in range(len(audio))) + f"concat=n={len(audio)}:v=0:a=1[a]")
    wav = wd / "timeline_audio.wav"
    run([*parts, "-filter_complex", ";".join(fc), "-map", "[a]", str(wav)])
    run(["-i", str(wd / "source_fixed.mp4"), "-i", str(wav), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
         "-c:a", "aac", "-b:a", "192k", "-shortest", str(wd / "source.mp4")])
    wav.unlink()
    print(f"{vid}: new timeline {t:.2f}s, {len(shots)} shots")
    for s in shots:
        print(f"  {s['n']:2d} {s['start']:6.2f}-{s['end']:6.2f} {s['source']}")


if __name__ == "__main__":
    for v in sys.argv[1:]:
        main(v)
