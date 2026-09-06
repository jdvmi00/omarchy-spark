# Hardware validation — 2026-09-06

Observed on one NVIDIA DGX Spark, booted natively from an external USB SSD.
The internal DGX OS installation was preserved. These are summarized local test
results, not a certification, independent replication or proof of full parity.
Private host identifiers, serial numbers, logs and credentials are not included.

| Layer | Tested version / result |
| --- | --- |
| Host | Arch Linux ARM, aarch64, 4 KiB kernel pages |
| Kernel | 6.17.9-dgx-spark; NVIDIA open modules built through DKMS |
| GPU | GB10, NVIDIA 610.57.04 |
| CUDA/compiler | CUDA 13.0.3, nvcc 13.0.88, side-by-side GCC 15.3.0 |
| Desktop | Omarchy 4.0.2-6, settings 4.0.2-3, Hyprland 0.56.1, Quickshell |
| Display | NVIDIA-accelerated 3840×2160; no Hyprland configuration errors |
| Workbench | Desktop 0.169.2.16-5; native service 0.95.2-5, CLI 0.72.1-10 |
| Dashboard | 0.25.11-2; both services active, HTTP 200, firmware discovery |
| RDMA | rdma-core 64.0; four devices found; fabric links down |
| perftest | 26.04.17-1, CUDA sm_121 plugin relocation checks pass |

## Compute and Workbench

The native CUDA smoke test executes a GPU kernel and verifies 4 MiB of unified
memory on the CPU. The same check passes inside a Docker GPU container.
Workbench creates and builds an ARM64 project using
`nvcr.io/nvidia/ai-workbench/python-cuda130:1.0.1`. With one GPU requested,
its container uses the NVIDIA runtime and sees GB10. Authenticated JupyterLab
returns HTTP 200. The CUDA smoke binary executes inside that container; the
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
lock/unlock, sustained thermals, comprehensive Nsight workflows, authenticated
Dashboard telemetry/notebooks, private registry/remote Workbench integrations,
firmware installation, a complete default application set, and update/rollback.
No firmware was flashed. The external drive negotiated USB 2.0 during bring-up;
storage performance is not representative of its advertised maximum.
