import subprocess, sys, math, json
FF="/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg"; FP="/opt/homebrew/opt/ffmpeg-full/bin/ffprobe"
SRC="/Users/wachas/Documents/higgs-purple/dub/feedback/user_clips"
OUT="/Users/wachas/Documents/higgs-purple/dub/tools/catalog"
step=float(sys.argv[2]) if len(sys.argv)>2 else 0.5
w=int(sys.argv[3]) if len(sys.argv)>3 else 180
suffix=sys.argv[4] if len(sys.argv)>4 else ""
start=float(sys.argv[5]) if len(sys.argv)>5 else 0.0
end=float(sys.argv[6]) if len(sys.argv)>6 else None
for c in sys.argv[1].split(","):
    f=f"{SRC}/{c}.mp4"
    d=float(subprocess.check_output([FP,"-v","error","-show_entries","format=duration","-of","csv=p=0",f]).decode().strip())
    e = end if end else d
    n=int(math.floor((e-start-0.01)/step))+1
    cols=min(n,10); rows=math.ceil(n/cols)
    vf=(f"fps=1/{step}:start_time=0,scale={w}:-2,"
        f"drawtext=text='%{{pts\\:flt\\:0}}':x=4:y=4:fontsize=18:fontcolor=yellow:box=1:boxcolor=black@0.6,"
        f"tile={cols}x{rows}:padding=2")
    # seek accurately; fps filter samples frames at step intervals starting at start
    cmd=[FF,"-y","-v","error","-ss",str(start),"-i",f,"-t",str(e-start),"-vf",
         f"fps={1/step}:round=near,scale={w}:-2,drawtext=text='%{{expr\\:{start}+n*{step}}}':x=3:y=3:fontsize=14:fontcolor=yellow:box=1:boxcolor=black@0.6,tile={cols}x{rows}:padding=2",
         "-frames:v","1","-q:v","4",f"{OUT}/{c}{suffix}.jpg"]
    r=subprocess.run(cmd,capture_output=True,text=True)
    print(c, n, r.stderr[-300:])
