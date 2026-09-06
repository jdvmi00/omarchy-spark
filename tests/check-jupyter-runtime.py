"""Run inside the validation container; prove the notebook server enforces its token.

Positive checks send the server token in an Authorization header and expect the
contents API, the status API and the JupyterLab page to answer directly.
Negative checks repeat the contents request with no token and with a wrong
token and expect a refusal. Redirects are never followed, so a login page can
never pass as notebook content. Tokens are never printed.
"""
import json
import secrets
import socket
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

LOCAL_HOSTS = ('localhost', '127.0.0.1', '0.0.0.0')


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def request(url, token=None, timeout=10):
    """Return (status, content type, body) without following redirects or proxies."""
    headers = {'Authorization': 'token ' + token} if token is not None else {}
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect)
    try:
        with opener.open(urllib.request.Request(url, headers=headers), timeout=timeout) as response:
            return response.status, response.headers.get('Content-Type', ''), response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get('Content-Type', ''), error.read()


def parse_json(content_type, body):
    if 'application/json' not in content_type:
        return None
    try:
        return json.loads(body)
    except ValueError:
        return None


def check(base, token):
    """Raise SystemExit describing the first failed expectation; return PASS lines."""
    if not token:
        raise SystemExit('FAIL: the server runs without a token; authentication enforcement cannot be shown')
    passed = []
    contents = base + '/api/contents/'

    status, content_type, body = request(contents, token)
    listing = parse_json(content_type, body)
    if status != 200 or not isinstance(listing, dict) or listing.get('type') != 'directory' or 'content' not in listing:
        raise SystemExit(f'FAIL: authenticated contents request returned HTTP {status} without a directory listing')
    passed.append('PASS: authenticated contents API lists the notebook directory')

    status, content_type, body = request(base + '/api/status', token)
    info = parse_json(content_type, body)
    if status != 200 or not isinstance(info, dict) or 'started' not in info:
        raise SystemExit(f'FAIL: authenticated status request returned HTTP {status}')
    passed.append('PASS: authenticated status API answers')

    status, content_type, body = request(base + '/lab', token)
    if status != 200 or 'text/html' not in content_type:
        raise SystemExit(f'FAIL: authenticated JupyterLab page returned HTTP {status} instead of the application')
    passed.append('PASS: authenticated JupyterLab page is served directly, without a login redirect')

    for label, bad in (('no token', None), ('a wrong token', secrets.token_hex(24))):
        status, content_type, body = request(contents, bad)
        leaked = parse_json(content_type, body)
        if status == 200 or (isinstance(leaked, dict) and leaked.get('type') == 'directory'):
            raise SystemExit(f'FAIL: contents request with {label} returned HTTP {status}; authentication is not enforced')
        if status not in (401, 403) and not 300 <= status < 400:
            raise SystemExit(f'FAIL: contents request with {label} returned unexpected HTTP {status}')
        passed.append(f'PASS: contents request with {label} is refused with HTTP {status}')
    return passed


def local_servers():
    result = subprocess.run(['jupyter', 'server', 'list', '--json'], capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        try:
            server = json.loads(line)
        except ValueError:
            continue
        parts = urllib.parse.urlsplit(server['url'])
        if parts.hostname not in LOCAL_HOSTS + (socket.gethostname(),):
            continue
        base = urllib.parse.urlunsplit(('http', f'127.0.0.1:{parts.port or 80}', parts.path.rstrip('/'), '', ''))
        yield base, server.get('token', '')


def main():
    for base, token in local_servers():
        for line in check(base, token):
            print(line)
        return 0
    raise SystemExit('No local Jupyter server found')


if __name__ == '__main__':
    sys.exit(main())
