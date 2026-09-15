import http.cookiejar, json, urllib.request
class CortexError(RuntimeError): pass
class CortexClient:
    def __init__(self, base_url):
        self.base=base_url.rstrip('/'); self.jar=http.cookiejar.CookieJar()
        self.opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.jar)); self.csrf=''
    def _request(self,path,method='GET',payload=None,csrf=False):
        data=None if payload is None else json.dumps(payload).encode()
        req=urllib.request.Request(self.base+path,data=data,method=method)
        if data is not None: req.add_header('Content-Type','application/json')
        if csrf:
            req.add_header('X-Cortex-CSRF',self.csrf); req.add_header('Origin',self.base)
        try: return self.opener.open(req,timeout=60)
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
        with self._request('/api/agent/run','POST',payload,csrf=True) as r:
            out=[]
            for raw in r:
                line=raw.decode('utf-8','replace').strip()
                if not line: continue
                try: out.append(json.loads(line))
                except json.JSONDecodeError: out.append({'type':'unparsed','raw':line})
            return out
