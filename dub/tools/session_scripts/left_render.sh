#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
IDS="7ea55172 7558fbf1 715b1b5c 23850d94 71e0977a"
nice -n 10 python3 feedback/assemble_fix.py $IDS --remux 2>&1 | grep -E "source_fixed|Error|Traceback|missing"
nice -n 10 .venv/bin/python post/render_post.py --ids $IDS --langs bn ta te ml or --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids $IDS --force 2>&1 | grep -E "FAIL|DONE"
R=feedback/review/STORY_19
for v in $IDS; do f=$(ls deliver_music/Bengali/*_$v.mp4); b=$(basename $f .mp4); cp $f "$R/${b}_FIXED.mp4"; done
echo "$(date +%T) LEFTOVER RENDER DONE"
