#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
ADS="a9be56d9 426b77bb eab38211 e9528636 b4c787e1"
.venv/bin/python -u feedback/ads_english_kokoro.py hf_beta a $ADS 2>&1 | grep -E "voiced|Traceback|Error"
nice -n 10 .venv/bin/python post/render_post.py --ids $ADS --langs en --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids $ADS --force 2>&1 | grep -E "FAIL|DONE"
R=feedback/review/ADS_v3; rm -rf $R; mkdir -p $R; cp deliver_music/English/*.mp4 $R/
.venv/bin/python post/build_folders.py 2>&1 | tail -1
.venv/bin/python - <<'PY' 2>&1 | grep -vE "Warning|Fetching" | tail -3
import mlx_whisper, glob
for f in sorted(glob.glob("Final_Deliverables/4_AI_General_Ads/*/*"))[:2]:
    print(f.split('/')[-1], "->", mlx_whisper.transcribe(f, path_or_hf_repo="mlx-community/whisper-large-v3-turbo", language="en")["text"].strip()[:150])
PY
echo "$(date +%T) REVOICE PACKAGED"
