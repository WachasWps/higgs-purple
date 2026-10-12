#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
IDS="d6c1e78e b876bd3c a135c7dc 751fe1db"
while ! grep -q "VOICE_ALL DONE" feedback/voice_all.log; do sleep 15; done
A=post/superseded/replaced_ugc
for v in 3d01d9fc 51440b1f; do
  [ -d work/$v ] && mv work/$v $A/work/
  for d in deliver deliver_music; do find $d -name "*_$v.mp4" | while read f; do mkdir -p $A/$(dirname $f); mv "$f" $A/$f; done; done
done
for v in ${=IDS}; do python3 -c "import sys;sys.path.insert(0,'feedback');sys.argv=['x'];import assemble_fix as A;A.remux('$v')" >/dev/null; done
nice -n 10 .venv/bin/python post/render_post.py --ids ${=IDS} --langs bn --jobs 2 --force 2>&1 | grep -E "FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids ${=IDS} --force 2>&1 | grep -E "FAIL|DONE"
echo "$(date +%T) BENGALI READY"
nice -n 10 .venv/bin/python post/render_post.py --ids ${=IDS} --langs ta te ml or --jobs 2 --force 2>&1 | grep -E "FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids ${=IDS} --force 2>&1 | grep -E "FAIL|DONE"
/Users/wachas/Documents/higgs-purple/dub/tools/pack.sh
echo "$(date +%T) UGC FINISH DONE"
