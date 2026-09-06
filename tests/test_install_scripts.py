"""The ARM patch must make Omarchy's installer scripts safe on the port's layout."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'upstream/omarchy'


class Stubs:
    """PATH stubs that record their arguments to a calls file."""

    def __init__(self, temp):
        self.dir = Path(temp) / 'stubs'
        self.dir.mkdir()
        self.calls = Path(temp) / 'calls'
        self.calls.write_text('')

    def add(self, name, body='exit 0'):
        (self.dir / name).write_text(f'#!/bin/bash\nprintf "%s\\n" "{name} $*" >> "$CALLS"\n{body}\n')
        (self.dir / name).chmod(0o755)

    def run(self, script, **extra):
        env = dict(os.environ, PATH=f'{self.dir}:/usr/bin:/bin', CALLS=str(self.calls), OMARCHY_PATH=str(SOURCE),
                   OMARCHY_INSTALL=str(SOURCE / 'install'), **extra)
        return subprocess.run(['bash', '-eE', '-c', 'source "$1"', 'bash', str(SOURCE / script)],
                              env=env, text=True, capture_output=True)

    def log(self):
        return self.calls.read_text()


class InstallerScripts(unittest.TestCase):
    def test_snapper_is_skipped_without_btrfs(self):
        with tempfile.TemporaryDirectory() as temp:
            stubs = Stubs(temp)
            stubs.add('findmnt', 'echo ext4')
            stubs.add('snapper')
            result = stubs.run('install/config/snapper.sh')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('Skipping Snapper', result.stdout)
            self.assertNotIn('snapper', stubs.log())

    def test_post_install_pacman_uses_arm_repositories_on_aarch64(self):
        for arch, expected in [('aarch64', 'spark/pacman-aarch64.conf /etc/pacman.conf'),
                               ('x86_64', 'default/pacman/pacman-stable.conf /etc/pacman.conf')]:
            with self.subTest(arch=arch), tempfile.TemporaryDirectory() as temp:
                stubs = Stubs(temp)
                stubs.add('uname', f'echo {arch}')
                for name in ('cp', 'install', 'rm', 'lspci'):
                    stubs.add(name)
                result = stubs.run('install/post-install/pacman.sh')
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(expected, stubs.log())
                if arch == 'aarch64':
                    self.assertIn('spark/mirrorlist-aarch64 /etc/pacman.d/mirrorlist', stubs.log())
                    self.assertNotIn('pacman-stable.conf', stubs.log())

    def test_firewall_keeps_enabled_remote_services_reachable(self):
        for enabled, present, absent in [
            ({'sshd.service', 'avahi-daemon.service'}, ['ufw allow in 22/tcp', 'ufw allow in 5353/udp'], ['tailscale0']),
            (set(), [], ['22/tcp', '5353/udp', 'tailscale0']),
            ({'tailscaled.service'}, ['ufw allow in on tailscale0'], ['22/tcp']),
        ]:
            with self.subTest(enabled=sorted(enabled)), tempfile.TemporaryDirectory() as temp:
                stubs = Stubs(temp)
                units = ' '.join(enabled)
                stubs.add('systemctl', f'if [[ $1 == is-enabled ]]; then [[ " {units} " == *" ${{@: -1}} "* ]]; exit $?; fi; exit 0')
                stubs.add('ufw')
                stubs.add('sed')
                stubs.add('ufw-docker', 'PATH=/usr/bin\nexit 0')
                result = stubs.run('install/config/firewall.sh')
                self.assertEqual(result.returncode, 0, result.stderr)
                log = stubs.log()
                self.assertIn('ufw default deny incoming', log)
                for line in present:
                    self.assertIn(line, log)
                for line in absent:
                    self.assertNotIn(line, log)

    def test_nvidia_leaves_dgx_spark_initramfs_alone(self):
        for kernel, expects_initramfs in [('linux-dgx-spark', False), ('linux', True)]:
            with self.subTest(kernel=kernel), tempfile.TemporaryDirectory() as temp:
                stubs = Stubs(temp)
                stubs.add('lspci', 'echo "0001:01:00.0 3D controller: NVIDIA Corporation GB10"')
                stubs.add('pacman', f'echo {kernel}')
                stubs.add('omarchy-pkg-add')
                stubs.add('omarchy-hw-nvidia-gsp')
                stubs.add('uname', 'echo aarch64')
                modprobe, mkinitcpio = Path(temp) / 'modprobe.d', Path(temp) / 'mkinitcpio.conf.d'
                result = stubs.run('install/hardware/nvidia.sh', OMARCHY_MODPROBE_DIR=str(modprobe),
                                   OMARCHY_MKINITCPIO_DIR=str(mkinitcpio))
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(f'omarchy-pkg-add {kernel}-headers', stubs.log())
                self.assertIn('omarchy-pkg-add nvidia-open-dkms nvidia-utils libva-nvidia-driver\n', stubs.log())
                self.assertEqual((modprobe / 'nvidia.conf').read_text(), 'options nvidia_drm modeset=1\n')
                self.assertEqual((mkinitcpio / 'nvidia.conf').exists(), expects_initramfs)


if __name__ == '__main__':
    unittest.main()
