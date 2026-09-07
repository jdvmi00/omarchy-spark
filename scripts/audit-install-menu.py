#!/usr/bin/env python3
"""Audit Omarchy's Install menu for the ARM port.

  extract   anywhere: read the menu and its helper scripts, print JSON mapping
            each install entry to the packages it would add
  probe     on an Arch Linux ARM host: read that JSON, report each package as
            installed, available or unavailable; nothing is installed
  aur       anywhere with network: for every package the probe found
            unavailable, fetch its AUR recipe and record the architectures it
            declares (Omarchy falls back to the AUR for packages its own
            repository lacks)
  classify  anywhere: merge the probe, the AUR architectures and the port's
            recipes into the tracked manifest, noting which entries the port's
            menu patch hides on aarch64
  render    anywhere: write docs/INSTALL-MENU.md from the manifest

Entries are tiered by their worst package: works (all installed or available),
port-recipe (the port already packages it), aur-arm64 (the AUR recipe fetches
or builds an ARM64 version, so Omarchy's normal AUR path works), buildable (an
omarchy-pkgs recipe declares aarch64), no-arm-build (no ARM recipe anywhere),
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
        entry = {'entry': key, 'label': value.get('label', ''), 'packages': [], 'note': '', 'when': value.get('when', '')}
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


def aur(args):
    import urllib.request
    data = json.load(open(args.probe))
    names = sorted(n for n, st in data['status'].items() if st in ('unavailable', 'installed-local'))
    arches = {}
    for name in names:
        url = f'https://aur.archlinux.org/cgit/aur.git/plain/PKGBUILD?h={name}'
        try:
            text = urllib.request.urlopen(url, timeout=30).read().decode('utf-8', 'replace')
        except Exception:
            arches[name] = None
            continue
        m = re.search(r"^arch=\(([^)]*)\)", text, re.M | re.S)
        arches[name] = shlex.split(m.group(1).replace('\n', ' ')) if m else []
    json.dump({'fetched': __import__('datetime').date.today().isoformat(), 'arch': arches}, sys.stdout, indent=2)
    print()


def hidden_on(when, arch):
    """Evaluate a menu `when` condition the way omarchy-menu does, with uname stubbed."""
    if not when:
        return False
    script = f'uname() {{ echo {arch}; }}; export -f uname; omarchy-pkg-present() {{ return 1; }}; flatpak() {{ return 1; }}; {when}'
    env = {'HOME': '/nonexistent', 'PATH': '/usr/bin:/bin'}
    return subprocess.run(['bash', '-c', script], env=env, capture_output=True).returncode != 0


def classify(args):
    data = json.load(open(args.probe))
    root = Path(__file__).resolve().parents[1]
    ported = set()
    for recipe in (root / 'packages').glob('*/PKGBUILD'):
        ported.add(recipe.parent.name)
        # Split packages: pkgname=(ollama ollama-cuda) lives in packages/ollama.
        m = re.search(r"^pkgname=\(([^)]*)\)", recipe.read_text(), re.M)
        if m:
            ported.update(shlex.split(m.group(1)))
    pkgbuilds = Path(args.pkgbuilds) if args.pkgbuilds else None
    aur_arch = json.load(open(args.aur))['arch'] if getattr(args, 'aur', None) else {}
    counts = {}
    for e in data['entries']:
        pkgs = {}
        for name in e['packages']:
            st = data['status'].get(name, 'unknown')
            local = st == 'installed-local'
            if st in ('unavailable', 'installed-local'):
                if name in ported:
                    st = 'port-recipe'
                elif aur_arch.get(name) and ({'aarch64', 'any'} & set(aur_arch[name])):
                    st = 'aur-arm64'
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
            order = ['no-arm-build', 'x86-only-recipe', 'buildable', 'port-recipe', 'aur-arm64', 'available', 'installed']
            worst = min((v.split(' ')[0] for v in pkgs.values()), key=order.index)
            tier = {'installed': 'works', 'available': 'works', 'aur-arm64': 'aur-arm64', 'port-recipe': 'port-recipe',
                    'buildable': 'buildable', 'x86-only-recipe': 'no-arm-build', 'no-arm-build': 'no-arm-build'}[worst]
        e['tier'] = tier
        e['hidden_on_aarch64'] = hidden_on(e.get('when', ''), 'aarch64') and not hidden_on(e.get('when', ''), 'x86_64')
        counts[tier] = counts.get(tier, 0) + 1
    out = {'source': 'upstream/omarchy default/omarchy/omarchy-menu.jsonc and bin/ at the omarchy commit in upstream-lock.json',
           'host_arch': data.get('host_arch'), 'counts': counts, 'entries': data['entries']}
    json.dump(out, sys.stdout, indent=2)
    print()


TIERS = [
    ('works', 'Works', "every package is installed from or available in Arch Linux ARM's repositories, "
                       'or the entry installs a mise toolchain or only configuration.'),
    ('port-recipe', 'Packaged by the port', 'Arch Linux ARM lacks at least one package; the port builds it under `packages/`.'),
    ('aur-arm64', 'AUR with an ARM64 build', "the AUR recipe declares aarch64 and fetches the vendor's ARM64 build, so "
                                             "Omarchy's normal AUR fallback installs it."),
    ('buildable', 'Buildable', 'an omarchy-pkgs recipe declares aarch64 but nobody has built it for the port yet.'),
    ('no-arm-build', 'No ARM build', 'an AUR or vendor binary with no ARM64 recipe; would fail with "target not found".'),
    ('interactive', 'Interactive', 'asks what to install; outcome depends on the choice.'),
    ('not-applicable', 'Not applicable', 'x86-only gaming stacks or a Windows VM.'),
]
RENDER_TAIL = '''## What the port does about each tier

- Packaged-by-the-port entries install from the recipes under `packages/`;
  none of them is in Arch Linux ARM's repositories, so a machine without the
  port's packages built or served from a repository still sees "target not
  found" for them.
- Hidden entries are removed from the menu on aarch64 by the port's menu patch
  (`patches/omarchy-menu-arm.patch`, applied by `omarchy-settings`), so users
  do not pick an install that cannot succeed. The x86 menu is unchanged.
- AUR entries stay in the menu: Chrome, Brave, Brave Origin and Zen publish
  ARM64 Linux builds and their AUR recipes fetch them, so Omarchy's install
  flow builds them with yay as on x86.
- Spotify is replaced on aarch64 by a Spotify web app entry (Omarchy's own
  `omarchy-webapp-install`); LM Studio has no ARM64 Linux build and Ollama is
  the port's alternative; Edge, Cursor, Grok and Dropbox publish no ARM64
  Linux binaries.
- The Omarchy preinstalls entry still lists OBS Studio and Pinta, which have no
  ARM recipe here: OBS would need a native build and Pinta needs .NET, which
  Arch Linux ARM does not ship.
- Not-applicable entries are the Wine and Steam gaming stack and the Windows
  VM; they have no ARM path and are hidden on the port.
'''


def render(args):
    m = json.load(open(args.manifest))
    hidden = [e for e in m['entries'] if e.get('hidden_on_aarch64')]
    out = ['# Omarchy\'s Install menu on the port', '',
           'Generated from `manifests/omarchy-install-menu-arm-status.json` by',
           '`scripts/audit-install-menu.py`, which reads the menu (with the port\'s ARM patch',
           'applied) and its helper scripts, probes each package on the test Spark and tiers',
           'every entry by its worst package. A package installed on the test machine from',
           'outside the configured repositories does not count as available to anyone else;',
           'it is marked as installed locally. "Hidden" means the port\'s menu patch removes',
           'the entry on aarch64.', '',
           '| Tier | Entries |', '| --- | --- |']
    for key, title, _ in TIERS:
        out.append(f'| {title} | {m["counts"].get(key, 0)} |')
    out.append(f'| of which hidden on aarch64 | {len(hidden)} |')
    out.append('')
    for key, title, blurb in TIERS:
        rows = [e for e in m['entries'] if e['tier'] == key]
        out += [f'## {title} ({len(rows)})', '', blurb, '']
        if not rows:
            out += ['None.', '']
            continue
        out += ['| Entry | Packages | On aarch64 | Note |', '| --- | --- | --- | --- |']
        for e in rows:
            pkgs = ', '.join(f'{n} ({st})' if not st.startswith(('installed', 'available')) else n
                             for n, st in e['package_status'].items()) or '—'
            pkgs = pkgs.replace(' (installed locally on the test machine)', ', local')
            shown = 'hidden' if e.get('hidden_on_aarch64') else 'shown'
            out.append(f"| {e['entry'][8:]} | {pkgs} | {shown} | {e['note']} |")
        out.append('')
    out.append(RENDER_TAIL)
    Path(args.out).write_text('\n'.join(out))


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest='command', required=True)
    e = sub.add_parser('extract'); e.add_argument('menu'); e.add_argument('bindir'); e.set_defaults(run=extract)
    p = sub.add_parser('probe'); p.add_argument('extract'); p.set_defaults(run=probe)
    a = sub.add_parser('aur'); a.add_argument('probe'); a.set_defaults(run=aur)
    c = sub.add_parser('classify'); c.add_argument('probe'); c.add_argument('--pkgbuilds'); c.add_argument('--aur')
    c.set_defaults(run=classify)
    r = sub.add_parser('render'); r.add_argument('manifest'); r.add_argument('out'); r.set_defaults(run=render)
    args = parser.parse_args()
    args.run(args)


if __name__ == '__main__':
    main()
