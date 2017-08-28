#!/bin/bash
#1.export toolchain
export ARCH=arm
export CROSS_COMPILE=`pwd`/host_tools/gcc-linaro-arm-linux-gnueabihf-4.8-2014.04_linux/bin/arm-linux-gnueabihf-

#2.make proloader
cd ./cv_soc_devkit_ghrd/software/spl_bsp
make clean && make
cd -
rm -f ./host_tools/sd_image/preloader-mkpimage.bin
cp ./cv_soc_devkit_ghrd/software/spl_bsp/preloader-mkpimage.bin ./host_tools/sd_image/bootloader

#3. make u-boot
cd u-boot.git
make clean
make socfpga_chameleon96_defconfig
make
cd -
rm -f ./host_tools/sd_image/u-boot-socfpga_cyclone5.img
cp ./u-boot.git/u-boot.img  ./host_tools/sd_image/bootloader

#4. make kernel
cd linux-socfpga.git
make clean
make atca-g400_defconfig
make zImage -j4
make dtbs
cd -

#cp zImage,u-boot.scr,soc_system.rbf,socfpga.dtb
rm -f ./host_tools/sd_image/zImage
rm -f ./host_tools/sd_image/socfpga.dtb
cp linux-socfpga.git/arch/arm/boot/zImage ./host_tools/sd_image/kernel/
cp linux-socfpga.git/arch/arm/boot/dts/socfpga_cyclone5_pcie.dtb ./host_tools/sd_image/kernel/
cd ./host_tools/sd_image

source makeimage.sh
