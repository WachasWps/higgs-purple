"""Corrected keyframes via Higgsfield Nano Banana Pro (used while Codex is rate-limited). 2 credits each.

usage: python3 feedback/hf_keyframe.py <key> [<key> ...]   (prompts below; source frame feedback/hf_keys/<key>_src.png)
Output: feedback/codex/out/LEFT_<key>.png (+ job JSON in feedback/hf_keys/), ready for wan_gen.py.
"""
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
K = ROOT / "feedback" / "hf_keys"
REF = ROOT / "feedback" / "product_refs"
KEEP = ("Edit image 1 (a frame from a vertical ad). Keep EXACTLY the same scene, people (same face, identity, hair, clothes, "
        "skin tone), cartoon characters, poses, framing, background, lighting and style. Change ONLY: ")
JAR = (" Any night-cream jar must match image 2 exactly (short wide jar, royal-blue base, white label band, white lid, "
       "label text and layout exactly as image 2).")
SPOTS = ("her skin shows REALISTIC hyperpigmentation — soft-edged FLAT brown sun spots and uneven darker patches on the "
         "cheekbones, never round raised dots or chicken-pox marks")
P = {
 "7ea55172_S5": (["ps_tube_with_box.png"], KEEP + "the small colour wheel the tube mascot holds must be a CORRECT painter's "
   "colour wheel: PURPLE segment at the TOP and YELLOW directly OPPOSITE at the BOTTOM with a vertical arrow between them. "
   "The mascot is the exact tube from image 2 (wide translucent lavender cap ON at the bottom, no nozzle). No new text.",
   "The tube mascot walks along the ledge holding its shield and the small colour wheel; the woman smiles; gentle city "
   "motion; the colour wheel and tube stay exactly as in the first frame."),
 "7558fbf1_S7": (["knc_tub_clean.png"], KEEP + "replace the thick white blob of cream under her eye with a few small dabs of "
   "white night cream being massaged in by her fingertips, mostly absorbed, only a thin soft sheen; " + SPOTS + "." + JAR + " No new text.",
   "She massages the night cream in with gentle strokes until it disappears completely, no white residue; warm night light."),
 "715b1b5c_S7": (["knc_tub_clean.png"], KEEP + "replace the white cream blob on her cheek with a few small dabs of white night "
   "cream being massaged in, mostly absorbed, thin sheen only; " + SPOTS + "." + JAR + " No new text.",
   "She massages the cream in with gentle upward strokes until it is fully absorbed, no white residue; warm night light."),
 "23850d94_S1": (["knc_tub_clean.png"], KEEP + "remove the small cartoon dots/stickers on her cheek and instead " + SPOTS +
   ". Keep the professor jar mascot she holds exactly as it is (face on the lid, glasses)." + JAR + " No new text.",
   "She smiles softly at the camera holding the professor jar mascot, which adjusts its glasses; warm night light; the jar stays exactly as in the first frame."),
 "71e0977a_S1": (["knc_tub_clean.png"], KEEP + "keep the little cartoon dark-spot villain characters exactly, but underneath "
   "them " + SPOTS + " (no round dots on the skin itself)." + JAR + " No new text.",
   "The little cartoon dark-spot villains bounce and taunt on her cheek; she holds the jar mascot close; the jar stays exactly as in the first frame."),
}


def run(key):
    refs, prompt, _ = P[key]
    cmd = ["higgsfield", "generate", "create", "nano_banana_pro", "--prompt", prompt, "--aspect_ratio", "9:16",
           "--resolution", "2k", "--image", str(K / f"{key}_src.png")]
    for r in refs:
        cmd += ["--image", str(REF / r)]
    r = subprocess.run(cmd + ["--wait", "--wait-timeout", "10m", "--json"], capture_output=True, text=True)
    (K / f"{key}.json").write_text(r.stdout + r.stderr)
    try:
        url = json.loads(r.stdout)[0]["result_url"]
    except Exception:
        return f"{key}: FAILED {(r.stdout + r.stderr)[-300:]}"
    out = ROOT / "feedback" / "codex" / "out" / f"LEFT_{key}.png"
    subprocess.run(["curl", "-sfL", "-o", str(out.with_suffix('.dl')), url], check=True)
    subprocess.run(["/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg", "-v", "error", "-y", "-i", str(out.with_suffix('.dl')), str(out)], check=True)
    out.with_suffix('.dl').unlink()
    return f"{key}: OK"


if __name__ == "__main__":
    keys = sys.argv[1:] or list(P)
    with ThreadPoolExecutor(5) as ex:
        for m in ex.map(run, keys):
            print(m, flush=True)
