"""Generate dubbed lines with Indic-Mio (Apache-2.0) in the original creator's voice.

Indic-Mio predicts MioCodec content tokens from text; the codec then renders them with the
speaker "global embedding" taken from the creator's original (Demucs-isolated) vocal.
Several takes are sampled per line and the best one is kept: lowest character error rate
on a Whisper back-transcription, then closest fit to the timing slot.

Usage: .venv/bin/python gen_mio.py <script.json> <out_dir> [takes]
"""
import json
import sys
import unicodedata
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")
import librosa
import numpy as np
import soundfile as sf
import torch
import whisper
from miocodec import MioCodecModel, load_audio
from transformers import AutoModelForCausalLM, AutoTokenizer

ROOT = Path(__file__).parent
REF_VOCALS = ROOT / "analysis/stems/htdemucs/audio_orig/vocals.wav"
SPEECH_OFFSET, CODEBOOK = 151669, 12800
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


def cer(ref, hyp):
    norm = lambda s: [c for c in unicodedata.normalize("NFC", s) if c.isalnum()]
    r, h = norm(ref), norm(hyp)
    d = list(range(len(h) + 1))
    for i in range(1, len(r) + 1):
        prev, d[0] = d[0], i
        for j in range(1, len(h) + 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (r[i - 1] != h[j - 1]))
    return d[len(h)] / max(len(r), 1)


def main(script_path, out_dir, takes=3):
    script = json.loads(Path(script_path).read_text())
    lang = script["language"]
    out = Path(out_dir)
    (out / "takes").mkdir(parents=True, exist_ok=True)

    tok = AutoTokenizer.from_pretrained("SPRINGLab/Indic-Mio", trust_remote_code=True)
    lm = AutoModelForCausalLM.from_pretrained("SPRINGLab/Indic-Mio", torch_dtype=torch.float32).to(DEVICE).eval()
    codec = MioCodecModel.from_pretrained("Aratako/MioCodec-25Hz-24kHz").eval().to(DEVICE)
    sr = codec.config.sample_rate
    asr = whisper.load_model("large-v3-turbo")

    # Speaker identity from the first ~10 s of the creator's isolated voice.
    ref = load_audio(str(REF_VOCALS), sample_rate=sr)[..., : 10 * sr].to(DEVICE)
    with torch.no_grad():
        spk = codec.encode(ref, return_content=False, return_global=True).global_embedding

    for line in script["lines"]:
        text = line["tts_text"] if "tts_text" in line else line[lang]
        if line.get("tag"):
            text = f"{text} <{line['tag']}>"
        prompt = tok.apply_chat_template([{"role": "user", "content": text}], tokenize=False, add_generation_prompt=True)
        inputs = tok(prompt, return_tensors="pt").to(DEVICE)
        slot = line["max_end"] - line["start"]

        cands = []
        for k in range(int(takes)):
            torch.manual_seed(1000 * line["id"] + k)
            with torch.no_grad():
                gen = lm.generate(**inputs, max_new_tokens=600, do_sample=True, temperature=0.8, top_p=0.9)
            codes = [t - SPEECH_OFFSET for t in gen[0, inputs["input_ids"].shape[1]:].tolist()
                     if SPEECH_OFFSET <= t < SPEECH_OFFSET + CODEBOOK]
            if not codes:
                continue
            with torch.no_grad():
                wav = codec.decode(global_embedding=spk, content_token_indices=torch.tensor(codes, device=DEVICE))
            wav = wav.squeeze().float().cpu().numpy()
            path = out / "takes" / f"line_{line['id']}_take{k}.wav"
            sf.write(path, wav, sr)
            speech, _ = librosa.effects.trim(wav, top_db=35)
            dur = len(speech) / sr
            heard = asr.transcribe(str(path), language=lang, fp16=False)["text"].strip()
            score = cer(line[lang], heard)
            cands.append((score, max(0.0, dur / slot - 1.0), k, dur, heard, path))
            print(f"  [{line['id']}.{k}] cer {score:.2f}  {dur:.2f}s/{slot:.2f}s  heard: {heard}", flush=True)

        # Intelligibility first (bucketed so tiny CER differences don't override a big timing win), then fit.
        best = min(cands, key=lambda c: (round(c[0] / 0.08), c[1]))
        sf.write(out / f"line_{line['id']}.wav", sf.read(best[5])[0], sr)
        print(f"line {line['id']}: kept take {best[2]} (cer {best[0]:.2f}, {best[3]:.2f}s for {slot:.2f}s slot)\n", flush=True)


if __name__ == "__main__":
    main(*sys.argv[1:])
