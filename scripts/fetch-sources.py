#!/usr/bin/env python3
"""Download a locked source manifest and verify content before publishing files."""
import argparse
import hashlib
import json
import re
from pathlib import Path
import urllib.request


def digest(path, algorithm):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('manifest', type=Path)
    parser.add_argument('destination', type=Path)
    args = parser.parse_args()
    entries = json.loads(args.manifest.read_text())
    for entry in entries:
        algorithm = entry['hash_algorithm']
        if algorithm not in ('sha256', 'sha512'):
            raise ValueError(f'Unsupported hash algorithm: {algorithm}')
        if not re.fullmatch('[0-9a-f]{' + str(hashlib.new(algorithm).digest_size * 2) + '}', entry['hash']):
            raise ValueError(f"Malformed source hash: {entry['filename']}")
    args.destination.mkdir(parents=True, exist_ok=True)
    for entry in entries:
        name = entry['filename']
        if Path(name).name != name or name in ('.', '..'):
            raise ValueError(f'Invalid source filename: {name}')
        target = args.destination / name
        algorithm = entry['hash_algorithm']
        if target.exists() and target.stat().st_size == entry['size'] and digest(target, algorithm) == entry['hash']:
            print(f'{name}: already verified', flush=True)
            continue
        temporary = target.with_name(target.name + '.partial')
        try:
            with urllib.request.urlopen(entry['url'], timeout=60) as response:
                with temporary.open('wb') as output:
                    while chunk := response.read(1024 * 1024):
                        output.write(chunk)
            if temporary.stat().st_size != entry['size']:
                raise ValueError(f'Size mismatch: {name}')
            if digest(temporary, algorithm) != entry['hash']:
                raise ValueError(f'{algorithm} mismatch: {name}')
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        print(f'{name}: verified', flush=True)


if __name__ == '__main__':
    main()
