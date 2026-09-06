# Spark ARM changes to Omarchy 4.0.2

Release 6 retains the ARM font dependency, excludes x86 lib32 NVIDIA packages on
ARM, and recognizes linux-dgx-spark when selecting matching kernel headers.
It also makes `omarchy refresh pacman` select signed Arch Linux ARM repositories
and their mirror list on ARM. Unsupported rc/edge channels fail before replacing
configuration. Copy failures stop before attempting an upgrade.

The source patch is `omarchy-spark-arm.patch`, based on the pinned Omarchy
commit in PKGBUILD. The earlier nvidia-only patch is retained as historical
reference but is no longer the recipe's input. Tests use command stubs to verify
ARM/x86 selection, rejected channels and early failure without writing /etc or
invoking pacman. The actual refresh/upgrade has not been run on the Spark host.

Release 5 corrects public payload permissions inherited from private build
checkouts. Release 6 removes the forced zero release age from generated mise
wrappers so the user's mise setting governs version resolution. The Spark uses
`minimum_release_age = "10m"`, and existing wrappers were regenerated.

## Installer scripts adapted by the patch

`omarchy-spark-arm.patch` also adapts four scripts under `install/` so that
`omarchy-apply-system` runs on the port: `config/snapper.sh` exits early unless
the root is Btrfs with snapper installed; `post-install/pacman.sh` writes the
`spark/` ARM pacman configuration on aarch64; `config/firewall.sh` adds rules
for SSH, mDNS and the Tailscale interface when those services are enabled;
and `hardware/nvidia.sh` does not write the early-KMS initramfs drop-in for
the DGX Spark kernel, whose initramfs the port integrates itself. Each is
covered by `tests/test_install_scripts.py`.
