#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
until grep -q "ADS V3 DONE" feedback/all_build.log; do sleep 10; done
UGC="02bad3b3 3d01d9fc 46d965c9 51440b1f 65a0c520 784c77c5 a5c00002 caf29456 cd5a6fe8 dad2130b"
STORY="00b304b4 291827ba c51221b6 ce849d3f e7e42eaf 33c29291 5fd50ab8 655a1328 74495eba 7ea55172 23850d94 390113f1 71e0977a bd3b8af7 f7ce58d4 595689d8 715b1b5c 7558fbf1 89697c77 906fbf3c"
echo "$(date +%T) re-stitch UGC + pilot"
nice -n 10 python3 feedback/assemble_fix.py $UGC 33c29291 --remux 2>&1 | grep -E "source_fixed|Error|Traceback|missing"
echo "$(date +%T) render 30 x 5 languages"
nice -n 10 .venv/bin/python post/render_post.py --ids $UGC $STORY --langs bn ta te ml or --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
echo "$(date +%T) music"
nice -n 10 .venv/bin/python post/add_audio.py --ids $UGC $STORY --force 2>&1 | grep -E "FAIL|DONE"
echo "$(date +%T) FINAL RENDER DONE"
