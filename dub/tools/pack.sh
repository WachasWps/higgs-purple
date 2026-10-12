#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
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
with ThreadPoolExecutor(6) as ex: print("loudness failures:", [x for x in ex.map(norm, sorted(glob.glob("Final_Deliverables/**/*.mp4",recursive=True))) if x])
PY
echo "$(date +%T) PACK DONE"
