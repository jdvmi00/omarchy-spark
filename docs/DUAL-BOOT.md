# Dual boot on the internal NVMe

The port can live on the Spark's internal NVMe beside DGX OS, which stays
bootable as the recovery path and factory baseline. This is how the test
machine has run since 2026-09-06, and the two scripts under `image/` are the
procedure that put it there. They assume an already working Arch installation
on an external drive; the external drive then becomes the fallback.

## Layout

| Partition | Before | After |
| --- | --- | --- |
| p1 | 298 MB EFI, Ubuntu's shim and GRUB | unchanged, plus `EFI/OmarchySpark/` |
| p2 | 3.7 TB ext4, DGX OS | 1 TB ext4, DGX OS, same UUID and partition GUID |
| p3 | — | 2.7 TB ext4 `SPARK_ARCH_NVME`, the port |

## Procedure

Boot the external Arch installation. DGX OS must be unmounted. Then, as root:

```sh
image/nvme-add-arch-partition.sh /dev/nvme0n1 2 1024   # shrink DGX OS to 1 TiB, add p3, copy /
image/nvme-configure-boot.sh    /dev/nvme0n1 1         # fstab, initramfs, GRUB, boot entry
```

The first script checks the DGX OS filesystem, shrinks it, rewrites its GPT
entry keeping the partition GUID and type, creates the new partition, formats
it and copies the running system with rsync. The second writes the new root's
fstab and initramfs configuration (NVMe plus the USB modules the external boot
used), a GRUB menu with entries for the port, DGX OS through Ubuntu's shim and
the firmware, then runs `grub-install` inside a chroot so Arch's loader lands
in its own directory of the shared EFI partition with its own UEFI boot entry.
Ubuntu's files there are not modified. Reboot; the firmware menu keeps
offering DGX OS and the external drive.

## Notes

- Secure Boot was disabled for the unsigned external boot and stays disabled;
  DGX OS's shim still chainloads with it off.
- The DGX OS partition's Ubuntu fstab and GRUB refer to filesystem UUIDs, which
  the shrink preserves. A 1 GiB margin sits between the shrunk filesystem and
  the partition end.
- The shrink took about ten minutes for 338 GB used; the copy of 107 GB about
  four minutes. Read throughput on the NVMe is roughly 8 GB/s against 1.6 GB/s
  on the external SSD over USB 3.2.
- The staged fwupd firmware capsule found in the EFI partition is left alone.
- Booting DGX OS from the new GRUB menu has not yet been exercised; the
  firmware's own `ubuntu` entry remains the tested way in.
