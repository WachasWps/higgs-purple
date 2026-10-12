#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
IDS="d6c1e78e b876bd3c"
nice -n 10 .venv/bin/python prep.py work_new/ 2>&1 | grep -E "PREP DONE|Error"
nice -n 10 .venv/bin/python -u dubplan.py work_new/ out/ 2>&1 | grep -E "OK|FAIL|Error|done"
echo "$(date +%T) dubs: $(ls out/ | grep -cE '^(d6c1e78e|b876bd3c)_(bn|ta|te|ml|or)\.mp4$')/10"
for v in ${=IDS}; do python3 -c "import sys;sys.path.insert(0,'feedback');sys.argv=['x'];import assemble_fix as A;A.remux('$v')" >/dev/null; done
nice -n 10 .venv/bin/python post/render_post.py --ids ${=IDS} --langs bn ta te ml or --jobs 2 --force 2>&1 | grep -E "FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids ${=IDS} --force 2>&1 | grep -E "FAIL|DONE"
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
echo "$(date +%T) NEWUGC DONE"
