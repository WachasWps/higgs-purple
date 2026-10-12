#!/usr/bin/env bash
# One-time VM setup for the CUDA dub engine: Ubuntu 22.04 / GCP Deep Learning VM + NVIDIA driver (CUDA 12).
# Idempotent: re-run any time; finished steps are skipped or are no-ops. Never touches a working driver.
# Usage: bash vm/setup.sh
# Env overrides: INSTALL_VLLM=0|1  TORCH_CU=cu121|cu124|cu126|cu128  TORCH_VERSION  VLLM_VERSION  WHISPER_MODEL
#                WHISPER_COMPUTE  DUB_VENV
set -euo pipefail
VM="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DUB="$(dirname "$VM")"
VLLM_VERSION="${VLLM_VERSION:-0.11.0}"  # pins torch 2.8.0; its kernels are CUDA 12.8 builds
export DUB_VENV="${DUB_VENV:-$DUB/.venv-cuda}"
SUDO=$([ "$(id -u)" = 0 ] || echo sudo)
ver2int() { local a="${1%%.*}" b="${1#*.}"; b="${b%%.*}"; echo $(( ${a:-0} * 100 + ${b:-0} )); }  # "12.4" -> 1204

echo "== 1/5 system packages + GPU driver"
missing=$(for p in ffmpeg git rsync curl ca-certificates build-essential; do dpkg -s "$p" >/dev/null 2>&1 || echo "$p"; done)
if [ -n "$missing" ]; then
  $SUDO apt-get update -y
  $SUDO env DEBIAN_FRONTEND=noninteractive apt-get install -y $missing
fi
if ! nvidia-smi >/dev/null 2>&1; then
  if [ -x /opt/deeplearning/install-driver.sh ]; then  # GCP Deep Learning VM images ship this installer
    $SUDO /opt/deeplearning/install-driver.sh
  else
    echo "nvidia-smi does not work: install the NVIDIA driver (CUDA 12) first"; exit 1
  fi
fi
GPU_CC=$(nvidia-smi --query-gpu=compute_cap --format=csv,noheader 2>/dev/null | head -1 | tr -d ' ' || true)
DRV_CUDA=$(nvidia-smi | grep -o 'CUDA Version: *[0-9.]*' | grep -o '[0-9.]*$' | head -1 || true)
CC_INT=$(ver2int "${GPU_CC:-0.0}")
DRV_INT=$(ver2int "${DRV_CUDA:-0.0}")
nvidia-smi --query-gpu=name,memory.total,driver_version --format=csv,noheader
echo "compute capability ${GPU_CC:-?}, driver supports CUDA ${DRV_CUDA:-?}"

# torch wheel built for a CUDA the driver supports. Volta (V100, cc 7.0) stays on cu126 even on newer drivers:
# the cu128 builds are not guaranteed to carry sm_70 kernels.
if [ -z "${TORCH_CU:-}" ]; then
  if [ "$DRV_INT" -ge 1208 ] && [ "$CC_INT" -ge 750 ]; then TORCH_CU=cu128
  elif [ "$DRV_INT" -ge 1206 ]; then TORCH_CU=cu126
  elif [ "$DRV_INT" -ge 1204 ]; then TORCH_CU=cu124
  elif [ "$DRV_INT" -ge 1201 ]; then TORCH_CU=cu121
  else echo "driver CUDA ${DRV_CUDA:-unknown} < 12.1: update the driver"; exit 1
  fi
fi
case "$TORCH_CU" in
  cu128|cu126) DEFAULT_TORCH=2.8.0 ;;
  cu124) DEFAULT_TORCH=2.6.0 ;;
  cu121) DEFAULT_TORCH=2.5.1 ;;
  *) echo "unsupported TORCH_CU=$TORCH_CU"; exit 1 ;;
esac
TORCH_VERSION="${TORCH_VERSION:-$DEFAULT_TORCH}"
# vLLM only where it can run: its V1 engine targets cc >= 8.0, and the 0.11 wheels need torch 2.8 built for CUDA 12.8.
# Without it the engine uses its transformers backend (`--backend auto` picks whatever is there).
if [ -z "${INSTALL_VLLM:-}" ]; then INSTALL_VLLM=$([ "$CC_INT" -ge 800 ] && echo 1 || echo 0); fi
if [ "$INSTALL_VLLM" = 1 ] && [ "$TORCH_CU" != cu128 ]; then
  echo "note: vLLM $VLLM_VERSION needs torch 2.8 + cu128 (driver CUDA >= 12.8); skipping it -> transformers backend"
  INSTALL_VLLM=0
