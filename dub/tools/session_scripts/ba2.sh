#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub/feedback/codex
V2="dad2130b caf29456 51440b1f 74495eba 7ea55172 33c29291 3d01d9fc 65a0c520 5fd50ab8 655a1328 02bad3b3 784c77c5 46d965c9 cd5a6fe8"
python3 gen.py BA_23850d94_AFTER BA_390113f1_AFTER BA_71e0977a_AFTER BA_bd3b8af7_AFTER BA_f7ce58d4_AFTER BA_595689d8_AFTER BA_715b1b5c_AFTER BA_89697c77_AFTER BA_906fbf3c_AFTER $(for v in $V2; do echo BA2_${v}_BEFORE; done) --jobs 3
python3 gen.py $(for v in $V2; do echo BA2_${v}_AFTER; done) --jobs 3
grep -l "usage limit" logs/BA*_*.log 2>/dev/null | sed 's/^/LIMIT HIT: /'
echo "$(date +%T) BA2 DONE"
