#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub/feedback/codex
until grep -q "UGC KEYFRAMES DONE" ugc_codex.log; do sleep 15; done
echo "$(date +%T) START PILOT KEYFRAMES"
python3 gen.py PILOT_33c29291_S1 PILOT_33c29291_S2 PILOT_33c29291_S5 --jobs 3
grep -l "usage limit" logs/PILOT_*.log 2>/dev/null | sed 's/^/LIMIT HIT: /'
echo "$(date +%T) PILOT KEYFRAMES DONE"
