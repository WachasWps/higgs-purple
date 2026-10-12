"""Turn Codex keyframes into 5 s Wan 3.0 clips on Higgsfield (480p, 9:16, no audio — 5 credits each).

usage: wan_gen.py [CLIP ...] [--jobs 4]   (default: every needs_wan clip in feedback/wan_jobs.json without a clip yet)
Output: feedback/clips/<CLIP>.mp4 (what assemble_fix.py uses), job JSON in feedback/clips/jobs/.
"""
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLIPS = ROOT / "feedback" / "clips"
JOBS = json.loads((ROOT / "feedback" / "wan_jobs.json").read_text())


def gen(j):
    cid = j["clip"]
    out = CLIPS / f"{cid}.mp4"
    if out.exists():
        return f"{cid}: exists"
    t0 = time.time()
    r = subprocess.run(["higgsfield", "generate", "create", "wan3_0", "--prompt", j["motion_prompt"],
                        "--start-image", str(ROOT / j["keyframe"]), "--resolution", "480p", "--duration", "5",
                        "--aspect_ratio", "9:16", "--generate_audio", "false", "--wait", "--wait-timeout", "20m",
                        "--json"], capture_output=True, text=True)
    (CLIPS / "jobs" / f"{cid}.json").write_text(r.stdout + r.stderr)
    try:
        url = json.loads(r.stdout)[0]["result_url"]
    except Exception:
        return f"{cid}: FAILED ({(r.stdout + r.stderr).strip()[-200:]})"
    subprocess.run(["curl", "-sfL", "-o", str(out), url], check=True)
    return f"{cid}: OK ({time.time() - t0:.0f}s)"


def main():
    args = sys.argv[1:]
    jobs = int(args[args.index("--jobs") + 1]) if "--jobs" in args else 4
    names = [a for a in args if not a.startswith("--") and not a.isdigit()]
    todo = [j for j in JOBS if (j["clip"] in names if names else j["needs_wan"])]
    (CLIPS / "jobs").mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(jobs) as ex:
        for msg in ex.map(gen, todo):
            print(time.strftime("%H:%M:%S"), msg, flush=True)
    print("WAN DONE", flush=True)


if __name__ == "__main__":
    main()
