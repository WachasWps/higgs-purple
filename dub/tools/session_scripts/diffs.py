import subprocess, re, sys
FF="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"
SRC="/Users/wachas/Documents/higgs-purple/dub/feedback/user_clips"
for c in sys.argv[1].split(","):
    r=subprocess.run([FF,"-hide_banner","-nostats","-i",f"{SRC}/{c}.mp4","-vf","scale=160:-2,select='gte(scene,0)',metadata=print","-an","-f","null","-"],capture_output=True,text=True)
    ts=[];ss=[]
    for line in r.stderr.splitlines():
        m=re.search(r"pts_time:([\d.]+)",line)
        if m: ts.append(float(m.group(1)))
        m=re.search(r"scene_score=([\d.]+)",line)
        if m: ss.append(float(m.group(1)))
    # report runs above 0.02, and spikes
    out=[]
    i=0
    while i<len(ss):
        if ss[i]>0.025:
            j=i
            while j+1<len(ss) and ss[j+1]>0.025: j+=1
            pk=max(range(i,j+1),key=lambda k:ss[k])
            out.append(f"{ts[i]:.2f}-{ts[j]:.2f}(pk {ts[pk]:.2f}:{ss[pk]:.2f})")
            i=j+1
        else: i+=1
    print(c, " ".join(out))
