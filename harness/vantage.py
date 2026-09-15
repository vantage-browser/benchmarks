import json, subprocess
def call(vant_bin,*args):
    p=subprocess.run([vant_bin,'agent','--json',*args],text=True,capture_output=True,timeout=35)
    if p.returncode: raise RuntimeError(f"vant agent {' '.join(args)} failed ({p.returncode}): {p.stderr.strip()}")
    return json.loads(p.stdout)
def preflight(vant_bin='vant'):
    return {k:call(vant_bin,*v) for k,v in {'status':('status',),'version':('version',),'capabilities':('capabilities',)}.items()}
