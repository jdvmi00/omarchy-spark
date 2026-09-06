# Release notes

## v0.1.0-preview.2 — Community developer preview

Source-only release incorporating the post-publication readiness corrections.
The updated settings and Workbench packages were installed and re-checked on the
single test Spark on 2026-09-06; the stricter Jupyter probe passed again after a
backend restart. See [hardware validation](HARDWARE-VALIDATION.md) for scope.
All 35 host regression tests pass. This does not establish a complete clean
package build or independent hardware replication.

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
- Base package parity: `scripts/audit-base-packages.py` and the generated
  `manifests/omarchy-base-arm-status.json` replace the dated research list.
  A `ttfx` recipe (upstream's, unchanged) restores the Omarchy screensaver,
  whose launcher exits silently without it. Every base package the Arch ARM
  repos offer is now installed on the test machine.

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
