#!/bin/zsh
# export each ad's cuts as soon as its rebuilt picture lands (newer than 00:59 and no build in progress for it)
cd /Users/wachas/Documents/higgs-purple/dub
M=/Users/wachas/Documents/higgs-purple/dub/tools/cuts_marker
touch -t 202610120059 $M
left=(4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1)
while (( ${#left} )); do
  for v in $left; do
    if [[ work/$v/source_fixed.mp4 -nt $M && ! -d work/$v/fix_tmp ]]; then
      .venv/bin/python post/export_cuts.py $v &
      left=(${left:#$v})
    fi
  done
  sleep 5
done
wait; echo "CUTS DONE"
