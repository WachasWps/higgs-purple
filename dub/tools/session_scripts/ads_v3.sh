#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
until grep -q "STORY BUILD DONE" feedback/story_build_knc.log 2>/dev/null; do sleep 10; done
IDS="4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1"
nice -n 10 python3 feedback/assemble_fix.py $IDS --remux 2>&1 | grep -E "source_fixed|Error|Traceback|missing"
nice -n 10 .venv/bin/python post/render_post.py --ids $IDS --langs en --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids $IDS --force 2>&1 | grep -E "FAIL"
R=feedback/review/ADS_v3; rm -rf $R; mkdir -p $R; cp deliver_music/English/*.mp4 $R/
echo "$(date +%T) ADS V3 DONE"
