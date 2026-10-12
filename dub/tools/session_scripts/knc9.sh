#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
IDS="23850d94 390113f1 71e0977a bd3b8af7 f7ce58d4 595689d8 715b1b5c 89697c77 906fbf3c"
nice -n 10 python3 feedback/assemble_fix.py $IDS --remux 2>&1 | grep -E "Error|Traceback|missing"
nice -n 10 .venv/bin/python post/render_post.py --ids $IDS --langs bn ta te ml or --jobs 2 --force 2>&1 | grep -E "FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids $IDS --force 2>&1 | grep -E "FAIL|DONE"
.venv/bin/python post/build_folders.py 2>&1 | tail -1
python3 - <<'PY'
import subprocess, glob, os
from concurrent.futures import ThreadPoolExecutor
FF="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
def norm(f):
    tmp=f[:-4]+".ln.mp4"
    r=subprocess.run([FF,"-v","error","-y","-i",f,"-c:v","copy","-af","loudnorm=I=-16:TP=-1.5:LRA=11","-c:a","aac","-b:a","192k","-ar","48000","-movflags","+faststart",tmp],capture_output=True,text=True)
    if r.returncode==0: os.replace(tmp,f); return 0
    return f
with ThreadPoolExecutor(4) as ex: print("loudness failures:", [x for x in ex.map(norm, sorted(glob.glob("Final_Deliverables/**/*.mp4",recursive=True))) if x])
PY
echo "$(date +%T) KNC9 DONE"
