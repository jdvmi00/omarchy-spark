import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/fetch-sources.py'


class VerifiedSourceDownloads(unittest.TestCase):
    def test_hash_algorithms_cache_repair_and_rejection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'source'
            source.write_bytes(b'verified source fixture\n')
            manifest = root / 'manifest.json'
            output = root / 'out'

            def fetch(destination):
                return subprocess.run(['python3', str(SCRIPT), str(manifest),
                                       str(destination)], capture_output=True)

            for algorithm in ('sha256', 'sha512'):
                entry = dict(url=source.as_uri(), filename='fixture',
                             size=source.stat().st_size, hash_algorithm=algorithm,
                             hash=hashlib.new(algorithm, source.read_bytes()).hexdigest())
                manifest.write_text(json.dumps([entry]))
                self.assertEqual(fetch(output).returncode, 0)
                self.assertEqual((output / 'fixture').read_bytes(), source.read_bytes())
                (output / 'fixture').write_bytes(b'corrupt')
                self.assertEqual(fetch(output).returncode, 0)
                self.assertEqual((output / 'fixture').read_bytes(), source.read_bytes())

            entry['hash'] = '0' * 128
            manifest.write_text(json.dumps([entry]))
            self.assertNotEqual(fetch(root / 'reject').returncode, 0)
            self.assertFalse((root / 'reject/fixture').exists())
            self.assertFalse((root / 'reject/fixture.partial').exists())


if __name__ == '__main__':
    unittest.main()
