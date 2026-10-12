#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub/feedback/codex
until [ "$(date +%H%M)" -ge 2214 ]; do sleep 30; done
echo "$(date +%T) START UGC KEYFRAMES"
python3 gen.py UGC_dad2130b_S9 UGC_65a0c520_S5 UGC_02bad3b3_S1 UGC_784c77c5_S1 UGC_a5c00002_S4 UGC_02bad3b3_S6 UGC_02bad3b3_S9 --jobs 3
[ -f out/UGC_a5c00002_S4.png ] && python3 gen.py UGC_a5c00002_AFTER --jobs 1
grep -l "usage limit" logs/UGC_*.log 2>/dev/null | sed 's/^/LIMIT HIT: /'
echo "$(date +%T) UGC KEYFRAMES DONE"