fi
echo "torch $TORCH_VERSION+$TORCH_CU, vLLM: $([ "$INSTALL_VLLM" = 1 ] && echo "$VLLM_VERSION" || echo "not installed")"

echo "== 2/5 uv + Python 3.12 venv ($DUB_VENV)"
export PATH="$HOME/.local/bin:$PATH"
command -v uv >/dev/null || curl -LsSf https://astral.sh/uv/install.sh | sh
[ -x "$DUB_VENV/bin/python" ] || uv venv --python 3.12 "$DUB_VENV"
PY="$DUB_VENV/bin/python"

echo "== 3/5 Python packages"
# torch + torchaudio from the PyTorch index for the chosen CUDA, then everything else from PyPI with torch pinned to
# that same version (the installed +cuXXX build satisfies the pin, so nothing swaps it behind our back).
uv pip install --python "$PY" --index-url "https://download.pytorch.org/whl/$TORCH_CU" \
  "torch==$TORCH_VERSION" "torchaudio==$TORCH_VERSION"
VLLM_PKG=""
if [ "$INSTALL_VLLM" = 1 ]; then VLLM_PKG="vllm==$VLLM_VERSION"; fi
uv pip install --python "$PY" "torch==$TORCH_VERSION" "torchaudio==$TORCH_VERSION" $VLLM_PKG \
  "transformers>=4.56,<5" "faster-whisper==1.2.1" "demucs==4.1.0" librosa soundfile pyloudnorm huggingface_hub \
  threadpoolctl "miocodec @ git+https://github.com/Aratako/MioCodec"

echo "== 4/5 models (cached under ~/.cache; already-downloaded files are skipped)"
"$PY" - <<'EOF'
import os
from huggingface_hub import snapshot_download
for repo in ("SPRINGLab/Indic-Mio", "Aratako/MioCodec-25Hz-24kHz"):
    print(repo, "->", snapshot_download(repo))
from faster_whisper import download_model
print("whisper ->", download_model(os.environ.get("WHISPER_MODEL", "large-v3-turbo")))
from demucs.pretrained import get_model
get_model("htdemucs")
print("htdemucs ok")
from miocodec import MioCodecModel
MioCodecModel.from_pretrained("Aratako/MioCodec-25Hz-24kHz")  # also caches its WavLM-base+ (torchaudio)
print("MioCodec ok")
EOF

echo "== 5/5 GPU check"
source "$VM/env.sh"
"$PY" - <<'EOF'
import os
import numpy as np
import torch
assert torch.cuda.is_available(), "torch sees no GPU"
cc = torch.cuda.get_device_capability(0)
print("torch", torch.__version__, "cuda", torch.version.cuda, "|", torch.cuda.get_device_name(0), "cc %d.%d" % cc)
try:  # fails with "no kernel image is available" if this torch build lacks kernels for the GPU
    x = torch.randn(64, 64, device="cuda", dtype=torch.float16)
    (x @ x).sum().item()
except RuntimeError as e:
    raise SystemExit(f"torch {torch.__version__} cannot run on cc {cc[0]}.{cc[1]} ({e}); set TORCH_CU / TORCH_VERSION")
from faster_whisper import WhisperModel  # loads ctranslate2's cuBLAS/cuDNN: fails here if LD_LIBRARY_PATH is wrong
compute = os.environ.get("WHISPER_COMPUTE", "float16")
m = WhisperModel(os.environ.get("WHISPER_MODEL", "large-v3-turbo"), device="cuda", compute_type=compute)
list(m.transcribe(np.zeros(16000, dtype=np.float32), language="bn")[0])
print(f"faster-whisper {compute} on CUDA ok")
try:
    import vllm
    print("vllm", vllm.__version__, "(backend auto will try it first)")
except ImportError:
    print("vllm not installed: the engine will use its transformers backend")
EOF
echo "setup done. Next: sync work/ in (vm/sync_to_vm.sh on the Mac), then:"
echo "  $VM/run_all.sh prep | selftest | dub | all"
