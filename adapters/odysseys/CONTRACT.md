# Odysseys adapter contract

Integrate at the upstream agent/trajectory boundary while leaving Odysseys task definitions and rubric grader authoritative. For each task, pass its public task instruction to `harness.runner.run_task(task, id, "odysseys")`; translate Cortex/Vantage actions/screenshots/final response into the trajectory representation expected by the pinned upstream revision.

Preserve the benchmark's normal starting-page and step-budget semantics. Do not use benchmark source, rubrics or hidden expected answers as agent context. Vantage screenshots should be retained where the upstream grader expects rendered evidence.

Smoke order: representative tasks -> 5 -> 10 -> full 200. Report both perfect-task rate and rubric/partial-progress metrics supplied by upstream, plus harness wall-time/failure counts.
