import json, math, sys
sys.path.insert(0, '/Users/wachas/Documents/higgs-purple/dub')
from validate_plan import count, CPS_LINE, CPS_TOTAL
p = json.load(open(sys.argv[1]))
tot = {'bn':[0,0.0],'or':[0,0.0]}
for l in p['lines']:
    slot = l['max_end'] - l['start']
    row = [str(l['id']), f"{slot:.2f}"]
    for k in ('bn','or'):
        n = count(l[k]); b = math.floor(slot*CPS_LINE[k])
        tot[k][0]+=n; tot[k][1]+=slot
        row.append(f"{k} {n}/{b}")
    print('  '.join(row))
for k,(n,s) in tot.items():
    B = math.floor(s*CPS_TOTAL[k]); print(k, n, '/', B, 'target', round(B*0.95))
