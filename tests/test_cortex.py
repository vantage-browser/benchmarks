import json, threading
from http.server import BaseHTTPRequestHandler,HTTPServer
from harness.cortex import CortexClient
class H(BaseHTTPRequestHandler):
 def log_message(self,*a): pass
 def do_GET(self):
  if self.path=='/api/auth/state':
   b=json.dumps({'authenticated':True,'csrf':'abc'}).encode(); self.send_response(200); self.send_header('Content-Type','application/json'); self.end_headers(); self.wfile.write(b)
 def do_POST(self):
  n=int(self.headers.get('Content-Length','0')); self.rfile.read(n)
  if self.path=='/api/auth/login':
   self.send_response(200); self.send_header('Set-Cookie','cortex_session=x'); self.end_headers(); self.wfile.write(b'{"ok":true}')
  elif self.path=='/api/agent/run':
   assert self.headers.get('X-Cortex-CSRF')=='abc'; self.send_response(200); self.end_headers(); self.wfile.write(b'{"type":"text","text":"ok"}\n')
def test_client():
 s=HTTPServer(('127.0.0.1',0),H); threading.Thread(target=s.serve_forever,daemon=True).start()
 c=CortexClient(f'http://127.0.0.1:{s.server_port}'); c.login('admin','password'); e=c.run('x'); s.shutdown(); assert e[0]['text']=='ok'
