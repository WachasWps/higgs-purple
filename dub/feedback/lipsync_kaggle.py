"""LatentSync lip-sync of the creator's on-camera shots, per dub language, on a free Kaggle GPU.

usage:
  python3 feedback/lipsync_kaggle.py prep [--test]   cut talking segments + voice-only dub audio -> kaggle_jobs/lipsync_in/,
                                                     create/update the Kaggle dataset wachaspati/dermdoc-lipsync-in
  python3 feedback/lipsync_kaggle.py push            write + push the notebook kernel wachaspati/dermdoc-lipsync
  python3 feedback/lipsync_kaggle.py pull            download lipsync_out.zip -> kaggle_out/lipsync/
  python3 feedback/lipsync_kaggle.py splice          per language: source_fixed + synced segments -> out/<id>_<lang>.mp4
--test: one segment with the creator's ORIGINAL audio (checks install, VRAM and quality before the real run).
"""
import json
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FF = "/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
KG = str(ROOT / ".venv" / "bin" / "kaggle")
IN = ROOT / "kaggle_jobs" / "lipsync_in"
JOB = ROOT / "kaggle_jobs" / "dermdoc-lipsync"
OUTD = ROOT / "kaggle_out" / "lipsync"
LANGS = ["bn", "ta", "te", "ml", "or"]
USER = "wachaspati"
# on-camera talking shots on the re-cut timelines (seconds)
SEGS = {"d6c1e78e": [(0.0, 2.37), (8.17, 12.77), (14.97, 18.37), (23.17, 29.17)],
        "b876bd3c": [(0.0, 3.9), (10.3, 16.17), (20.57, 24.42), (29.22, 32.49)],
        "a135c7dc": [(0.0, 8.6), (8.6, 13.05), (15.55, 17.55), (17.55, 20.3), (25.0, 27.3)],
        "751fe1db": [(0.0, 9.2), (9.2, 12.55), (12.55, 14.3), (16.8, 18.1), (18.1, 21.1), (25.8, 27.9)]}


def ff(*a):
    subprocess.run([FF, "-v", "error", "-y", *map(str, a)], check=True)


def voice_track(vid, lang, dst):
    """voice only: the dubbed line clips at their final-timeline starts (no music bed)"""
    od = ROOT / "out" / f"{vid}_{lang}"
    lay = json.loads((od / "layout.json").read_text())["lines"]
    args, fc = [], []
    for k, l in enumerate(lay):
        args += ["-i", od / f"line_{l['id']}.wav"]
        fc.append(f"[{k}:a]aresample=16000,aformat=channel_layouts=mono,adelay={int(l['start'] * 1000)}:all=1[a{k}]")
    fc.append("".join(f"[a{k}]" for k in range(len(lay))) + f"amix=inputs={len(lay)}:normalize=0")
    ff(*args, "-filter_complex", ";".join(fc), "-ar", "16000", "-ac", "1", dst)


