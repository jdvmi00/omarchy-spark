# Hardware validation — 2026-09-06

Observed on one NVIDIA DGX Spark, booted natively from an external USB SSD.
The internal DGX OS installation was preserved. These are summarized local test
results, not a certification, independent replication or proof of full parity.
Private host identifiers, serial numbers, logs and credentials are not included.
The post-review corrections were later installed on this same machine and
re-checked; see the final section.

| Layer | Tested version / result |
| --- | --- |
| Host | Arch Linux ARM, aarch64, 4 KiB kernel pages |
| Kernel | 6.17.9-dgx-spark; NVIDIA open modules built through DKMS |
| GPU | GB10, NVIDIA 610.57.04 |
| CUDA/compiler | CUDA 13.0.3, nvcc 13.0.88, side-by-side GCC 15.3.0 |
| Desktop | Omarchy 4.0.2-6, settings 4.0.2-3 (later 4.0.2-4), Hyprland 0.56.1, Quickshell |
| Display | NVIDIA-accelerated 3840×2160 at 60 Hz; 6144×2560 at 120 Hz verified working, 60 Hz not (below) |
| Workbench | Desktop 0.169.2.16-5 (later -6); native service 0.95.2-5, CLI 0.72.1-10 |
| Dashboard | 0.25.11-2; both services active, HTTP 200, firmware discovery |
| RDMA | rdma-core 64.0; four devices found; fabric links down |
| perftest | 26.04.17-1, CUDA sm_121 plugin relocation checks pass |

## Compute and Workbench

The native CUDA smoke test executes a GPU kernel and verifies 4 MiB of unified
memory on the CPU. The same check passes inside a Docker GPU container.
Workbench creates and builds an ARM64 project using
`nvcr.io/nvidia/ai-workbench/python-cuda130:1.0.1`. With one GPU requested,
its container uses the NVIDIA runtime and sees GB10. JupyterLab answered HTTP
200 to a request carrying the server token; that original probe checked only
for an HTML page. The stricter probe that replaced it was run later on this
machine (final section). The CUDA smoke binary executes inside that container; the
runtime base itself does not include nvcc. Backend stop/start and project restart
were followed by successful repeats of the notebook and compute checks.

Workbench's original backend runs natively. A service-private OS metadata view
selects its supported Linux detection branch; scoped adapters query the real Arch
Container Toolkit package and normalize NVIDIA's deprecated scalar version
annotations. This is compatibility work, not vendor support for Arch.

## Dashboard

A separate repository database provides actual Arch package status and a
print-only dependency-resolved transaction preview. Live sync database SHA256s
were unchanged. At test time there were zero repository updates and 15 locally
built packages outside the configured repositories. This does not prove the
custom packages are current.

An isolated instance of NVIDIA's backend parsed a synthetic package update's
epoch versions, description and size. The production service retained firmware
inventory and its HTTP endpoint. The combined Ubuntu update/reboot method was
denied before dispatch. Package integrity: 51 files, zero altered.

## Not established

Audible audio, Bluetooth pairing, RDMA throughput/GPU-direct networking, suspend,
sustained thermals, comprehensive Nsight workflows, authenticated
Dashboard telemetry/notebooks, private registry/remote Workbench integrations,
a complete default application set, update/rollback, and recovery from a failed
firmware update.
No firmware was flashed. The external drive negotiated USB 2.0 during bring-up
because of its cable; with a 10 Gb/s-rated USB-C cable on the same port it
links at 20 Gb/s and reads 1.6 GB/s with direct I/O (2026-09-06).

## Post-review corrections re-checked — 2026-09-06

`omarchy-settings` 4.0.2-4 and `nvidia-ai-workbench` 0.169.2.16-6 were built
natively with `makepkg` from the public checkout on the Spark, where the
repository's host-side test suite also passes on aarch64, and installed with
pacman.

- Before the upgrade, the five live override files were byte-identical to the
  packaged overrides; CUPS is not installed, so its two overrides were skipped.
  After the upgrade the five files were unchanged (checksums verified), their
  checksums were recorded under `/var/lib/omarchy/etc-overrides`, and no
  `.pacnew` was created. The only `.pacnew` under `/etc` is pacman's own for the
  locally modified Docker `daemon.json`, created by the first install a day
  earlier. The scriptlet's `.pacnew` branch for edited files was therefore
  exercised only by the host-side tests.
- `nvwb-spark-setup` was re-run against the existing configuration: its checks
  accepted the existing local context, `config.yaml` and `contexts.json` content
  was unchanged, the config mode was 0600, the links and `.bashrc` were
  unchanged, and the service stayed active and enabled.
