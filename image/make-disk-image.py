#!/usr/bin/env python3
"""Assemble a GPT/EFI/ext4 image using regular files only; never writes devices."""
import argparse
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import uuid


def run(*args):
    subprocess.run([str(a) for a in args], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path, help='staged, root-owned filesystem')
    parser.add_argument('efi', type=Path, help='ARM64 removable EFI bootloader')
    parser.add_argument('output', type=Path, help='new regular image file')
    parser.add_argument('--root-uuid', required=True, type=uuid.UUID)
    parser.add_argument('--size-gib', type=int, default=24)
    args = parser.parse_args()
    if not args.root.is_dir() or not args.efi.is_file():
        parser.error('root directory and EFI file must exist')
    if args.size_gib < 4:
        parser.error('image must be at least 4 GiB')
    for binary in ['sgdisk', 'mkfs.fat', 'mcopy', 'mmd', 'mke2fs', 'e2fsck']:
        if not shutil.which(binary):
            parser.error(f'missing command: {binary}')
    # O_EXCL refuses existing files, symlinks and devices before any writes.
    fd = os.open(args.output, os.O_RDWR | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise ValueError('output is not a regular file')
        os.ftruncate(fd, args.size_gib * 1024**3)
        esp_start = 2048
        esp_sectors = 1024 * 1024  # 512 MiB
        root_start = esp_start + esp_sectors
        root_end = args.size_gib * 1024**3 // 512 - 34
        run('sgdisk', '--clear', f'--new=1:{esp_start}:{root_start - 1}',
            '--typecode=1:ef00', '--change-name=1:SPARK_EFI',
            f'--new=2:{root_start}:{root_end}', '--typecode=2:8300',
            '--change-name=2:SPARK_ARCH', args.output)
        with tempfile.TemporaryDirectory(prefix='spark-image-', dir=args.output.parent) as tmp:
            tmp = Path(tmp)
            esp = tmp / 'esp.img'
            root = tmp / 'root.img'
            with esp.open('xb') as f:
                f.truncate(esp_sectors * 512)
            run('mkfs.fat', '-F', '32', '-n', 'SPARK_EFI', esp)
            run('mmd', '-i', esp, '::/EFI', '::/EFI/BOOT')
            run('mcopy', '-i', esp, args.efi, '::/EFI/BOOT/BOOTAA64.EFI')
            with root.open('xb') as f:
                f.truncate((root_end - root_start + 1) * 512)
            run('mke2fs', '-q', '-F', '-t', 'ext4', '-b', '4096', '-L', 'SPARK_ARCH',
                '-U', args.root_uuid, '-d', args.root, root)
            run('e2fsck', '-fn', root)
            # Preserve holes while copying filesystem images into the disk file.
            for source, offset in [(esp, esp_start * 512), (root, root_start * 512)]:
                with source.open('rb') as f:
                    while chunk := f.read(4 * 1024**2):
                        if chunk.strip(b'\0'):
                            os.pwrite(fd, chunk, offset)
                        offset += len(chunk)
        os.fsync(fd)
        run('sgdisk', '--verify', args.output)
        manifest = dict(image=str(args.output), root_uuid=str(args.root_uuid),
                        esp_start=esp_start, root_start=root_start,
                        size_bytes=args.size_gib * 1024**3, sector_size=512)
        args.output.with_suffix('.json').write_text(json.dumps(manifest, indent=2) + '\n')
    except BaseException:
        os.close(fd)
        args.output.unlink()
        raise
    else:
        os.close(fd)


if __name__ == '__main__':
    main()
