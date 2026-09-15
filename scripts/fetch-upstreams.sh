#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); cd "$ROOT"
set -a; source benchmarks.lock; set +a
mkdir -p upstream artifacts
fetch(){ local n=$1 r=$2 ref=$3; [[ -d upstream/$n/.git ]] || git clone "$r" "upstream/$n"; git -C "upstream/$n" fetch --tags origin; git -C "upstream/$n" checkout --detach "$ref"; }
fetch bu-bench "$BU_BENCH_REPO" "$BU_BENCH_REF"
fetch odysseys "$ODYSSEYS_REPO" "$ODYSSEYS_REF"
python3 scripts/write-provenance.py