- The stricter notebook probe, run inside the project container, passed:
  authenticated contents and status API responses, the JupyterLab page without
  a login redirect, and HTTP 403 for requests with no token and with a wrong
  token. After restarting the backend service (ready in about two seconds) and
  starting the project's JupyterLab again through the CLI, the probe passed a
  second time. No tokens were printed or recorded.

This remains a single-machine result; no second machine has reproduced it.

## Base packages and screensaver — 2026-09-06

The 28 packages from Omarchy's base list that the Arch ARM repos offer but the
bring-up had skipped were installed (162 packages with dependencies, including
CUPS, fcitx5, ufw, gpu-screen-recorder, LibreOffice and Kdenlive). `ttfx` 0.3.2
was built natively from upstream's recipe with Rust 1.98 and installed. With it
present, a forced screensaver launch inside the running Hyprland session opened
a fullscreen `org.omarchy.screensaver` window with ttfx running, and stopped
cleanly. The shell's 150-second idle timer was not observed. Omarchy 4 handles
idle and lock in its own shell; `hypridle` and `hyprlock` are intentionally
absent. The audit afterwards reports 124 of 147 base packages installed and
none missing that the repos provide.

## Display modes over HDMI 2.1a — 2026-09-06

NVIDIA's hardware page lists only "1x HDMI 2.1a display connector" and no
maximum. On the attached Dell U5226KW, driver 610.57.04 advertises the panel's
full mode list up to 6144×2560 at 120 Hz. Omarchy's default picks the
display's preferred mode, which this monitor reports as 3840×2160 at 60 Hz
over HDMI, so bring-up ran at 4K.

Switching the live session to 6144×2560 at 120 Hz through Hyprland succeeded
and displayed correctly, confirmed by eye at the panel. 6144×2560 at 60 Hz did
not: Hyprland reported the mode set, but the panel stayed black when the
monitor reconnected after an input switch, and the monitor's input menu froze
until the mode was changed. The 120 Hz mode needs DSC while 60 Hz runs the
uncompressed FRL link at a higher raw rate, so the cable or the monitor's
handling of that path is the likely cause; it was not isolated. The
configuration was returned to the preferred 3840×2160 at 60 Hz, which is also
the cheapest mode in unified-memory scanout bandwidth for a machine serving
models. Only this one monitor and cable were tested.

## Omarchy recipes built natively — 2026-09-06

The 13 remaining base-list packages whose upstream recipes declare aarch64
were built on the Spark with `makepkg -s` from the recipes now under
`packages/`, each unchanged from omarchy-pkgs, and installed. Build times
ranged from 5 seconds (scripts) to about 4.5 minutes (herdr, Rust with a
bundled Zig). Every native binary is an ARM64 ELF, pacman reports no altered
files, and the command-line tools answer version or help calls: cliamp,
herdr, tzupdate, yay, try, tensaku. The desktop apps (omacalc, omacut,
omawrite, aether) were opened on the desktop and launch. The share picker and
the LazyVim configuration were installed but not exercised. localsend was not
attempted: its
recipe builds a Flutter app through fvm, and Flutter publishes no Linux
aarch64 SDK. The audit afterwards reports 137 of 147 base packages installed.

## Omarchy system setup applied — 2026-09-06

`omarchy-apply-system --install-user jmartin --first-install` from omarchy
4.0.2-7 ran on the Spark with zero failed steps. Snapper was skipped on the
ext4 root, the ARM pacman configuration was kept, the NVIDIA step installed
only libva-nvidia-driver and the modprobe file and left the initramfs
drop-ins untouched, and the lock-screen PAM file, faillock limit, SDDM PAM
cleanup, SSH keepalive, PAM PATH, Chromium policies and updatedb settings
were all written. cups, systemd-resolved, systemd-oomd and the kernel-modules
cleanup service are enabled and NetworkManager-wait-online is masked. ufw was
enabled and then started: a fresh SSH connection, mDNS resolution of the
hostname and the running Docker containers all still worked, with the SSH,
mDNS, LocalSend and Docker DNS rules present and ufw-docker's block in
after.rules. The shell's lock screen was then locked and unlocked with the
account password, confirmed at the desk. After a reboot, ufw was active from
boot, systemd-resolved was active with NetworkManager feeding it the network's
DNS servers, name resolution and mDNS worked, every service including the
Workbench backend and Dashboard came up, the desktop session started at
3840×2160, and no unit had failed.
Omarchy's aarch64 package repository was synced and holds only omarchy-keyring.

## Clean build of every recipe — 2026-09-06

