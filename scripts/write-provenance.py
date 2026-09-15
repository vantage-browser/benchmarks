#!/usr/bin/env python3
import json,subprocess,time
from pathlib import Path
def git(p,*a): return subprocess.check_output(['git','-C',p,*a],text=True).strip()
out={'captured_at':time.time(),'upstreams':{}}
for n in ('bu-bench','odysseys'):
 p=f'upstream/{n}'; out['upstreams'][n]={'commit':git(p,'rev-parse','HEAD'),'remote':git(p,'remote','get-url','origin')}
Path('artifacts').mkdir(exist_ok=True); Path('artifacts/provenance.json').write_text(json.dumps(out,indent=2)+'\n'); print(json.dumps(out,indent=2))
