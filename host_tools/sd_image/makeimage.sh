#!/bin/bash
FAT_SPACE="102400"

# uBoot ENV offset
SDIMG_UBOOT_ENV_OFFSET="512"
ENV_BASE_NAME="${UBOOT_CONFIG}"

# Boot partition begin at sector 1024
# This is required as for c5/a5 mainline uboot hard codes the location
# of the uboot image in the sdcard to 0xa00 sector
IMAGE_ROOTFS_ALIGNMENT="1024"

ROOTFS_SIZE="2048000"
# ROOTFS_SIZE_MOD="524288"
ROOTFS_SIZE_MOD="16384" #16KiB

# Align partitions
BOOT_SPACE_ALIGNED=$(expr ${BOOT_SPACE} + ${IMAGE_ROOTFS_ALIGNMENT} - 1)   #(2048 + 1024 -1 = 3071)
BOOT_SPACE_ALIGNED=$(expr ${BOOT_SPACE_ALIGNED} - ${BOOT_SPACE_ALIGNED} % ${IMAGE_ROOTFS_ALIGNMENT}) #3071 - 3071%1024 = 2048
FAT_SPACE_ALIGNED=$(expr ${FAT_SPACE} + ${IMAGE_ROOTFS_ALIGNMENT} - 1)   # 102400  + 1024 -1 = 102400 + 1023
FAT_SPACE_ALIGNED=$(expr ${FAT_SPACE_ALIGNED} - ${FAT_SPACE_ALIGNED} % ${IMAGE_ROOTFS_ALIGNMENT}) # 102400 + 1023 - (102400 + 1023)%1024 = 102400

ROOTFS_SIZE_ALIGNED=$(expr ${ROOTFS_SIZE} \+ ${ROOTFS_SIZE_MOD})  #
ROOTFS_SIZE_ALIGNED=$(expr ${ROOTFS_SIZE_ALIGNED} \- ${ROOTFS_SIZE_ALIGNED} \% ${ROOTFS_SIZE_MOD})

SDIMG_SIZE=$(expr ${IMAGE_ROOTFS_ALIGNMENT} \+ ${BOOT_SPACE_ALIGNED} \+ ${FAT_SPACE_ALIGNED} \+ ${ROOTFS_SIZE_ALIGNED} \+ ${IMAGE_ROOTFS_ALIGNMENT})

SDIMG="atca-g400.img"
rm -f ./${SDIMG}
dd if=/dev/zero of=${SDIMG} bs=1K count=0 seek=${SDIMG_SIZE} 

# Create partition table
parted -s ${SDIMG} mklabel msdos

parted -s ${SDIMG} unit KiB mkpart primary fat32 $(expr  ${IMAGE_ROOTFS_ALIGNMENT} \+ ${BOOT_SPACE_ALIGNED}) $(expr ${IMAGE_ROOTFS_ALIGNMENT} \+ ${BOOT_SPACE_ALIGNED} \+ ${FAT_SPACE_ALIGNED})

# set fat partition as bootable for distroboot
parted -s ${SDIMG} set 1 boot on

# P2: Linux FS partition
parted -s ${SDIMG} unit KiB mkpart primary $(expr ${IMAGE_ROOTFS_ALIGNMENT} \+ ${BOOT_SPACE_ALIGNED} \+ ${FAT_SPACE_ALIGNED}) $(expr ${IMAGE_ROOTFS_ALIGNMENT} \+ ${BOOT_SPACE_ALIGNED} \+ ${FAT_SPACE_ALIGNED} \+ ${ROOTFS_SIZE_ALIGNED})

# P3: A2 partition for bootloader
parted -s ${SDIMG} unit KiB mkpart primary ${IMAGE_ROOTFS_ALIGNMENT} $(expr ${BOOT_SPACE_ALIGNED} \+ ${IMAGE_ROOTFS_ALIGNMENT})

# set part 3 to type a2 for spl / uboot image
# 446 to partition table, 16 bytes per entry, 4 byte offset to partition type
echo -ne "\xa2" | dd of=${SDIMG} bs=1 count=1 seek=$(expr 446 + 16 + 16 + 4) conv=notrunc && sync && sync

# Create a vfat image with boot files
FAT_BLOCKS=$(LC_ALL=C parted -s ${SDIMG} unit b print | awk '/ 1 / { print substr($4, 1, length($4 -1)) / 512 /2 }')
echo "FAT_BLOCKS" ${FAT_BLOCKS}
rm -f ./vfat.img
mkfs.vfat -n "${BOOTDD_VOLUME_ID}" -S 512 -C ./vfat.img ${FAT_BLOCKS}

#copy zImage dtb rtf to vfat image.
mcopy -i vfat.img  -s ./kernel/zImage ::/zImage
mcopy -i vfat.img  -s ./kernel/chameleon96.rbf ::/chameleon96.rbf
mcopy -i vfat.img  -s ./kernel/extlinux ::/
mcopy -i vfat.img  -s ./kernel/image-version-info ::/image-version-info
mcopy -i vfat.img  -s ./kernel/socfpga_cyclone5_chameleon96.dtb ::/socfpga_cyclone5_chameleon96.dtb
mcopy -i vfat.img  -s ./kernel/u-boot.scr ::/u-boot.scr

#Generate root filesystem.
dd if=/dev/zero of=rootfs.img bs=1K count=0 seek=${ROOTFS_SIZE}

#format to ext3
mkfs.ext3 rootfs.img

#mount to /mnt
#  losetup -d /dev/loop1
losetup /dev/loop1 rootfs.img
mount /dev/loop1 /mnt
cp -a rootfs/* /mnt
umount /mnt
losetup -d /dev/loop1

dd if=vfat.img of=${SDIMG} bs=1M count=100 seek=3 conv=notrunc
dd if=rootfs.img of=${SDIMG} bs=1M count=1900 seek=103 conv=notrunc
dd if=bootloader/preloader-mkpimage.bin of=${SDIMG} bs=256K  seek=4 conv=notrunc
dd if=bootloader/u-boot.img  of=${SDIMG} bs=256K  seek=5 conv=notrunc
rm vfat.img rootfs.img
