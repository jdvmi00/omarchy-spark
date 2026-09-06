import os
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'upstream/arch-dgx-spark-iso/airootfs/root/limine-hooks/limine-mkconfig'


class LimineConfiguration(unittest.TestCase):
    def test_root_filesystems_and_missing_uuid(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            binaries, boot = root / 'bin', root / 'boot'
            binaries.mkdir()
            boot.mkdir()
            findmnt = binaries / 'findmnt'
            findmnt.write_text('''#!/bin/sh
case "$3" in
UUID) printf '%s\\n' "$TEST_ROOT_UUID";;
FSTYPE) printf '%s\\n' "$TEST_ROOT_FSTYPE";;
FSROOT) printf '%s\\n' "$TEST_ROOT_FSROOT";;
*) exit 1;;
esac
''')
            findmnt.chmod(0o755)
            (boot / 'vmlinuz-linux-dgx-spark').write_bytes(b'fixture')
            (boot / 'initramfs-linux-dgx-spark.img').write_bytes(b'fixture')
            env = dict(os.environ, PATH=f'{binaries}:{os.environ["PATH"]}',
                       DGX_SPARK_BOOT_DIR=str(boot), TEST_ROOT_UUID='test-uuid',
                       TEST_ROOT_FSTYPE='ext4', TEST_ROOT_FSROOT='/')
            subprocess.run(['bash', str(SCRIPT)], env=env, check=True, capture_output=True)
            self.assertIn('root=UUID=test-uuid', (boot / 'limine.conf').read_text())
            env.update(TEST_ROOT_FSTYPE='btrfs', TEST_ROOT_FSROOT='/@')
            subprocess.run(['bash', str(SCRIPT)], env=env, check=True, capture_output=True)
            before = (boot / 'limine.conf').read_text()
            self.assertIn('rootflags=subvol=/@ ', before)
            env['TEST_ROOT_UUID'] = ''
            result = subprocess.run(['bash', str(SCRIPT)], env=env, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual((boot / 'limine.conf').read_text(), before)


if __name__ == '__main__':
    unittest.main()
