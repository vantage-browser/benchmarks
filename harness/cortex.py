import http.cookiejar, json, urllib.request
class CortexError(RuntimeError): pass
class CortexClient:
    def __init__(self, base_url):
        self.base=base_url.rstrip('/'); self.jar=http.cookiejar.CookieJar()
        self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar)); self.csrf=''
    def _request(self,path,method='GET',payload=None,csrf=False,timeout=60):
        data=None if payload is None else json.dumps(payload).encode()
        req=urllib.request.Request(self.base+path,data=data,method=method)
        if data is not None: req.add_header('Content-Type','application/json')
        if csrf:
            req.add_header('X-Cortex-CSRF',self.csrf)
            # Loopback local client: do not send Origin. Cortex exempts loopback
            # clients from the Origin CSRF check (see auth.go sameOrigin).
        try: return self.opener.open(req,timeout=timeout)
        except Exception as e: raise CortexError(f'{method} {path}: {e}') from e
    def state(self):
        with self._request('/api/auth/state') as r: return json.load(r)
    def login(self,username,password):
        with self._request('/api/auth/login','POST',{'Username':username,'Password':password}) as r: json.load(r)
        s=self.state(); self.csrf=s.get('csrf','')
        if not s.get('authenticated') or not self.csrf: raise CortexError('login did not establish an authenticated CSRF session')
        return s
    def run(self,prompt,workspace='',client_session='benchmark'):
        payload={'prompt':prompt,'workspace':workspace,'clientSession':client_session}
        run_id=None
        out=[]
        try:
            with self._request('/api/agent/run','POST',payload,csrf=True,timeout=1800) as r:
                for raw in r:
                    line=raw.decode('utf-8','replace').strip()
                    if not line: continue
                    try: ev=json.loads(line)
                    except json.JSONDecodeError: ev={'type':'unparsed','raw':line}
                    out.append(ev)
                    if ev.get('type')=='run' and ev.get('data',{}).get('runID'):
                        run_id=ev['data']['runID']
            return out
        except Exception:
            # Never leave an orphaned server-side agent run consuming the host
            # (the VM wedges under memory pressure). Cancel best-effort.
            if run_id:
                try:
                    with self._request('/api/agent/cancel','POST',{'runID':run_id},csrf=True,timeout=30):
                        pass
                except Exception:
                    pass
            raise
