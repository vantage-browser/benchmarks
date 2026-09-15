#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip jq curl ca-certificates xvfb dbus-x11 build-essential pkg-config libgtk-4-dev libwebkitgtk-6.0-dev libsqlite3-dev
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip

# WebKitGTK's web-process sandbox uses bubblewrap, which needs unprivileged user
# namespaces. Ubuntu 24.04 restricts them via AppArmor by default, which makes
# Vantage abort with "bwrap: setting up uid map: Permission denied". Enable and
# persist user namespaces so WebKit's normal sandbox can run.
if [ "$(cat /proc/sys/kernel/unprivileged_userns_clone 2>/dev/null || echo 0)" != "1" ] \
   || [ "$(cat /proc/sys/kernel/apparmor_restrict_unprivileged_userns 2>/dev/null || echo 1)" != "0" ]; then
    sudo sysctl -w kernel.unprivileged_userns_clone=1 || true
    sudo sysctl -w kernel.apparmor_restrict_unprivileged_userns=0 || true
    printf 'kernel.unprivileged_userns_clone=1\nkernel.apparmor_restrict_unprivileged_userns=0\n' \
        | sudo tee /etc/sysctl.d/99-vantage-userns.conf >/dev/null
    echo 'Enabled unprivileged user namespaces for the WebKitGTK sandbox.'
fi

# The Cortex and Vantage services run as systemd USER services on a headless
# VM; enable linger so they start without a login session.
if command -v loginctl >/dev/null 2>&1; then
    sudo loginctl enable-linger "$(id -un)" 2>/dev/null || true
fi

echo 'Base benchmark dependencies installed. Install the toolchain (Go >= 1.25,'
echo 'CPU-compatible OpenCode, uv, Caddy) per HANDOVER.md, build/install the'
echo 'frozen Cortex and Vantage revisions, then run scripts/preflight.sh.'
