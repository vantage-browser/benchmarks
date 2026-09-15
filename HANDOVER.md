# Vantage agent benchmarks — handover

Reproducible benchmark harness for **Cortex + Vantage**, targeting **BU Bench V1**
and **Odysseys**. This repository is only the adapter/orchestration layer: task
sets and graders stay in their upstream repositories and are resolved into an
exact provenance record before a run.

This handover is the durable master document. Operational details live in
[`docs/LINODE-RUNBOOK.md`](docs/LINODE-RUNBOOK.md), methodology in
[`docs/METHODOLOGY.md`](docs/METHODOLOGY.md), and the original campaign handover
in [`docs/DEEPSEEK-HANDOVER.md`](docs/DEEPSEEK-HANDOVER.md).

---

# Remote Cortex + Vantage Benchmark Deployment

This section records the first real remote deployment of the benchmark, the
known-good frozen revisions, every pain point encountered, and the exact resume
boundary. It is written so a future agent can recreate the environment on a
fresh Ubuntu Linode **without rediscovering the problems below**. The measured
benchmark baseline has **not** started: zero BU Bench and zero Odysseys tasks
have been run.

## Intended architecture

Two separate model consumers exist. Keep them distinct.

```text
BU Bench / Odysseys
        ↓
benchmark adapter (this repo)
        ↓
Cortex
        ↓
OpenCode Zen
        ↓
deepseek-v4-flash
        ↓
Vantage protocol 1
        ↓
WebKitGTK
```

and, separately, scoring:

```text
BU Bench trajectory/result
        ↓
canonical BU Bench V1 judge
        ↓
Google gemini-2.5-flash
```

The Google credential is **only for the canonical BU Bench V1 judge** (an
LLM-as-judge grader). It is not used by Cortex or Vantage.

## Known-good frozen versions (measured baseline)

These are the revisions the deployment was frozen on. Keep them unless a
genuine infrastructure defect forces a change, and record any change explicitly.

```text
Cortex:            f0ddec5  (version 0.1.2)
Vantage:           d7b917e  (tag v0.1.2, version 0.1.2, protocol 1 stable)
WebKitGTK:         2.52.6   (GTK 4.14.5)
OpenCode:          1.18.31
Provider:          OpenCode Zen
Agent model:       opencode-chat/deepseek-v4-flash
BU Bench V1:       421390ea
benchmark harness: 8900d5f  (measured revision; setup base 83f487d)
Odysseys:          83781463
max steps:         100
task timeout:      1800 seconds
```

The benchmark harness revision is `8900d5f` — the commit that includes the
generic Cortex-client corrections, the BU Bench `cortex-vantage` adapter and
the fixed familiarization suite. `83f487d` is only the original setup/base
commit and must not be called the measured harness revision.

## Host template (what worked)

- Ubuntu 24.04 LTS (24.04.x, updated) x86_64, headless Linode.
- 1 vCPU / 1 GB RAM / 25 GB disk was sufficient for the familiarization phase
  but wedges if an agent run is orphaned (see pain points). More RAM is safer.
- Non-root benchmark user (e.g. `bench`) with sudo and `loginctl enable-linger
  <user>` so systemd **user** services run without a login.
- Firewall (UFW): allow only 22, 80, 443 inbound; deny everything else.
- WebKitGTK bubblewrap sandbox requires unprivileged user namespaces on Ubuntu
  24.04 — set and persist:
  ```sh
  sysctl -w kernel.unprivileged_userns_clone=1
  sysctl -w kernel.apparmor_restrict_unprivileged_userns=0
  # persist via /etc/sysctl.d/99-vantage-userns.conf
  ```
  Without this, WebKit web processes fail with `bwrap: setting up uid map:
  Permission denied` and Vantage aborts.

## Service layout

All run under the benchmark user's systemd **user** manager (linger enabled):

```text
cortex.service     Cortex on 127.0.0.1:7331 (loopback only)
vantage.service    dbus-run-session -- xvfb-run -a -s "-screen 0 1280x800x24" vant
fam-fixtures.service  python3 -m http.server 8090 --bind 127.0.0.1 (local fixtures)
caddy              system service: reverse proxy -> 127.0.0.1:7331
```

Vantage needs a graphical session on the headless VM:
`dbus-run-session -- xvfb-run -a -s "-screen 0 1280x800x24" <vant-binary>`, with
`XDG_RUNTIME_DIR=/run/user/<uid>` and `WEBKIT_DISABLE_COMPOSITING_MODE=1` set.
The agent socket lands at `$XDG_RUNTIME_DIR/vantage-agent-<uid>.sock`; every
consumer (the harness, and the agent inside Cortex/OpenCode) must use the same
`XDG_RUNTIME_DIR`.

## Directory layout on the VM

