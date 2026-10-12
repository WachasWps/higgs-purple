#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
until [ -f feedback/script_audit/translations.json ] && python3 -c "import json;assert len(json.load(open('feedback/script_audit/translations.json')))>=42" 2>/dev/null; do sleep 15; done
python3 feedback/apply_script.py || { echo "APPLY FAILED"; exit 1; }
DUB=$(python3 -c "import json;A=set('4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1'.split());print(' '.join(v for v in json.load(open('feedback/script_audit/final_changes.json')) if v not in A))")
ADS=$(python3 -c "import json;A='4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1'.split();F=json.load(open('feedback/script_audit/final_changes.json'));print(' '.join(v for v in A if v in F))")
for v in $DUB; do r=$(nice -n 10 .venv/bin/python redub.py $v 2>&1 | grep -E "REDUB OK|FAILED|Error" | tail -1); echo "$(date +%T) redub $v: $r"; done
nice -n 10 .venv/bin/python -u feedback/ads_english_kokoro.py hf_beta a $ADS 2>&1 | grep -E "voiced|Error|Traceback"
for v in $DUB $ADS; do python3 -c "import sys;sys.path.insert(0,'feedback');sys.argv=['x'];import assemble_fix as A;A.remux('$v')" >/dev/null; done
nice -n 10 .venv/bin/python post/render_post.py --ids $DUB --langs bn ta te ml or --jobs 2 --force 2>&1 | grep -E "FAIL|done:"
[ -n "$ADS" ] && nice -n 10 .venv/bin/python post/render_post.py --ids $ADS --langs en --jobs 2 --force 2>&1 | grep -E "FAIL|done:"
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
echo "$(date +%T) SCRIPT2 DONE"
