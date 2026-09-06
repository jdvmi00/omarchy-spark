"""Run inside the validation container; never print notebook tokens."""
import json
import subprocess
import socket
import urllib.parse
import urllib.request

result = subprocess.run(['jupyter', 'server', 'list', '--json'], capture_output=True, text=True, check=True)
for line in result.stdout.splitlines():
    try:
        server = json.loads(line)
    except ValueError:
        continue
    parts = urllib.parse.urlsplit(server['url'])
    if parts.hostname not in ('localhost', '127.0.0.1', '0.0.0.0', socket.gethostname()):
        continue
    path = parts.path.rstrip('/') + '/lab'
    url = urllib.parse.urlunsplit(('http', '127.0.0.1:' + str(parts.port), path, urllib.parse.urlencode({'token': server.get('token', '')}), ''))
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    with opener.open(url, timeout=10) as response:
        assert response.status == 200
        assert 'text/html' in response.headers.get('Content-Type', '')
        print('PASS: authenticated JupyterLab endpoint returns HTTP 200')
    break
else:
    raise SystemExit('No local Jupyter server found')
