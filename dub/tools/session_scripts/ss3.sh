#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
IDS="4010f985"
#for v in ${=IDS}; do find deliver/English deliver_music/English -name "*_$v.mp4" -delete; done
nice -n 10 .venv/bin/python -u feedback/ads_english_kokoro.py hf_alpha h ${=IDS} 2>&1 | grep -E "slot|voiced|Error|Traceback|WARNING"
nice -n 10 .venv/bin/python post/render_post.py --ids ${=IDS} --langs en --jobs 2 --force 2>&1 | grep -E "FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids ${=IDS} --force 2>&1 | grep -E "FAIL|DONE"
echo "$(date +%T) SS3 RENDERED"
/Users/wachas/Documents/higgs-purple/dub/tools/pack.sh; echo "$(date +%T) SS3 DONE"
