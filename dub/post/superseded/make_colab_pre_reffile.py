"""Build vm/colab_dub.ipynb: a self-contained Google Colab notebook (free T4: cc 7.5, fp16, no bf16, no SSH) that dubs an
explicit list of videos end to end. Nothing to upload: the engine code, each video's plan.json + meta.json and the
source-video URLs are embedded (gzip + base64), and the notebook downloads the sources itself.

Notebook cells: 1 GPU check | 2 pip install (Colab's torch kept, via a constraints file) | 3 write code + plans |
4 download sources + Demucs stems on the GPU | 5 dub (transformers backend, fp16 + fp32 fallback) + repair |
6 zip out/<id>_<lang>.mp4 + qa.json and download | 7 optional copy to Google Drive (off unless COPY_TO_DRIVE = True).

Usage: python3 vm/make_colab.py id1,id2,... [--gens gens_oct8.json,gens_batch.json] [--out vm/colab_dub.ipynb]
"""
import base64
import gzip
import json
import sys
from pathlib import Path

DUB = Path(__file__).resolve().parent.parent
CODE = ["vm/dubplan_cuda.py", "vm/cudacfg.py", "vm/prep_cuda.py", "vm/repair_cuda.py", "assemble.py", "validate_plan.py"]

INTRO = """# DERMDOC dubbing on Colab (T4): @@N@@ videos -> Bengali, Tamil, Telugu, Malayalam, Odia
**Runtime -> Change runtime type -> T4 GPU**, then **Runtime -> Run all**. Nothing to upload or edit: the code, the dub
plans and the source-video URLs are embedded. Each step prints its progress; a failure in one video never stops the
others. At the end `/content/dub_out_colab.zip` (the dubbed mp4s + QA reports) downloads automatically.

Videos: @@IDS@@

Expected on a free T4 (estimate): ~3-5 min of installs, then roughly 1 min per video. If the session drops, just
**Run all** again: finished videos are skipped."""

CELL1 = '''# 1/6  GPU check
import os, subprocess, sys, time
from pathlib import Path

IDS = @@IDLIST@@
ROOT = Path("/content/dub")
ROOT.mkdir(parents=True, exist_ok=True)
os.environ["PYTHONUNBUFFERED"] = "1"


def run(cmd, cwd=ROOT):
    """Run a command and stream its output. Never raises: one failed step must not stop Run all."""
    cmd = [str(c) for c in cmd]
    print("$", " ".join(cmd), flush=True)
    t = time.time()
    try:
        p = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            print(line, end="", flush=True)
        rc = p.wait()
    except Exception as e:
        print(f"!! {e!r}", flush=True)
        rc = -1
    print(f"[exit {rc} after {time.time() - t:.0f}s]", flush=True)
    return rc


print(subprocess.run(["nvidia-smi"], capture_output=True, text=True).stdout or "nvidia-smi not found")
import torch
if not torch.cuda.is_available():
    raise RuntimeError("No GPU. Runtime -> Change runtime type -> T4 GPU, then Runtime -> Run all.")
cc = torch.cuda.get_device_capability(0)
print(f"python {sys.version.split()[0]} | torch {torch.__version__} (CUDA {torch.version.cuda}) | "
      f"{torch.cuda.get_device_name(0)} cc {cc[0]}.{cc[1]} | "
      f"{'bf16 ok' if cc >= (8, 0) else 'no bf16 -> Indic-Mio fp16 (fp32 fallback), MioCodec fp32'} | "
      f"{torch.cuda.mem_get_info()[1] / 2**30:.1f} GB GPU memory")
print(f"{len(IDS)} videos: {', '.join(IDS)}")
'''

