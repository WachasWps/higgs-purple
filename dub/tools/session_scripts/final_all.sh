#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
IDS="00b304b4 010ea465 02bad3b3 23850d94 291827ba 33c29291 390113f1 46d965c9 595689d8 5fd50ab8 655a1328 715b1b5c 71e0977a 74495eba 751fe1db 7558fbf1 784c77c5 7ea55172 89697c77 906fbf3c a135c7dc a5c00002 b876bd3c bd3b8af7 c51221b6 cd5a6fe8 ce849d3f d6c1e78e e7e42eaf f7ce58d4"
.venv/bin/python post/render_post.py --ids ${=IDS} --langs bn ta te ml or --jobs 5 --force 2>&1 | grep -E "FAIL|done:"
.venv/bin/python post/add_audio.py --ids ${=IDS} --force 2>&1 | grep -E "FAIL|DONE"
/Users/wachas/Documents/higgs-purple/dub/tools/pack.sh
echo "$(date +%T) FINAL ALL DONE"