def prep(test, ids=None):
    """per ad: the on-camera talking shots joined into ONE clip; per language: the dubbed voice over the same shots,
    joined the same way -> one LatentSync job per ad x language (model loads once per job, not per shot)"""
    if IN.exists():
        shutil.rmtree(IN)
    IN.mkdir(parents=True)
    jobs = []
    for vid, segs in SEGS.items():
        if ids and vid not in ids:
            continue
        pic = ROOT / "work" / vid / "source.mp4"
        parts = []
        for k, (a, b) in enumerate(segs, 1):
            seg = IN / f"_{vid}_{k}.mp4"
            ff("-ss", f"{a:.3f}", "-i", pic, "-t", f"{b - a:.3f}", "-vf", "fps=25", "-c:v", "libx264", "-crf", "14",
               "-pix_fmt", "yuv420p", "-an", seg)
            parts.append(seg)
        (IN / "_list.txt").write_text("".join(f"file '{x}'\n" for x in parts))
        v = IN / f"{vid}.mp4"
        ff("-f", "concat", "-safe", "0", "-i", IN / "_list.txt", "-c", "copy", v)
        for lang in LANGS:
            full = IN / f"_{vid}_{lang}_voice.wav"
            voice_track(vid, lang, full)
            fc = "".join(f"[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[a{k}];" for k, (a, b) in enumerate(segs))
            fc += "".join(f"[a{k}]" for k in range(len(segs))) + f"concat=n={len(segs)}:v=0:a=1"
            w = IN / f"{vid}_{lang}.wav"
            ff("-i", full, "-af", "apad", "-t", "60", IN / "_pad.wav")
            ff("-i", IN / "_pad.wav", "-filter_complex", fc, "-ar", "16000", "-ac", "1", w)
            jobs.append({"video": v.name, "audio": w.name, "out": f"{vid}_{lang}.mp4"})
    for f in IN.glob("_*"):
        f.unlink()
    (IN / "jobs.json").write_text(json.dumps(jobs, indent=1))
    (IN / "dataset-metadata.json").write_text(json.dumps(
        {"title": "dermdoc-lipsync-in", "id": f"{USER}/dermdoc-lipsync-in", "licenses": [{"name": "CC0-1.0"}]}))
    r = subprocess.run([KG, "datasets", "version", "-p", str(IN), "-m", "jobs", "-r", "zip"], capture_output=True, text=True)
    print(r.stdout[-300:], r.stderr[-300:])
    print(f"{len(jobs)} jobs")


NB = r'''
import json, os, subprocess, sys, time, shutil, zipfile
from pathlib import Path
def run(cmd, cwd=None):
    print("$", cmd, flush=True); t = time.time()
    p = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in p.stdout: print(line, end="", flush=True)
    rc = p.wait(); print(f"[exit {rc} after {time.time()-t:.0f}s]", flush=True); return rc
print(subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout)
IN = Path("/kaggle/input/dermdoc-lipsync-in")
if not (IN / "jobs.json").exists():
    IN = next(Path("/kaggle/input").rglob("jobs.json")).parent
jobs = json.loads((IN / "jobs.json").read_text())
W = Path("/kaggle/working"); OUT = Path("/tmp/ls_out"); OUT.mkdir(exist_ok=True)
run("git clone -q https://github.com/bytedance/LatentSync.git /tmp/LatentSync")
for pk in ["diffusers==0.32.2", "transformers==4.48.0", "huggingface-hub==0.30.2", "accelerate==1.2.1", "peft", "einops", "omegaconf", "opencv-python", "mediapipe",
           "python_speech_features", "librosa", "scenedetect", "ffmpeg-python", "imageio", "imageio-ffmpeg", "lpips",
           "face-alignment", "kornia", "insightface", "onnxruntime-gpu", "DeepCache"]:
    run(f"pip install -q {pk}")
if run("pip install -q eva-decord") != 0:
    run("pip install -q decord")
run("python -c 'import decord, mediapipe, diffusers, insightface; print(\"imports ok\")'")
from huggingface_hub import snapshot_download
def fetch(repo):
    shutil.rmtree("/tmp/LatentSync/checkpoints", ignore_errors=True)
    snapshot_download(repo, local_dir="/tmp/LatentSync/checkpoints")
    print(sorted(str(x) for x in Path("/tmp/LatentSync/checkpoints").rglob("*") if x.is_file()), flush=True)
fetch("ByteDance/LatentSync-1.5")
cfg = "configs/unet/stage2.yaml"
import threading, queue
q = queue.Queue()
for j in jobs: q.put(j)
res = {}
def worker(gpu):
    while True:
        try: j = q.get_nowait()
        except queue.Empty: return
        if (OUT / j["out"]).exists(): res[j["out"]] = 0; continue
        rc = run(f"CUDA_VISIBLE_DEVICES={gpu} python -m scripts.inference --unet_config_path {cfg} "
                 f"--inference_ckpt_path checkpoints/latentsync_unet.pt --inference_steps 20 --guidance_scale 1.5 "
                 f"--enable_deepcache --video_path {IN/j['video']} --audio_path {IN/j['audio']} "
                 f"--video_out_path {OUT/j['out']}", cwd="/tmp/LatentSync")
        res[j["out"]] = rc
        print(f"== gpu{gpu} {j['out']}: {'OK' if rc == 0 else 'FAILED'} ({len(res)}/{len(jobs)})", flush=True)
ts = [threading.Thread(target=worker, args=(g,)) for g in (0, 1)]
[t.start() for t in ts]; [t.join() for t in ts]
ok = sum(1 for v in res.values() if v == 0)
with zipfile.ZipFile(W / "lipsync_out.zip", "w") as zf:
    for f in OUT.glob("*.mp4"): zf.write(f, f.name)
    zf.writestr("model.txt", cfg)
print(f"DONE {ok}/{len(jobs)}")
'''


