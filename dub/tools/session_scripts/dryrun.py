import json, math, sys
sys.path.insert(0, '/Users/wachas/Documents/higgs-purple/dub')
sys.path.insert(0, '/Users/wachas/Documents/higgs-purple/dub/tools')
from validate_plan import count, CPS_LINE, CPS_TOTAL
from changes import CHANGES
root = '/Users/wachas/Documents/higgs-purple/dub'
for vid, ch in CHANGES.items():
    p = json.load(open(f'{root}/work/{vid}/plan.json'))
    tot = {k: [0, 0.0] for k in CPS_TOTAL}
    for l in p['lines']:
        slot = l['max_end'] - l['start']
        new = ch.get(l['id'])
        for k in CPS_TOTAL:
            t = new[k] if new else l[k]
            n = count(t)
            tot[k][0] += n; tot[k][1] += slot
            if new:
                old = count(l[k])
                b = math.floor(slot * CPS_LINE[k])
                flag = 'OVER' if n > b else ''
                print(f"{vid} L{l['id']} {k}: {n}/{b} (old {old}) slot {slot:.2f} {flag}")
    print(vid, 'totals', {k: f"{n}/{math.floor(s*CPS_TOTAL[k])}" for k, (n, s) in tot.items()})
