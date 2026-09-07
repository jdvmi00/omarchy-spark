#!/bin/bash
# Make room for the port on the Spark's internal NVMe beside DGX OS, and copy
# the running Arch system into the new partition. Run as root from the booted
# external-SSD installation; DGX OS must be unmounted throughout.
#
#   nvme-add-arch-partition.sh DISK DGX_PART NEW_SIZE_GIB
#   e.g. nvme-add-arch-partition.sh /dev/nvme0n1 2 1024
#
# 1. e2fsck, then shrink the DGX OS ext4 filesystem to NEW_SIZE_GIB.
# 2. Rewrite its GPT entry to that size plus a 1 GiB margin, keeping the
#    partition GUID and type, and add a new partition for Arch in the rest.
# 3. mkfs.ext4 the new partition and rsync the running system into it.
# The first step is the only destructive one; the filesystem check before it
# and the free-space margin after it are what make it routine. DGX OS
# references its root by filesystem UUID, which the shrink does not change.
set -euo pipefail
DISK=${1:?disk}; DGX=${2:?DGX partition number}; SIZE_GIB=${3:?new DGX size in GiB}
PART="${DISK}p${DGX}"
(( EUID == 0 )) || { echo "run as root"; exit 1; }
findmnt "$PART" >/dev/null && { echo "$PART is mounted"; exit 1; }
LABEL=SPARK_ARCH_NVME

read -r START END GUID TYPE < <(sgdisk -i "$DGX" "$DISK" | awk '
  /^First sector/ {s=$3} /^Last sector/ {e=$3} /unique GUID/ {g=$4} /^Partition GUID code/ {t=$4}
  END {print s, e, g, t}')
DISK_END=$(sgdisk -p "$DISK" | awk -v n="$DGX" '$1==n {print $3}')
BLOCKS=$(( SIZE_GIB * 1024 * 1024 * 1024 / 4096 ))
NEW_END=$(( START + SIZE_GIB * 2097152 + 2097152 - 1 ))
NEXT=$(( NEW_END + 1 ))
(( NEXT % 2048 == 0 )) || { echo "new partition would not be 2048-aligned"; exit 1; }
(( NEW_END < END )) || { echo "requested size is not smaller than the partition"; exit 1; }
MIN=$(resize2fs -P "$PART" | awk '{print $NF}')
(( BLOCKS > MIN + MIN / 10 )) || { echo "requested size too close to the filesystem minimum ($MIN blocks)"; exit 1; }

echo "=== checking and shrinking $PART to ${SIZE_GIB} GiB"
e2fsck -f -y "$PART"
resize2fs -p "$PART" "$BLOCKS"
echo "=== rewriting the partition table"
sgdisk -d "$DGX" -n "$DGX:$START:$NEW_END" -t "$DGX:$TYPE" -u "$DGX:$GUID" \
       -n "0:$NEXT:$DISK_END" -t 0:8300 -c 0:"$LABEL" "$DISK"
partprobe "$DISK"; sleep 2
sgdisk -p "$DISK" | tail -n +8
e2fsck -fn "$PART" | tail -1
NEW=$(blkid -L "$LABEL")
echo "=== new root $NEW"
mkfs.ext4 -q -F -L "$LABEL" "$NEW"
mkdir -p /mnt/nvme && mount "$NEW" /mnt/nvme
echo "=== copying the running system"
rsync -aHAXx --numeric-ids --info=stats1 \
  --exclude=/dev/* --exclude=/proc/* --exclude=/sys/* --exclude=/run/* --exclude=/tmp/* \
  --exclude=/mnt/* --exclude=/media/* --exclude=/efi/* --exclude=/lost+found --exclude=/var/tmp/* \
  / /mnt/nvme/ | tail -3
mkdir -p /mnt/nvme/{dev,proc,sys,run,tmp,mnt,media,efi,var/tmp}
chmod 1777 /mnt/nvme/tmp /mnt/nvme/var/tmp
blkid -s UUID -o value "$NEW" > /tmp/nvme-root-uuid
echo "copied; new root UUID $(cat /tmp/nvme-root-uuid). Next: nvme-configure-boot.sh"
