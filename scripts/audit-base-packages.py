#!/usr/bin/env python3
"""Classify Omarchy's base package list for the ARM port.

Two steps, because pacman must run on the target while the recipes live in
the checkout:

  probe     on an Arch Linux ARM host: read the upstream base list and report
            which packages are installed, available in the configured repos,
            or unavailable. Read-only; nothing is installed.
  classify  anywhere: merge a probe report with omarchy-pkgs recipes and write
            the tiered manifest the port tracks.

Tiers for unavailable packages:
  omarchy-recipe   upstream recipe declares aarch64; build it into the port
  omarchy-x86-only upstream recipe exists but is x86_64-only
  external         AUR or vendor package; needs its own recipe and review
  not-applicable   x86-specific purpose; documented gap, not work
"""
import argparse
import datetime
import json
from pathlib import Path
import re
import subprocess
import sys

NOT_APPLICABLE = {
    'qemu-user-static-binfmt': 'runs foreign-architecture binaries; the port is the foreign architecture',
    'asdcontrol': 'Apple Studio Display brightness control',
}
# Upstream recipe declares aarch64 but its toolchain has no ARM64 Linux build.
BLOCKED = {
    'localsend': 'Flutter app built through fvm; Flutter publishes no Linux aarch64 SDK',
}


def read_list(path):
    return [line.strip() for line in Path(path).read_text().splitlines()
            if line.strip() and not line.startswith('#')]


def probe(args):
    report = {'generated': datetime.date.today().isoformat(), 'host_arch': subprocess.check_output(['uname', '-m'], text=True).strip(),
              'installed': [], 'available': [], 'unavailable': []}
    for name in read_list(args.base_list):
        # pacman -T reports whether a dependency is satisfied, so a package
        # provided under another name (neovim for nvim) counts as installed.
        if subprocess.run(['pacman', '-T', name], capture_output=True).returncode == 0:
            report['installed'].append(name)
        elif subprocess.run(['pacman', '-Sp', name], capture_output=True).returncode == 0:
            report['available'].append(name)
        else:
            report['unavailable'].append(name)
    json.dump(report, sys.stdout, indent=2)
    print()


def recipe_tier(name, pkgbuilds):
    if name in NOT_APPLICABLE:
        return 'not-applicable', NOT_APPLICABLE[name]
    if name in BLOCKED:
        return 'external', BLOCKED[name]
    recipe = pkgbuilds / name / 'PKGBUILD' if pkgbuilds else None
    if recipe and recipe.exists():
        arch = re.search(r"^arch=\((.*)\)", recipe.read_text(), re.M)
        if arch and ('aarch64' in arch.group(1) or "'any'" in arch.group(1)):
            return 'omarchy-recipe', f'upstream/omarchy-pkgs/pkgbuilds/{name}/PKGBUILD'
        return 'omarchy-x86-only', f'upstream/omarchy-pkgs/pkgbuilds/{name}/PKGBUILD'
    return 'external', 'no omarchy-pkgs recipe; AUR or vendor source'


def classify(args):
    report = json.load(open(args.probe))
    pkgbuilds = Path(args.pkgbuilds) if args.pkgbuilds else None
    ported = set(p.name for p in (Path(__file__).resolve().parents[1] / 'packages').iterdir())
    unavailable = []
    for name in report['unavailable']:
        tier, note = recipe_tier(name, pkgbuilds)
        entry = {'name': name, 'tier': tier, 'note': note}
        if name in ported:
            entry['port_recipe'] = f'packages/{name}'
        unavailable.append(entry)
    manifest = {
        'source': 'upstream/omarchy/install/omarchy-base.packages at the omarchy commit in upstream-lock.json',
        'probed': report['generated'], 'host_arch': report['host_arch'],
        'counts': {'total': sum(len(report[k]) for k in ('installed', 'available', 'unavailable')),
                   'installed': len(report['installed']), 'available_not_installed': len(report['available']),
                   'unavailable': len(report['unavailable'])},
        'available_not_installed': report['available'],
        'unavailable': unavailable,
        'installed': report['installed'],
    }
    json.dump(manifest, sys.stdout, indent=2)
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('probe'); p.add_argument('base_list'); p.set_defaults(run=probe)
    c = sub.add_parser('classify'); c.add_argument('probe'); c.add_argument('--pkgbuilds', help='omarchy-pkgs/pkgbuilds directory'); c.set_defaults(run=classify)
    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
