#!/usr/bin/env bash
set -euo pipefail
: "${CORTEX_URL:=http://127.0.0.1:7331}"
command -v cortex; cortex --version
command -v "${VANT_BIN:-vant}"; "${VANT_BIN:-vant}" --version
command -v opencode; opencode --version
curl -fsS "$CORTEX_URL/api/health" | jq -e '.ok == true' >/dev/null
"${VANT_BIN:-vant}" agent status
"${VANT_BIN:-vant}" agent version
"${VANT_BIN:-vant}" agent capabilities >/dev/null
echo 'Cortex + Vantage preflight OK'
