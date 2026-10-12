#!/bin/zsh
cd /Users/wachas/Documents/higgs-purple/dub
nice -n 10 .venv/bin/python prep.py work_new3/ 2>&1 | grep -E "PREP DONE|Error"
nice -n 10 .venv/bin/python -u dubplan.py work_new3/ out/ 2>&1 | grep -E "OK|FAIL|Error"
echo "$(date +%T) UGC5 dubbed: $(ls out | grep -cE '^010ea465_(bn|ta|te|ml|or)\.mp4$')/5"
while ! grep -q "UGC FINISH DONE" feedback/ugc_finish.log; do sleep 15; done
A=post/superseded/replaced_ugc; v=65a0c520
[ -d work/$v ] && mv work/$v $A/work/
for d in deliver deliver_music; do find $d -name "*_$v.mp4" | while read f; do mkdir -p $A/$(dirname $f); mv "$f" $A/$f; done; done
python3 -c "import sys;sys.path.insert(0,'feedback');sys.argv=['x'];import assemble_fix as A;A.remux('010ea465')" >/dev/null
nice -n 10 .venv/bin/python post/render_post.py --ids 010ea465 --langs bn ta te ml or --jobs 2 --force 2>&1 | grep -E "FAIL|done:"
nice -n 10 .venv/bin/python post/add_audio.py --ids 010ea465 --force 2>&1 | grep -E "FAIL|DONE"
/Users/wachas/Documents/higgs-purple/dub/tools/pack.sh
echo "$(date +%T) UGC5 DONE"
