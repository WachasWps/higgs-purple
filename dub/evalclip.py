"""Quick QA for TTS clips: speech duration vs slot, pitch vs original creator, and a Whisper back-transcription."""
import json, sys, warnings
warnings.filterwarnings("ignore")
import librosa, numpy as np, whisper
clips_dir, script = sys.argv[1], json.load(open(sys.argv[2]))
ids = [int(i) for i in sys.argv[3].split(",")] if len(sys.argv) > 3 else [l["id"] for l in script["lines"]]
m = whisper.load_model("large-v3-turbo")
for l in script["lines"]:
    if l["id"] not in ids: continue
    y, sr = librosa.load(f"{clips_dir}/line_{l['id']}.wav", sr=24000)
    yt, _ = librosa.effects.trim(y, top_db=35)
    f0, _, _ = librosa.pyin(yt, fmin=80, fmax=500, sr=sr)
    f0 = f0[~np.isnan(f0)]
    slot = l["max_end"] - l["start"]
    r = m.transcribe(f"{clips_dir}/line_{l['id']}.wav", language=script["language"], fp16=False)
    print(f"[{l['id']}] speech {len(yt)/sr:.2f}s / slot {slot:.2f}s (x{len(yt)/sr/slot:.2f}) | F0 med {np.median(f0):.0f}Hz range {np.percentile(f0,90)/np.percentile(f0,10):.2f}x")
    print(f"    want: {l[script['language']]}\n    heard: {r['text'].strip()}")
