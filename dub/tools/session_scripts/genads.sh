#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
IDS="a9be56d9 426b77bb eab38211 e9528636 b4c787e1 c01adcce fe7174d4 fb3fa838 ce52c347"
nice -n 10 .venv/bin/python -u feedback/ads_english_kokoro.py hf_beta a ${=IDS} 2>&1 | grep -E "slot|voiced|Error|Traceback|WARNING"
nice -n 10 .venv/bin/python post/render_post.py --ids ${=IDS} --langs en --jobs 2 --force 2>&1 | grep -E "FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids ${=IDS} --force 2>&1 | grep -E "FAIL|DONE"
echo "$(date +%T) GENADS RENDERED"
