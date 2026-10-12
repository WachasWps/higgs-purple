#!/bin/bash
cd /Users/wachas/Documents/higgs-purple/dub
nice -n 10 python3 feedback/assemble_fix.py dad2130b 65a0c520 02bad3b3 a5c00002 --remux 2>&1 | grep -E "source_fixed|Error|Traceback|missing"
nice -n 10 .venv/bin/python post/render_post.py --ids dad2130b 65a0c520 02bad3b3 a5c00002 --langs bn --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids dad2130b 65a0c520 02bad3b3 a5c00002 --force 2>&1 | grep -cE "ok "
R=feedback/review/UGC
for v in dad2130b 65a0c520 02bad3b3 a5c00002; do
  old=$(ls $R/*_${v}_FIXED-free-pass.mp4 2>/dev/null); [ -n "$old" ] && rm -f "$old"
  n=$(basename "$(ls $R/*${v}_ORIGINAL-not-fixed-yet.mp4)" | cut -c1-2); f=$(ls deliver_music/Bengali/*_$v.mp4); b=$(basename $f .mp4)
  cp "$f" "$R/${n}_${b#*_}_FIXED-final.mp4"
done
echo "$(date +%T) UGC CREDIT BUILD DONE"
