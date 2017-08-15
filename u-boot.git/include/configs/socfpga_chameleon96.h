/*
 * Copyright (C) 2017 Arrow Electronics
 *
 * SPDX-License-Identifier:	GPL-2.0+
 */
#ifndef __CONFIG_CHAMELEON96_H__
#define __CONFIG_CHAMELEON96_H__

#include <asm/arch/base_addr_ac5.h>

/* U-Boot Commands */
#define CONFIG_FAT_WRITE
#define CONFIG_HW_WATCHDOG

/* Memory configurations */
#define PHYS_SDRAM_1_SIZE		0x20000000	/* 500MiB */

/* Booting Linux */
#define CONFIG_BOOTFILE		"zImage"
#define CONFIG_BOOTARGS		"console=ttyS0," __stringify(CONFIG_BAUDRATE)
#define CONFIG_LOADADDR		0x01000000
#define CONFIG_SYS_LOAD_ADDR	CONFIG_LOADADDR

/* Ethernet on SoC (EMAC) */
#if defined(CONFIG_CMD_NET)
#define CONFIG_PHY_MICREL
#define CONFIG_PHY_MICREL_KSZ9031
#endif

#define CONFIG_ENV_IS_IN_MMC

#ifndef CONFIG_SPL_BUILD
#define CONFIG_EXTRA_ENV_SETTINGS \
	"verify=n\0" \
	"bootimage=" CONFIG_BOOTFILE "\0" \
	"fdt_addr=100\0" \
	"fdtfile=" CONFIG_DEFAULT_FDT_FILE "\0" \
	"bootm_size=0xa000000\0" \
	"kernel_addr_r="__stringify(CONFIG_SYS_LOAD_ADDR)"\0" \
	"fdt_addr_r=0x02000000\0" \
	"scriptaddr=0x02100000\0" \
	"pxefile_addr_r=0x02200000\0" \
	"ramdisk_addr_r=0x02300000\0" \
	\
	"fpga_cfg="							\
		"env exists fpga_files || setenv fpga_files "		\
			"${board}.rbf; "				\
		"for target in ${boot_targets}; do "			\
			"run fpga_cfg_${target}; "			\
		"done\0"						\
	\
	"fpga_cfg_mmc0="						\
		"setenv devnum 0; "					\
		"setenv devtype mmc; "					\
		"run scan_dev_for_boot_part_fpga\0"			\
	\
	"scan_dev_for_boot_part_fpga="					\
		"part list ${devtype} ${devnum} -bootable devplist; "	\
		"env exists devplist || setenv devplist 1; "		\
		"for distro_bootpart in ${devplist}; do "		\
			"if fstype ${devtype} "				\
					"${devnum}:${distro_bootpart} "	\
					"bootfstype; then "		\
				"run scan_dev_for_boot_fpga; "		\
			"fi; "						\
		"done\0"						\
	\
	"scan_dev_for_boot_fpga="					\
		"echo Scanning ${devtype} "				\
			"${devnum}:${distro_bootpart}...; " 		\
		"for prefix in ${boot_prefixes}; do "			\
			"run scan_dev_for_fpga; "			\
		"done\0"						\
	\
	"scan_dev_for_fpga="						\
		"for file in ${fpga_files}; do "			\
			"if test -e ${devtype} "			\
					"${devnum}:${distro_bootpart} "	\
					"${prefix}${file}; then "	\
				"echo Found FPGA Configuration "	\
					"${prefix}${file}; "		\
				"load ${devtype} "			\
					"${devnum}:${distro_bootpart} " \
					"${kernel_addr_r} "		\
					"${prefix}${file}; "		\
				"fpga load 0 ${kernel_addr_r} "		\
					"${filesize}; "			\
				"bridge enable; "			\
			"fi; "						\
		"done\0"						\
	\
	"usb_reset="							\
		"echo Resetting USB HUB...; "				\
		"gpio clear porta0; "					\
		"sleep 1; "						\
		"gpio set porta0\0"					\
	\
	"hdmi_init="							\
                "echo Initializing HDMI Transmitter for 1080p...; "	\
		"i2c dev 2; "						\
		"i2c mw 37 FF.1 02 1; "					\
                "i2c mw 73 FF.1 00 1; "					\
                "i2c mw 73 A0.1 06 1; "					\
                "i2c mw 73 CB.1 00 1; "					\
                "i2c mw 73 F0.1 00 1; "					\
                "i2c mw 73 18.1 FF 1; "					\
                "i2c mw 73 19.1 FF 1; "					\
                "i2c mw 73 1A.1 FF 1; "					\
                "i2c mw 73 20.1 45 1; "					\
                "i2c mw 73 21.1 23 1; "					\
                "i2c mw 73 22.1 01 1; "					\
                "i2c mw 73 23.1 20 1\0"					\
	\
	BOOTENV

#endif

#define CONFIG_BOOTCOMMAND "run usb_reset; run fpga_cfg; run hdmi_init; run distro_bootcmd"

/* The rest of the configuration is shared */
#include <configs/socfpga_common.h>

#endif	/* __CONFIG_CHAMELEON96_H__ */