```text
~/deploy/benchmarks   this repository (frozen harness revision), .env, run_data/
~/deploy/vant         Vantage checkout at v0.1.2
~/deploy/cortex       Cortex checkout at f0ddec5
~/deploy/benchmarks/upstream/bu-bench    BU Bench at 421390ea (gitignored)
~/deploy/benchmarks/upstream/odysseys    Odysseys at 83781463 (gitignored)
```

Bootstrap: `scripts/bootstrap-ubuntu.sh` (base deps + venv), then the toolchain
below, then `scripts/fetch-upstreams.sh`, then `scripts/preflight.sh`.

## Toolchain install notes

- Go 1.26.8 (Cortex requires go >= 1.25) from the official tarball; Ubuntu's
  apt `golang-go` is too old.
- OpenCode: install via the official installer (`curl -fsSL
  https://opencode.ai/install | bash`) which picks a CPU-compatible build. See
  the OpenCode pain point below.
- `uv` from the official installer (`curl -LsSf https://astral.sh/uv/install.sh
  | sh`); `pip install uv` fails on Ubuntu 24.04 (PEP 668).
- Caddy from the official Ubuntu repo (systemd-managed).
- Python venv with `pytest` for the harness tests.

## Benchmark flow (familiarized)

```text
vant agent tabs / snapshot / inspect          discover state
vant agent click / fill / call page.interact  interact (refs are ephemeral; re-snapshot)
vant agent js                                  escape hatch
vant agent call browser.navigate              navigate (rejected schemes error explicitly)
```

See `harness/prompt.py` for the exact browser-control contract given to the
agent.

## Pain points encountered (do not rediscover these)

### Vantage on the agent PATH

Cortex/OpenCode's agent shell could not find `vant` initially: every first tool
call failed with `exit 127: vant: command not found`, and the agent wasted
tokens discovering `/home/bench/deploy/vant/build/vant`. **Fix:** symlink the
built binary into the benchmark user's `~/.local/bin/vant` (the Cortex user
service PATH includes `~/.local/bin`). Verify with `vant --version` and
`vant agent status` from that PATH.

### Cortex Origin handling

The benchmark Cortex client originally sent `Origin: http://127.0.0.1:7331` on
CSRF'd requests. When Cortex's `--public-origin` is anything other than that
(here `http://<ip>`), the request is rejected with `403 Forbidden` on
`/api/agent/run`. **Fix (in the harness):** the client no longer sends an
`Origin` header. Cortex exempts loopback local clients from the Origin CSRF
check (`auth.go sameOrigin`), which is the intended path for local automation.
Deployment expectation: Cortex stays on loopback, and the harness talks to it
over loopback.

### Cortex streaming timeout

The original 60-second client socket timeout was inadequate for long agent
runs (model thinking gaps routinely exceed it). **Fix (in the harness):** the
agent-run stream timeout is 1800 seconds, matching `BENCHMARK_TASK_TIMEOUT`.

### Disconnected client / orphaned Cortex runs

Disconnecting the harness while a run was in progress did not cancel the
server-side run; the orphaned OpenCode agent kept consuming the 1 GB VM and
wedged the whole host (SSH banner timeout, port 80 dead) until a Linode reboot.
**Fix (in the harness):** on a failed stream read the client now cancels the run
server-side (`/api/agent/cancel`). **Before any measured gate**, check for
orphans with `pgrep -af "opencode run"` and clean them up.

### OpenCode CPU compatibility

The locally frozen OpenCode 1.18.27 Bun binary crashed on the AMD EPYC 7642
with `Illegal instruction` / `Bus error` (no AVX-512). **Known-good deployed
version: OpenCode 1.18.31**, installed via the official installer. Do not
casually downgrade/upgrade OpenCode on the next baseline without recording the
change and re-verifying it runs on the target CPU.

### Headless WebKitGTK

WebKitGTK needs a display and user namespaces (see host template). The working
arrangement is the `vantage.service` unit above; it is verified by `vant agent
status` plus an actual navigation/snapshot (open a page, then `page.inspect`
metadata and `page.snapshot`). Do not assume headless WebKit behavior until a
real page renders.

### Caddy / IP access

Caddy initially served its default page for `http://<ip>/` because the only
configured virtual host was `bench.crtx.dev` (no DNS record was created). The
working configuration proxies the Linode IP over plain HTTP:
```caddy
http://104.237.151.131 {
    reverse_proxy 127.0.0.1:7331
}
```
Cortex itself remains bound to `127.0.0.1:7331` and port 7331 is firewall
blocked publicly. **Plain HTTP over the IP was a temporary convenience and is
not appropriate for entering secrets.** On a future deployment prefer HTTPS/DNS
(or another secure credential-entry path) before entering provider/judge keys.

### Cortex credentials

