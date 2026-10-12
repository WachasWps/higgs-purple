# Dub engine on an NVIDIA VM (CUDA port of prep/dubplan/repair; assemble, organize, validate_plan reused as-is)
VM (current): GCP n1-standard-8 (8 vCPU, 30 GB RAM) + 1x Tesla V100 16 GB, 200 GB SSD, Deep Learning VM image (Ubuntu 22.04, CUDA 12 driver).
  V100 = cc 7.0, no bf16: auto-picks Indic-Mio fp16 on transformers (fp32 fallback on overflow), MioCodec fp32, Whisper float16, no vLLM.
  Bigger GPUs (L40S/A100, cc >= 8.0, driver CUDA >= 12.8) get vLLM + bf16 automatically. Overrides: BACKEND, DTYPE, CODEC_DTYPE, WHISPER_COMPUTE, BATCH.
1. Mac: `vm/sync_to_vm.sh me@VM [--ids id1,id2,... | --ids-file f]` pushes code + work/ (only those ids if given; writes ~/dub/vm_ids.txt).
2. VM: `bash ~/dub/vm/setup.sh` installs apt deps, uv + Python 3.12 venv, torch for the driver's CUDA (cu121-cu128), vLLM only on cc >= 8.0, all models (idempotent).
3. VM (in tmux): `~/dub/vm/run_all.sh prep [gens.json ...]` runs optional downloads, then stems + transcript.json per work/<id>/.
4. VM: `~/dub/vm/run_all.sh selftest` prints backend, dtypes, a 1-line sample length and TTS tok/s; exits non-zero on failure (wavs in ~/dub/selftest/).
5. Mac: `vm/sync_from_vm.sh me@VM` (transcripts + frames back), director agents write + validate plans, `vm/sync_to_vm.sh me@VM ...` again.
6. VM (in tmux): `IDS_FILE=vm_ids.txt ~/dub/vm/run_all.sh dub` = validate -> dubplan_cuda -> repair_cuda -> organize (`WATCH=N` waits for N plans).
7. Mac: `vm/sync_from_vm.sh me@VM` brings out/ + final/ back. Logs: `~/dub/logs/`.
Design: one engine voices GROUP=8 videos per GPU pass (batched TTS sampling + batched codec/Whisper QA rounds) while a CPU pool does pitch-match/fx/mixing.
Expected (estimates; check per-video timings in logs/dub.log): V100 ~25-40 s/video for all 5 languages (~100-140 videos/h), prep ~5 s/video;
an L40S with vLLM ~5-8 s/video. Colab (T4, free): `python3 vm/make_colab.py id1,id2,...` writes a self-contained vm/colab_dub.ipynb.
