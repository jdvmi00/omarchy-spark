# Spark baseline kernel

Adapted from RageLtd/linux-dgx-spark at the revision recorded in
`upstream-lock.json`; the upstream MIT packaging license is retained here.

This build pins Ubuntu/NVIDIA source release `6.17.0-1014.14`, matching the test machine’s
running kernel package. The patched source reports Linux **6.17.9** internally.
The resulting Arch kernel release is `6.17.9-dgx-spark`.

The source archive/diff SHA256 values come from the corresponding Launchpad DSC
retrieved over HTTPS; the PGP signature has not independently been verified.
The initial config was captured from the test machine. Source and config checksums are
required, and Ubuntu patch failures abort the build.

Changes to the captured config:

- Remove Canonical certificate file references, which are not Arch signing keys.
- Disable optional debug-info/BTF and Rust build support to avoid unrelated
  Ubuntu toolchain dependencies in this initial bring-up build.
- Apply the upstream Arch packaging's framebuffer, live-image filesystem, USB,
  Wi-Fi and ConnectX-7 requirements.
- Keep 4 KB pages, matching the test machine. The upstream optional 64 KB variant has not
  been tested here.

The build retains the broad Ubuntu hardware/module configuration and may take
substantial time. `BUILD_JOBS` defaults to six. Use a fresh build directory for
each configuration or page-size variant; do not reuse prepared source trees
across variants.

Kernel compilation is not proof of bootability. Boot, GPU module loading,
networking, firmware handling, and a complete DKMS build remain separate tests.
