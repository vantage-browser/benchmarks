#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update
sudo apt-get install -y git python3 python3-venv python3-pip jq curl ca-certificates xvfb dbus-x11 build-essential pkg-config libgtk-4-dev libwebkitgtk-6.0-dev libsqlite3-dev
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -U pip
echo 'Base benchmark dependencies installed. Build/install the frozen Cortex and Vantage revisions next.'
