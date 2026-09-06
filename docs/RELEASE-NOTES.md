# Release notes

## Unreleased changes after v0.1.0-preview.1

Corrections from the post-publication readiness review, present in the main
branch and not in a tagged release. They were installed and re-checked on the
single test Spark on 2026-09-06 (see the hardware report):

- `omarchy-settings` 4.0.2-4: the install scriptlet keeps administrator edits
  to `/etc/nsswitch.conf`, `/etc/security/faillock.conf`, `/etc/os-release`,
  plymouth, CUPS and `/etc/skel/.bashrc`, writing changed content as `.pacnew`
  and recording applied checksums under `/var/lib/omarchy/etc-overrides`.
- `nvidia-ai-workbench` 0.169.2.16-6: `nvwb-spark-setup` runs every check,
  including the local-context conflict check, before writing anything, writes
  its config atomically and no longer runs a global `daemon-reload`. The README
  lists the exact privileged commands, the fixed port and the single-user scope.
- `image/make-disk-image.py` refuses image names ending in `.json` and never
  overwrites an existing manifest sidecar.
- `tests/check-jupyter-runtime.py` requires authenticated contents and status
  API responses without following redirects and fails unless requests with no
  token and with a wrong token are refused. Tokens are still never printed.
- New host-side regression tests cover each change; a SECURITY.md describes
  private reporting.

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
