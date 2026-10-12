"""Hindi REVIEW cut of the re-scripted UGCs (internal: lets the team follow the script). Same picture + on-screen text
as the delivered cut, NO captions, Hindi voice (Kokoro hf_alpha, Hindi G2P) on the plan's line timings, plus our music
and SFX.  usage: .venv/bin/python post/review_hindi.py [<id> ...]   -> feedback/REVIEW_UGC_HINDI/UGC<n>_HINDI.mp4
"""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

sys.path.insert(0, str(Path(__file__).resolve().parent))
import add_audio as AA  # noqa: E402
import render_post as R  # noqa: E402

ROOT = R.ROOT
OUT = ROOT / "feedback" / "REVIEW_UGC_HINDI"
NAMES = {"d6c1e78e": "UGC1", "b876bd3c": "UGC2", "a135c7dc": "UGC3", "751fe1db": "UGC4", "010ea465": "UGC5"}
HI = {
    "d6c1e78e": ["आज की मॉर्निंग स्किनकेयर में पर्पल सनस्क्रीन।", "नियासिनामाइड, पर्पल टिंट, इंस्टेंट ग्लो।",
                 "कलर व्हील पर पर्पल पीले के उल्टा है, इसलिए डलनेस कटती है।",
                 "चार छोटे डॉट्स, फिर ब्लेंड। देखो, पर्पल गायब, नो व्हाइट कास्ट।", "धूप के लिए एस पी एफ फिफ्टी।",
                 "और ये ग्लो? इंस्टेंट। कोई फ़िल्टर नहीं।", "हल्का, इंडियन स्किन के लिए।",
                 "पहले डल, अब इंस्टेंट ग्लो।", "अब यही मेरी डेली सनस्क्रीन है।",
                 "पर्पल डॉट कॉम पर शॉप करो, बाद में थैंक यू बोलना!"],
    "b876bd3c": ["पर्पल सनस्क्रीन? मुझे लगा चेहरा ही पर्पल हो जाएगा।", "तो मैंने टेस्ट किया, नियासिनामाइड रिपेयर करता है।",
                 "ट्रिक ये है, कलर व्हील पर पर्पल पीले को काटता है।",
                 "लगाओ तो लैवेंडर, ब्लेंड किया, और गायब। ज़रा भी पर्पल नहीं!", "नियासिनामाइड से मज़बूत बैरियर,",
                 "एस पी एफ फिफ्टी, पी ए ट्रिपल प्लस।", "अब स्किन देखो, कितनी फ्रेश, इंस्टेंट ग्लो!",
                 "पहले डल, अब इंस्टेंट ग्लो।", "इंडियन स्किन के लिए बनी।", "टेस्ट पास! पर्पल डॉट कॉम पर शॉप करो।"],
    "a135c7dc": ["अच्छा, कुछ सनस्क्रीन कितनी इरिटेटिंग होती हैं, है ना?", "व्हाइट कास्ट, चिपचिपी, ऊपर से ये गर्मी!",
                 "तो मैं ये डर्मडॉक सनस्क्रीन ट्राई कर रही हूँ, देखो, एकदम पर्पल!", "कलर व्हील पर पर्पल पीले को काटता है।",
                 "ब्लेंड करो, गायब, नो कास्ट।", "और कितनी हल्की लगती है, कमाल!", "साथ में एस पी एफ फिफ्टी, पी ए ट्रिपल प्लस।",
                 "पहले डल, अब इंस्टेंट ग्लो।", "पर्पल डॉट कॉम पर शॉप करो!"],
    "751fe1db": ["अच्छा, कुछ सनस्क्रीन कितनी इरिटेटिंग होती हैं, है ना?", "व्हाइट कास्ट, चिपचिपी, ऊपर से ये गर्मी!",
                 "तो मैं ये डर्मडॉक अल्ट्रावायलेट सनस्क्रीन ट्राई कर रही हूँ।", "और देखो, एकदम पर्पल!",
                 "कलर व्हील पर पर्पल पीले को काटता है।", "ब्लेंड करो, गायब।", "और कितनी हल्की लगती है, कमाल!",
                 "साथ में एस पी एफ फिफ्टी, पी ए ट्रिपल प्लस।", "पहले डल, अब इंस्टेंट ग्लो।", "पर्पल डॉट कॉम पर शॉप करो!"],
    "010ea465": ["यार, स्किन कुछ दिनों से इतनी डल थी, और अच्छी सनस्क्रीन ढूँढना? बड़ी मुश्किल!",
                 "फिर मिली ये डर्मडॉक अल्ट्रावायलेट सनस्क्रीन, और सच में, मैं फ़िदा हूँ।", "देखो, कितना प्यारा पर्पल टिंट!",
                 "कलर व्हील पर पर्पल पीले को काटता है।", "पूरी ब्लेंड हो जाती है, नो व्हाइट कास्ट, कुछ नहीं।",
                 "स्किन कितनी फ्रेश और ग्लोई!", "साथ में एस पी एफ फिफ्टी, पी ए ट्रिपल प्लस।", "पहले डल, अब इंस्टेंट ग्लो।",
                 "रोज़ की सनस्क्रीन, पर्पल डॉट कॉम पर शॉप करो!"],
}
SR = 24000


