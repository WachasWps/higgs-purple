import json,sys
id=sys.argv[1]
c=json.load(open(f'work/{id}/captions.json'))
print(' '.join(f"{w['w']}@{w['s']:.2f}" for w in c['words']))
print('last word end', c['words'][-1]['e'])
