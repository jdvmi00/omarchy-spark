import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'upstream/omarchy'


class RefreshArchitecture(unittest.TestCase):
    def test_architecture_channels_and_copy_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            commands = {
                'uname': '#!/bin/bash\necho "$TEST_ARCH"\n',
                'sudo': '#!/bin/bash\nprintf "%s\\n" "$*" >> "$CALLS"\n'
                        'if [[ ${FAIL_COPY:-} == yes && $1 == cp ]]; then exit 1; fi\n',
                'omarchy-hook': '#!/bin/bash\nprintf "hook %s\\n" "$*" >> "$CALLS"\n',
            }
            for name, body in commands.items():
                path = temp / name
                path.write_text(body)
                path.chmod(0o755)
            for arch, channel, failure in [('aarch64', 'stable', False),
                                           ('x86_64', 'rc', False),
                                           ('aarch64', 'edge', False),
                                           ('aarch64', 'invalid', False),
                                           ('aarch64', 'stable', True)]:
                with self.subTest(arch=arch, channel=channel, failure=failure):
                    calls = temp / 'calls'
                    calls.write_text('')
                    env = dict(os.environ, PATH=f'{temp}:/usr/bin:/bin',
                               TEST_ARCH=arch, OMARCHY_PATH=str(SOURCE),
                               CALLS=str(calls), FAIL_COPY='yes' if failure else 'no')
                    result = subprocess.run(['bash', str(SOURCE / 'bin/omarchy-refresh-pacman'), channel],
                                            env=env, text=True, capture_output=True)
                    log = calls.read_text()
                    if failure or (arch == 'aarch64' and channel != 'stable'):
                        self.assertNotEqual(result.returncode, 0)
                        self.assertNotIn('pacman -Syyuu', log)
                    else:
                        self.assertEqual(result.returncode, 0, result.stderr)
                        expected = 'aarch64' if arch == 'aarch64' else channel
                        self.assertIn(f'pacman-{expected}.conf /etc/pacman.conf', log)
                        self.assertIn(f'mirrorlist-{expected} /etc/pacman.d/mirrorlist', log)
                        self.assertIn('pacman -Syyuu', log)
        config = (SOURCE / 'spark/pacman-aarch64.conf').read_text()
        self.assertNotIn('[multilib]', config)
        self.assertIn('SigLevel = Required DatabaseOptional', config)
        self.assertNotIn('TrustAll', config)
        self.assertNotIn('pkgs.omarchy.org/stable', config)
