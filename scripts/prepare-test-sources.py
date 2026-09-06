#!/usr/bin/env python3
"""Fetch exact test inputs; never replace an existing checkout."""
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
PATCHES = {'omarchy': 'omarchy-spark-arm.patch',
           'arch-dgx-spark-iso': 'archiso-hook-directory.patch'}


def main():
    entries = {e['name']: e for e in json.loads((ROOT / 'upstream-lock.json').read_text())}
    parent = ROOT / 'upstream'
    parent.mkdir(exist_ok=True)
    for name, patch in PATCHES.items():
        entry = entries[name]
        target = parent / name
        if target.exists():
            raise SystemExit(f'{target} already exists; inspect it and move it aside before preparing fresh test sources')
        subprocess.run(['git', 'init', str(target)], check=True)
        subprocess.run(['git', '-C', str(target), 'fetch', '--depth=1', entry['url'], entry['commit']], check=True)
        subprocess.run(['git', '-C', str(target), 'checkout', '--detach', 'FETCH_HEAD'], check=True)
        actual = subprocess.check_output(['git', '-C', str(target), 'rev-parse', 'HEAD'], text=True).strip()
        if actual != entry['commit']:
            raise SystemExit('Fetched commit does not match lock')
        subprocess.run(['git', '-C', str(target), 'apply', '--check', str(ROOT / 'patches' / patch)], check=True)
        subprocess.run(['git', '-C', str(target), 'apply', str(ROOT / 'patches' / patch)], check=True)


if __name__ == '__main__':
    main()
