# v0.1.0-preview.1 — Omarchy Spark developer preview

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
