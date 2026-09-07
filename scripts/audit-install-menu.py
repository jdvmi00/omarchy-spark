#!/usr/bin/env python3
"""Audit Omarchy's Install menu for the ARM port.

  extract   anywhere: read the menu and its helper scripts, print JSON mapping
            each install entry to the packages it would add
  probe     on an Arch Linux ARM host: read that JSON, report each package as
            installed, available or unavailable; nothing is installed
  classify  anywhere: merge the probe with omarchy-pkgs recipes and the port's
            recipes into the tracked manifest

Entries are tiered by their worst package: works (all installed or available),
port-recipe (the port already packages it), buildable (an omarchy-pkgs recipe
declares aarch64), no-arm-build (AUR or vendor binary with no ARM recipe here),
interactive (the entry asks what to install), or not-applicable (x86 gaming
stacks, Windows VM).
"""
import argparse
import json
from pathlib import Path
import re
import shlex
import subprocess
import sys

WRAPPERS = ('omarchy-launch-floating-terminal-with-presentation', 'xdg-terminal-exec')
INTERACTIVE = {'omarchy-pkg-install', 'omarchy-pkg-aur-install', 'omarchy-webapp-install', 'omarchy-tui-install',
               'omarchy-theme-install', 'omarchy-theme-bg-install', 'omarchy-games-retro-install'}
NOT_APPLICABLE = {
    'install.windows': 'x86 Windows virtual machine',
    'install.gaming.steam': 'Steam is x86-only',
    'install.gaming.battlenet': 'Windows games through Wine/umu, x86-only',
    'install.gaming.lutris': 'Wine-based, x86-only',
    'install.gaming.heroic': 'Windows game stores through Wine, x86-only',
    'install.gaming.geforce-now': 'Flatpak app published for x86-64 only',
    'install.gaming.xbox-cloud': 'browser web app; packaging is a Chromium web app',
    'install.gaming.minecraft': 'official launcher is x86-64 only',
}
PKG_ADD = re.compile(r'omarchy-pkg-(?:aur-)?add\s+(.*)')


def strip_wrappers(action):
    tokens = shlex.split(action)
    while tokens and (tokens[0] in WRAPPERS or tokens[0].startswith('--app-id=')):
        tokens.pop(0)
    if len(tokens) == 1 and ' ' in tokens[0]:
        tokens = shlex.split(tokens[0])
    return tokens


def pkg_add_lines(text):
    packages = []
    lines = text.replace('\\\n', ' ').splitlines()
    for line in lines:
        m = PKG_ADD.search(line)
        if not m:
            continue
        for tok in shlex.split(m.group(1).split('||')[0].split('&&')[0].split(';')[0]):
            if tok.startswith(('$', '"$', '-')):
                continue
            packages.append(tok)
    return packages


def case_block(text, key):
    m = re.search(r'^\s*%s\)\s*$(.*?)^\s*;;' % re.escape(key), text, re.M | re.S)
    return m.group(1) if m else ''


def function_block(text, name):
    m = re.search(r'^%s\(\)\s*\{(.*?)^\}' % re.escape(name), text, re.M | re.S)
    return m.group(1) if m else ''


def extract(args):
    raw = Path(args.menu).read_text()
    raw = re.sub(r'^\s*//.*$', '', raw, flags=re.M)
    raw = re.sub(r',(\s*[}\]])', r'\1', raw)
    menu = json.loads(raw)
    bindir = Path(args.bindir)
    entries = []
    for key, value in menu.items():
        if not key.startswith('install.') or not isinstance(value, dict) or 'action' not in value:
            continue
        action = value['action']
        entry = {'entry': key, 'label': value.get('label', ''), 'packages': [], 'note': ''}
        if action.startswith('if '):
            entry['packages'] = ['ollama-cuda'] if 'ollama-cuda' in action else []
            entry['note'] = 'inline: picks ollama-cuda when nvidia-smi is present'
        else:
            tokens = strip_wrappers(action)
            cmd = tokens[0] if tokens else ''
            script = bindir / cmd
            if cmd in INTERACTIVE:
                entry['note'] = 'interactive'
            elif cmd in ('omarchy-install-app', 'omarchy-install-and-launch'):
                entry['packages'] = tokens[2].split()
            elif cmd == 'omarchy-install-font':
                entry['packages'] = [tokens[2]]
            elif cmd == 'omarchy-install-terminal':
                entry['packages'] = [tokens[1]]
            elif cmd == 'omarchy-install-browser':
                entry['packages'] = pkg_add_lines(case_block(script.read_text(), tokens[1]))
            elif cmd == 'omarchy-install-dev-env':
                block = function_block(script.read_text(), 'install_' + tokens[1])
                entry['packages'] = pkg_add_lines(block)
                if not entry['packages'] or 'mise' in block:
                    entry['note'] = 'mise-managed toolchain; arm64 availability depends on the tool'
            elif script.exists():
                text = script.read_text()
                entry['packages'] = pkg_add_lines(text)
                if 'flatpak' in text:
                    entry['note'] = 'flatpak'
                elif not entry['packages']:
                    entry['note'] = 'configuration only, no packages'
            else:
                entry['note'] = f'unhandled action: {action[:60]}'
        entries.append(entry)
    json.dump({'entries': entries}, sys.stdout, indent=2)
    print()


