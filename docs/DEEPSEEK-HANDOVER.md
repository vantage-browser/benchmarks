# DeepSeek handover: first Linode baseline

Objective: run an honest **Cortex + Vantage** baseline on BU Bench V1 and Odysseys from a Linode VM.

Do not modify Cortex or Vantage to improve task outcomes before the baseline is complete. First verify the repo's Cortex HTTP client against the supplied Cortex checkout and Vantage protocol preflight against the supplied Vantage checkout. The Cortex client deliberately authenticates and calls `/api/agent/run`; do not shortcut it by invoking OpenCode directly. The task prompt deliberately requires `vant agent`; do not substitute Chromium/CDP.

Fetch current upstream benchmark repos with `scripts/fetch-upstreams.sh`, inspect the exact pinned interfaces, and complete only the thin format adapters described under `adapters/`. BU Bench's current public runner advertises framework adapters; register a `cortex-vantage` adapter without copying decrypted task material. For Odysseys, integrate at its agent/trajectory boundary and preserve its scorer/rubrics/screenshots.

Run preflight and a harmless example.com smoke task. Then gate each benchmark at 1, 5 and 10 tasks. Stop and report if the adapter cannot preserve upstream scoring semantics, Vantage cannot provide required screenshot evidence, Cortex auth cannot be automated safely, or benchmark rules prohibit this integration.

Only after gates are valid run BU Bench V1 100/100 and Odysseys 200/200. Record exact commits, model/settings, VM details, wall time, upstream scores, failures, crashes and costs/tokens where available. Keep sensitive run data private. Commit only harness/adapter/provenance documentation changes; do not commit task traces or decrypted benchmark data.
