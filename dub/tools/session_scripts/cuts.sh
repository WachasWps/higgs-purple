#!/bin/bash
# usage: cuts.sh <id> -> prints scene cut times in source.mp4
/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg -hide_banner -nostdin -i /Users/wachas/Documents/higgs-purple/dub/work/$1/source.mp4 -an -vf "scale=180:-2,select='gt(scene,0.25)',showinfo" -f null - 2>&1 | grep -o 'pts_time:[0-9.]*' | cut -d: -f2 | tr '\n' ' '; echo
