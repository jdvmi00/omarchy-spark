"""The settings scriptlet must not discard administrator edits to /etc files."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPTLET = Path(__file__).resolve().parents[1] / 'packages/omarchy-settings/omarchy-settings.install'
OVERRIDES = {
    'os-release': 'ID=omarchy\n',
    'security-faillock.conf': 'deny = 10\n',
    'nsswitch.conf': 'hosts: files omarchy dns\n',
    'plymouth-plymouthd.conf': 'Theme=omarchy\n',
    'dot.bashrc': 'omarchy bashrc\n',
}
LIVE = {
    'os-release': 'etc/os-release',
    'security-faillock.conf': 'etc/security/faillock.conf',
    'nsswitch.conf': 'etc/nsswitch.conf',
    'plymouth-plymouthd.conf': 'etc/plymouth/plymouthd.conf',
    'dot.bashrc': 'etc/skel/.bashrc',
}
STOCK_NSSWITCH = 'hosts: files dns\n'


def stage(root):
    """A stock Arch root: os-release link, filesystem-owned nsswitch.conf, package overrides."""
    for name, content in OVERRIDES.items():
        path = root / 'usr/share/omarchy/etc-overrides' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    (root / 'usr/lib').mkdir(parents=True)
    (root / 'usr/lib/os-release').write_text('ID=arch\n')
    (root / 'etc').mkdir()
    os.symlink('../usr/lib/os-release', root / 'etc/os-release')
    (root / 'etc/nsswitch.conf').write_text(STOCK_NSSWITCH)
    db = root / 'var/lib/pacman/local/filesystem-2025.10.12-1'
    db.mkdir(parents=True)
    checksum = hashlib.md5(STOCK_NSSWITCH.encode()).hexdigest()
    (db / 'files').write_text(f'%FILES%\netc/\netc/nsswitch.conf\n\n%BACKUP%\netc/nsswitch.conf\t{checksum}\n')
    stubs = root / 'stubs'
    stubs.mkdir()
    (stubs / 'uname').write_text('#!/bin/sh\necho x86_64\n')
    (stubs / 'uname').chmod(0o755)


def apply(root):
    env = dict(os.environ, PATH=f'{root / "stubs"}:/usr/bin:/bin')
    script = 'source "$1"; _etc_overrides_root="$2"; _etc_overrides_apply'
    return subprocess.run(['bash', '-c', script, 'scriptlet', str(SCRIPTLET), str(root)],
                          env=env, text=True, capture_output=True, check=True)


def pacnews(root):
    return sorted(str(p.relative_to(root)) for p in (root / 'etc').rglob('*.pacnew'))


class EtcOverrides(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        stage(self.root)

    def tearDown(self):
        self.temp.cleanup()

    def test_fresh_system_receives_every_override(self):
        result = apply(self.root)
        for name, live in LIVE.items():
            with self.subTest(name=name):
                path = self.root / live
                self.assertFalse(path.is_symlink())
                self.assertEqual(path.read_text(), OVERRIDES[name])
                self.assertEqual(path.stat().st_mode & 0o777, 0o644)
                self.assertEqual((self.root / 'var/lib/omarchy/etc-overrides' / f'{name}.sha256').read_text().strip(),
                                 hashlib.sha256(OVERRIDES[name].encode()).hexdigest())
        self.assertEqual(pacnews(self.root), [])
        self.assertNotIn('WARNING', result.stdout)
        self.assertEqual((self.root / 'usr/lib/os-release').read_text(), 'ID=arch\n')

    def test_reapplying_changes_nothing(self):
        apply(self.root)
        before = {live: (self.root / live).stat().st_mtime_ns for live in LIVE.values()}
        apply(self.root)
        after = {live: (self.root / live).stat().st_mtime_ns for live in LIVE.values()}
        self.assertEqual(before, after)
        self.assertEqual(pacnews(self.root), [])

    def test_upgrade_keeps_administrator_edits_and_replaces_untouched_files(self):
        apply(self.root)
        edited = 'hosts: files ldap dns\n'
        (self.root / 'etc/nsswitch.conf').write_text(edited)
        overrides = self.root / 'usr/share/omarchy/etc-overrides'
        (overrides / 'nsswitch.conf').write_text('hosts: files omarchy mdns dns\n')
        (overrides / 'security-faillock.conf').write_text('deny = 5\n')
        result = apply(self.root)
        self.assertEqual((self.root / 'etc/nsswitch.conf').read_text(), edited)
        self.assertEqual((self.root / 'etc/nsswitch.conf.pacnew').read_text(), 'hosts: files omarchy mdns dns\n')
        self.assertIn('/etc/nsswitch.conf.pacnew', result.stdout)
        self.assertEqual((self.root / 'etc/security/faillock.conf').read_text(), 'deny = 5\n')
        self.assertEqual(pacnews(self.root), ['etc/nsswitch.conf.pacnew'])
        # A later merge that adopts the packaged content is recognized silently.
        (self.root / 'etc/nsswitch.conf').write_text('hosts: files omarchy mdns dns\n')
        (self.root / 'etc/nsswitch.conf.pacnew').unlink()
        result = apply(self.root)
        self.assertNotIn('WARNING', result.stdout)
        self.assertEqual(pacnews(self.root), [])

    def test_first_install_keeps_files_already_customized(self):
        custom_nss = 'hosts: files sss dns\n'
        (self.root / 'etc/nsswitch.conf').write_text(custom_nss)
        (self.root / 'etc/os-release').unlink()
        (self.root / 'etc/os-release').write_text('ID=custom\n')
        (self.root / 'etc/skel').mkdir()
        os.symlink('/srv/shared-bashrc', self.root / 'etc/skel/.bashrc')
        result = apply(self.root)
        self.assertEqual((self.root / 'etc/nsswitch.conf').read_text(), custom_nss)
        self.assertEqual((self.root / 'etc/os-release').read_text(), 'ID=custom\n')
        self.assertEqual(os.readlink(self.root / 'etc/skel/.bashrc'), '/srv/shared-bashrc')
        self.assertEqual(pacnews(self.root), ['etc/nsswitch.conf.pacnew', 'etc/os-release.pacnew', 'etc/skel/.bashrc.pacnew'])
        for line in ('/etc/nsswitch.conf.pacnew', '/etc/os-release.pacnew', '/etc/skel/.bashrc.pacnew'):
            self.assertIn(line, result.stdout)
        state = self.root / 'var/lib/omarchy/etc-overrides'
        self.assertEqual(sorted(p.name for p in state.iterdir()),
                         ['plymouth-plymouthd.conf.sha256', 'security-faillock.conf.sha256'])
        self.assertEqual((self.root / 'etc/security/faillock.conf').read_text(), OVERRIDES['security-faillock.conf'])


if __name__ == '__main__':
    unittest.main()
