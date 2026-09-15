"""Run a single BU Bench V1 task through Cortex + Vantage protocol 1.

Thin cortex-vantage framework adapter for the pinned BU Bench runner. Cortex
(the agent under test) drives the already-running Vantage browser through
Vantage protocol 1 (vant agent). The upstream runner and scorer stay
authoritative; this adapter only translates task invocation and the
Cortex/Vantage trajectory into the ExecutionResult the upstream judge consumes.

Ground truth is only ever passed to the upstream judge inside run_and_judge,
never to Cortex.
"""
import asyncio
import hashlib
import json
import os
import sys
from pathlib import Path

BENCH_HARNESS = "/home/bench/deploy/benchmarks"
if BENCH_HARNESS not in sys.path:
    sys.path.insert(0, BENCH_HARNESS)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from frameworks import ExecutionResult, load_tasks, run_and_judge, interleave
from harness.runner import run_task as vantage_run_task


def _extract(rec):
    texts, cmds, cost = [], [], 0.0
    for e in rec.get("events", []):
        if e.get("type") != "opencode":
            continue
        p = e.get("data", {}).get("part", {})
        t = p.get("type")
        if t == "text":
            txt = (p.get("text") or "").strip()
            if txt:
                texts.append(txt)
        elif t == "tool":
            st = p.get("state", {})
            cmd = st.get("input", {}).get("command", "")
            if cmd:
                cmds.append(cmd)
        elif t == "cost":
            cost = max(cost, float(p.get("cost") or 0))
    final = texts[-1] if texts else "Agent did not emit a final answer"
    return final, cmds, cost


async def execute(task_description: str) -> ExecutionResult:
    task_id = "bu-" + hashlib.sha1(task_description.encode("utf-8")).hexdigest()[:12]
    rec, path = vantage_run_task(task_description, task_id, "BU_Bench_V1")
    final, steps, cost = _extract(rec)
    return ExecutionResult(
        final_result=final,
        steps=steps,
        screenshots_b64=[],
        num_steps=len(steps),
        duration_seconds=rec.get("duration_s", 0.0),
        cost=cost,
    )


async def main():
    task_index = int(os.environ["TASK_INDEX"])
    benchmark = os.environ.get("BENCHMARK", "BU_Bench_V1")
    tasks = load_tasks(benchmark)
    if len(tasks) == 100:
        tasks = interleave(tasks)
    task = tasks[task_index]
    task["_index"] = task_index
    await run_and_judge(task, execute)


if __name__ == "__main__":
    asyncio.run(main())
