# Announcement draft

## Omarchy Spark: native Arch Linux ARM and Omarchy on DGX Spark

Omarchy Spark is now available as a community developer preview. It brings
native Arch Linux ARM and the Omarchy desktop to NVIDIA DGX Spark, alongside
integration for NVIDIA compute and development tools.

On one physical Spark booting from an external SSD, we have verified accelerated
Omarchy at 4K, native CUDA execution, Docker GPU workloads, and an AI Workbench
GPU project with token-protected JupyterLab. DGX Dashboard provides firmware
inventory and read-only Arch package status. These run on the native Arch host;
container workloads still use their own container images.

The public repository includes package recipes, pinned upstream sources,
compatibility patches, provenance notes and 35 passing host regression tests.
This second preview includes configuration-preservation fixes, Workbench setup
preflight checks, image-sidecar protection and stricter Jupyter authentication
checks. The updated packages and Jupyter checks have been re-checked on the Spark.

This is a **source-only developer preview**: no installer or boot image, no
complete clean build or second-machine replication yet, and no tested
update/rollback workflow. Full factory-tooling parity remains in progress.
It is an independent community project, with no official NVIDIA or Omarchy
endorsement.

We welcome contributors who can help reproduce clean ARM64 builds, document an
external-drive installation and test on another Spark. Exact test scope and
remaining release requirements are public.

- [Repository and getting started](https://github.com/jdvmi00/omarchy-spark)
- [Developer preview release](https://github.com/jdvmi00/omarchy-spark/releases/tag/v0.1.0-preview.2)
- [Hardware evidence](https://github.com/jdvmi00/omarchy-spark/blob/v0.1.0-preview.2/docs/HARDWARE-VALIDATION.md)
- [Contribution guide](https://github.com/jdvmi00/omarchy-spark/blob/v0.1.0-preview.2/CONTRIBUTING.md)

---

This is a ready-to-adapt announcement draft; its presence in the repository does
not mean it has been posted to any community forum.
