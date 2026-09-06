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
firmware installation, a complete default application set, and update/rollback.
No firmware was flashed. The external drive negotiated USB 2.0 during bring-up;
storage performance is not representative of its advertised maximum.

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
account password, confirmed at the desk. systemd-resolved starts on the next
boot; DNS through it and the firewall at boot were not yet observed.
Omarchy's aarch64 package repository was synced and holds only omarchy-keyring.
