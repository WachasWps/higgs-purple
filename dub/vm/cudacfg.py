"""GPU / CLI settings shared by the CUDA dub scripts. Light module: torch and MioCodec are imported only when needed.

Env (all optional):
  DTYPE=auto|fp16|fp32|bf16      Indic-Mio weights. auto: bf16 on compute capability >= 8.0, else fp16 (V100 has no bf16)
  CODEC_DTYPE=auto|fp32|fp16|bf16  MioCodec autocast. auto: bf16 where DTYPE is bf16, else fp32 (its iSTFT head builds
                                 complex spectrograms; fp16 there is the risky part, and the 132M codec is cheap in fp32)
  WHISPER_COMPUTE=float16|int8_float16   faster-whisper (CTranslate2) compute type; both run on V100 (cc 7.0)
"""
import os
import re
import subprocess
from pathlib import Path

_ALIASES = {"float16": "fp16", "half": "fp16", "float32": "fp32", "float": "fp32", "bfloat16": "bf16"}
_CC = None


def compute_cap():
    """(major, minor) of GPU 0, read through nvidia-smi so CUDA is not initialised before vLLM starts."""
    global _CC
    if _CC is None:
        try:
            out = subprocess.run(["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader"],
                                 capture_output=True, text=True, check=True).stdout.split()[0]
            _CC = tuple(int(x) for x in out.split(".")[:2])
        except Exception:
            import torch
            _CC = torch.cuda.get_device_capability(0)
    return _CC


def _norm(d, var):
    d = _ALIASES.get(d.lower(), d.lower())
    if d not in ("fp16", "fp32", "bf16"):
        raise ValueError(f"{var} must be auto, fp16, fp32 or bf16 (got {d!r})")
    return d


def dtype_name():
    d = os.environ.get("DTYPE", "auto")
    return ("bf16" if compute_cap() >= (8, 0) else "fp16") if d.lower() == "auto" else _norm(d, "DTYPE")


def codec_dtype():
    d = os.environ.get("CODEC_DTYPE", "auto")
    return ("bf16" if dtype_name() == "bf16" else "fp32") if d.lower() == "auto" else _norm(d, "CODEC_DTYPE")


def whisper_compute():
    return os.environ.get("WHISPER_COMPUTE", "float16")


def torch_dtype(name):
    import torch
    return {"bf16": torch.bfloat16, "fp16": torch.float16, "fp32": torch.float32}[name]


def patch_codec(name):
    """MioCodec hard-codes bf16 autocast on CUDA (miocodec.model._get_autocast_context); swap in our dtype."""
    import contextlib

    import miocodec.model as mm
    import torch
    if not hasattr(mm, "_get_autocast_context"):
        print("warning: miocodec has no _get_autocast_context any more; codec dtype not applied", flush=True)
        return
    if name == "fp32":
        mm._get_autocast_context = lambda device_type: contextlib.nullcontext()
    else:
        dt = torch_dtype(name)
        mm._get_autocast_context = lambda device_type: (torch.autocast(device_type="cuda", dtype=dt)
                                                        if device_type == "cuda" else contextlib.nullcontext())


def ids_filter(args):
    """--only id1,id2,... and/or --ids-file f (ids split by commas/whitespace/newlines, '#' comments; full uuids are
    cut to the 8-char work/ dir names). Returns a set, or None when neither flag is given."""
    if "--only" not in args and "--ids-file" not in args:
        return None
    raw = []
    if "--only" in args:
        raw.append(args[args.index("--only") + 1])
    if "--ids-file" in args:
        raw += [line.split("#")[0] for line in Path(args[args.index("--ids-file") + 1]).read_text().splitlines()]
    return {i[:8] for chunk in raw for i in re.split(r"[,\s]+", chunk) if i}
