#!/usr/bin/env bash
# End-to-end on the VM:  prep -> (plans written by the director agents, synced in) -> dub -> repair -> organize.
# Usage: vm/run_all.sh [all|prep|dub|selftest] [gens.json ...]
#   prep  [gens.json ...]  optional downloads from generation-history JSON, then stems + transcript.json
#                          (then on the Mac: sync_from_vm.sh -> agents write + validate plans -> sync_to_vm.sh)
#   dub                    validate plans -> dubplan_cuda -> repair_cuda -> organize
#   all   [gens.json ...]  prep, then dub (set WATCH=N to wait until N validated plans have been synced in)
#   selftest               5-language smoke test (needs one prepped video): prints backend, dtypes, sample length
#                          and TTS tokens/s; exits non-zero on failure
# Env: BACKEND=auto|vllm|transformers  IDS_FILE=vm_ids.txt or ONLY=id1,id2 (just these videos, e.g. the VM's share)
#      WATCH=N  WORKERS=N  GROUP=N  REPAIR_CER=0.6  DTYPE / CODEC_DTYPE / WHISPER_COMPUTE / BATCH (see vm/cudacfg.py)
set -euo pipefail
VM="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DUB="$(dirname "$VM")"
source "$VM/env.sh"
cd "$DUB"
STAGE="${1:-all}"
shift || true
mkdir -p work out logs
log() { echo "[$(date +%T)] $*"; }
IDS=""
if [ -n "${IDS_FILE:-}" ]; then IDS="--ids-file $IDS_FILE"; log "restricted to the ids in $IDS_FILE"; fi
if [ -n "${ONLY:-}" ]; then IDS="$IDS --only $ONLY"; log "restricted to $ONLY"; fi
BACKEND_ARG="--backend ${BACKEND:-auto}"

prep() {
  log "prep"
  if [ $# -gt 0 ]; then set -- --gens "$@"; fi
  # shellcheck disable=SC2086
  python vm/prep_cuda.py work/ "$@" $IDS 2>&1 | tee -a logs/prep.log
}

dub() {
  # dub.lock claims are per machine and only matter while an engine runs: clear leftovers from a crashed run.
  find work -mindepth 2 -maxdepth 2 -name dub.lock -delete
  for p in work/*/plan.json; do
    [ -e "$p" ] || continue
    python validate_plan.py "$p" >/dev/null || log "INVALID plan, skipped: $p"
  done
  log "dub"
  # shellcheck disable=SC2086
  python vm/dubplan_cuda.py work/ out/ ${WATCH:+--watch "$WATCH"} --workers "${WORKERS:-1}" ${GROUP:+--group "$GROUP"} \
    $BACKEND_ARG $IDS 2>&1 | tee -a logs/dub.log
  log "repair"
  # shellcheck disable=SC2086
  python vm/repair_cuda.py work/ out/ "${REPAIR_CER:-0.6}" $BACKEND_ARG $IDS 2>&1 | tee -a logs/repair.log
  log "organize"
  python organize.py 2>&1 | tee -a logs/organize.log
}

case "$STAGE" in
  prep) prep "$@" ;;
  dub) dub ;;
  all) prep "$@"; dub ;;
  # shellcheck disable=SC2086
  selftest) python vm/dubplan_cuda.py --selftest work/ $BACKEND_ARG 2>&1 | tee -a logs/selftest.log ;;
  *) echo "usage: $0 [all|prep|dub|selftest] [gens.json ...]"; exit 2 ;;
esac
log "done ($STAGE)"
