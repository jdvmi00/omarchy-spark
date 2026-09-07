# Requirements for a supported release

The goal is a maintained native Arch Linux ARM port with the Spark development
experience available on the host. The current source-only developer preview is
an early milestone. These gates define the evidence required before calling the
port stable or recommending it as a supported daily-driver installation.

| Gate | Current evidence | Required before promotion |
| --- | --- | --- |
| Source and provenance | Public recipes, hashes, Git pins, license notices and regression CI | Review new payload terms and provenance for every distributed artifact; preserve corresponding source and notices where required |
| Complete build | All 28 recipes built from the committed tree in a fresh ARM64 container with logs and hashes (`manifests/clean-build-2026-09-06.json`); host regression suite passes | Build every shipped package in a fresh ARM64 environment with recorded dependencies, logs and resulting hashes |
| Installation | One manually integrated external-SSD installation, since moved onto the internal NVMe beside DGX OS by a scripted, documented procedure | Publish and test a complete procedure from stock DGX OS, including boot setup, external-drive selection and recovery |
| Independent replication | One physical Spark tested | A second contributor reproduces installation and core workloads on another Spark using only public instructions |
| Updates and recovery | No validated update/rollback path | Test a coherent kernel/driver/userspace update and recovery from a failed update; document supported version combinations |
| Desktop and hardware | Accelerated Omarchy at 4K and 6K; screensaver, lock screen and firewall verified; several devices detected | Verify suspend/resume where supported, sustained workloads, networking, audible audio and Bluetooth pairing; document exclusions |
| Compute and developer tools | Native CUDA, GPU containers and a Workbench GPU/Jupyter project | Maintain an explicit factory-tooling parity matrix with supported versions, workload tests and documented omissions |
| Workbench and Dashboard | Single-user Workbench; read-only Dashboard package status | Validate documented lifecycle and failure recovery; clearly delimit unsupported vendor update and firmware operations |
| Release operation | Source prereleases and CI | Name maintainers, define support scope and release procedure, and verify artifact integrity for any binary distribution |

A passing host test suite covers repository behavior, not these hardware and
release gates. Record evidence against an exact commit and hardware/software
combination in [hardware validation](HARDWARE-VALIDATION.md). Revise this table as
evidence arrives; unresolved requirements stay visible in [known issues](KNOWN-ISSUES.md).

Official endorsement from NVIDIA, Arch Linux ARM or Omarchy is not implied by
meeting these criteria. The project remains an independent community port.
