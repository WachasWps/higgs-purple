import json
from pathlib import Path
W = Path('/Users/wachas/Documents/higgs-purple/dub/work')
ids = '00b304b4 02bad3b3 23850d94 291827ba 33c29291 390113f1 3d01d9fc 46d965c9 51440b1f 595689d8 5fd50ab8 655a1328 65a0c520 715b1b5c'.split()
# ordered replacements (longest first)
R = [
 ('എസ്പിഎഫ് ഫിഫ്റ്റി, പിഎ ട്രിപ്പിൾ പ്ലസ്', 'SPF 50 PA+++'),
 ('എസ്പിഎഫ് ഫിഫ്റ്റി പിഎ ട്രിപ്പിൾ പ്ലസ്', 'SPF 50 PA+++'),
 ('ഗ്ലോ ഫ്യൂഷൻ ഫോർമുല', 'Glow Fusion Formula'),
 ('ഗ്ലോ ഫ്യൂഷനിൽ', 'Glow Fusion-ൽ'),
 ('ഗ്ലോ ഫ്യൂഷൻ', 'Glow Fusion'),
 ('ഡെർമ്ഡോക്', 'DERMDOC'),
 ('ടൂ പേഴ്സന്റ്', '2%'),
 ('ടു പെർസെന്റ്', '2%'),
 ('ഫോർ പെർസന്റ്', '4%'),
 ('നാല് പെർസെന്റ്', '4%'),
 ('നാല് ശതമാനം', '4%'),
 ('കോജിക് ആസിഡ്', 'Kojic Acid'),
 ('നിയാസിനാമൈഡ്', 'Niacinamide'),
 ('നിയാസിനമൈഡ്', 'Niacinamide'),
 ('ആൽഫ ആർബ്യൂട്ടിനും', 'Alpha Arbutin-നും'),
 ('ആൽഫ അർബുട്ടിൻ', 'Alpha Arbutin'),
 ('ആൽഫ ആർബുട്ടിൻ', 'Alpha Arbutin'),
 ('നൈറ്റ് ക്രീമിൽ', 'Night Cream-ൽ'),
 ('നൈറ്റ് ക്രീം', 'Night Cream'),
 ('സൺസ്ക്രീനിൽ', 'Sunscreen-ൽ'),
 ('സൺസ്ക്രീനും', 'Sunscreen-നും'),
 ('സൺസ്ക്രീൻ', 'Sunscreen'),
 ('ത്രീ എക്സ്പേർട്ട്', '3Xpert'),
 ('യൂവിഎ', 'UVA'),
 ('യൂവിബി', 'UVB'),
 ('നമ്പർ വൺ', 'നമ്പർ 1'),
 ('നമ്പർ ടൂ', 'നമ്പർ 2'),
 ('ലെസൺ വൺ', 'ലെസൺ 1'),
 ('ലെസൺ ടൂ', 'ലെസൺ 2'),
]
for i in ids:
    plan = json.loads((W/i/'plan.json').read_text())
    lines = {}
    for l in plan['lines']:
        t = l.get('ml', '')
        if l.get('keep_original') or not t.strip():
            continue
        c = t
        for a, b in R:
            c = c.replace(a, b)
        lines[str(l['id'])] = c
        if c != t:
            print(i, l['id'], '|', t, '->', c)
    (W/i/'captions_ml.json').write_text(json.dumps({'language': 'ml', 'lines': lines}, ensure_ascii=False, indent=1) + '\n')
