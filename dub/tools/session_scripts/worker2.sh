#!/bin/zsh
# second redub worker: takes the DUB queue from the end; skips videos already done or currently being redubbed by script2
cd /Users/wachas/Documents/higgs-purple/dub
Q=($(python3 -c "import json;A=set('4010f985 c01adcce fe7174d4 fb3fa838 ce52c347 a9be56d9 426b77bb eab38211 e9528636 b4c787e1'.split());print(' '.join(reversed([v for v in json.load(open('feedback/script_audit/final_changes.json')) if v not in A])))"))
for v in $Q; do
  left=$(python3 -c "import json;print(len(json.load(open('work/$v/redub.json'))['lines']))")
  [[ $left == 0 ]] && { echo "$(date +%T) w2 stop at $v (done already)"; break; }
  pgrep -f "redub.py $v" >/dev/null && { echo "$(date +%T) w2 stop at $v (script2 on it)"; break; }
  r=$(nice -n 10 .venv/bin/python redub.py $v 2>&1 | grep -E "REDUB OK|FAILED|Error" | tail -1); echo "$(date +%T) w2 redub $v: $r"
done
echo "W2 DONE"