The temporary bootstrap administrator password from this campaign is **not
preserved**. A fresh deployment must create/configure an administrator (Cortex
`setup` subcommand with a `--password-file`, then change the password after
first login) and must never commit credentials.

### OpenCode Zen credential

The provider credential is configured **through Cortex** (the user does it in
the Cortex UI), not placed in benchmark source or handed to an agent in chat.
The harness `.env` only holds non-secret configuration plus `CORTEX_PASSWORD`
for its own API login; keep that file out of Git.

### BU Bench Google judge requirement

This was investigated at the pinned revision `421390ea`. Findings:

- The BU Bench V1 judge uses `ChatGoogle` (`browser_use`), configured to
  `gemini-2.5-flash`.
- `run_eval.py` states the judge is "always gemini-2.5-flash for consistent
  judging across all evaluations"; the framework runner does the same via
  `JUDGE_MODEL` (default `gemini-2.5-flash`) + `GOOGLE_API_KEY`.
- **There is no judge-provider switch** in the benchmark and **no
  deterministic/non-LLM V1 scorer** (`findings_judge.py` is V2-only).
- Changing the judge model changes scoring semantics and loses apples-to-apples
  comparability with the published BU Bench V1 results.
- The published results were produced with the same fixed `gemini-2.5-flash`
  judge across all agent models, including an official `deepseek-v4-flash`
  result: **37 / 100 successful, 2,172 steps, 105,860 s wall time**.

**Do not inspect the individual failures/trajectories of that (or any)
published result before our own baseline is complete** — that would invite
benchmark-specific tuning.

### BU Bench protected material

Never commit decrypted tasks, ground truth, judge material, screenshots, or
sensitive run data. The repository `.gitignore` already excludes `run_data/`,
`results/`, `upstream/`, `artifacts/`, `.env` and logs. Keep it that way.

## Familiarization (do this before measured work)

Eight synthetic, benchmark-independent exercises exercise the Vantage
mechanics through Cortex (`familiarization.py`). They are deliberately **not
derived from either benchmark** and never contribute scores. Their purpose:

```text
verify Cortex understands Vantage mechanics
discover infrastructure problems
do not train or tune against benchmark tasks
```

Results go to `run_data/familiarization/` and are separate from measured
results. Cortex sessions used for familiarization must be discarded and must
not carry into benchmark execution. This familiarization run is what surfaced
the PATH, Origin, timeout, cancellation and orphaned-run problems above —
**before any measured task was run**.

## Resume boundary (exactly where the campaign stopped)

```text
Infrastructure deployment:       COMPLETE
Cortex/Vantage integration:      COMPLETE
Synthetic familiarization:       COMPLETE
BU Bench adapter:                COMPLETE
Frozen baseline provenance:      COMPLETE

GOOGLE_API_KEY:                  NOT CONFIGURED
BU Bench measured tasks:         0
Odysseys measured tasks:         0
```

The next campaign should **not repeat the design/investigation work**. The
intended resume sequence:

```text
provision fresh VM
    ↓
recreate known-good environment
    ↓
run preflight
    ↓
run fixed synthetic familiarization
    ↓
discard familiarization sessions
    ↓
freeze/record actual deployment revisions
    ↓
configure OpenCode Zen credential securely
    ↓
configure GOOGLE_API_KEY securely
    ↓
verify canonical gemini-2.5-flash judge
    ↓
BU Bench 1-task calibration
    ↓
STOP AND REVIEW
    ↓
5-task gate
    ↓
10-task gate
    ↓
STOP AND REVIEW
    ↓
full 100-task BU Bench baseline
    ↓
Odysseys adapter/gates/full suite
```

## Credentials — summary of the correct handling

- **OpenCode Zen credential**: configure in Cortex via its UI. Never in source,
  never pasted into chat, never committed.
- **Google judge credential (`GOOGLE_API_KEY`)**: put it in the VM's private
  `.env` (for the BU Bench judge). Never print it or its length/prefix/suffix.
  Keep the canonical `gemini-2.5-flash` judge.
- **Cortex admin password**: bootstrap via `cortex setup --password-file ...`,
  then change it after first login. Never commit it.
- **Linode / cloud tokens**: environment or CLI config only, never in docs.

## Handover index

- [`docs/LINODE-RUNBOOK.md`](docs/LINODE-RUNBOOK.md) — operational provisioning
  and gate order.
- [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) — measurement methodology and
  integrity rules.
- [`docs/DEEPSEEK-HANDOVER.md`](docs/DEEPSEEK-HANDOVER.md) — original campaign
  handover (BU Bench V1 + Odysseys first baseline).
- `adapters/bu_bench_v1/CONTRACT.md` — BU Bench adapter contract; the
  `cortex-vantage` adapter implementation is `adapters/bu_bench_v1/run_task.py`.