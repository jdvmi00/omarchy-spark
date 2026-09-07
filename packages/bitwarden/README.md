# bitwarden

Omarchy's Install → Service → Bitwarden adds `bitwarden` and `bitwarden-cli`.
The AUR/Arch desktop package is x86_64-only; Bitwarden publishes a Linux arm64
tarball of the Electron app, which this recipe installs under `/opt/Bitwarden`
with the normal Electron namespace sandbox (no setuid helper), its desktop
entry and icons.
