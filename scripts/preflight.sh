#!/usr/bin/env bash
# Cortex + Vantage benchmark environment preflight.
# Generic, benchmark-independent checks that catch every known deployment pain
# point before any measured work: toolchain presence, Vantage protocol 1,
# loopback-only Cortex, a working graphical/display environment for WebKitGTK,
# judge-credential presence (without printing it), orphaned agent runs and
# upstream benchmark revisions.
#
# Exit status is 0 only when every critical check passes. Warnings do not fail.
set -uo pipefail

: "${CORTEX_URL:=http://127.0.0.1:7331}"
: "${VANT_BIN:=vant}"
FAILED=0
ok(){ printf 'ok:   %s\n' "$*"; }
bad(){ printf 'FAIL: %s\n' "$*"; FAILED=1; }
warn(){ printf 'warn: %s\n' "$*"; }

# --- toolchain presence -----------------------------------------------------
for tool in cortex opencode; do
    if command -v "$tool" >/dev/null 2>&1; then
        ok "$tool: $(command -v "$tool")"
    else
        bad "$tool missing from PATH"
    fi
done
cortex --version | sed 's/^/      cortex version: /'
if ! opencode --version 2>/dev/null | grep -v '^=' | grep -qE '[0-9]+\.[0-9]+\.[0-9]+'; then
    warn "opencode --version did not report a version (CPU-incompatible binary?)"
fi

if command -v "$VANT_BIN" >/dev/null 2>&1; then
    ok "vant: $(command -v "$VANT_BIN")"
    "$VANT_BIN" --version | sed 's/^/      vant version: /'
else
    bad "vant ($VANT_BIN) missing from PATH"
fi
# The agent shell (inside Cortex/OpenCode) needs the bare `vant` on PATH, which
# the deployment provides via a symlink in the benchmark user's ~/.local/bin.
if command -v vant >/dev/null 2>&1; then
    ok "bare 'vant' resolvable for the agent process"
elif [ -x "$HOME/.local/bin/vant" ]; then
    warn "bare 'vant' not on this PATH but ~/.local/bin/vant exists (add ~/.local/bin to PATH)"
else
    bad "bare 'vant' not resolvable; the Cortex agent shell needs it (symlink ~/.local/bin/vant)"
fi

# --- Cortex reachability + loopback-only binding ----------------------------
if curl -fsS "$CORTEX_URL/api/health" | jq -e '.ok == true' >/dev/null 2>&1; then
    ok "Cortex health ok ($CORTEX_URL)"
else
    bad "Cortex health check failed ($CORTEX_URL)"
fi
if ss -tln 2>/dev/null | grep -q ':7331 '; then
    if ss -tln 2>/dev/null | grep ':7331 ' | grep -q '127.0.0.1:7331'; then
        ok "Cortex listens on loopback 127.0.0.1:7331 only"
    else
        bad "Cortex is not loopback-only; port 7331 is publicly reachable"
    fi
else
    bad "Cortex is not listening on 7331"
fi

# --- Vantage protocol 1 stable ----------------------------------------------
if "$VANT_BIN" agent status >/dev/null 2>&1; then
    ok "Vantage agent status ok"
else
    bad "Vantage agent status failed"
fi
"$VANT_BIN" agent version 2>/dev/null | sed 's/^/      vantage agent version: /'
cap="$("$VANT_BIN" agent capabilities 2>/dev/null || true)"
if printf '%s' "$cap" | jq -e '.protocol == 1 and .stability == "stable"' >/dev/null 2>&1; then
    ok "Vantage protocol 1 stable"
else
    bad "Vantage capabilities did not report protocol 1 stable"
fi

# --- graphical/display environment for WebKitGTK ----------------------------
if [ -n "${DISPLAY:-}" ]; then
    ok "DISPLAY set ($DISPLAY)"
elif pgrep -x Xvfb >/dev/null 2>&1; then
    warn "no DISPLAY in this shell but Xvfb is running (expected inside the session)"
else
    bad "no DISPLAY and no Xvfb process; WebKitGTK/Vantage needs a graphical session"
fi

# --- judge credential presence (never printed) ------------------------------
if [ -n "${GOOGLE_API_KEY:-}" ]; then
    ok "BU Bench judge credential present (GOOGLE_API_KEY set)"
else
    warn "BU Bench judge credential not set (GOOGLE_API_KEY); canonical gemini-2.5-flash judge needs it at scoring time"
fi

# --- orphaned agent runs ----------------------------------------------------
orphans=$(pgrep -af "opencode run" 2>/dev/null | grep -v pgrep || true)
if [ -n "$orphans" ]; then
    warn "orphaned opencode run processes present:"
    printf '%s\n' "$orphans" | sed 's/^/      /'
else
    ok "no orphaned opencode run processes"
fi

# --- upstream benchmark revisions (informational) ---------------------------
for name in bu-bench odysseys; do
    if [ -d "upstream/$name/.git" ]; then
        ok "upstream/$name: $(git -C "upstream/$name" rev-parse HEAD 2>/dev/null | cut -c1-12)"
    else
        warn "upstream/$name not fetched yet (run scripts/fetch-upstreams.sh)"
    fi
done

if [ "$FAILED" -eq 0 ]; then
    echo 'Cortex + Vantage preflight OK'
    exit 0
fi
echo 'Cortex + Vantage preflight FAILED' >&2
exit 1