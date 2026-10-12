# Environment for the CUDA dub engine. Sourced by setup.sh and run_all.sh (or by hand: `source vm/env.sh`).
VM_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export DUB_VENV="${DUB_VENV:-$(dirname "$VM_DIR")/.venv-cuda}"
export PATH="$DUB_VENV/bin:$HOME/.local/bin:$PATH"
# ctranslate2 (faster-whisper) looks for cuBLAS / cuDNN on the library path: reuse the pip CUDA libs torch ships with.
for d in "$DUB_VENV"/lib/python3*/site-packages/nvidia/cublas/lib "$DUB_VENV"/lib/python3*/site-packages/nvidia/cudnn/lib; do
  if [ -d "$d" ]; then
    case ":${LD_LIBRARY_PATH:-}:" in *":$d:"*) ;; *) export LD_LIBRARY_PATH="$d${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}" ;; esac
  fi
done
export TOKENIZERS_PARALLELISM=false
# PyTorch-native top-p sampling in vLLM (no FlashInfer JIT / nvcc needed; the vocab is small).
export VLLM_USE_FLASHINFER_SAMPLER="${VLLM_USE_FLASHINFER_SAMPLER:-0}"
true
