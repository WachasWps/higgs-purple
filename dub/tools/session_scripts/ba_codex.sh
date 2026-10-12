#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub/feedback/codex
while pgrep -f "gen.py STORY_" >/dev/null; do sleep 10; done
echo "$(date +%T) START BA BEFORE"
python3 gen.py BA_23850d94_BEFORE BA_390113f1_BEFORE BA_71e0977a_BEFORE BA_bd3b8af7_BEFORE BA_f7ce58d4_BEFORE BA_595689d8_BEFORE BA_715b1b5c_BEFORE BA_89697c77_BEFORE BA_906fbf3c_BEFORE BA_7558fbf1_BEFORE --jobs 3
echo "$(date +%T) START BA AFTER"
python3 gen.py BA_23850d94_AFTER BA_390113f1_AFTER BA_71e0977a_AFTER BA_bd3b8af7_AFTER BA_f7ce58d4_AFTER BA_595689d8_AFTER BA_715b1b5c_AFTER BA_89697c77_AFTER BA_906fbf3c_AFTER --jobs 3
grep -l "usage limit" logs/BA_*.log 2>/dev/null | sed 's/^/LIMIT HIT: /'
echo "$(date +%T) BA DONE"
