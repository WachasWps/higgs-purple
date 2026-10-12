#!/bin/bash
# usage: story_build.sh <id> ...   assemble v2 picture -> remux -> Bengali render -> music -> review copy + side-by-side
cd /Users/wachas/Documents/higgs-purple/dub
FF=/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg
R=feedback/review/STORY_19; mkdir -p $R
for v in "$@"; do [ -f work/$v/source_fixed.libv1.mp4 ] || cp work/$v/source_fixed.mp4 work/$v/source_fixed.libv1.mp4; done
nice -n 10 python3 feedback/assemble_fix.py "$@" --remux 2>&1 | grep -E "source_fixed|Error|Traceback|missing"
nice -n 10 .venv/bin/python post/render_post.py --ids "$@" --langs bn --jobs 2 --force 2>&1 | grep -E "FAIL|skip|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids "$@" --force 2>&1 | grep -E "FAIL" 
for v in "$@"; do
  N=$(ls deliver_music/Bengali/*_$v.mp4); O=post/superseded/round1_1808/deliver_music/Bengali/$(basename $N); b=$(basename $N .mp4)
  cp $N "$R/${b}_FIXED.mp4"
  [ -f "$O" ] && $FF -v error -y -i "$O" -i "$N" -filter_complex "[0:v]scale=540:960,setsar=1,fps=30,drawtext=fontfile=post/fonts/Lato-Black.ttf:text='CLIENT SAW':fontsize=34:fontcolor=white:box=1:boxcolor=red@0.8:boxborderw=10:x=(w-tw)/2:y=20[a];[1:v]scale=540:960,setsar=1,fps=30,drawtext=fontfile=post/fonts/Lato-Black.ttf:text='FIXED':fontsize=34:fontcolor=white:box=1:boxcolor=green@0.8:boxborderw=10:x=(w-tw)/2:y=20[b];[a][b]hstack=2[v]" -map "[v]" -map 1:a -c:v libx264 -crf 21 -preset veryfast -c:a aac -shortest "$R/${b}_SIDE-BY-SIDE.mp4"
done
echo "$(date +%T) STORY BUILD DONE: $*"
