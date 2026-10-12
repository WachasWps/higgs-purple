"""Keep heavy ML work inside this Mac's limits (16 GB RAM, 4P+6E cores).

Import this FIRST in any ML script: it caps CPU threads before torch/numpy load, and
`wait_for_headroom()` pauses between work items while memory or thermals are under pressure.
"""
import os

for var in ("OMP_NUM_THREADS", "MKL_NUM_THREADS", "OPENBLAS_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(var, "4")
os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

import re
import subprocess
import time

MIN_FREE_PCT = 25  # keep at least ~4 GB free for macOS + the user's apps


def _free_pct():
    out = subprocess.run(["memory_pressure", "-Q"], capture_output=True, text=True).stdout
    m = re.search(r"free percentage:\s*(\d+)%", out)
    return int(m.group(1)) if m else 100


def _thermal_ok():
    out = subprocess.run(["pmset", "-g", "therm"], capture_output=True, text=True).stdout
    return "No thermal warning level has been recorded" in out or "warning level" not in out.lower()


def wait_for_headroom(tag=""):
    waited = 0
    while True:
        free, cool = _free_pct(), _thermal_ok()
        if free >= MIN_FREE_PCT and cool:
            if waited:
                print(f"[guard] resumed {tag} after {waited}s (free {free}%)", flush=True)
            return
        if waited % 60 == 0:
            print(f"[guard] pausing {tag}: free memory {free}%, thermal ok={cool}", flush=True)
        time.sleep(15)
        waited += 15


def cap_torch():
    import torch
    torch.set_num_threads(4)
