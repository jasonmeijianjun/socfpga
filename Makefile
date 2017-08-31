#!/bin/bash
#1.export toolchain
export CORECOUNT=$(shell cat /proc/cpuinfo| grep "physical id"| sort| uniq| wc -l)
export ARCH=arm
export CROSS_COMPILE=${PWD}/host_tools/gcc-linaro-arm-linux-gnueabihf-4.8-2014.04_linux/bin/arm-linux-gnueabihf-
export WORKSPACE=${PWD}

#2.make proloader
preloader:
	make -C cv_soc_devkit_ghrd/software/spl_bsp
	rm -f ./host_tools/sd_image/preloader-mkpimage.bin
	cp ./cv_soc_devkit_ghrd/software/spl_bsp/preloader-mkpimage.bin ./host_tools/sd_image/bootloader

#3. make u-boot
uboot:
	make socfpga_chameleon96_defconfig -C u-boot.git
	make -C u-boot.git -j$(CORECOUNT)
	rm -f ./host_tools/sd_image/u-boot-socfpga_cyclone5.img
	cp ./u-boot.git/u-boot.img  ./host_tools/sd_image/bootloader

#4. make kernel
kernel:
	make atca-g400_defconfig -C linux-socfpga.git
	make zImage -j4 -C linux-socfpga.git -j$(CORECOUNT)
	make dtbs -C linux-socfpga.git

#5.make flash tools. atca has 2 seperate flash controlled by fpga
tools:
	make -C flashtools

bcmsdk: kernel
	make -C sdk-all-6.5.7/systems/linux/user/cyconevsoc-4_1 -j$(CORECOUNT)
#6.cp zImage,u-boot.scr,soc_system.rbf,socfpga.dtb

sd_image:preloader uboot kernel flashtools bcmsdk
	cp -rf linux-socfpga.git/arch/arm/boot/zImage ./host_tools/sd_image/kernel/
	cp -rf linux-socfpga.git/arch/arm/boot/dts/socfpga_cyclone5_pcie.dtb  ./host_tools/sd_image/kernel/socfpga_cyclone5_chameleon96.dtb
	cp -f flashtools/flash_read host_tools/sd_image/rootfs/usr/bin/
	cp -f flashtools/flash_write host_tools/sd_image/rootfs/usr/bin/
	rm -rf host_tools/sd_image/rootfs/opt/bcmsdk
	mkdir -p host_tools/sd_image/rootfs/opt
	mkdir -p host_tools/sd_image/rootfs/opt/bcmsdk
	cp -rf sdk-all-6.5.7/rc/* host_tools/sd_image/rootfs/opt/bcmsdk
	cp -rf sdk-all-6.5.7/build/linux/user/cyconevsoc-4_1/* host_tools/sd_image/rootfs/opt/bcmsdk
	cd ./host_tools/sd_image;echo y | ./makeimage.sh
	
all:sd_image
.PHONY: all

clean:
	make clean -C cv_soc_devkit_ghrd/software/spl_bsp
	make clean -C u-boot.git
	make clean -C linux-socfpga.git
	make clean -C sdk-all-6.5.7/systems/linux/user/cyconevsoc-4_1 
	
help:
	@echo "make preloader"
	@echo "make uboot"
	@echo "make kernel"
	@echo "make tools"
	@echo "make bcmsdk"
	@echo "make sd_image"
	@echo "make all"
	@echo "make"
	@echo "make clean"