def voice(vid, dur):
    from kokoro import KPipeline
    pipe = KPipeline(lang_code="h", repo_id="hexgrad/Kokoro-82M")
    lines = json.loads((ROOT / "work" / vid / "plan.json").read_text())["lines"]
    track = np.zeros(int((dur + 1) * SR), np.float32)
    for l, t in zip(lines, HI[vid]):
        slot = l["max_end"] - l["start"]
        sp = 1.1
        for _ in range(3):
            a = np.concatenate([np.asarray(x.numpy() if hasattr(x, "numpy") else x, np.float32)
                                for _, _, x in pipe(t, voice="hf_alpha", speed=sp)])
            nz = np.nonzero(np.abs(a) > 0.01)[0]
            a = a[max(0, nz[0] - 240): nz[-1] + 1200] if len(nz) else a
            if len(a) / SR <= slot or sp >= 1.35:
                break
            sp = min(1.35, sp * len(a) / SR / slot + 0.03)
        i = int(l["start"] * SR)
        track[i:i + len(a)] += a[: len(track) - i]
    return track[: int(dur * SR)]


def main(ids):
    OUT.mkdir(parents=True, exist_ok=True)
    beds = {k: np.load(AA.CACHE / f"bed_{k}.npy") for k in ("uv_sunscreen", "kojic_night_cream")}
    bank = AA.sfx_bank()
    for vid in ids:
        job, why = R.prepare(vid, "bn")
        if not job:
            print(vid, "skip:", why)
            continue
        # picture: graphics only (drop the Bengali caption layers 200-202)
        ass = job.ass_path.read_text(encoding="utf-8").splitlines()
        keep = [ln for ln in ass if not (ln.startswith("Dialogue: 20") and ln.split(",")[0].endswith(("200", "201", "202")))]
        job.ass_path.write_text("\n".join(keep) + "\n", encoding="utf-8")
        tmp = OUT / f"_{vid}_pic.mp4"
        subprocess.run([R.FFMPEG, "-v", "error", "-y", *R.inputs(job), "-filter_complex", R.filter_graph(job, False),
                        "-map", "[v]", "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", str(tmp)], check=True)
        dur = job.dur
        vo = voice(vid, dur)
        vo48 = np.interp(np.arange(int(dur * AA.SR)) / AA.SR, np.arange(len(vo)) / SR, vo).astype(np.float32)
        product, sfx = AA.build(vid, dur, bank)
        bed = beds[product][: int(dur * AA.SR)].copy()
        n = min(len(bed), len(vo48), len(sfx))
        talk = np.convolve(np.abs(vo48[:n]), np.ones(4800) / 4800, mode="same") > 0.01   # duck music under the voice
        mix = bed[:n] * np.where(talk, 0.35, 0.8)[:, None] + sfx[:n] + (vo48[:n] * 1.6)[:, None]
        mix = np.clip(mix / max(1.0, np.abs(mix).max() / 0.89), -1, 1)
        wav = OUT / f"_{vid}.wav"
        sf.write(wav, mix, AA.SR)
        dst = OUT / f"{NAMES[vid]}_HINDI_review_{vid}.mp4"
        subprocess.run([R.FFMPEG, "-v", "error", "-y", "-i", str(tmp), "-i", str(wav), "-map", "0:v", "-map", "1:a",
                        "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", str(dst)], check=True)
        tmp.unlink()
        wav.unlink()
        print(vid, "->", dst.name, flush=True)


if __name__ == "__main__":
    main(sys.argv[1:] or list(NAMES))
