"""Build + push a Kaggle GPU job (T4) that dubs the given video ids; results come back as one zip.

Usage: python3 vm/make_kaggle.py <slug> id1,id2,...      (then: .venv/bin/kaggle kernels push -p kaggle_jobs/<slug>)
Reuses make_colab.py's self-contained notebook; only paths change (work in /tmp, zip to /kaggle/working).
"""
import json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
slug, ids = sys.argv[1], sys.argv[2]
job = ROOT / "kaggle_jobs" / slug
job.mkdir(parents=True, exist_ok=True)
tmp_nb = job / "colab.ipynb"
subprocess.run([sys.executable, str(ROOT / "vm" / "make_colab.py"), ids, "--out", str(tmp_nb)] + sys.argv[3:], check=True, cwd=ROOT)
nb = tmp_nb.read_text()
nb = (nb.replace("/content/dub_out_colab.zip", "/kaggle/working/dub_out.zip")
        .replace("/content/constraints.txt", "/tmp/constraints.txt")
        .replace("/content/dub", "/tmp/dub"))
(job / "dub.ipynb").write_text(nb)
tmp_nb.unlink()
user = subprocess.run([str(ROOT / ".venv/bin/kaggle"), "config", "view"], capture_output=True, text=True).stdout
user = next(l.split(":", 1)[1].strip() for l in user.splitlines() if "username" in l)
(job / "kernel-metadata.json").write_text(json.dumps({
    "id": f"{user}/{slug}", "title": slug, "code_file": "dub.ipynb", "language": "python",
    "kernel_type": "notebook", "is_private": True, "enable_gpu": True, "enable_tpu": False,
    "enable_internet": True, "machine_shape": "NvidiaTeslaT4",
    "dataset_sources": [], "competition_sources": [], "kernel_sources": []}, indent=1))
print(f"built {job} for {user}/{slug}: {ids}")
