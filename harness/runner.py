import json, platform, subprocess, time, uuid
from pathlib import Path
from .config import Config
from .cortex import CortexClient
from .prompt import task_prompt
from .vantage import preflight
def ver(cmd):
    try: return subprocess.check_output(cmd,text=True,stderr=subprocess.STDOUT,timeout=10).strip()
    except Exception: return None
def run_task(task,task_id,benchmark,out_dir='run_data'):
    cfg=Config(); browser=preflight(cfg.vant_bin); c=CortexClient(cfg.cortex_url); c.login(cfg.username,cfg.password)
    started=time.time(); session='bench-'+uuid.uuid4().hex[:20]
    events=c.run(task_prompt(task,cfg.max_steps),cfg.workspace,session); duration=time.time()-started
    rec={'schema':1,'benchmark':benchmark,'task_id':task_id,'duration_s':duration,'client_session':session,'environment':{'platform':platform.platform(),'cortex':ver(['cortex','--version']),'vantage':ver([cfg.vant_bin,'--version']),'browser_preflight':browser},'events':events}
    d=Path(out_dir)/benchmark; d.mkdir(parents=True,exist_ok=True); p=d/f'{task_id}.json'; p.write_text(json.dumps(rec,indent=2)+'\n')
    return rec,p
