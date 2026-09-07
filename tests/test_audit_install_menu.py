"""The Install menu audit must map entries to packages and tier them honestly."""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'upstream/omarchy'
path = ROOT / 'scripts/audit-install-menu.py'
loader = importlib.machinery.SourceFileLoader('audit_install_menu', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


def run(func, args):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        func(type('Args', (), args)())
    return json.loads(out.getvalue())


class InstallMenuAudit(unittest.TestCase):
    def test_extract_maps_entries_to_packages(self):
        data = run(module.extract, {'menu': str(SOURCE / 'default/omarchy/omarchy-menu.jsonc'), 'bindir': str(SOURCE / 'bin')})
        by = {e['entry']: e for e in data['entries']}
        self.assertEqual(by['install.terminal.ghostty']['packages'], ['ghostty'])
        self.assertEqual(by['install.browser.firefox']['packages'], ['firefox'])
        self.assertEqual(by['install.service.bitwarden']['packages'], ['bitwarden', 'bitwarden-cli'])
        self.assertEqual(by['install.style.font.fira']['packages'], ['ttf-firacode-nerd'])
        self.assertEqual(by['install.package']['note'], 'interactive')
        self.assertIn('mise', by['install.development.go']['note'])
        self.assertTrue(all(';' not in p for e in data['entries'] for p in e['packages']))
        self.assertFalse([e for e in data['entries'] if e['note'].startswith('unhandled')])

    def test_classify_tiers_by_worst_package(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            (temp / 'buildme').mkdir(); (temp / 'buildme/PKGBUILD').write_text("arch=('x86_64' 'aarch64')\n")
            (temp / 'x86only').mkdir(); (temp / 'x86only/PKGBUILD').write_text("arch=('x86_64')\n")
            probe = temp / 'probe.json'
            probe.write_text(json.dumps({'host_arch': 'aarch64', 'status': {
                'foot': 'installed', 'kitty': 'available', 'ghostty': 'unavailable', 'buildme': 'unavailable',
                'x86only': 'unavailable', 'vendor': 'unavailable'},
                'entries': [
                    {'entry': 'install.terminal.foot', 'label': 'Foot', 'packages': ['foot'], 'note': ''},
                    {'entry': 'install.terminal.kitty', 'label': 'Kitty', 'packages': ['kitty'], 'note': ''},
                    {'entry': 'install.terminal.ghostty', 'label': 'Ghostty', 'packages': ['ghostty'], 'note': ''},
                    {'entry': 'install.service.a', 'label': 'A', 'packages': ['buildme', 'kitty'], 'note': ''},
                    {'entry': 'install.service.b', 'label': 'B', 'packages': ['x86only'], 'note': ''},
                    {'entry': 'install.service.c', 'label': 'C', 'packages': ['vendor', 'buildme'], 'note': ''},
                    {'entry': 'install.package', 'label': 'Package', 'packages': [], 'note': 'interactive'},
                    {'entry': 'install.gaming.steam', 'label': 'Steam', 'packages': ['vendor'], 'note': ''},
                ]}))
            out = run(module.classify, {'probe': str(probe), 'pkgbuilds': str(temp)})
        tiers = {e['entry']: e['tier'] for e in out['entries']}
        self.assertEqual(tiers, {'install.terminal.foot': 'works', 'install.terminal.kitty': 'works',
                                 'install.terminal.ghostty': 'port-recipe', 'install.service.a': 'buildable',
                                 'install.service.b': 'no-arm-build', 'install.service.c': 'no-arm-build',
                                 'install.package': 'interactive', 'install.gaming.steam': 'not-applicable'})


if __name__ == '__main__':
    unittest.main()
