# BU Bench V1 adapter contract

Use upstream `run_framework_eval.py`, which currently supports registered framework adapters and `BU_Bench_V1`. The adapter must receive only the task text/ID needed for execution, call `harness.runner.run_task(task, id, "BU_Bench_V1")`, then translate the Cortex trajectory/final answer into the trace/result shape required by the upstream judge.

Do **not** inspect ground truth, decrypted sibling tasks, or grader material. Do not replace Cortex with direct OpenCode execution: the HTTP call to `/api/agent/run` is intentional because Cortex is the agent product under test. Do not replace Vantage with Chromium/CDP.

Pin the exact upstream commit in `artifacts/provenance.json` and record any adapter compatibility patch as a patch file under `artifacts/`, not as an unexplained edit.

Smoke order: 1 task -> 5 tasks -> 10 tasks -> full 100 only if scorer output is valid and no task material leaks into git.
