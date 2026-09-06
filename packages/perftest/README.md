# RDMA performance tests on Spark

Pinned upstream linux-rdma/perftest 26.04.17, matching the revision selected by
our pinned NixOS reference. The official tag archive is SHA256-verified.

This build enables CUDA explicitly and targets GB10 (sm_121). NVCC uses the
packaged GCC 15 compiler through NVCC_CCBIN; the system GCC 16 exceeds CUDA 13.0's
supported compiler range. The upstream build autodetects CUDA and does not honor
`--without-cuda`, so relying on that option is insufficient on a CUDA host.

The binary offers ordinary host-memory tests as well as CUDA modes. Runtime
fabric throughput, GPU-direct registration and peer connectivity remain
unverified; the four local RDMA devices currently report down links.
