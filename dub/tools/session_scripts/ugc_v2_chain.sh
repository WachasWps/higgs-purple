#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
nice -n 10 python3 feedback/assemble_fix.py dad2130b caf29456 3d01d9fc 65a0c520 51440b1f --remux >> feedback/assemble_ugc_v2.log 2>&1
echo "$(date +%T) PS assembled"
for v in 02bad3b3 cd5a6fe8 784c77c5 46d965c9 a5c00002; do [ -f work/$v/source_fixed.libv1.mp4 ] || cp work/$v/source_fixed.mp4 work/$v/source_fixed.libv1.mp4; done
nice -n 10 python3 feedback/assemble_fix.py 02bad3b3 cd5a6fe8 784c77c5 46d965c9 a5c00002 --remux >> feedback/assemble_ugc_v2.log 2>&1
echo "$(date +%T) KNC assembled"
IDS="51440b1f dad2130b caf29456 3d01d9fc 65a0c520 02bad3b3 cd5a6fe8 784c77c5 46d965c9 a5c00002"
nice -n 10 .venv/bin/python post/render_post.py --ids $IDS --langs bn --jobs 2 --force 2>&1 | grep -E "ok |FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids $IDS --force 2>&1 | grep -E "Bengali|FAIL|DONE"
R=feedback/review/UGC
for v in $IDS; do f=$(ls deliver_music/Bengali/*_$v.mp4); b=$(basename $f .mp4); o=$(ls $R/*_$v_ORIGINAL-not-fixed-yet.mp4 2>/dev/null); n=$(basename "$(ls $R/*${v}_ORIGINAL-not-fixed-yet.mp4)" | cut -c1-2); cp "$f" "$R/${n}_${b#*_}_FIXED-free-pass.mp4"; done
echo "$(date +%T) UGC V2 CHAIN DONE"
