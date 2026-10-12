import json,sys,os
from PIL import Image,ImageDraw,ImageFont
base="/Users/wachas/Documents/higgs-purple/dub/feedback/script_audit"
out=sys.argv[1]
font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc",22)
for vid in sys.argv[2:]:
    m=json.load(open(f"{base}/{vid}/manifest.json"))
    shots=m["shots"]
    for ci in range(0,len(shots),5):
        chunk=shots[ci:ci+5]
        W=270*len(chunk); H=480*2+40
        im=Image.new("RGB",(W,H),"white"); d=ImageDraw.Draw(im)
        for i,s in enumerate(chunk):
            d.text((i*270+4,4),f"S{s['n']} {s['what'][:18]}",fill="black",font=font)
            for j,f in enumerate(s["frames"]):
                im.paste(Image.open(f"{base}/{vid}/{f}").convert("RGB"),(i*270,40+j*480))
            d.line([(i*270,0),(i*270,H)],fill="red",width=3)
        im.save(f"{out}/{vid}_{ci//5}.jpg",quality=85)
    print("====",vid,m.get("style"),[c["id"]+": "+c["description"] for c in m["cast"]])
    for s in shots: print(f"  S{s['n']} {s['start']}-{s['end']} {s['what']} lines={[l['id'] for l in s['lines']]}")
    L=m["lines"]
    for k,l in enumerate(L):
        slot=(L[k+1]["start"]-l["start"]-0.15) if k+1<len(L) else (l["end"]-l["start"]+0.5)
        print(f"  L{l['id']} {l['start']}-{l['end']} slot={slot:.2f} max={int(slot*2.4)} [{l['speaker']}] ({len(l['en'].split())}w) {l['en']}")
