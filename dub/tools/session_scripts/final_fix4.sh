#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
while ! grep -q "FINAL ALL DONE" feedback/final_all.log; do sleep 10; done
IDS="715b1b5c 23850d94 71e0977a f7ce58d4"
.venv/bin/python post/render_post.py --ids ${=IDS} --langs bn ta te ml or --jobs 5 --force 2>&1 | grep -E "FAIL|done:"
.venv/bin/python post/add_audio.py --ids ${=IDS} --force 2>&1 | grep -E "FAIL|DONE"
/Users/wachas/Documents/higgs-purple/dub/tools/pack.sh
echo "$(date +%T) FIX4 DONE"
