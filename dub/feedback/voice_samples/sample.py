import sys, numpy as np, soundfile as sf
from kokoro import KPipeline
lines = ["Dull, yellow-looking skin?", "Purple sits opposite yellow, so it helps cancel it out.",
         "Derm-doc Ultra Violet, with four percent Niacinamide and S P F fifty.",
         "It blends in fully. No white cast, just Instant Glow!", "Made for Indian skin tones."]
for lang in ("a", "h"):
    pipe = KPipeline(lang_code=lang, repo_id="hexgrad/Kokoro-82M")
    for voice in ("hf_alpha", "hf_beta"):
        audio = []
        for t in lines:
            for _, _, a in pipe(t, voice=voice, speed=1.0):
                audio.append(a.numpy() if hasattr(a, "numpy") else np.asarray(a))
            audio.append(np.zeros(int(24000 * 0.35), np.float32))
        sf.write(f"feedback/voice_samples/{voice}_{lang}.wav", np.concatenate(audio), 24000)
        print("wrote", voice, lang, flush=True)
