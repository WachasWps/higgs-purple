#!/bin/bash
# Watch Kaggle dub jobs. On COMPLETE: pull dub_out.zip into out/ and refresh final/.
# On failure (or no zip): give the job's videos back to the Mac engine (remove locks + request a rescan).
# Usage: bash kaggle_watch.sh slug:id1,id2 [slug:id3,id4 ...]
cd "$(dirname "$0")"
K=.venv/bin/kaggle
USER_=$($K config view 2>/dev/null | awk -F': ' '/username/{print $2}')
pending="$*"
last=""

give_back() {  # $1 = comma-separated ids
  for v in ${1//,/ }; do rm -f "work/$v/dub.lock"; done
  touch out/.restart
}

while [ -n "$pending" ]; do
  next=""
  for j in $pending; do
    slug=${j%%:*}; vids=${j#*:}
    st=$($K kernels status "$USER_/$slug" 2>&1 | grep -oE 'RUNNING|COMPLETE|ERROR|QUEUED|CANCEL[A-Z_]*' | head -1)
    prev=$(echo "$last" | tr ' ' '\n' | grep "^$slug=" | cut -d= -f2)
    [ "$st" != "$prev" ] && echo "$(date +%H:%M) kaggle $slug: ${st:-unknown}"
    last="$(echo "$last" | tr ' ' '\n' | grep -v "^$slug=" | tr '\n' ' ') $slug=$st"
    case "$st" in
      COMPLETE)
        mkdir -p "kaggle_out/$slug"
        $K kernels output "$USER_/$slug" -p "kaggle_out/$slug" -o >/dev/null 2>&1
        if [ -f "kaggle_out/$slug/dub_out.zip" ]; then
          unzip -o -q "kaggle_out/$slug/dub_out.zip" -d .  # zip paths already start with out/
          n=$(unzip -l "kaggle_out/$slug/dub_out.zip" | grep -c '\.mp4$')
          python3 organize.py >/dev/null 2>&1
          echo "$(date +%H:%M) kaggle $slug DONE: $n dubbed videos pulled into out/ + final/ ($(ls out/????????_??.mp4 | wc -l | tr -d ' ')/145 total)"
          missing=""
          for v in ${vids//,/ }; do
            c=$(ls out/${v}_{bn,ta,te,ml,or}.mp4 2>/dev/null | wc -l | tr -d ' ')
            [ "$c" -lt 5 ] && missing="$missing,$v"
          done
          [ -n "$missing" ] && { echo "$(date +%H:%M) kaggle $slug incomplete for ${missing#,} — returning to the Mac"; give_back "${missing#,}"; }
        else
          echo "$(date +%H:%M) kaggle $slug finished without results — returning $vids to the Mac (log: kaggle_out/$slug)"
          give_back "$vids"
        fi ;;
      ERROR|CANCEL*)
        mkdir -p "kaggle_out/$slug"
        $K kernels output "$USER_/$slug" -p "kaggle_out/$slug" -o >/dev/null 2>&1
        echo "$(date +%H:%M) kaggle $slug FAILED — returning $vids to the Mac (log: kaggle_out/$slug)"
        give_back "$vids" ;;
      *) next="$next $j" ;;
    esac
  done
  pending=$(echo $next)
  [ -n "$pending" ] && sleep 45
done
echo "all kaggle jobs settled"