def push():
    JOB.mkdir(parents=True, exist_ok=True)
    nb = {"cells": [{"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": NB.strip()}],
          "metadata": {"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}},
          "nbformat": 4, "nbformat_minor": 4}
    (JOB / "lipsync.ipynb").write_text(json.dumps(nb))
    (JOB / "kernel-metadata.json").write_text(json.dumps(
        {"id": f"{USER}/dermdoc-lipsync", "title": "dermdoc-lipsync", "code_file": "lipsync.ipynb", "language": "python",
         "kernel_type": "notebook", "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": True,
         "machine_shape": "NvidiaTeslaT4", "dataset_sources": [f"{USER}/dermdoc-lipsync-in"], "competition_sources": [],
         "kernel_sources": []}, indent=1))
    r = subprocess.run([KG, "kernels", "push", "-p", str(JOB)], capture_output=True, text=True)
    print(r.stdout, r.stderr)


def pull():
    if OUTD.exists():
        shutil.rmtree(OUTD)
    OUTD.mkdir(parents=True)
    subprocess.run([KG, "kernels", "output", f"{USER}/dermdoc-lipsync", "-p", str(OUTD)], check=True)
    z = OUTD / "lipsync_out.zip"
    if z.exists():
        zipfile.ZipFile(z).extractall(OUTD)
    print(sorted(p.name for p in OUTD.glob("*.mp4")))


def splice(ids=None):
    """per language: cut the joined lip-synced clip back into its shots (25 -> 30 fps), overlay each on the re-cut
    picture at its time, keep the dub's mixed audio -> out/<id>_<lang>.mp4 (render_post reads these)"""
    for vid, segs in SEGS.items():
        if ids and vid not in ids:
            continue
        pic = ROOT / "work" / vid / "source_fixed.mp4"
        for lang in LANGS:
            dub, syn = ROOT / "out" / f"{vid}_{lang}.mp4", OUTD / f"{vid}_{lang}.mp4"
            if not dub.exists() or not syn.exists():
                print(f"{vid}_{lang}: missing ({dub.exists()=}, {syn.exists()=})")
                continue
            args, fc, last, off = ["-i", pic, "-i", syn], [f"[1:v]fps=30,scale=1080:1920,setsar=1,split={len(segs)}" +
                                                             "".join(f"[p{k}]" for k in range(len(segs)))], "[0:v]", 0.0
            for k, (a, b) in enumerate(segs):
                fc.append(f"[p{k}]trim={off:.3f}:{off + b - a:.3f},setpts=PTS-STARTPTS+{a:.3f}/TB[s{k}]")
                fc.append(f"{last}[s{k}]overlay=eof_action=pass:enable='between(t,{a:.3f},{b - 0.001:.3f})'[v{k}]")
                last, off = f"[v{k}]", off + b - a
            tmp = dub.with_suffix(".ls.mp4")
            ff(*args, "-i", dub, "-filter_complex", ";".join(fc), "-map", last, "-map", "2:a", "-c:v", "libx264",
               "-crf", "16", "-pix_fmt", "yuv420p", "-c:a", "copy", "-shortest", tmp)
            tmp.replace(dub)
            print(f"{vid}_{lang}: lip-synced {len(segs)} shots")


if __name__ == "__main__":
    cmd = sys.argv[1]
    ids = [a for a in sys.argv[2:] if not a.startswith("--")] or None
    {"prep": lambda: prep("--test" in sys.argv, ids), "push": push, "pull": pull, "splice": lambda: splice(ids)}[cmd]()
