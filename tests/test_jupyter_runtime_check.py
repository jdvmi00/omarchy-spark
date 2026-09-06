"""The notebook probe must prove token enforcement and never accept a login page."""
import contextlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import threading
import unittest
import unittest.mock
from urllib.parse import urlsplit

path = Path(__file__).resolve().parents[1] / 'tests/check-jupyter-runtime.py'
loader = importlib.machinery.SourceFileLoader('jupyter_runtime_check', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)
TOKEN = 'c0ffee5ecret70ken0123456789abcdef'


class Jupyter(BaseHTTPRequestHandler):
    """Minimal imitation of jupyter_server's token handling."""

    def authenticated(self):
        return self.headers.get('Authorization') == 'token ' + TOKEN

    def reply(self, status, content_type, body, location=None):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        if location:
            self.send_header('Location', location)
        self.end_headers()
        self.wfile.write(body.encode())

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == '/login':
            return self.reply(200, 'text/html; charset=UTF-8', '<html><form>password</form></html>')
        if not self.authenticated():
            if route.startswith('/api/'):
                return self.reply(403, 'application/json', json.dumps({'message': 'Forbidden'}))
            return self.reply(302, 'text/html; charset=UTF-8', '', location='/login?next=' + route)
        if route == '/api/contents/':
            return self.reply(200, 'application/json', json.dumps({'name': '', 'path': '', 'type': 'directory', 'content': []}))
        if route == '/api/status':
            return self.reply(200, 'application/json', json.dumps({'started': '2026-09-06T00:00:00Z', 'kernels': 0}))
        if route == '/lab':
            return self.reply(200, 'text/html; charset=UTF-8', '<html><body class="jp-Lab">lab</body></html>')
        self.reply(404, 'application/json', json.dumps({'message': 'Not found'}))

    def log_message(self, *args):
        pass


class Unenforced(Jupyter):
    def authenticated(self):
        return True


class AnyTokenAccepted(Jupyter):
    def authenticated(self):
        return self.headers.get('Authorization', '').startswith('token ')


class LoginWall(Jupyter):
    def do_GET(self):
        if urlsplit(self.path).path == '/login':
            return self.reply(200, 'text/html; charset=UTF-8', '<html>login</html>')
        self.reply(302, 'text/html; charset=UTF-8', '', location='/login')


@contextlib.contextmanager
def serve(handler):
    server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f'http://127.0.0.1:{server.server_address[1]}'
    finally:
        server.shutdown()
        server.server_close()


class NotebookProbe(unittest.TestCase):
    def probe(self, handler, token=TOKEN):
        output = io.StringIO()
        with serve(handler) as base, contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            try:
                return module.check(base, token), output.getvalue(), None
            except SystemExit as raised:
                return None, output.getvalue(), str(raised)

    def test_enforcing_server_passes_without_printing_the_token(self):
        passed, output, failure = self.probe(Jupyter)
        self.assertIsNone(failure)
        self.assertEqual(len(passed), 5)
        self.assertTrue(all(line.startswith('PASS: ') for line in passed))
        self.assertNotIn(TOKEN, '\n'.join(passed) + output)

    def test_server_without_enforcement_fails(self):
        passed, output, failure = self.probe(Unenforced)
        self.assertIsNone(passed)
        self.assertIn('no token', failure)
        self.assertNotIn(TOKEN, failure + output)

    def test_server_accepting_any_token_fails(self):
        passed, output, failure = self.probe(AnyTokenAccepted)
        self.assertIsNone(passed)
        self.assertIn('wrong token', failure)
        self.assertNotIn(TOKEN, failure + output)

    def test_login_page_is_not_notebook_content(self):
        passed, output, failure = self.probe(LoginWall)
        self.assertIsNone(passed)
        self.assertIn('HTTP 302', failure)

    def test_missing_token_fails_before_any_request(self):
        passed, output, failure = self.probe(LoginWall, token='')
        self.assertIsNone(passed)
        self.assertIn('without a token', failure)

    def test_only_local_servers_are_probed(self):
        lines = [json.dumps({'url': 'http://remote.example:8888/', 'token': 'x'}),
                 'not json',
                 json.dumps({'url': 'http://localhost:8888/prefix/', 'token': 'local-token'})]
        with unittest.mock.patch.object(module.subprocess, 'run') as run:
            run.return_value.stdout = '\n'.join(lines)
            self.assertEqual(list(module.local_servers()), [('http://127.0.0.1:8888/prefix', 'local-token')])


if __name__ == '__main__':
    unittest.main()
