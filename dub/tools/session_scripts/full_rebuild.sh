#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
DUB="02bad3b3 3d01d9fc 46d965c9 51440b1f 65a0c520 784c77c5 a5c00002 caf29456 cd5a6fe8 dad2130b 00b304b4 291827ba c51221b6 ce849d3f e7e42eaf 33c29291 5fd50ab8 655a1328 74495eba 7ea55172 23850d94 390113f1 71e0977a bd3b8af7 f7ce58d4 595689d8 715b1b5c 7558fbf1 89697c77 906fbf3c"
ADS="4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1"
nice -n 10 python3 feedback/assemble_fix.py $DUB $ADS --remux 2>&1 | grep -E "Error|Traceback|missing"
echo "$(date +%T) ASSEMBLED"
nice -n 10 .venv/bin/python post/render_post.py --ids $DUB --langs bn ta te ml or --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
nice -n 10 .venv/bin/python post/render_post.py --ids $ADS --langs en --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids $DUB $ADS --force 2>&1 | grep -E "FAIL|DONE"
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
python3 /Users/wachas/Documents/higgs-purple/dub/tools/qc_all.py 2>&1 | head -5
echo "$(date +%T) FULL REBUILD DONE"
