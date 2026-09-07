# Omarchy's Install menu on the port

Generated from `manifests/omarchy-install-menu-arm-status.json` by
`scripts/audit-install-menu.py`, which reads the menu (with the port's ARM patch
applied) and its helper scripts, probes each package on the test Spark and tiers
every entry by its worst package. A package installed on the test machine from
outside the configured repositories does not count as available to anyone else;
it is marked as installed locally. "Hidden" means the port's menu patch removes
the entry on aarch64.

| Tier | Entries |
| --- | --- |
| Works | 34 |
| Packaged by the port | 12 |
| Buildable | 0 |
| No ARM build | 13 |
| Interactive | 8 |
| Not applicable | 8 |
| of which hidden on aarch64 | 20 |

## Works (34)

every package is installed from or available in Arch Linux ARM's repositories, or the entry installs a mise toolchain or only configuration.

| Entry | Packages | On aarch64 | Note |
| --- | --- | --- | --- |
| style.font.cascadia | ttf-cascadia-mono-nerd | shown |  |
| style.font.meslo | ttf-meslo-nerd | shown |  |
| style.font.fira | ttf-firacode-nerd | shown |  |
| style.font.victor | ttf-victor-mono-nerd | shown |  |
| style.font.bitstream | ttf-bitstream-vera-mono-nerd | shown |  |
| style.font.iosevka | ttf-iosevka-nerd | shown |  |
| browser.firefox | firefox | shown |  |
| service.signal | signal-desktop | shown |  |
| service.tailscale | tailscale | shown |  |
| service.chromium-account | — | shown | configuration only, no packages |
| editor.helix | helix | shown |  |
| editor.vim | vim | shown |  |
| terminal.alacritty | alacritty | shown |  |
| terminal.foot | foot | shown |  |
| terminal.kitty | kitty | shown |  |
| development.rails | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.docker-dbs | — | shown | configuration only, no packages |
| development.go | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.python | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.zig | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.rust | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.java | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.dotnet | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.ocaml | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.clojure | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.scala | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.javascript.node | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.javascript.bun | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.javascript.deno | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.php.php | php, composer, php-sqlite, xdebug | shown |  |
| development.php.laravel | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.php.symfony | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.elixir.elixir | — | shown | mise-managed toolchain; arm64 availability depends on the tool |
| development.elixir.phoenix | — | shown | mise-managed toolchain; arm64 availability depends on the tool |

## Packaged by the port (12)

Arch Linux ARM lacks at least one package; the port builds it under `packages/`.

| Entry | Packages | On aarch64 | Note |
| --- | --- | --- | --- |
| service.1password | 1password (port-recipe, local), 1password-cli (port-recipe, local) | shown |  |
| service.nordvpn | nordvpn-bin (port-recipe, local) | shown |  |
| service.once | once-bin (port-recipe, local) | shown |  |
| service.bitwarden | bitwarden (port-recipe, local), bitwarden-cli | shown |  |
| editor.vscode | visual-studio-code-bin (port-recipe, local) | shown |  |
| editor.zed | zed (port-recipe, local), omazed (port-recipe, local) | shown |  |
| editor.sublime | sublime-text-4 (port-recipe, local) | shown |  |
| editor.emacs | omarchy-emacs (port-recipe, local) | shown |  |
| terminal.ghostty | ghostty (port-recipe, local) | shown |  |
| ai.chatgpt | openai-codex-desktop (port-recipe, local) | shown |  |
| ai.dictation | wtype, voxtype-bin (port-recipe, local) | shown |  |
| ai.ollama | ollama-cuda (port-recipe, local) | shown | inline: picks ollama-cuda when nvidia-smi is present |

## Buildable (0)

an omarchy-pkgs recipe declares aarch64 but nobody has built it for the port yet.

None.

## No ARM build (13)

an AUR or vendor binary with no ARM64 recipe; would fail with "target not found".

