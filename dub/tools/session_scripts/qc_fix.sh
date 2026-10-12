#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
IDS="390113f1 f7ce58d4 71e0977a 23850d94 74495eba 89697c77 e7e42eaf"
nice -n 10 python3 feedback/assemble_fix.py $IDS --remux 2>&1 | grep -E "source_fixed|Error|Traceback|missing"
nice -n 10 .venv/bin/python post/render_post.py --ids $IDS --langs bn ta te ml or --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids $IDS --force 2>&1 | grep -E "FAIL|DONE"
.venv/bin/python post/build_folders.py 2>&1 | tail -1
echo "$(date +%T) loudness"
python3 - <<'PY'
import subprocess, glob, json, os
from concurrent.futures import ThreadPoolExecutor
FF="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
def norm(f):
    tmp=f[:-4]+".ln.mp4"
    r=subprocess.run([FF,"-v","error","-y","-i",f,"-c:v","copy","-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",tmp],capture_output=True,text=True)
    if r.returncode==0: os.replace(tmp,f); return 0
    return f
with ThreadPoolExecutor(4) as ex: bad=[x for x in ex.map(norm, sorted(glob.glob("Final_Deliverables/**/*.mp4",recursive=True))) if x]
print("loudness normalised; failures:", bad)
PY
python3 /Users/wachas/Documents/higgs-purple/dub/tools/qc_all.py 2>&1 | head -6
echo "$(date +%T) QC FIX DONE"
