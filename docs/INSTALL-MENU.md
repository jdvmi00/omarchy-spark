# Omarchy's Install menu on the port

Generated from `manifests/omarchy-install-menu-arm-status.json` by
`scripts/audit-install-menu.py`, which reads the menu and its helper scripts,
probes each package on the test Spark and tiers every entry by its worst package.
A package installed on the test machine from outside the configured repositories
does not count as available; it is marked as installed locally.

| Tier | Entries |
| --- | --- |
| Works | 34 |
| Packaged by the port | 1 |
| Buildable | 8 |
| No ARM build | 16 |
| Interactive | 7 |
| Not applicable | 8 |

## Works (34)

every package is installed from or available in Arch Linux ARM's repositories, or the entry installs a mise toolchain or only configuration.

| Entry | Packages | Note |
| --- | --- | --- |
| style.font.cascadia | ttf-cascadia-mono-nerd |  |
| style.font.meslo | ttf-meslo-nerd |  |
| style.font.fira | ttf-firacode-nerd |  |
| style.font.victor | ttf-victor-mono-nerd |  |
| style.font.bitstream | ttf-bitstream-vera-mono-nerd |  |
| style.font.iosevka | ttf-iosevka-nerd |  |
| browser.firefox | firefox |  |
| service.signal | signal-desktop |  |
| service.tailscale | tailscale |  |
| service.chromium-account | — | configuration only, no packages |
| editor.helix | helix |  |
| editor.vim | vim |  |
| terminal.alacritty | alacritty |  |
| terminal.foot | foot |  |
| terminal.kitty | kitty |  |
| development.rails | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.docker-dbs | — | configuration only, no packages |
| development.go | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.python | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.zig | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.rust | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.java | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.dotnet | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.ocaml | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.clojure | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.scala | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.javascript.node | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.javascript.bun | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.javascript.deno | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.php.php | php, composer, php-sqlite, xdebug |  |
| development.php.laravel | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.php.symfony | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.elixir.elixir | — | mise-managed toolchain; arm64 availability depends on the tool |
| development.elixir.phoenix | — | mise-managed toolchain; arm64 availability depends on the tool |

## Packaged by the port (1)

Arch Linux ARM lacks it; the port builds it.

| Entry | Packages | Note |
| --- | --- | --- |
| terminal.ghostty | ghostty (port-recipe (installed locally on the test machine)) |  |

## Buildable (8)

an omarchy-pkgs recipe declares aarch64 but nobody has built it for the port yet.

| Entry | Packages | Note |
| --- | --- | --- |
| service.1password | 1password (buildable), 1password-cli (buildable) |  |
| service.nordvpn | nordvpn-bin (buildable) |  |
| service.once | once-bin (buildable) |  |
| editor.vscode | visual-studio-code-bin (buildable) |  |
| editor.sublime | sublime-text-4 (buildable) |  |
| editor.emacs | omarchy-emacs (buildable) |  |
| ai.chatgpt | openai-codex-desktop (buildable) |  |
| ai.dictation | voxtype-bin (buildable) |  |

## No ARM build (16)

an AUR or vendor binary with no ARM64 recipe; fails with "target not found".

| Entry | Packages | Note |
| --- | --- | --- |
| preinstalls | aether (port-recipe (installed locally on the test machine)), cliamp (port-recipe (installed locally on the te |  |
| browser.chrome | google-chrome (no-arm-build (installed locally on the test machine)) |  |
| browser.edge | microsoft-edge-stable-bin (no-arm-build) |  |
| browser.brave | brave-bin (no-arm-build) |  |
| browser.brave-origin | brave-origin-bin (no-arm-build) |  |
| browser.zen | zen-browser-bin (no-arm-build) |  |
| service.dropbox | dropbox (x86-only-recipe), dropbox-cli (x86-only-recipe), nautilus-dropbox (x86-only-recipe) |  |
| service.spotify | spotify (x86-only-recipe) |  |
| service.bitwarden | bitwarden (no-arm-build) |  |
| editor.cursor | cursor-bin (x86-only-recipe) |  |
| editor.zed | zed (no-arm-build), omazed (buildable) |  |
| ai.grok-bot | grok-bot (x86-only-recipe) |  |
| ai.lm-studio | lmstudio-bin (x86-only-recipe) |  |
| ai.ollama | ollama-cuda (no-arm-build) | inline: picks ollama-cuda when nvidia-smi is present |
| gaming.retroarch | libretro-ppsspp (no-arm-build), libretro-cap32-git (buildable), libretro-fbneo-git (buildable), libretro-uae-g |  |
| gaming.xbox-controllers | linux-headers (no-arm-build (installed locally on the test machine)), xpadneo-dkms (x86-only-recipe) |  |

## Interactive (7)

asks what to install; outcome depends on the choice.

| Entry | Packages | Note |
| --- | --- | --- |
| package | — | interactive |
| aur | — | interactive |
| webapp | — | interactive |
| tui | — | interactive |
| style.theme | — | interactive |
| style.background | — | interactive |
| gaming.retro-launcher | — | interactive |

## Not applicable (8)

x86-only gaming stacks or a Windows VM.

| Entry | Packages | Note |
| --- | --- | --- |
| windows | freerdp, openbsd-netcat, gum | x86 Windows virtual machine |
| gaming.steam | steam (no-arm-build) | Steam is x86-only |
| gaming.minecraft | minecraft-launcher (x86-only-recipe) | official launcher is x86-64 only |
| gaming.geforce-now | flatpak | Flatpak app published for x86-64 only |
| gaming.xbox-cloud | — | browser web app; packaging is a Chromium web app |
| gaming.battlenet | umu-launcher (no-arm-build) | Windows games through Wine/umu, x86-only |
| gaming.lutris | umu-launcher (no-arm-build), wine-staging (no-arm-build), wine-mono (no-arm-build), wine-gecko (no-arm-build), | Wine-based, x86-only |
| gaming.heroic | heroic-games-launcher-bin (x86-only-recipe) | Windows game stores through Wine, x86-only |

## What to do about each tier

- Buildable entries are the same shape of work as ttfx and the 13 recipes added on
  2026-09-06: copy the omarchy-pkgs recipe, build on the Spark, verify. Several are
  vendor binaries whose recipes already fetch an arm64 download.
- No-ARM-build entries need a vendor to publish ARM64 Linux builds. Zed, Bitwarden,
  Obsidian, OBS and Pinta do have ARM64 sources or builds and can be packaged like
  LocalSend; Chrome, Edge, Brave, Zen, Cursor, Spotify, LM Studio and Dropbox do
  not, and the port should hide or mark those entries rather than let them fail.
  The Chrome on the test machine is a local build outside any repository.
- Not-applicable entries are the Wine and Steam gaming stack and the Windows VM;
  they have no ARM path and should be hidden on the port.
