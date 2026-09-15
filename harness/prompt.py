BROWSER_CONTRACT='''You are being evaluated on a public browser-agent benchmark. Complete the TASK using the already-running Vantage browser.

Browser control contract:
- Use Vantage's shipped `vant agent` CLI (protocol 1). Do not launch Chromium, Chrome, Playwright, Selenium, browser-use cloud, or another browser.
- Discover state with `vant agent tabs`, `vant agent snapshot`, page inspection, screenshots, waits and diagnostics.
- Interact through `vant agent click`, `vant agent fill`, or `vant agent call page.interact ...`; `vant agent call` is the universal escape hatch.
- `vant agent js` is allowed when semantic interaction is insufficient.
- Semantic refs are ephemeral; take a fresh snapshot after DOM mutation/stale refs.
- Use the browser, not direct HTTP scraping, to perform the task.
- Never read benchmark datasets, grader files, ground truth, hidden answers, other traces, or benchmark source code to solve a task.
- Do not modify Vantage, Cortex, this harness, or benchmark files during a task.
- Stop when complete or impossible. Return the requested result concisely.'''
def task_prompt(task,max_steps=100): return f'{BROWSER_CONTRACT}\n\nMaximum browser-agent interaction budget: {max_steps} steps.\n\nTASK:\n{task.strip()}'