| Entry | Packages | On aarch64 | Note |
| --- | --- | --- | --- |
| preinstalls | aether (port-recipe, local), cliamp (port-recipe, local), libreoffice-fresh, xournalpp, pinta (no-arm-build), obsidian (port-recipe, local), obs-studio (no-arm-build), kdenlive, moonlight-qt, lazydocker, omacut (port-recipe, local), omacalc (port-recipe, local), omawrite (port-recipe, local) | shown |  |
| browser.chrome | google-chrome (no-arm-build, local) | hidden |  |
| browser.edge | microsoft-edge-stable-bin (no-arm-build) | hidden |  |
| browser.brave | brave-bin (no-arm-build) | hidden |  |
| browser.brave-origin | brave-origin-bin (no-arm-build) | hidden |  |
| browser.zen | zen-browser-bin (no-arm-build) | hidden |  |
| service.dropbox | dropbox (x86-only-recipe), dropbox-cli (x86-only-recipe), libappindicator-gtk3 (no-arm-build, local), python-gpgme, nautilus-dropbox (x86-only-recipe) | hidden |  |
| service.spotify | spotify (x86-only-recipe) | hidden |  |
| editor.cursor | cursor-bin (x86-only-recipe) | hidden |  |
| ai.grok-bot | grok-bot (x86-only-recipe) | hidden |  |
| ai.lm-studio | lmstudio-bin (x86-only-recipe) | hidden |  |
| gaming.retroarch | retroarch, retroarch-assets-glui, retroarch-assets-ozone, retroarch-assets-xmb, libretro-beetle-pce, libretro-beetle-pce-fast, libretro-beetle-psx, libretro-beetle-psx-hw, libretro-beetle-supergrafx, libretro-blastem, libretro-bsnes, libretro-bsnes-hd, libretro-core-info, libretro-desmume, libretro-dolphin, libretro-flycast, libretro-gambatte, libretro-genesis-plus-gx, libretro-kronos, libretro-mame, libretro-melonds, libretro-mesen, libretro-mesen-s, libretro-mgba, libretro-mupen64plus-next, libretro-nestopia, libretro-overlays, libretro-parallel-n64, libretro-picodrive, libretro-play, libretro-ppsspp (no-arm-build), libretro-sameboy, libretro-scummvm, libretro-shaders-slang, libretro-snes9x, libretro-yabause, libretro-cap32-git (buildable), libretro-fbneo-git (buildable), libretro-uae-git (x86-only-recipe), libretro-vice-x128-git (no-arm-build), libretro-vice-x64-git (no-arm-build), libretro-vice-x64dtv-git (no-arm-build), libretro-vice-x64sc-git (no-arm-build), libretro-vice-xcbm2-git (no-arm-build), libretro-vice-xcbm5x0-git (no-arm-build), libretro-vice-xpet-git (no-arm-build), libretro-vice-xplus4-git (no-arm-build), libretro-vice-xscpu64-git (no-arm-build), libretro-vice-xvic-git (no-arm-build), libretro-database-git (buildable), retroarch-joypad-autoconfig-git (buildable) | hidden |  |
| gaming.xbox-controllers | linux-headers (no-arm-build, local), xpadneo-dkms (x86-only-recipe) | hidden |  |

## Interactive (8)

asks what to install; outcome depends on the choice.

| Entry | Packages | On aarch64 | Note |
| --- | --- | --- | --- |
| package | — | shown | interactive |
| aur | — | shown | interactive |
| webapp | — | shown | interactive |
| tui | — | shown | interactive |
| style.theme | — | shown | interactive |
| style.background | — | shown | interactive |
| service.spotify-web | — | shown | interactive |
| gaming.retro-launcher | — | hidden | interactive |

## Not applicable (8)

x86-only gaming stacks or a Windows VM.

| Entry | Packages | On aarch64 | Note |
| --- | --- | --- | --- |
| windows | freerdp, openbsd-netcat, gum | hidden | x86 Windows virtual machine |
| gaming.steam | steam (no-arm-build) | hidden | Steam is x86-only |
| gaming.minecraft | minecraft-launcher (x86-only-recipe) | hidden | official launcher is x86-64 only |
| gaming.geforce-now | flatpak | hidden | Flatpak app published for x86-64 only |
| gaming.xbox-cloud | — | shown | browser web app; packaging is a Chromium web app |
| gaming.battlenet | umu-launcher (no-arm-build) | hidden | Windows games through Wine/umu, x86-only |
| gaming.lutris | lutris, umu-launcher (no-arm-build), wine-staging (no-arm-build), wine-mono (no-arm-build), wine-gecko (no-arm-build), winetricks (no-arm-build), python-protobuf | hidden | Wine-based, x86-only |
| gaming.heroic | heroic-games-launcher-bin (x86-only-recipe) | hidden | Windows game stores through Wine, x86-only |

## What the port does about each tier

- Packaged-by-the-port entries install from the recipes under `packages/`;
  none of them is in Arch Linux ARM's repositories, so a machine without the
  port's packages built or served from a repository still sees "target not
  found" for them.
- Hidden entries are removed from the menu on aarch64 by the port's menu patch
  (`patches/omarchy-menu-arm.patch`, applied by `omarchy-settings`), so users
  do not pick an install that cannot succeed. The x86 menu is unchanged.
- Spotify is replaced on aarch64 by a Spotify web app entry (Omarchy's own
  `omarchy-webapp-install`); LM Studio has no ARM64 Linux build and Ollama is
  the port's alternative; Chrome, Edge, Brave, Zen, Cursor and Dropbox publish
  no ARM64 Linux binaries.
- The Omarchy preinstalls entry still lists OBS Studio and Pinta, which have no
  ARM recipe here: OBS would need a native build and Pinta needs .NET, which
  Arch Linux ARM does not ship.
- Not-applicable entries are the Wine and Steam gaming stack and the Windows
  VM; they have no ARM path and are hidden on the port.
