"""Browser view of the local lab results."""
import argparse,datetime,html,json
from http.server import BaseHTTPRequestHandler,HTTPServer
from pathlib import Path
from urllib.parse import urlparse,parse_qs
import lab
ROOT=Path(__file__).parent
VIEWS={'identity': 'Who can retrieve this secret?', 'containment': 'What else can this workload reach?'}

def report(view):
    return lab.evaluate()

def page(view):
    r=report(view);esc=lambda s:html.escape(str(s));stage='before' if view=='before' else 'after'
    title=VIEWS[view]
    if 'findings' in r:
        rows=''.join('<tr><td><strong>'+esc(f['id'])+'</strong><small>'+esc(f['file'])+':'+str(f['line'])+'</small></td><td><b class="'+f['outcome'].lower()+'">'+f['outcome']+'</b></td><td>'+esc(f['remediation'])+'<small>Owner: '+esc(f['owner'])+(' · exception expires '+esc(f['exception']['expires']) if f['exception'] else '')+'</small></td></tr>' for f in r['findings'])
        content='<div class="summary">'+esc(r['status'])+' · '+esc(r['counts']['BLOCK'])+' block · '+esc(r['counts']['WARN'])+' warn · '+esc(r['counts']['TRACK'])+' track</div><table><thead><tr><th>Finding / location</th><th>Decision</th><th>Fix and ownership</th></tr></thead><tbody>'+rows+'</tbody></table>'
        detail='The check reads fixture files. Dependency and analysis findings are synthetic; the credential marker cannot authenticate.'
    else:
        rows=''.join('<tr><td>'+esc(c['name'])+'</td><td><b class="'+c['before'].lower()+'">'+c['before']+'</b></td><td><b class="'+c['after'].lower()+'">'+c['after']+'</b></td></tr>' for c in r['checks'] if not (view=='identity' and 'secret' not in c['name'].lower()))
        content='<table><thead><tr><th>Controlled test</th><th>Before</th><th>After</th></tr></thead><tbody>'+rows+'</tbody></table>'
        if 'subject' in r.get('after',{}):
            detail=('Broad subject before hardening: '+r['before']['subject']) if view=='before' else ('Exact subject after hardening: '+r['after']['subject'])
            content+='<h2>Workflow '+('before' if view=='before' else 'after')+' hardening</h2><p><code>'+esc(r[stage]['workflow_permissions'])+'</code></p><p>'+esc(r[stage]['action_reference'])+'</p>'
        else:
            detail='Action/Resource subset model only. Synthetic ARNs. No JWT authentication, AWS SDK requests, or CloudTrail events.'
            content+='<h2>Workload identity</h2><p>Secret references in configuration · no static access keys · no secret values displayed</p>'
    links=''.join('<a '+('aria-current="page" ' if k==view else '')+'href="/?view='+k+'">'+esc(v)+'</a>' for k,v in VIEWS.items())
    doc='''<!doctype html><html><head><meta charset="utf-8"><title>360TrustLab local demo</title><style>
    *{box-sizing:border-box}body{margin:0;background:#f8fafc;color:#142337;font:22px Arial,sans-serif}header{background:#142337;color:white;padding:22px 40px;display:flex;justify-content:space-between}header span{color:#9fdfda;font-size:18px}main{margin:28px 40px;max-width:1400px}nav{display:flex;gap:20px;font-size:16px;margin-bottom:25px}a{color:#255d6a;padding:8px 0;text-decoration:none}a[aria-current]{border-bottom:3px solid #459b9c;font-weight:bold}h1{font-size:38px;line-height:1.15;margin:15px 0}h2{font-size:24px;margin:24px 0 8px}.scope{font-size:16px;font-weight:bold;color:#73531b;margin:12px 0 24px}table{width:100%;border-collapse:collapse;background:white;font-size:21px;line-height:1.4}th{text-align:left;background:#e6eeef;font-size:17px}th,td{padding:16px 18px;border-bottom:1px solid #ccd5db;vertical-align:top}td:first-child{width:39%}b{font-size:18px}.allow,.pass,.track{color:#12664b}.deny,.block,.fail{color:#b12f2d}.warn{color:#8c5d00}small{display:block;font-size:15px;color:#506274;margin-top:7px;line-height:1.4}.summary{font-size:24px;font-weight:bold;margin:18px 0}.detail{background:#e6eeef;border-left:5px solid #459b9c;padding:16px;font-size:17px;line-height:1.45;overflow-wrap:anywhere}footer{font-size:15px;color:#506274;margin-top:20px}p{font-size:20px;margin:8px 0}code,pre{font-family:"Lucida Console",monospace}code{font-size:.9em}pre{white-space:pre-wrap;overflow-wrap:anywhere}
    </style></head><body><header><strong>360TrustLab</strong><span>Live! 360 Orlando 2026 · Local lab</span></header><main>'''
    doc+='<nav>'+links+'</nav><h1>'+esc(title)+'</h1><div class="scope">'+esc(r['scope'])+'</div>'+content+'<p class="detail">'+esc(detail)+'</p><footer>Actual output of this local Python lab · '+esc(datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'))+' · Cloud deployment has not been run</footer></main></body></html>'
    return doc
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        q=parse_qs(urlparse(self.path).query);view=q.get('view',[next(iter(VIEWS))])[0]
        if view not in VIEWS:self.send_error(404);return
        if urlparse(self.path).path=='/report.json':body=json.dumps(report(view),indent=2).encode();ct='application/json'
        else:body=page(view).encode();ct='text/html; charset=utf-8'
        self.send_response(200);self.send_header('Content-Type',ct);self.send_header('Content-Length',str(len(body)));self.end_headers();self.wfile.write(body)
    def log_message(self,*args):pass
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--port',type=int,default=8765);a=p.parse_args();print(f'Local lab viewer: http://127.0.0.1:{a.port}',flush=True);HTTPServer(('127.0.0.1',a.port),Handler).serve_forever()
