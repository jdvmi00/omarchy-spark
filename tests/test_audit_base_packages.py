"""The base-package audit must tier unavailable packages by what the port can act on."""
import contextlib
import importlib.machinery
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / 'scripts/audit-base-packages.py'
loader = importlib.machinery.SourceFileLoader('audit_base_packages', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)


class Classification(unittest.TestCase):
    def test_tiers_follow_recipe_architecture_and_port_coverage(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            for name, arch in [('ttfx', "arch=('x86_64' 'aarch64')"), ('x86tool', "arch=('x86_64')"), ('fonts', "arch=('any')")]:
                (temp / name).mkdir()
                (temp / name / 'PKGBUILD').write_text(f'pkgname={name}\n{arch}\n')
            probe = temp / 'probe.json'
            probe.write_text(json.dumps({'generated': '2026-09-06', 'host_arch': 'aarch64', 'installed': ['foot'],
                                         'available': ['cups'], 'unavailable': ['ttfx', 'x86tool', 'fonts', 'obsidian', 'qemu-user-static-binfmt']}))
            args = type('Args', (), {'probe': str(probe), 'pkgbuilds': str(temp)})()
            out = io.StringIO()
            with contextlib.redirect_stdout(out):
                module.classify(args)
            manifest = json.loads(out.getvalue())
        tiers = {e['name']: e['tier'] for e in manifest['unavailable']}
        self.assertEqual(tiers, {'ttfx': 'omarchy-recipe', 'x86tool': 'omarchy-x86-only', 'fonts': 'omarchy-recipe',
                                 'obsidian': 'external', 'qemu-user-static-binfmt': 'not-applicable'})
        self.assertEqual(manifest['counts'], {'total': 7, 'installed': 1, 'available_not_installed': 1, 'unavailable': 5})
        ported = [e for e in manifest['unavailable'] if e['name'] == 'ttfx'][0]
        self.assertEqual(ported.get('port_recipe'), 'packages/ttfx')

    def test_probe_reports_each_state_without_installing(self):
        calls = []

        def run(argv, **kwargs):
            calls.append(argv)
            if argv[1] == '-T':
                return type('R', (), {'returncode': 0 if argv[-1] == 'foot' else 1})()
            return type('R', (), {'returncode': 0 if argv[-1] == 'cups' else 1})()

        with tempfile.TemporaryDirectory() as temp:
            base = Path(temp) / 'base.packages'
            base.write_text('# comment\nfoot\ncups\nttfx\n\n')
            out = io.StringIO()
            with patch.object(module.subprocess, 'run', side_effect=run), \
                    patch.object(module.subprocess, 'check_output', return_value='aarch64\n'), contextlib.redirect_stdout(out):
                module.probe(type('Args', (), {'base_list': str(base)})())
        report = json.loads(out.getvalue())
        self.assertEqual((report['installed'], report['available'], report['unavailable']), (['foot'], ['cups'], ['ttfx']))
        self.assertTrue(all(argv[1] in ('-T', '-Sp') for argv in calls), calls)


if __name__ == '__main__':
    unittest.main()
