import json, math, sys
sys.path.insert(0, sys.argv[1]); from new import NEW
PUNCT=set(",.?!।"); J={"‌","‍"}
CT={"bn":13.0,"or":12.5}; CL={k:round(v*17/14.5,1) for k,v in CT.items()}
def count(t): return sum(1 for c in t if not c.isspace() and c not in PUNCT and c not in J)
for vid, d in NEW.items():
    p=json.load(open(f'/Users/wachas/Documents/higgs-purple/dub/work/{vid}/plan.json'))
    tot={k:[0,0.0] for k in CT}
    print('##',vid)
    for l in p['lines']:
        slot=l['max_end']-l['start']; row=[]
        for k in CT:
            t=d.get(l['id'],{}).get(k,l[k]); n=count(t); b=math.floor(slot*CL[k])
            tot[k][0]+=n; tot[k][1]+=slot
            row.append(f"{k} {n}/{b} ({100*(b-n)/b:+.0f}%)")
        print(l['id'], '  '.join(row))
    for k,(n,s) in tot.items():
        b=math.floor(s*CT[k]); print(' ',k,'total',n,'/',b, f"{100*(b-n)/b:.1f}% under")
