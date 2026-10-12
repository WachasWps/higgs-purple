# Caption text brief — regional captions with English ingredient/brand names

The dubbed voice lines in `work/<id>/plan.json` (fields `bn`, `ta`, `te`, `ml`, `or`) spell English terms phonetically in
the regional script (the TTS needs that). On-screen CAPTIONS must instead show those terms in proper English (Latin
letters, digits), while everything else stays exactly as dubbed, in the regional script.

For your language `<L>` and each assigned video, write `work/<id>/captions_<L>.json`:
```json
{"language": "<L>", "lines": {"1": "<caption text for line 1>", "2": "...", ...}}
```
- One entry per plan line id that has `<L>` text (skip `keep_original` lines).
- Take the line's `<L>` text and ONLY swap these terms (whatever their spelling in the regional script) to English:
  DERMDOC, Honest Science, Niacinamide, Kojic Acid (Kojic), Alpha Arbutin, Glow Fusion Formula, 3Xpert, Night Cream,
  Ultra Violet, Sunscreen, SPF, PA+++, UVA, UVB, and numbers/percentages as digits: "চার পার্সেন্ট"/"four percent" → 4%,
  "two percent" → 2%, "fifty" in "SPF fifty" → 50, "triple plus" → +++  (so "এসপিএফ ফিফটি, পিএ ট্রিপল প্লাস" →
  "SPF 50 PA+++").
  Capitalise as shown (DERMDOC all caps; Niacinamide, Kojic Acid, Alpha Arbutin, Glow Fusion Formula title case).
- Keep every other word EXACTLY as in the dubbed `<L>` text (same words, same order, same script) — including other
  English loanwords like glow, white cast, dark spots, cream, routine (leave those in the regional script).
- Keep the line's punctuation. Don't translate, don't add or drop words.
- Grammatical suffixes glued to a term stay in the regional script attached after a hyphen-less join, e.g. Bengali
  "নিয়াসিনামাইডে" → "Niacinamide-এ", Tamil "நியாசினமைடு" → "Niacinamide", Malayalam "നിയാസിനമൈഡിന്റെ" → "Niacinamide-ന്റെ".

Validate: `python3 post/validate_captions.py work/<id>/captions_<L>.json` until OK. Write only captions_<L>.json files.
Reply: number of files written and 3 example before→after lines.
