import subprocess, json, glob, re, collections
from concurrent.futures import ThreadPoolExecutor
FF="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"; FP="/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"
files=sorted(glob.glob("Final_Deliverables/**/*.mp4", recursive=True))
def check(f):
    o=json.loads(subprocess.run([FP,"-v","error","-print_format","json","-show_streams","-show_format",f],capture_output=True,text=True).stdout)
    v=next(s for s in o["streams"] if s["codec_type"]=="video"); a=[s for s in o["streams"] if s["codec_type"]=="audio"]
    dur=float(o["format"]["duration"]); main=dur-5.0
    r=subprocess.run([FF,"-v","info","-t",f"{main:.2f}","-i",f,"-vf","blackdetect=d=0.4:pix_th=0.08,freezedetect=n=0.002:d=3.0","-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
    blacks=re.findall(r"black_start:([\d.]+) black_end:([\d.]+)",r)
    freezes=re.findall(r"freeze_start: ([\d.]+)",r)
    I=re.findall(r"I:\s+(-?[\d.]+) LUFS",r)
    return dict(f=f, w=v["width"], h=v["height"], fps=v["r_frame_rate"], dur=round(dur,2), audio=len(a)>0,
                lufs=float(I[-1]) if I else None, blacks=blacks, freezes=freezes)
with ThreadPoolExecutor(4) as ex: res=list(ex.map(check, files))
json.dump(res, open("feedback/final_qc.json","w"), indent=1)
probs=[r for r in res if (r["w"],r["h"])!=(1080,1920) or not r["audio"] or r["blacks"] or r["freezes"] or (r["lufs"] is not None and not -20<=r["lufs"]<=-10)]
print("checked", len(res), "| 1080x1920:", sum((r['w'],r['h'])==(1080,1920) for r in res), "| audio:", sum(r['audio'] for r in res))
lu=[r["lufs"] for r in res if r["lufs"] is not None]; print("loudness LUFS range", min(lu), max(lu))
print("files with issues:", len(probs))
for r in probs: print(" ", r["f"].split("/",1)[1][:95], r["dur"], "LUFS", r["lufs"], "black", r["blacks"][:2], "freeze", r["freezes"][:3])
# same video across languages -> same duration
by=collections.defaultdict(list)
for r in res:
    vid=re.sub(r"_(Bengali_WB|Tamil_TN|Telugu_APTS|Malayalam_KL|Odia_Od|English)\.mp4$","",r["f"].split("/")[-1]); by[vid].append(r["dur"])
mism={k:v for k,v in by.items() if max(v)-min(v)>0.15}
print("videos:", len(by), "| language sets with duration mismatch:", len(mism), list(mism.items())[:3])
print("per-video language counts:", collections.Counter(len(v) for v in by.values()))
