# Building the developer preview

This repository reproduces package sources and host-side tests. It does not yet
reproduce the complete installed test machine in one command. The initial image
was hand-integrated; its personal provisioning and disk-writing scripts are not
public installation tooling.

## Run regression tests

On Linux with Python 3.11+, PyYAML, Git, Bash and patch:

```sh
python3 scripts/prepare-test-sources.py
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The preparation script fetches two exact public Git revisions from
`upstream-lock.json` and applies this repository's patches. It refuses to replace
an existing checkout. Tests use stubs for privileged host commands and do not
install packages, change desktop settings or write block devices. Native probes
named `check-*.sh` or `check-*.py` are not part of this suite; inspect their
requirements before running them on a configured Spark. The notebook probe
requires a token-protected server and fails when authentication is not
enforced, so a pass means more than an HTTP 200.

## Build packages

Use a disposable **aarch64 Arch Linux ARM** build environment. An ARM64 container
on DGX OS can build packages, but shares the host kernel and cannot establish
native boot or driver compatibility. Later Workbench and Dashboard packages were
built directly on the native Arch test installation.

Install `base-devel`, Git, Python and each recipe's `makedepends`. Follow the
normal Arch `makepkg` workflow as an unprivileged builder, one recipe at a time:

```sh
cd packages/gcc15-dgx
makepkg --verifysource
makepkg -s
```

`-s` may install build dependencies in your build environment. Do not bypass
source validation or dependency checks. Some initial historical builds used
manually provisioned dependencies; a complete clean-chroot build of every recipe
is still outstanding. Do not treat this command example as evidence of that.

Suggested dependency order:

1. `linux-dgx-spark` and headers, and `gcc15-dgx`.
2. `cuda-dgx-spark`, then GPU-dependent tools such as `perftest`.
3. `aquamarine-compat13`, `omarchy-keyring`, `omarchy-settings`, then `omarchy`.
4. `dgx-spark-mlnx-hotplug`, `nsight-dgx-spark`, `nvidia-ai-workbench`,
   `dgx-dashboard`, `mise-bin` and `xdg-terminal-exec` as needed.

Read each package README and PKGBUILD. The kernel config and version file are
already included; do not run an absent upstream configuration generator. The
kernel source release is 6.17.0-1014.14, while its compiled kernel identifies as
6.17.9-dgx-spark. The tested page size is 4 KiB.

The tested NVIDIA module/userspace version is 610.57.04. Installing a matching
NVIDIA open-module/DKMS, userspace, headers and Container Toolkit set is a separate
integration prerequisite; this preview does not provide a complete pinned Arch
repository for it. Rolling repositories may no longer provide the tested set.
The Aquamarine ABI 13 compatibility recipe addresses the repository combination
observed during bring-up, not every future Hyprland release.

For large vendor payloads, `scripts/fetch-sources.py MANIFEST DESTINATION` can
prefetch and verify the locked source lists. Recipes still verify their own
sources. Download URLs and checksums do not establish redistribution rights.

## Base package audit

Omarchy's ISO installer applies `install/omarchy-base.packages`; the port
tracks how far the test machine is from that list. On an Arch ARM host with
the fetched upstream tree, probe read-only, then classify against the
omarchy-pkgs recipes:

```sh
python3 scripts/audit-base-packages.py probe upstream/omarchy/install/omarchy-base.packages > probe.json
python3 scripts/audit-base-packages.py classify probe.json --pkgbuilds <omarchy-pkgs>/pkgbuilds \
  > manifests/omarchy-base-arm-status.json
```

The manifest lists what is installed, what the repos offer but is missing, and
tiers the rest by whether an upstream recipe builds on aarch64. Packages in
the `omarchy-recipe` tier belong under `packages/` here; all 14 that build on
aarch64 are now present, copied unchanged from omarchy-pkgs.

## Native integration

On an already configured Arch Spark, the Workbench README documents
`nvwb-spark-setup`, the exact `systemctl` verbs it and the CLI adapter run
through `sudo -n` for the user's own `nvwb-spark@<username>.service`, and a
sudoers rule limited to them. The setup expects a home under `/home/<username>`
and validates everything before it changes `~/.nvwb`. The bring-up machine used
temporary passwordless sudo; do not add unrestricted sudo just to reproduce the
preview. The package installs no policy, and its backend uses one fixed
loopback port, so it is a single-user arrangement.

Upgrading `omarchy-settings` keeps locally edited `/etc/nsswitch.conf`,
`/etc/security/faillock.conf`, `/etc/os-release`, plymouth, CUPS and
`/etc/skel/.bashrc` files and leaves the packaged content beside them as
`<path>.pacnew` with a warning, as pacman does for its own configuration
files. Untouched distribution defaults and files the package itself applied
earlier are replaced. The upgrade path was exercised on the test Spark, where
the live files were left untouched; the `.pacnew` branch is covered by the
regression tests.

Dashboard read-only status is available through
`sudo dgx-arch-package-status --refresh`. Its combined Ubuntu update/reboot method
is disabled. It does not install Arch updates or firmware.

Omarchy's own system setup runs on the port through its normal entry point,
with the ARM patch adapting four of its scripts:

```sh
sudo omarchy-apply-system --install-user <user> --first-install
```

That applies the config, hardware, login and post-install phases: lock-screen
PAM, the faillock limit, SSH and PATH defaults, Chromium policies, service
enablement (cups, systemd-resolved, oomd, kernel-modules cleanup) and the
firewall. The patch skips Snapper on a non-Btrfs root, writes the ARM pacman
configuration instead of the x86 one, adds firewall rules for SSH, mDNS and
Tailscale when those services are enabled so the machine stays reachable, and
leaves the DGX Spark kernel's initramfs without the early NVIDIA module
drop-in. The firewall denies all other incoming traffic, including the
ConnectX ports; add rules before multi-node RDMA. The user phase
(`install/user`) runs through Omarchy's first-boot provisioning as upstream.

Bootloader installation, key enrollment, external-drive selection and rollback
are still not automated here, and the ISO's partitioning and bootloader steps
assume Limine and Btrfs rather than the tested external ext4/GRUB layout.
