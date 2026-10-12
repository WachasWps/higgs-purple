import json, sys, subprocess
vid = sys.argv[1]
p = f'/Users/wachas/Documents/higgs-purple/dub/work/{vid}/graphics.json'
g = json.load(open(p))
code = sys.stdin.read()
exec(code, {'g': g, 'json': json})
out = '{' + f'"video_id": "{g["video_id"]}", "product": "{g["product"]}", "caption_y": {g["caption_y"]},\n'
if g.get('caption_moves'):
    out += ' "caption_moves": ' + json.dumps(g['caption_moves']) + ',\n'
out += ' "elements": [\n' + ',\n'.join('  ' + json.dumps(e, ensure_ascii=False) for e in g['elements']) + '\n ]'
extra = {k: v for k, v in g.items() if k not in ('video_id', 'product', 'caption_y', 'elements', 'caption_moves')}
for k, v in extra.items():
    out += f',\n {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}'
out += '}\n'
json.loads(out)
open(p, 'w').write(out)
print(out)
subprocess.run(['python3', '/Users/wachas/Documents/higgs-purple/dub/post/validate_graphics.py', p])
