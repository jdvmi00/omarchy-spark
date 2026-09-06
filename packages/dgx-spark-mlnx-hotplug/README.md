# ConnectX-7 hotplug package

Initial Arch packaging of NVIDIA's `26.01-1` userspace helper. The source version
and SHA256 come from the pinned NixOS port in `upstream-lock.json`; this is not
yet confirmed to match the test machine’s installed version.

The NVIDIA script and its expected `/opt/nvidia` path are retained. The udev rule
is installed under Arch's `/usr/lib/udev/rules.d`. The vendor installation's
enablement marker is represented as a package-managed configuration file. The
kernel module is loaded at boot, matching the NixOS integration. A kernel with
`CONFIG_MTK_PCIE_HOTPLUG` is required.

This package does not trigger udev events or unload/reload networking during
installation. Hardware behavior must be verified on the Spark after boot.
Removing the enablement marker disables hotplug according to the vendor helper;
review marker restoration during package reinstall/upgrade if using that mode.

Build on Arch ARM with `makepkg`. The payload contains scripts and configuration,
so packaging can also be checked on x86 with a makepkg configuration setting
`CARCH=aarch64`; this does not validate runtime behavior on ARM.

Reference: https://github.com/graham33/nixos-dgx-spark/tree/main/packages/dgx-spark-mlnx-hotplug