def probe(args):
    data = json.load(open(args.extract))
    names = sorted({p for e in data['entries'] for p in e['packages']})
    status = {}
    for name in names:
        if subprocess.run(['pacman', '-T', name], capture_output=True).returncode == 0:
            # Installed from outside the configured repositories counts as unavailable
            # for anyone else: the test machine's local builds are not the port's.
            in_repo = subprocess.run(['pacman', '-Si', name], capture_output=True).returncode == 0
            status[name] = 'installed' if in_repo else 'installed-local'
        elif subprocess.run(['pacman', '-Sp', name], capture_output=True).returncode == 0:
            status[name] = 'available'
        else:
            status[name] = 'unavailable'
    data['status'] = status
    data['host_arch'] = subprocess.check_output(['uname', '-m'], text=True).strip()
    json.dump(data, sys.stdout, indent=2)
    print()


def classify(args):
    data = json.load(open(args.probe))
    root = Path(__file__).resolve().parents[1]
    ported = {p.name for p in (root / 'packages').iterdir()}
    pkgbuilds = Path(args.pkgbuilds) if args.pkgbuilds else None
    counts = {}
    for e in data['entries']:
        pkgs = {}
        for name in e['packages']:
            st = data['status'].get(name, 'unknown')
            local = st == 'installed-local'
            if st in ('unavailable', 'installed-local'):
                if name in ported:
                    st = 'port-recipe'
                elif pkgbuilds and (pkgbuilds / name / 'PKGBUILD').exists():
                    arch = re.search(r"^arch=\((.*)\)", (pkgbuilds / name / 'PKGBUILD').read_text(), re.M)
                    st = 'buildable' if arch and ('aarch64' in arch.group(1) or "'any'" in arch.group(1)) else 'x86-only-recipe'
                else:
                    st = 'no-arm-build'
                if local:
                    st += ' (installed locally on the test machine)'
            pkgs[name] = st
        e['package_status'] = pkgs
        if e['entry'] in NOT_APPLICABLE:
            tier = 'not-applicable'; e['note'] = NOT_APPLICABLE[e['entry']]
        elif e['note'] == 'interactive':
            tier = 'interactive'
        elif not pkgs:
            tier = 'works' if e['note'] else 'unknown'
        else:
            order = ['no-arm-build', 'x86-only-recipe', 'buildable', 'port-recipe', 'available', 'installed']
            worst = min((v.split(' ')[0] for v in pkgs.values()), key=order.index)
            tier = {'installed': 'works', 'available': 'works', 'port-recipe': 'port-recipe', 'buildable': 'buildable',
                    'x86-only-recipe': 'no-arm-build', 'no-arm-build': 'no-arm-build'}[worst]
        e['tier'] = tier
        counts[tier] = counts.get(tier, 0) + 1
    out = {'source': 'upstream/omarchy default/omarchy/omarchy-menu.jsonc and bin/ at the omarchy commit in upstream-lock.json',
           'host_arch': data.get('host_arch'), 'counts': counts, 'entries': data['entries']}
    json.dump(out, sys.stdout, indent=2)
    print()


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    e = sub.add_parser('extract'); e.add_argument('menu'); e.add_argument('bindir'); e.set_defaults(run=extract)
    p = sub.add_parser('probe'); p.add_argument('extract'); p.set_defaults(run=probe)
    c = sub.add_parser('classify'); c.add_argument('probe'); c.add_argument('--pkgbuilds'); c.set_defaults(run=classify)
    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
