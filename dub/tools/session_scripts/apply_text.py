import json, os, sys
sys.path.insert(0, '/Users/wachas/Documents/higgs-purple/dub/tools')
from changes import CHANGES, CAPTIONS
root = '/Users/wachas/Documents/higgs-purple/dub/work'
LANGS = ('bn', 'ta', 'te', 'ml', 'or')
NOTE = {
 "23850d94": "Text pass (client feedback EDL): L4 now 'Lesson two: brighter skin. Three: even-looking tone.' so Alpha Arbutin gets its beat; L6 says the full product name instead of 'KNC' (dubs say 'DERMDOC Kojic Acid Night Cream' without 'two percent' to fit the 2.96 s slot with 'Class dismissed').",
 "595689d8": "Text pass (client feedback EDL): L9 is now the product name 'DERMDOC 2% Kojic Acid Night Cream.'; dubs say 'DERMDOC Kojic Acid Night Cream' (no 'two percent') to fit the 1.84 s slot.",
 "715b1b5c": "Text pass (client feedback EDL): L8 hedged to 'more even-looking'; L9 is now the product name ('overnight brightener' moved to an on-screen super); dubs say 'DERMDOC Kojic Acid Night Cream' without 'two percent' because this video already runs at max tempo.",
 "71e0977a": "Text pass (client feedback EDL): L5 says the full product name instead of 'KNC' plus a shorter tagline; dubs say 'DERMDOC Kojic Acid Night Cream' (no 'two percent') to fit the 2.94 s slot with the tagline.",
 "7558fbf1": "Text pass (client feedback EDL): L8 is now 'DERMDOC 2% Kojic Acid Night Cream.' in full in every dub ('Overnight Brightener' is an on-screen super at 11.4 s).",
 "89697c77": "Text pass (client feedback EDL): L9 drops the 'Sleep to glow' tagline for the product name; dubs say 'DERMDOC Kojic Acid Night Cream' (Acid restored; 'two percent' cannot fit the 2.12 s slot in any language).",
 "906fbf3c": "Text pass (client feedback EDL): L8 drops 'Sleep to glow' (baked on the end shot) so every dub says the full 'DERMDOC 2% Kojic Acid Night Cream'.",
 "f7ce58d4": "Text pass (client feedback EDL): L2 'Team KNC' -> 'Night team' (never 'KNC').",
}

def dump_atomic(path, obj, indent, trailing_nl):
    tmp = path + '.tmp_textpass'
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
        if trailing_nl:
            f.write('\n')
    os.replace(tmp, path)

def style(path):
    raw = open(path, encoding='utf-8').read()
    second = raw.split('\n')[1] if '\n' in raw else ''
    indent = (len(second) - len(second.lstrip(' '))) or None if raw.startswith('{\n') else None
    return indent, raw.endswith('\n')

for vid, ch in CHANGES.items():
    pp = f'{root}/{vid}/plan.json'
    indent, nl = style(pp)
    plan = json.load(open(pp, encoding='utf-8'))
    byid = {l['id']: l for l in plan['lines']}
    for lid, new in ch.items():
        l = byid[lid]
        for k, v in new.items():
            l[k] = v
    if NOTE.get(vid) and NOTE[vid] not in plan.get('notes', ''):
        plan['notes'] = (plan.get('notes', '') + ' ' + NOTE[vid]).strip()
    dump_atomic(pp, plan, indent or 1, nl)
    # captions
    for L in LANGS:
        cp = f'{root}/{vid}/captions_{L}.json'
        ci, cnl = style(cp)
        cap = json.load(open(cp, encoding='utf-8'))
        for lid, per in CAPTIONS[vid].items():
            cap['lines'][str(lid)] = per[L]
        dump_atomic(cp, cap, ci or 1, cnl)
    # redub_text.json (merge)
    rp = f'{root}/{vid}/redub_text.json'
    have = json.load(open(rp))['lines'] if os.path.exists(rp) else []
    ids = sorted(set(have) | set(ch))
    dump_atomic(rp, {"lines": ids}, None, False)
    print(vid, 'plan indent', indent, 'lines', sorted(ch), '-> redub_text', ids)