CELL2 = '''# 2/6  Install (Colab's own torch / torchaudio are kept: pinned through a constraints file)
import glob, shutil, site
cons = [f"torch=={torch.__version__}"]
try:
    import torchaudio
    cons.append(f"torchaudio=={torchaudio.__version__}")
except ImportError:
    print("torchaudio not preinstalled: pip will pick the one matching torch")
Path("/content/constraints.txt").write_text("\\n".join(cons) + "\\n")
if shutil.which("ffmpeg") is None:
    run(["apt-get", "-qq", "update"])
    run(["apt-get", "-qq", "install", "-y", "ffmpeg"])
run([sys.executable, "-m", "pip", "install", "-q", "-c", "/content/constraints.txt", "faster-whisper==1.2.1",
     "demucs==4.1.0", "librosa", "soundfile", "pyloudnorm", "threadpoolctl", "packaging"])
# MioCodec declares Python >= 3.12; on an older Colab Python try it anyway
extra = [] if sys.version_info >= (3, 12) else ["--ignore-requires-python"]
run([sys.executable, "-m", "pip", "install", "-q", "-c", "/content/constraints.txt", *extra,
     "git+https://github.com/Aratako/MioCodec"])
# CTranslate2 (faster-whisper) needs cuBLAS + cuDNN 9: point it at the pip CUDA libraries that came with torch
libs = sorted({d for sp in site.getsitepackages() for d in glob.glob(f"{sp}/nvidia/*/lib")})
os.environ["LD_LIBRARY_PATH"] = ":".join(libs + [os.environ.get("LD_LIBRARY_PATH", "")]).rstrip(":")
os.environ["TOKENIZERS_PARALLELISM"] = "false"
run([sys.executable, "-c", "import faster_whisper, demucs.api, miocodec, librosa, pyloudnorm, transformers, torch; "
     "print('imports ok | transformers', transformers.__version__, '| torch', torch.__version__)"])
'''

CELL3 = '''# 3/6  Write the engine code and every video's plan.json + meta.json (embedded below), then validate the plans
import base64, gzip, json
PAYLOAD = """
@@PAYLOAD@@
"""
files = json.loads(gzip.decompress(base64.b64decode(PAYLOAD)).decode("utf-8"))
for rel, text in files.items():
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
print(f"wrote {len(files)} files under {ROOT}")
for vid in IDS:
    (ROOT / "work" / vid / "dub.lock").unlink(missing_ok=True)  # single engine here: clear claims of a dropped session
    r = subprocess.run([sys.executable, "validate_plan.py", str(ROOT / "work" / vid / "plan.json")], cwd=ROOT,
                       capture_output=True, text=True)
    msg = (r.stdout + r.stderr).strip().splitlines()
    print(f"{vid}: plan {'OK' if r.returncode == 0 else 'INVALID (video will be skipped)'}  {msg[0] if msg else ''}")
'''

CELL4 = '''# 4/6  Download the source videos, decode their audio (44.1 kHz stereo) and split vocals / background with
#       Demucs htdemucs --two-stems=vocals on the GPU -> work/<id>/stems/{vocals,no_vocals}.wav
run([sys.executable, "vm/prep_cuda.py", "work", "--gens", "colab_gens.json", "--only", ",".join(IDS), "--stems-only"])
for vid in IDS:
    ok = all((ROOT / "work" / vid / "stems" / f).exists() for f in ("vocals.wav", "no_vocals.wav"))
    print(f"{vid}: {'stems ready' if ok else 'NO STEMS (download or separation failed; video will be skipped)'}")
'''

CELL5 = '''# 5/6  Dub: Indic-Mio on transformers (fp16 on T4, fp32 fallback) -> MioCodec voice cloning per character ->
#       Whisper QA with retries -> pitch/fx -> mix. One video at a time (--group 1) so finished videos land early;
#       then a repair pass re-voices lines the QA flagged.
t0 = time.time()
run([sys.executable, "vm/dubplan_cuda.py", "work", "out", "--backend", "transformers", "--group", "1",
     "--only", ",".join(IDS)])
run([sys.executable, "vm/repair_cuda.py", "work", "out", "0.6", "--backend", "transformers", "--only", ",".join(IDS)])
LANGS = ["bn", "ta", "te", "ml", "or"]
done = {vid: [l for l in LANGS if (ROOT / "out" / f"{vid}_{l}.mp4").exists()] for vid in IDS}
for vid, langs in done.items():
    print(f"{vid}: {len(langs)}/5 languages {' '.join(langs)}")
print(f"dub + repair took {(time.time() - t0) / 60:.1f} min; {sum(map(len, done.values()))} mp4s")
'''

CELL6 = '''# 6/6  Zip out/<id>_<lang>.mp4 + out/<id>_<lang>/qa.json and download it
import zipfile
ZIP = Path("/content/dub_out_colab.zip")
n = 0
with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for vid in IDS:
        for lang in ["bn", "ta", "te", "ml", "or"]:
            mp4, qa = ROOT / "out" / f"{vid}_{lang}.mp4", ROOT / "out" / f"{vid}_{lang}" / "qa.json"
            if mp4.exists():
                zf.write(mp4, f"out/{mp4.name}", compress_type=zipfile.ZIP_STORED)
                n += 1
            clips = ROOT / "out" / f"{vid}_{lang}"
            if clips.is_dir():  # line clips + script/layout/qa: needed for captions and repair back home
                for f in sorted(clips.iterdir()):
                    if f.is_file() and f.suffix in (".json", ".wav"):
                        zf.write(f, f"out/{vid}_{lang}/{f.name}")
print(f"{ZIP}: {n} videos, {ZIP.stat().st_size / 2**20:.1f} MB")
try:
    from google.colab import files
    files.download(str(ZIP))
except Exception as e:
    print(f"automatic download unavailable ({e!r}); use the Files panel on the left: /content/dub_out_colab.zip")
'''

