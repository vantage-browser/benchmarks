#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "$0")/.." && pwd); UP="$ROOT/upstream/bu-bench"
[[ -f "$UP/run_framework_eval.py" ]] || { echo 'fetch upstream BU Bench first' >&2; exit 1; }
cat <<'MSG'
BU Bench V1 now has a public framework-adapter runner, but its adapter API is upstream-owned and may change.
Before a scored run, inspect upstream/frameworks and implement/register `cortex-vantage` using adapters/bu_bench_v1/CONTRACT.md.
Do not copy/decrypt BU_Bench_V1 into this repository. Keep upstream run_data ignored/private.
MSG