All 28 recipes under `packages/` built with `makepkg -s` from the committed tree
alone (commit 28b895f) inside a fresh `menci/archlinuxarm` container on the
Spark, using only Arch Linux ARM's repositories plus a local repository of the
recipes built earlier in the run. Every package version equals the one
installed on the test machine. The kernel took 97 minutes on the recipe's
default six build jobs, GCC 15 sixteen minutes, CUDA nine; the whole run about
two and a half hours. One failure, `omarchy`, was caused by the local
repository not being configured in the container at that point and passed on
rerun; the container script now configures it during setup. Checksums and the
container toolchain are in `manifests/clean-build-2026-09-06.json`. The NVIDIA
driver packages were not part of the run; they come from Arch Linux ARM.

## Moved onto the internal NVMe — 2026-09-06

DGX OS's 3.7 TB ext4 partition (338 GB used) was checked and shrunk to 1 TiB
in about ten minutes, its GPT entry rewritten with the partition GUID and type
preserved, and a 2.7 TB partition created after it. The running external-SSD
system (107 GB) was copied in with rsync, given an NVMe-capable initramfs and
a GRUB menu that also chainloads Ubuntu's shim, and Arch's GRUB was installed
into the shared EFI partition as `EFI/OmarchySpark` with its own UEFI entry,
placed first in the boot order. The Spark rebooted from the NVMe through that
entry: root on the new partition, EFI from the shared one, every service up,
Hyprland on the GB10, and no failed unit. The DGX OS filesystem checks clean
afterwards. Direct reads from the NVMe run about 8.3 GB/s. The external SSD
remains intact as a fallback. Booting DGX OS through the new menu entry was
not exercised; its own firmware entry still exists. The procedure is in
docs/DUAL-BOOT.md and image/nvme-*.sh.

## Workbench after the NVMe boot — 2026-09-06

The desktop app reported a compatibility error. The backend log showed every
outbound lookup going to a refused localhost resolver: the unit orders after
`network-online.target`, which Omarchy's masking of NetworkManager-wait-online
now reaches 0.05 s after NetworkManager starts, and the backend came up two
seconds later, before DHCP. Host DNS itself was fine. Restarting the service
fixed it immediately, and the model catalog loaded. nvidia-ai-workbench
0.169.2.16-7 adds a non-fatal `nm-online` wait to the unit; it was installed
and the service restarted through the new unit.

The desktop app separately showed "Cannot install on your operating system".
Its code runs `cat /etc/*-release` and requires Ubuntu's `DISTRIB_*` lines
before contacting the backend. Launched through a bubblewrap wrapper that
binds a compatibility file over `/etc/os-release` for the app only, its log
reports the OS supported and Workbench installed, and it opens its Locations
Manager. nvidia-ai-workbench 0.169.2.16-8 ships that launcher as
`/usr/bin/nvidia-ai-workbench` and points the desktop entry at it.

## Dashboard launcher and Share — 2026-09-06

The DGX Dashboard desktop entry failed with permission denied: NVIDIA's
archive ships `/usr/bin/dgx-dashboard` without an executable bit and the
recipe copied it as-is. dgx-dashboard 0.25.11-3 sets the mode; the entry now
opens Chromium on the Dashboard. Omarchy's Share menu runs `localsend`, which
the port could not build from source; `localsend` 1.18.2-1 packages the
project's own Linux arm64 bundle and the app starts on the desktop. Sending to
a peer was not exercised.

## Firmware updated from the port — 2026-09-06

fwupd 2.1.7 on the port, with the standard LVFS remote, offered NVIDIA's
Embedded Controller update (0x03000302 to 0x03000508) and SoC firmware update
(0x0200980f to 0x02009b0b), both signed and delivered as UEFI capsules on
disk. `fwupdmgr update` wrote both capsules to the shared EFI partition and
set the firmware's capsule flag; the UEFI applied them during the next boot.
Afterwards fwupd reports both as Success at the new versions, the capsules
were consumed and the flag cleared, and the Spark booted through its NVMe
entry with the GPU driver, 4K display and all services as before. This is
the same mechanism the DGX Dashboard uses, so its firmware update button is
expected to work on the port; that button itself was not pressed. Recovery
from a failed update was not exercised.

## Ghostty — 2026-09-07

Omarchy's Install → Terminal → Ghostty failed with "target not found": Arch
Linux ARM does not build Ghostty. Arch's own recipe builds it on the Spark
once two things are changed: Zig 0.15.2 is fetched from ziglang.org because
the repository's Zig is 0.16 and Ghostty 1.3.1 cannot use it, and the pandoc
documentation step is disabled because Arch Linux ARM has no pandoc. The four
split packages install cleanly, `ghostty --version` answers, the desktop entry
is present, and Omarchy's install flow now finds the package. Man pages are
not shipped.
