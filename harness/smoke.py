import argparse
from .runner import run_task
def main():
    p=argparse.ArgumentParser(); p.add_argument('--task',required=True); p.add_argument('--id',default='smoke'); a=p.parse_args()
    r,path=run_task(a.task,a.id,'smoke'); print(f"wrote {path} ({r['duration_s']:.1f}s, {len(r['events'])} Cortex events)")
if __name__=='__main__': main()
