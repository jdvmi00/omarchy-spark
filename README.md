# Omarchy Spark

Native Arch Linux ARM and Omarchy for NVIDIA DGX Spark, with ports of its NVIDIA
compute and development tools.

**Developer preview: v0.1.0-preview.1.** This is a source release for developers,
not an installer or a supported replacement for DGX OS. One physical Spark has
booted from an external SSD with accelerated Omarchy, native CUDA, GPU containers
and an AI Workbench GPU project. Full factory software parity is still in progress.

## What works on the test machine

| Component | Verified behavior |
| --- | --- |
| Boot and storage | Native ARM64 kernel, external USB SSD root, Ethernet and SSH |
| Omarchy | Login, Hyprland/Quickshell, NVIDIA acceleration at 3840×2160 |
| CUDA | Native compilation and kernel execution; 4 MiB unified-memory verification |
| Containers | Docker with NVIDIA runtime; CUDA execution inside containers |
| AI Workbench | Native backend, ARM64 project build, GPU execution, JupyterLab HTTP 200 with the server token (page-level check only); repeated after backend restart |
| DGX Dashboard | Web service, firmware inventory and read-only Arch package status |
| Networking and audio | Four RDMA devices, Bluetooth controller and HDMI audio sink detected |

See [hardware validation](docs/HARDWARE-VALIDATION.md) for versions, test scope and
limitations. Container workloads run on the native Arch host; Workbench itself
is not hidden inside an Ubuntu VM.

## Start here

- [Build and test the source](BUILDING.md)
- [Known issues and remaining work](docs/KNOWN-ISSUES.md)
- [Release notes and unreleased corrections](docs/RELEASE-NOTES.md)
- [Publication review and post-publication reassessment](docs/RELEASE-REVIEW.md)
- [Upstream provenance and licenses](THIRD_PARTY.md)
- [Contributing](CONTRIBUTING.md)

`packages/` contains Arch recipes and compatibility helpers; `patches/` contains
upstream changes; `manifests/` and `upstream-lock.json` record source locations and
pins. Tests include host-side regression checks and explicitly separate native
integration probes; passing them does not certify the operating system, the
vendor software or any installed machine. `image/make-disk-image.py` assembles
regular files only; it is not an installer and does not configure a bootable
root filesystem for you.

The preview deliberately ships no boot image, vendor binary packages, firmware,
private inventories, credentials, or automated raw-disk writer. NVIDIA payloads
are downloaded from their upstream locations when you build the recipes, under
their own terms. Original project code is MIT licensed; third-party material
retains its applicable licenses.

This is an independent community project, not an official NVIDIA or Omarchy
release. Keep a working recovery path. Kernel, graphics, firmware and rolling Arch
updates require testing as a set; an ordinary package upgrade is not yet a
validated update/rollback workflow for this port.
