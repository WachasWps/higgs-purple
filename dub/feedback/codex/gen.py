"""Generate keyframes with Codex CLI image generation, a few in parallel.

usage: gen.py <id> [<id> ...]   (ids from library.json "models" or "clips"); --jobs N (default 3); --force
Outputs out/<id>.png; logs/<id>.log. Model-identity refs (out/<model>.png) are attached automatically.
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

HERE = Path(__file__).resolve().parent
LIB = json.loads((HERE / "library.json").read_text())


def entry(i):
    return LIB["models"].get(i) or LIB["clips"][i]


def run(i, force=False):
    out = HERE / "out" / f"{i}.png"
    if out.exists() and not force:
        return f"{i}: exists"
    e = entry(i)
    refs = list(e.get("refs", []))
    model = e.get("model")
    if model:
        refs.append(f"out/{model}.png")
    extra = e.get("fix", "")
    ref_note = ""
    if refs:
        ref_note = ("Attached reference images: " + ", ".join(refs) +
                    ". Product photos are the ground truth for packaging; the out/*_model_ref.png image is the identity "
                    "reference for the woman — keep the SAME face, hair and skin tone.\n")
    prompt = (f"Read CODEX_BRIEF.md in this folder first and follow it strictly.\n{ref_note}"
              f"TASK: generate ONE photorealistic vertical 9:16 keyframe image:\n{e['prompt']}\n{extra}\n"
              f"Use your image generation tool (pass the reference images to it), then copy the generated file to "
              f"out/{i}.png. Reply only with the saved path.")
    (HERE / "prompts" / f"{i}.txt").write_text(prompt)
    cmd = ["codex", "exec", "--skip-git-repo-check", "-s", "workspace-write", "-m", "gpt-5.6-luna", "-c", "model_reasoning_effort=low", "-C", str(HERE)]   # smallest model: saves quota
    if refs:
        cmd += ["--image", ",".join(refs)]
    cmd.append("-")
    with open(HERE / "logs" / f"{i}.log", "w") as log:
        r = subprocess.run(cmd, input=prompt, text=True, stdout=log, stderr=subprocess.STDOUT, cwd=HERE)
    return f"{i}: {'OK' if out.exists() else 'FAILED rc=' + str(r.returncode)}"


def main():
    args = sys.argv[1:]
    jobs = 3
    force = "--force" in args
    if "--jobs" in args:
        jobs = int(args[args.index("--jobs") + 1])
        del args[args.index("--jobs"):args.index("--jobs") + 2]
    ids = [a for a in args if not a.startswith("--")]
    (HERE / "prompts").mkdir(exist_ok=True)
    (HERE / "logs").mkdir(exist_ok=True)
    (HERE / "out").mkdir(exist_ok=True)
    with ThreadPoolExecutor(jobs) as ex:
        for msg in ex.map(lambda i: run(i, force), ids):
            print(msg, flush=True)


if __name__ == "__main__":
    main()
