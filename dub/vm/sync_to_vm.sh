#!/usr/bin/env bash
# Mac -> VM: code + work/ (sources, prompts, meta, frames, stems, transcripts, plans + plan.ok).
# Never pushes dub.lock (claims are per machine), demucs leftovers, temp wavs or the Mac venv.
# Files that are newer on the VM are kept (-u). Works with macOS openrsync / rsync 2.6.9 and bash 3.2.
# Usage: vm/sync_to_vm.sh user@host [remote_dir=dub] [--ids id1,id2,... | --ids-file ids.txt] [--with-out]
#   --ids / --ids-file  push only these work/<id> folders (the VM's share of the work) and write the list to
#                       <remote_dir>/vm_ids.txt on the VM; then run there:  IDS_FILE=vm_ids.txt vm/run_all.sh dub
#   --with-out          also push out/, so the VM skips (and may repair) dubs the Mac already finished
set -euf -o pipefail
HOST="${1:?usage: sync_to_vm.sh user@host [remote_dir=dub] [--ids a,b | --ids-file f] [--with-out]}"
shift
REMOTE="dub"
OUT_RULES=""
IDS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --with-out) OUT_RULES="--include=/out/ --include=/out/**" ;;
    --ids) IDS="$IDS $(echo "${2:?--ids needs a value}" | tr ',' ' ')"; shift ;;
    --ids-file) IDS="$IDS $(sed 's/#.*//' "${2:?--ids-file needs a file}" | tr ',\n' '  ')"; shift ;;
    *) REMOTE="$1" ;;
  esac
  shift
done
WORK_RULES="--include=/work/**"
if [ -n "$(echo $IDS)" ]; then
  WORK_RULES=""
  for id in $IDS; do
    id=$(echo "$id" | cut -c1-8)
    WORK_RULES="$WORK_RULES --include=/work/$id/ --include=/work/$id/**"
  done
fi
DUB="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ssh "$HOST" "mkdir -p '$REMOTE'"
# shellcheck disable=SC2086  # the *_RULES strings are intentionally split into args (globbing is off: set -f)
rsync -azu -e ssh \
  --exclude='.DS_Store' --exclude='__pycache__/' --exclude='dub.lock' \
  --exclude='/work/_demucs/' --exclude='/work/*/*.wav' --exclude='/work/*/stems.tmp/' \
  --include='/*.py' --include='/DIRECTOR_BRIEF.md' --include='/vm/' --include='/vm/**' \
  --include='/work/' $WORK_RULES $OUT_RULES \
  --exclude='*' \
  "$DUB/" "$HOST:$REMOTE/"
if [ -n "$(echo $IDS)" ]; then
  # shellcheck disable=SC2086
  printf '%s\n' $IDS | cut -c1-8 | ssh "$HOST" "cat > '$REMOTE/vm_ids.txt'"
  echo "pushed $(printf '%s\n' $IDS | wc -l | tr -d ' ') video folders; ids in $HOST:$REMOTE/vm_ids.txt"
fi
echo "pushed to $HOST:$REMOTE/"
