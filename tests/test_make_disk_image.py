"""The image assembler must never alias or overwrite its manifest sidecar."""
import contextlib
import importlib.machinery
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

path = Path(__file__).resolve().parents[1] / 'image/make-disk-image.py'
loader = importlib.machinery.SourceFileLoader('make_disk_image', str(path))
spec = importlib.util.spec_from_loader(loader.name, loader)
module = importlib.util.module_from_spec(spec)
loader.exec_module(module)
UUID = '6ea849d5-f6cc-4652-9af8-ecdc172b0bf1'


class Sidecar(unittest.TestCase):
    def test_manifest_sits_beside_image_and_never_is_the_image(self):
        self.assertEqual(module.sidecar_path(Path('/out/spark.img')), Path('/out/spark.json'))
        self.assertEqual(module.sidecar_path(Path('/out/spark')), Path('/out/spark.json'))
        with self.assertRaises(ValueError):
            module.sidecar_path(Path('/out/spark.json'))

    def test_refusals_happen_before_anything_is_created(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            (temp / 'root').mkdir()
            (temp / 'boot.efi').write_bytes(b'efi')
            existing = temp / 'spark.json'
            existing.write_text('{"keep": true}\n')
            for output in ('spark.img', 'spark.json'):
                with self.subTest(output=output):
                    argv = ['make-disk-image', str(temp / 'root'), str(temp / 'boot.efi'), str(temp / output), '--root-uuid', UUID]
                    with patch.object(module.sys, 'argv', argv), contextlib.redirect_stderr(io.StringIO()), \
                            self.assertRaises(SystemExit) as raised:
                        module.main()
                    self.assertNotEqual(raised.exception.code, 0)
                    self.assertEqual(existing.read_text(), '{"keep": true}\n')
                    self.assertFalse((temp / 'spark.img').exists())


if __name__ == '__main__':
    unittest.main()
