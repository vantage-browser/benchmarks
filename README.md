# Vantage agent benchmarks

Reproducible benchmark harness for **Cortex + Vantage**, initially targeting **BU Bench V1** and **Odysseys**. This repository is only the adapter/orchestration layer: task sets and graders stay in their upstream repositories and are resolved into an exact provenance record before a run.

The first campaign freezes Cortex and Vantage before task-level tuning. Cortex remains the agent product under test: it launches its normal OpenCode-backed run. The benchmark prompt instructs that agent to operate the already-running Vantage instance through Vantage protocol 1 (`vant agent ...`).

## Linode quick start

```sh
./scripts/bootstrap-ubuntu.sh
./scripts/fetch-upstreams.sh
cp .env.example .env
# Build/install the frozen Cortex and Vantage revisions and configure Cortex.
set -a; source .env; set +a
./scripts/preflight.sh
python3 -m harness.smoke --task 'Open https://example.com and report the page title.'
```

Then run the compatibility gates described in `docs/LINODE-RUNBOOK.md`. Do not begin 100/200-task runs until the upstream adapters pass their smoke gates.

## What is measured

The common harness records benchmark/task identity, exact Cortex/Vantage versions, Vantage protocol preflight, Cortex's complete NDJSON run trajectory, wall time and lightweight Cortex/Vantage RSS samples. Upstream graders remain authoritative for benchmark scores.

## Integrity

Never commit decrypted BU Bench task text, ground truth, screenshots, `run_data`, authenticated browser profiles, Cortex passwords, cookies, or provider/judge keys. BU Bench's public verifier itself warns that its `run_data/` contains decrypted task text and ground truth.
