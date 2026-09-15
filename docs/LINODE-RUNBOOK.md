# Linode runbook

1. Provision a disposable Ubuntu x86_64 VM with enough RAM for WebKitGTK + Cortex/OpenCode. Keep VM type/region/image in provenance. Use a non-root benchmark user.
2. Clone this repo plus frozen Cortex/Vantage sources. Run `scripts/bootstrap-ubuntu.sh`; build/install Cortex and Vantage normally.
3. Vantage needs a graphical session. On a headless VM start a DBus/Xvfb session (for example `dbus-run-session -- xvfb-run -a vant`) and confirm `vant agent status` from the same user/session. Do not assume headless WebKit behavior is score-equivalent until screenshots and interactions pass smoke tests.
4. Configure Cortex exactly as a normal deployment, including OpenCode/provider authentication. Put `CORTEX_PASSWORD` and judge/provider keys only in `.env`/process environment.
5. `scripts/fetch-upstreams.sh` clones BU Bench and Odysseys and records exact SHAs. Review upstream setup instructions at those pinned SHAs and install their dependencies in isolated environments.
6. Run `scripts/preflight.sh`, then `python3 -m harness.smoke --task 'Open https://example.com and report the page title.'`.
7. Implement/verify the thin upstream adapters from `adapters/*/CONTRACT.md` against the pinned interfaces. This final compatibility step must happen on the VM because upstream evolves and is intentionally not vendored here.
8. Gate each benchmark 1 -> 5 -> 10 tasks. Only then run BU Bench V1 100 tasks and Odysseys 200 tasks.
9. Archive sanitized summaries/provenance separately from sensitive trajectories. Never push decrypted tasks, cookies, screenshots containing private sessions, or secrets.

### Failure policy
Infrastructure/auth/display failures are not silently counted as agent failures. Classify them, fix general infrastructure once, restart the affected gate, and record the intervention. Genuine task failures stay failures until the entire frozen baseline is complete.
