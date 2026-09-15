import sys, time, json
sys.path.insert(0, ".")
from harness.runner import run_task

EXERCISES = [
    ("fam-01", "Open https://example.com in the Vantage browser and report the page title."),
    ("fam-02", "Open http://127.0.0.1:8090/index.html in the Vantage browser. Take a semantic snapshot, follow the ordinary link to page two, report the destination page title, then navigate back to the first page."),
    ("fam-03", "Open http://127.0.0.1:8090/index.html and http://127.0.0.1:8090/page2.html in two separate tabs of the Vantage browser. List the tabs, switch between them, and report each page title."),
    ("fam-04", "On the page http://127.0.0.1:8090/index.html, fill the text field with the value \"familiarization\" but do NOT submit anything. Verify and report the resulting field value."),
    ("fam-05", "Take a screenshot of http://127.0.0.1:8090/index.html to a file and also inspect the same page with a semantic snapshot. Report both the screenshot path and the snapshot element count."),
    ("fam-06", "Navigate the Vantage browser to http://127.0.0.1:8090/page2.html and use a wait operation for visible body text \"Page two\". Report the wait result."),
    ("fam-07", "On http://127.0.0.1:8090/index.html, take a semantic snapshot, click the button that changes the DOM, then deliberately attempt to reuse the pre-mutation element reference and observe the stale/missing failure. Recover by taking a fresh snapshot and report what the button label is now."),
    ("fam-08", "Use Vantage page JavaScript for a harmless read-only inspection of http://127.0.0.1:8090/index.html: return the document title and the number of links on the page."),
]

def main():
    results = {}
    for fid, task in EXERCISES:
        t0 = time.time()
        print(f"[{fid}] running ...", flush=True)
        try:
            rec, path = run_task(task, fid, "familiarization")
            dur = rec["duration_s"]
            events = len(rec["events"])
            print(f"[{fid}] done in {dur:.1f}s, {events} Cortex events -> {path}", flush=True)
            results[fid] = {"ok": True, "duration_s": dur, "events": events, "path": str(path)}
        except Exception as e:
            print(f"[{fid}] ERROR: {e}", flush=True)
            results[fid] = {"ok": False, "error": str(e)}
    summary = {"schema": 1, "kind": "familiarization", "results": results}
    with open("run_data/familiarization-summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("familiarization summary written to run_data/familiarization-summary.json")

if __name__ == "__main__":
    main()
