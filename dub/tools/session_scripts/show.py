import json, sys
root = '/Users/wachas/Documents/higgs-purple/dub'
vid = sys.argv[1]
p = json.load(open(f'{root}/work/{vid}/plan.json'))
print('CAST', [(c['id'], c['role']) for c in p['cast']])
for l in p['lines']:
    print(f"L{l['id']} {l['speaker']} {l['start']}-{l['end']} max {l['max_end']} tag={l['tag']} ko={l['keep_original']} | {l['en']}")
    if '-v' in sys.argv:
        for k in ('bn','ta','te','ml','or'):
            print('    ', k, l[k])
print('NOTES', p.get('notes'))
g = json.load(open(f'{root}/work/{vid}/graphics.json'))
print('GRAPHICS caption_y', g.get('caption_y'), 'moves', g.get('caption_moves'))
for i, e in enumerate(g['elements']):
    print('  ', i, json.dumps(e, ensure_ascii=False))
print('GNOTES', g.get('notes'))
