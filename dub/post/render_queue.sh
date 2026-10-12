#!/bin/bash
# Render each video as soon as its art-director approval marker appears (work/<id>/graphics.approved).
# Dubbed videos render all 5 languages; Hinglish ads (meta.json "kind": "ad") render via --ads.
# render_post.py itself caps the Mac at 3 concurrent renders and checks memory before each one.
cd "$(dirname "$0")/.."
PY=.venv/bin/python
total=$(ls work/*/graphics.json | wc -l | tr -d ' ')
while true; do
  for a in work/*/graphics.approved; do
    [ -f "$a" ] || continue
    d=$(dirname "$a"); id=$(basename "$d")
    [ -f "$d/rendered.ok" ] && [ "$d/rendered.ok" -nt "$d/graphics.json" ] && continue
    if grep -q '"kind": *"ad"' "$d/meta.json" 2>/dev/null; then
      $PY post/render_post.py --ads --ids "$id" --force >> post/logs/queue.log 2>&1
    else
      $PY post/render_post.py --ids "$id" --force >> post/logs/queue.log 2>&1
    fi && touch "$d/rendered.ok" && echo "$(date +%H:%M) RENDERED $id ($(ls work/*/rendered.ok 2>/dev/null | wc -l | tr -d ' ')/$total)"
  done
  done_n=$(ls work/*/rendered.ok 2>/dev/null | wc -l | tr -d ' ')
  [ "$done_n" -ge "$total" ] && { echo "ALL $total VIDEOS RENDERED"; break; }
  sleep 10
done
