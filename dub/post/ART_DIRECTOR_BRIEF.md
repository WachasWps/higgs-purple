# Art-director pass — make every video look like a premium paid ad before final render

The client rejected a frame where white cover boxes looked cheap. Your job: review rendered stills of each assigned
video and fix `work/<id>/graphics.json` until every frame looks polished, intentional and on-brand (like
`post/ref/sheet_1.png` / `sheet_2.png` — look at them first). Work dir: `/Users/wachas/Documents/higgs-purple/dub`.

## Loop per video
1. Render stills: dubbed video → `.venv/bin/python post/render_post.py --preview <id> <lang>` (use the language given
   to you); Hinglish ad (work/<id>/meta.json "kind":"ad") → `.venv/bin/python post/render_post.py --preview <id>`.
   Add `--times t1 t2 ...` to see the exact moments of EVERY element in graphics.json (each super, each cover/blur,
   before/after labels) — at least one still per element, mid-way through it. Stills land in `post/preview/`.
2. Read every still. Fix in graphics.json whatever looks bad:
   - text over faces/eyes/mouth, over the product label, over the key action, or fighting baked-in text → move it
     (position / x,y), shorten it, or delete it. Fewer, better supers beat more supers.
   - clutter: never two cards stacked/crowding; a super right next to a similar baked-in title → remove ours.
   - cover cards (pills with "mask"): the renderer blurs the garbled area (feathered) and draws the pill at natural
     size centred on the mask; if it still looks patchy, adjust the mask box, add "text_x","text_y" to place the pill
     in a cleaner spot, or use a plain {"type":"blur","box":{...}} with no text when the correct info is already
     shown elsewhere. Never leave visible garbled letters; never use big boxes.
   - captions colliding with baked-in bottom text → add a `caption_moves` window.
   - illegible text (low contrast) → move it to a calmer area.
3. Re-render the stills you changed and check again. Validate:
   `python3 post/validate_graphics.py work/<id>/graphics.json` → OK.
4. When the video looks right, create the approval marker: `touch work/<id>/graphics.approved`
   (a render queue picks approved videos up immediately — approve as soon as each one is done, don't batch).

Rules: never touch text printed on the product/packaging or its reflections; 3XPERT is a correct brand name;
claims stay hedged as written (no fairness/whitening, keep "looking"/"helps"). Only edit work/<id>/graphics.json and
create work/<id>/graphics.approved. Run at most ONE preview command at a time (the Mac is also rendering).
Final reply: one line per video — what you changed (or "no change") and "approved".
