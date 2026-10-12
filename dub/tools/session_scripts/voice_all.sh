#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
echo "$(date +%T) start"
nice -n 10 .venv/bin/python prep.py work_new2/ 2>&1 | grep -E "PREP DONE|Error"
nice -n 10 .venv/bin/python -u dubplan.py work_new2/ out/ 2>&1 | grep -E "OK|FAIL|Error"
echo "$(date +%T) UGC3/4 dubbed: $(ls out | grep -cE '^(a135c7dc|751fe1db)_(bn|ta|te|ml|or)\.mp4$')/10"
nice -n 10 .venv/bin/python redub.py d6c1e78e b876bd3c 2>&1 | grep -E "REDUB OK|FAILED"
echo "$(date +%T) VOICE_ALL DONE"
