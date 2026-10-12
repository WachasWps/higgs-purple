#!/usr/bin/env bash
# VM -> Mac: out/ + final/ (hard links preserved), plus what the director agents need from a VM-side prep:
# work/<id>/{transcript.json, meta.json, prompt.txt, frames/}. Files that are newer on the Mac are kept (-u).
# Works with macOS openrsync / rsync 2.6.9 and bash 3.2.
# Usage: vm/sync_from_vm.sh user@host [remote_dir=dub]
set -euf -o pipefail
HOST="${1:?usage: sync_from_vm.sh user@host [remote_dir=dub]}"
REMOTE="${2:-dub}"
DUB="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
rsync -azuH -e ssh \
  --exclude='__pycache__/' \
  --include='/out/' --include='/out/**' --include='/final/' --include='/final/**' \
  --include='/work/' --include='/work/*/' \
  --include='/work/*/transcript.json' --include='/work/*/meta.json' --include='/work/*/prompt.txt' \
  --include='/work/*/frames/' --include='/work/*/frames/**' \
  --exclude='*' \
  "$HOST:$REMOTE/" "$DUB/"
echo "pulled from $HOST:$REMOTE/"
