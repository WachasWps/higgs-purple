import json,sys
id=sys.argv[1]
d=json.load(open(f'post/text_audit/{id}.json'))
for t in d:
    flag='*' if t.get('crop') else ' '
    print(f"{flag}{t['n']:3d} {t['start']:5.2f}-{t['end']:5.2f} box={[round(x,3) for x in t['box']]} {t['text']!r} var={t['variants'][:4]}")
