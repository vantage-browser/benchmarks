# Methodology

## Primary question
Can the released/frozen Cortex agent complete public live-web agent benchmarks through released/frozen Vantage protocol 1 without benchmark-specific product changes?

## Freeze before baseline
Record exact Cortex commit/version, Vantage commit/version, OpenCode version, model/provider/reasoning settings, VM image/type/region, benchmark upstream SHAs, max steps and task timeout. Do not tune against individual failures during the baseline.

## Controlled comparisons later
The harness is intentionally browser/agent separable. Later campaigns can hold Cortex/model fixed and compare Vantage vs Chromium, or hold Vantage/model fixed and compare Cortex vs Codex/OpenCode. Do not mix those comparisons into the initial Cortex+Vantage baseline.

## Metrics
Use upstream benchmark scores as authoritative. Additionally retain: task completion/error counts, wall time, Cortex trajectory, model/token/cost fields when Cortex/OpenCode exposes them, browser/agent crashes, Vantage protocol failures and machine resource observations. For Odysseys retain perfect-task rate and rubric/partial-progress score.

## Integrity
No task-specific patches during baseline. No direct HTTP answer retrieval. No reading benchmark source/ground truth by the agent. No publishing decrypted BU Bench material. A compatibility adapter may translate formats but must not add task hints.
