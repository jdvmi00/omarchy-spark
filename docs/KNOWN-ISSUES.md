# Known issues and remaining work

- No end-user installer, public boot image, signed port package repository or
  tested upgrade/rollback workflow. The test installation was assembled manually.
- No complete clean-chroot build or independent hardware replication yet.
  Source pins do not freeze rolling Arch build/runtime dependencies. A fresh
  ARM clean build and a second-machine installation are required before the
  port is promoted beyond a source-only developer preview.
- Corrections made after the preview.1 review (the settings scriptlet keeping
  local `/etc` edits, Workbench setup validating before writing, the image
  manifest guard and the stricter notebook probe) are covered by host-side
  tests only. They have not yet been installed or re-run on the Spark, and the
  hardware report describes the preview.1 packages.
- Full DGX OS and Omarchy default application parity is incomplete. The missing
  ARM package manifest is a dated research list, not an installer manifest.
- Dashboard package queries work, but package-query failures may be collapsed
  into an empty list by NVIDIA's UI. Check the status helper's exit code and
  timestamp. The UI may offer Update, but its combined update/reboot operation
  returns Access denied. Native installation/rollback is not implemented.
- Workbench's native backend uses scoped compatibility adapters. Its vendor
  installer/self-updater still assumes Ubuntu. Remote locations, private
  credentials and full desktop project interaction remain unvalidated. The
  package README lists the exact privileged commands and an example sudoers
  rule, but installs no policy; the backend uses one fixed loopback port and
  supports a single user per host.
- Bluetooth/audio devices and RDMA interfaces are detected; practical playback,
  pairing and peer throughput have not been established.
- Firmware discovery works; firmware maintenance and recovery are unvalidated.
- The tested external ext4/GRUB setup differs from Omarchy's standard
  Limine/Snapper assumptions. The Limine patch tests are source-level regression
  checks, not evidence that the preview boots with Limine.
- CUDA's host compiler is GCC 15 under `/opt/gcc15`; the system compiler can be
  newer. GDS, all profiler/debugger paths and broad AI workloads are unvalidated.

Priorities: reproducible clean builds and a coherent package repository; native
Dashboard transactions and failure reporting; remaining default applications;
hardware stress/power testing; then installation and recovery automation.
