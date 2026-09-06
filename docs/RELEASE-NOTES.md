# Release notes

## v0.1.0-preview.3 — Clean build, base packages and system setup

Source-only release. Every recipe now builds from the committed tree in a
fresh Arch Linux ARM container, Omarchy's base package list is nearly complete
on ARM, and Omarchy's own system setup runs on the port. All verified on the
single test Spark on 2026-09-06; see [hardware validation](HARDWARE-VALIDATION.md).
41 host regression tests pass. Independent replication on a second machine,
a package repository and a tested update/rollback path remain outstanding.

- Base package parity: `scripts/audit-base-packages.py` and the generated
  `manifests/omarchy-base-arm-status.json` replace the dated research list.
  A `ttfx` recipe (upstream's, unchanged) restores the Omarchy screensaver,
  whose launcher exits silently without it. Thirteen more upstream recipes
  that declare aarch64 (aether, cliamp, herdr, hyprland-preview-share-picker,
  omacalc, omacut, omawrite, omarchy-nvim, tensaku, tobi-try, tzupdate,
  ufw-docker, yay) are added unchanged and build natively. With the repo
  packages installed, 137 of 147 base packages are present on the test
  machine.

- `omarchy` 4.0.2-7: the ARM patch also adapts the installer's Snapper,
  post-install pacman, firewall and NVIDIA scripts, so `omarchy-apply-system`
  runs on the port. Run on the test Spark with no failed steps; the lock
  screen's PAM configuration, the firewall (with SSH, mDNS and Tailscale
  rules) and the remaining system defaults are now applied the upstream way.
- Clean build: `scripts/clean-build.sh` builds every recipe from the committed
  tree in a fresh Arch Linux ARM container. All 28 passed, with checksums in
  `manifests/clean-build-2026-09-06.json`.
- Screensaver, lock screen and firewall work on the test machine, and all of
  it survived a reboot with systemd-resolved taking over DNS.
- Display: 6144×2560 at 120 Hz verified over HDMI 2.1a; 60 Hz at that
  resolution blanks the panel on this cable, so 3840×2160 at 60 Hz stays
  configured. Recorded in the hardware report.
- Artwork: hero, announcement card, wallpaper and icon in Omarchy's pixel
  wordmark style under `docs/media`, with provenance notes.
- The NVIDIA driver packages are documented as coming from Arch Linux ARM's
  repositories rather than a port recipe.

## v0.1.0-preview.2 — Community developer preview

Source-only release incorporating the post-publication readiness corrections.
The updated settings and Workbench packages were installed and re-checked on the
single test Spark on 2026-09-06; the stricter Jupyter probe passed again after a
backend restart. See [hardware validation](HARDWARE-VALIDATION.md) for scope.
All 35 host regression tests passed. This release did not establish a complete
clean package build or independent hardware replication.

- `omarchy-settings` 4.0.2-4: the install scriptlet keeps administrator edits
  to `/etc/nsswitch.conf`, `/etc/security/faillock.conf`, `/etc/os-release`,
  plymouth, CUPS and `/etc/skel/.bashrc`, writing changed content as `.pacnew`
  and recording applied checksums under `/var/lib/omarchy/etc-overrides`.
- `nvidia-ai-workbench` 0.169.2.16-6: `nvwb-spark-setup` runs its preflight checks,
  including the local-context conflict check, before configuration changes, writes
  its config atomically and no longer runs a global `daemon-reload`. The README
  lists the exact privileged commands, the fixed port and the single-user scope.
- `image/make-disk-image.py` refuses image names ending in `.json` and never
  overwrites an existing manifest sidecar.
- `tests/check-jupyter-runtime.py` requires authenticated contents and status
  API responses without following redirects and fails unless requests with no
  token and with a wrong token are refused. Tokens are still never printed.
- New host-side regression tests cover each change; a SECURITY.md describes
  private reporting.
The release also adds a [getting-started guide](GETTING-STARTED.md), a
[community announcement draft](ANNOUNCEMENT.md), and explicit
[requirements for a supported release](RELEASE-CRITERIA.md). No installer,
boot image or binary package repository is included.

## v0.1.0-preview.1 — Omarchy Spark developer preview

First public **source-only** preview of native Arch Linux ARM and Omarchy on
NVIDIA DGX Spark. Intended for developers investigating the port, not unattended
installation or production use.

One Spark has demonstrated native external-SSD boot, accelerated Omarchy, native
CUDA and Docker GPU execution, and a Workbench GPU project with authenticated
JupyterLab. Dashboard has working service/firmware discovery and read-only Arch
package status. See the hardware report for exact scope and versions.

Includes package recipes, source hashes and Git pins, ARM compatibility patches,
regression tests, an isolated Dashboard protocol probe, and build/provenance notes.
No vendor binaries, firmware, boot images, raw device writers or personal
provisioning data are shipped.

Known gaps include a complete clean build, independent replication, application
parity, Dashboard installation, Workbench self-update, firmware maintenance,
hardware stress testing and a supported installer/update/rollback path.
