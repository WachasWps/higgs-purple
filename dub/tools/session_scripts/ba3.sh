#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub/feedback/codex
python3 gen.py ADS_PS_AFTER ADS_KNC_AFTER BA2_00b304b4_BEFORE BA2_291827ba_BEFORE BA2_c51221b6_BEFORE BA2_ce849d3f_BEFORE BA2_e7e42eaf_BEFORE --jobs 3
python3 gen.py BA2_00b304b4_AFTER BA2_291827ba_AFTER BA2_c51221b6_AFTER BA2_ce849d3f_AFTER BA2_e7e42eaf_AFTER --jobs 3
grep -l "usage limit" logs/ADS_*.log logs/BA2_*.log 2>/dev/null | sed 's/^/LIMIT HIT: /'
echo "$(date +%T) BA3 DONE"
