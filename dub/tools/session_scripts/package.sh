#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
until [ $(grep -c "voiced (" feedback/ads_kokoro.log) -ge 10 ] || ! pgrep -f ads_english_kokoro.py >/dev/null; do sleep 10; done
ADS="4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1"
nice -n 10 .venv/bin/python post/render_post.py --ids $ADS --langs en --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids $ADS --force 2>&1 | grep -E "FAIL|DONE"
R=feedback/review/ADS_v3; rm -rf $R; mkdir -p $R; cp deliver_music/English/*.mp4 $R/
echo "$(date +%T) ADS VOICED + RENDERED"
TS=$(date +%Y%m%d_%H%M)
[ -d Final_Deliverables ] && mv Final_Deliverables post/superseded/Final_Deliverables_round1_$TS
.venv/bin/python post/build_folders.py 2>&1 | tail -20
echo "$(date +%T) PACKAGED"
