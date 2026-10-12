"""Overlapped finishing pipeline: one dub lane (single ML process — Mac limit) + two render lanes.

Per video:  text ready (feedback/text_done/<group>) -> dub lane: re-voice queued lines (or dub a rebuilt ad from
scratch) -> work/<id>/dub2.ok -> render lane: remux fixed picture -> render_post (5 langs) -> add_audio -> final.ok.
usage: nohup nice -n 10 .venv/bin/python -u feedback/pipeline.py > feedback/pipeline.log 2>&1 &
"""
import json
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PY = str(ROOT / ".venv" / "bin" / "python")
GROUPS = {
    "ugc": "02bad3b3 3d01d9fc 46d965c9 51440b1f 65a0c520 784c77c5 a5c00002 caf29456 cd5a6fe8 dad2130b".split(),
    "ps": "00b304b4 291827ba 33c29291 5fd50ab8 655a1328 74495eba 7ea55172 c51221b6 ce849d3f e7e42eaf".split(),
    "knc": "23850d94 390113f1 595689d8 715b1b5c 71e0977a 7558fbf1 89697c77 906fbf3c bd3b8af7 f7ce58d4".split(),
    "ads": "4010f985 426b77bb a9be56d9 b4c787e1 c01adcce ce52c347 e9528636 eab38211 fb3fa838 fe7174d4".split(),
}
GROUP_OF = {v: g for g, ids in GROUPS.items() for v in ids}
FLAGS = ROOT / "feedback" / "text_done"
RENDER_LANES = 2


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def wd(v):
    return ROOT / "work" / v


def text_ready(v):
    return (FLAGS / GROUP_OF[v]).exists()


def pass1_running():
    r = subprocess.run(["pgrep", "-f", "redub.py"], capture_output=True, text=True)
    return bool(r.stdout.strip())


def queue_lines(v):
    """Merge the text pass's queue (and, for UGC, every line: calmer delivery) into redub.json."""
    rd, rt = wd(v) / "redub.json", wd(v) / "redub_text.json"
    cur = set(json.loads(rd.read_text())["lines"]) if rd.exists() else set()
    if rt.exists():
        cur |= set(json.loads(rt.read_text())["lines"])
    if GROUP_OF[v] == "ugc":
        plan = json.loads((wd(v) / "plan.json").read_text())
        cur |= {l["id"] for l in plan["lines"] if not l.get("keep_original")}
    rd.write_text(json.dumps({"lines": sorted(cur)}))
    return sorted(cur)


def dub_lane():
    order = GROUPS["ugc"] + GROUPS["ps"] + GROUPS["knc"] + GROUPS["ads"]
    while True:
        pending = [v for v in order if not (wd(v) / "dub2.ok").exists()]
        if not pending:
            log("DUB LANE DONE")
            return
        if pass1_running():
            time.sleep(20)
            continue
        ready = [v for v in pending if text_ready(v)]
        if not ready:
            time.sleep(20)
            continue
        v = ready[0]
        t0 = time.time()
        if GROUP_OF[v] == "ads":
            if not (wd(v) / "plan.ok").exists():
                log(f"[{v}] ad plan not validated yet — skipping for now")
                order.remove(v)
                order.append(v)
                time.sleep(5)
                continue
            code = ("import sys; sys.path.insert(0, '.'); from pathlib import Path; from dubplan import Engine; "
                    f"Engine().process(Path('work/{v}'), Path('out'))")
            r = subprocess.run(["nice", "-n", "10", PY, "-c", code], cwd=ROOT, capture_output=True, text=True)
        else:
            lines = queue_lines(v)
            if not lines:
                (wd(v) / "dub2.ok").write_text("nothing to re-dub")
                log(f"[{v}] no lines to re-dub")
                continue
            r = subprocess.run(["nice", "-n", "10", PY, "redub.py", v], cwd=ROOT, capture_output=True, text=True)
        ok = r.returncode == 0 and "FAILED" not in r.stdout
        tail = (r.stdout + r.stderr).strip().splitlines()[-1:] if not ok else []
        if ok:
            (wd(v) / "dub2.ok").write_text(time.strftime("%H:%M"))
        log(f"[{v}] dub {'OK' if ok else 'FAILED'} ({time.time() - t0:.0f}s) {tail}")
        if not ok:
            order.remove(v)   # don't loop on a broken one; report it
            (wd(v) / "dub2.failed").write_text("\n".join((r.stdout + r.stderr).splitlines()[-30:]))


def render_one(v):
    t0 = time.time()
    steps = [
        [PY, "feedback/assemble_fix.py", v, "--remux"] if not (wd(v) / "source_fixed.mp4").exists()
        else [PY, "-c", f"import sys; sys.path.insert(0,'feedback'); import assemble_fix as A; A.remux('{v}')"],
        [PY, "post/render_post.py", "--ids", v, "--force", "--jobs", "1"],
        [PY, "post/add_audio.py", "--ids", v, "--force", "--jobs", "2"],
    ]
    for cmd in steps:
        r = subprocess.run(["nice", "-n", "10"] + cmd, cwd=ROOT, capture_output=True, text=True)
        if r.returncode != 0:
            (wd(v) / "final.failed").write_text((r.stdout + r.stderr)[-3000:])
            log(f"[{v}] RENDER FAILED at {cmd[1]}")
            return
    (wd(v) / "final.ok").write_text(time.strftime("%H:%M"))
    done = sum((wd(x) / "final.ok").exists() for x in GROUP_OF)
    log(f"[{v}] FINAL OK ({time.time() - t0:.0f}s)  [{done}/{len(GROUP_OF)} videos]")


def render_lane():
    busy = set()
    lock = threading.Lock()

    def run(v):
        try:
            render_one(v)
        finally:
            with lock:
                busy.discard(v)

    with ThreadPoolExecutor(RENDER_LANES) as ex:
        while True:
            todo = [v for v in GROUP_OF if not (wd(v) / "final.ok").exists() and not (wd(v) / "final.failed").exists()]
            if not todo and not busy:
                log("RENDER LANE DONE")
                return
            with lock:
                ready = [v for v in todo if v not in busy and (wd(v) / "dub2.ok").exists() and text_ready(v)
                         and (wd(v) / "source_fixed.mp4").exists()]
                for v in ready[: max(0, RENDER_LANES - len(busy))]:
                    busy.add(v)
                    ex.submit(run, v)
            time.sleep(15)


if __name__ == "__main__":
    FLAGS.mkdir(exist_ok=True)
    t = threading.Thread(target=dub_lane, daemon=True)
    t.start()
    render_lane()
    t.join()
