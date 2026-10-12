#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
while pgrep -f "lipfit/lipfit.py" >/dev/null; do sleep 5; done
IDS="d6c1e78e b876bd3c a135c7dc 751fe1db 010ea465"
nice -n 10 .venv/bin/python post/render_post.py --ids ${=IDS} --langs bn ta te ml or --jobs 3 --force 2>&1 | grep -E "FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids ${=IDS} --force 2>&1 | grep -E "FAIL|DONE"
/Users/wachas/Documents/higgs-purple/dub/tools/pack.sh
echo "$(date +%T) LIPFIT FINISH DONE"
