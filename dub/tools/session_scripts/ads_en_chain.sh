#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
IDS="4010f985 426b77bb a9be56d9 b4c787e1 c01adcce ce52c347 e9528636 eab38211 fb3fa838 fe7174d4"
nice -n 10 python3 feedback/assemble_fix.py $IDS 2>&1 | grep -E "source_fixed|Error|Traceback"
echo "$(date +%T) ADS ASSEMBLED"
nice -n 10 .venv/bin/python -u feedback/ads_english.py $IDS 2>&1 | grep -E "langs in|heard|Traceback|Error"
echo "$(date +%T) ADS VOICED"
nice -n 10 .venv/bin/python post/render_post.py --ids $IDS --langs en --jobs 2 --force 2>&1 | grep -E "ok |FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids $IDS --force 2>&1 | grep -E "English|FAIL"
mkdir -p feedback/review/ADS/English_all
cp deliver_music/English/*.mp4 feedback/review/ADS/English_all/
echo "$(date +%T) ADS EN CHAIN DONE"
