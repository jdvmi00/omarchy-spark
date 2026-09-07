#!/bin/bash
# Configure the copied Arch root on the internal NVMe to boot on its own and
# install its GRUB into the EFI partition shared with DGX OS, whose loader
# files are left untouched. Run as root after nvme-add-arch-partition.sh.
#
#   nvme-configure-boot.sh DISK ESP_PART
#   e.g. nvme-configure-boot.sh /dev/nvme0n1 1
set -euo pipefail
DISK=${1:?disk}; ESP="${DISK}p${2:?EFI partition number}"
(( EUID == 0 )) || { echo "run as root"; exit 1; }
NEW_UUID=$(cat /tmp/nvme-root-uuid)
ESP_UUID=$(blkid -s UUID -o value "$ESP")
KERNEL=$(ls /usr/lib/modules | grep dgx-spark | head -1)
mountpoint -q /mnt/nvme || mount "$(blkid -U "$NEW_UUID")" /mnt/nvme
mkdir -p /mnt/nvme/efi && mount "$ESP" /mnt/nvme/efi

cat > /mnt/nvme/etc/fstab <<F
UUID=$NEW_UUID / ext4 defaults,noatime 0 1
UUID=$ESP_UUID /efi vfat defaults,umask=0077,nofail 0 2
F
cat > /mnt/nvme/etc/mkinitcpio.conf.d/20-spark.conf <<'F'
# No host autodetection: include NVMe root, USB root and filesystem support.
MODULES=(nvme xhci_pci xhci_hcd uas usb_storage sd_mod ext4)
HOOKS=(base systemd modconf keyboard block filesystems fsck)
COMPRESSION="zstd"
F
# Same command line the external-SSD bring-up boots with.
CMDLINE="rw rootwait init_on_alloc=0 iommu.passthrough=0 console=tty0 console=ttyS0,921600 earlycon=uart,mmio32,0x16A00000 modprobe.blacklist=nouveau,r8169 initcall_blacklist=tegra234_cbb_init pci=pcie_bus_safe"
cat > /mnt/nvme/boot/grub/grub.cfg <<F
set timeout=5
set default=0
menuentry 'Omarchy Spark (Arch Linux ARM, internal NVMe)' {
 search --no-floppy --fs-uuid --set=root $NEW_UUID
 linux /boot/vmlinuz-linux-dgx-spark root=UUID=$NEW_UUID $CMDLINE
 initrd /boot/initramfs-linux-dgx-spark.img
}
menuentry 'DGX OS (Ubuntu, internal NVMe)' {
 search --no-floppy --fs-uuid --set=root $ESP_UUID
 chainloader /EFI/ubuntu/shimaa64.efi
}
menuentry 'UEFI firmware settings' { fwsetup }
F
grub-script-check /mnt/nvme/boot/grub/grub.cfg
arch-chroot /mnt/nvme bash -e -c "
  mkinitcpio -k $KERNEL -g /boot/initramfs-linux-dgx-spark.img 2>&1 | grep -E 'Image generation|ERROR'
  grub-install --target=arm64-efi --efi-directory=/efi --bootloader-id=OmarchySpark --recheck 2>&1 | tail -1"
ls /mnt/nvme/efi/EFI
efibootmgr | grep -E 'BootOrder|OmarchySpark|ubuntu'
umount /mnt/nvme/efi; sync; umount /mnt/nvme
echo "done: reboot; the firmware menu still offers DGX OS and the external drive"
