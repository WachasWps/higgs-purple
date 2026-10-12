# DERMDOC × Purplle ad engine

Read `../HANDOVER.md` first (rules, pipeline, fix recipes), then `../PROJECT_HISTORY.md` (all client feedback + status, all 40 ad ids).
- Run scripts with `.venv/bin/python`; ffmpeg is `/opt/homebrew/opt/ffmpeg-full/bin/ffmpeg`.
- Mac limits: one ML (voice) job at a time, at most 3–5 renders.
- Never change the company end slate (post/assets/outro_*.mp4); it must end every video. CTA: "Shop at Purplle.com".
- PS tube: cap always on, never a nozzle. Female voices only. General Ads English only. Never say "KNC". Don't edit the colour wheel.
- No new AI generation or paid credits without showing the user the plan + cost first (Higgsfield credits are 0).
- After any change: render_post → add_audio → tools/pack.sh → check Final_Deliverables = 160 files → make_canva_kit.py for changed ids.
