import json,sys,math
sys.path.insert(0,'.')
from validate_plan import count, CPS_LINE
for vid in sys.argv[1:]:
    p=json.load(open(f'work/{vid}/plan.json'))
    print('=====',vid,p['style'],p['duration'])
    for l in p['lines']:
        slot=l['max_end']-l['start']
        print(f"L{l['id']} {l['speaker']} {l['start']}-{l['end']} max {l['max_end']} tag={l['tag']} ko={l['keep_original']} | {l['en']}")
        if l['keep_original']: continue
        for k in ['bn','ta','te','ml','or']:
            print(f"   {k} [{count(l[k])}/{math.floor(slot*CPS_LINE[k])}] {l[k]}")
    print('notes:',p.get('notes'))
    g=json.load(open(f'work/{vid}/graphics.json'))
    print('--- graphics caption_y',g.get('caption_y'),'moves',g.get('caption_moves'))
    for i,e in enumerate(g['elements']):
        print(' ',i,json.dumps(e,ensure_ascii=False))
    print(' notes:',g.get('notes'))