CELL7 = '''# Optional: also copy the zip to Google Drive. Off by default (mounting asks for authorisation, which would block
# Run all): set COPY_TO_DRIVE = True and run this cell by hand.
COPY_TO_DRIVE = False
if COPY_TO_DRIVE:
    try:
        from google.colab import drive
        drive.mount("/content/drive")
        shutil.copy(ZIP, "/content/drive/MyDrive/dub_out_colab.zip")
        print("copied to MyDrive/dub_out_colab.zip")
    except Exception as e:
        print(f"Drive copy failed: {e!r}")
else:
    print("Drive copy skipped (set COPY_TO_DRIVE = True to enable)")
'''


def cell(kind, text):
    lines = text.strip("\n").split("\n")
    src = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    c = {"cell_type": kind, "metadata": {}, "source": src}
    if kind == "code":
        c.update(execution_count=None, outputs=[])
    return c


def main(ids_arg, *args):
    ids = [i.strip()[:8] for i in ids_arg.split(",") if i.strip()]
    gens_names = (args[args.index("--gens") + 1] if "--gens" in args else "gens_oct8.json,gens_batch.json").split(",")
    out = Path(args[args.index("--out") + 1]) if "--out" in args else DUB / "vm" / "colab_dub.ipynb"
    gens = {}
    for name in reversed(gens_names):  # earlier files win
        p = Path(name) if Path(name).is_absolute() else DUB / name
        if p.exists():
            gens.update({g["id"][:8]: g for g in json.loads(p.read_text())})
    files, mini, problems = {rel: (DUB / rel).read_text(encoding="utf-8") for rel in CODE}, [], []
    for vid in ids:
        wd, g = DUB / "work" / vid, gens.get(vid)
        url = ((g or {}).get("results") or {}).get("rawUrl")
        if not (wd / "plan.json").exists() or not url:
            problems.append(f"{vid}: {'no plan.json' if not (wd / 'plan.json').exists() else 'no source URL in gens'}")
            continue
        files[f"work/{vid}/plan.json"] = (wd / "plan.json").read_text(encoding="utf-8")
        if (wd / "meta.json").exists():
            files[f"work/{vid}/meta.json"] = (wd / "meta.json").read_text(encoding="utf-8")
        mini.append({"id": g["id"], "type": "video", "status": "completed", "createdAt": g.get("createdAt", 0),
                     "results": {"rawUrl": url}})
    if problems:
        sys.exit("cannot build notebook:\n  " + "\n  ".join(problems))
    files["colab_gens.json"] = json.dumps(mini, indent=1)
    blob = base64.b64encode(gzip.compress(json.dumps(files, ensure_ascii=False).encode("utf-8"), 9)).decode()
    payload = "\n".join(blob[i: i + 120] for i in range(0, len(blob), 120))
    cells = [cell("markdown", INTRO.replace("@@N@@", str(len(ids))).replace("@@IDS@@", ", ".join(ids))),
             cell("code", CELL1.replace("@@IDLIST@@", json.dumps(ids))), cell("code", CELL2),
             cell("code", CELL3.replace("@@PAYLOAD@@", payload)), cell("code", CELL4), cell("code", CELL5),
             cell("code", CELL6), cell("code", CELL7)]
    nb = {"nbformat": 4, "nbformat_minor": 0, "cells": cells,
          "metadata": {"accelerator": "GPU", "colab": {"provenance": [], "gpuType": "T4", "name": out.name},
                       "kernelspec": {"display_name": "Python 3", "name": "python3"},
                       "language_info": {"name": "python"}}}
    out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    # self-check: valid JSON, every code cell compiles, the payload round-trips
    nb2 = json.loads(out.read_text(encoding="utf-8"))
    for k, c in enumerate(nb2["cells"]):
        if c["cell_type"] == "code":
            compile("".join(c["source"]), f"{out.name}[cell {k}]", "exec")
    assert json.loads(gzip.decompress(base64.b64decode(payload)).decode("utf-8")) == files
    print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB): {len(ids)} videos, {len(files)} embedded files")


if __name__ == "__main__":
    main(*sys.argv[1:])
