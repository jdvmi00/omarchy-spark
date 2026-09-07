"""The patched Install menu must hide entries that cannot work on aarch64 and offer ARM alternatives."""
import json
from pathlib import Path
import re
import subprocess
import unittest

MENU = Path(__file__).resolve().parents[1] / 'upstream/omarchy/default/omarchy/omarchy-menu.jsonc'
HIDDEN = ['install.windows', 'install.browser.chrome', 'install.browser.edge', 'install.browser.brave',
          'install.browser.brave-origin', 'install.browser.zen', 'install.service.dropbox', 'install.service.spotify',
          'install.editor.cursor', 'install.ai.grok-bot', 'install.ai.lm-studio', 'install.gaming.steam',
          'install.gaming.retroarch', 'install.gaming.minecraft', 'install.gaming.geforce-now',
          'install.gaming.xbox-controllers', 'install.gaming.battlenet', 'install.gaming.lutris',
          'install.gaming.heroic', 'install.gaming.retro-launcher']
KEPT = ['install.terminal.ghostty', 'install.editor.zed', 'install.service.bitwarden', 'install.ai.ollama',
        'install.browser.firefox', 'install.editor.vscode', 'install.service.1password']


def load():
    raw = MENU.read_text()
    raw = re.sub(r'^\s*//.*$', '', raw, flags=re.M)
    raw = re.sub(r',(\s*[}\]])', r'\1', raw)
    return json.loads(raw)


def evaluate(when, arch):
    """Run a menu `when` condition the way Omarchy does, with uname stubbed to arch."""
    script = f'uname() {{ echo {arch}; }}; export -f uname; omarchy-pkg-present() {{ return 1; }}; flatpak() {{ return 1; }}; {when}'
    return subprocess.run(['bash', '-c', script], env={'HOME': '/nonexistent', 'PATH': '/usr/bin:/bin'}).returncode == 0


class ArmInstallMenu(unittest.TestCase):
    def test_entries_without_an_arm_path_are_hidden_only_on_aarch64(self):
        menu = load()
        for key in HIDDEN:
            with self.subTest(entry=key):
                when = menu[key]['when']
                self.assertFalse(evaluate(when, 'aarch64'), when)
                self.assertTrue(evaluate(when, 'x86_64'), when)

    def test_entries_with_arm_packages_stay_visible(self):
        menu = load()
        for key in KEPT:
            with self.subTest(entry=key):
                when = menu[key].get('when', 'true')
                self.assertTrue(evaluate(when, 'aarch64'), when)

    def test_spotify_becomes_a_web_app_on_aarch64(self):
        menu = load()
        entry = menu['install.service.spotify-web']
        self.assertTrue(evaluate(entry['when'], 'aarch64'))
        self.assertFalse(evaluate(entry['when'], 'x86_64'))
        self.assertIn('omarchy-webapp-install Spotify https://open.spotify.com', entry['action'])
        self.assertEqual(entry['label'], menu['install.service.spotify']['label'])


if __name__ == '__main__':
    unittest.main()
