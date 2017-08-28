#!/bin/bash
#generate sd image
sudo dd if=/dev/zero of=sdimage.img bs=1  count=0 seek=5G
sudo dd if=mbr.img   of=sdimage.img bs=1M count=3 conv=notrunc 
#generate vfat image
sudo dd if=/dev/zero of=vfat.img bs=1 count=0 seek=100M
#format to vfat
sudo mkfs.vfat vfat.img
#copy zImage dtb rtf to vfat image.
# chameleon96.rbf
# extlinux
# image-version-info
# socfpga_cyclone5_chameleon96.dtb
# socfpga.dtb
# soc_system.rbf
# u-boot.scr
# zImage
sudo mcopy -i vfat.img  -s ./kernel/zImage ::/zImage
sudo mcopy -i vfat.img  -s ./kernel/chameleon96.rbf ::/chameleon96.rbf
sudo mcopy -i vfat.img  -s ./kernel/extlinux ::/
sudo mcopy -i vfat.img  -s ./kernel/image-version-info ::/image-version-info
sudo mcopy -i vfat.img  -s ./kernel/socfpga_cyclone5_chameleon96.dtb ::/socfpga_cyclone5_chameleon96.dtb
sudo mcopy -i vfat.img  -s ./kernel/u-boot.scr ::/u-boot.scr

#Generate root filesystem.
sudo dd if=/dev/zero of=rootfs.img bs=1 count=0 seek=4G


#format to ext3
sudo mkfs.ext3 rootfs.img

#mount to /mnt
#sudo losetup -d /dev/loop1
sudo losetup /dev/loop1 rootfs.img
sudo mount /dev/loop1 /mnt
sudo cp -a rootfs/* /mnt
sudo umount /mnt
sudo losetup -d /dev/loop1

sudo dd if=vfat.img    of=sdimage.img bs=1M count=100  seek=3    conv=notrunc
sudo dd if=rootfs.img  of=sdimage.img bs=1M count=4096 seek=103  conv=notrunc
