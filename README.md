# socfpga
ATCA board bsp

Preloader and U-Boot Customization - v13.1
Overview
This page introduces the reader to the Preloader and U-Boot source code and how to customize them for a new board. An overview of HPS boot flow and Preloader generation flow are also included.
HPS Boot Flow
The typical HPS boot flow includes the following stages:
  1. BootROM
  2. Preloader
  3. U-Boot
  4. Linux

The BootROM and the Preloader stages are needed for all the applications in which the Cyclone V or Arria V SoCs are used. They are shown in blue in the above figure.
The U-Boot and Linux are used by the GSRD, but they are not required for all applications.
The next stage boot image loaded and executed by the Preloader does not necessarily needs to be an U-boot image. For example the Preloader can :
  ● Load bare-metal applications directly,
  ● Load RTOS-es or OS-es directly,
  ● Load another bootloader that can subsequently load the applications.
The only requirement is that the next stage image has the proper mkimage header, that is required for U-boot to recognize the image.
The following table presents a short description of the different boot stages:
Stage Description
BootROM Performs minimal configuration and loads Preloader into 64KB OCRAM
Preloader Configures clocking, IOCSR, pinmuxing, DDRAM and loads U-boot into DDRAM
U-boot Configures FPGA, loads Linux kernel
Linux Runs the end application
For more information about SoC FPGA booting please refer to the following documents:
  ● Cyclone V Booting and Configuration
  ● Arria V Booting and Configuration
  ● Golden System Reference Design Boot Flow
Preloader Generation Flow
The Preloader is based on the SPL (Secondary Program Loader), which is a component of U-Boot, the open source bootloader.
The following figure presents an overview of how the Preloader is generated, by using the tools provided with SoC EDS.

See Generating and Compiling the Preloader for detailed steps on how to generate and compile the Preloader.
Note that the make command above first extracts the full U-Boot source code, then it copies the generated Preloader configuration files to the U-Boot source code, and finally compiles the Preloader.
For applications where only the Preloader is needed, the above is sufficient. But for applications where U-Boot is needed too, the command make uboot can be used to also compile the U-Boot image.

Note that the main repository for the U-Boot source code is the git tree at http://rocketboards.org/gitweb/. U-Boot is also included with the Yocto Source Package. The U-Boot source code generated by SoC EDS tools is provided for reference only, but it can be useful in understanding the interactions between Preloader and U-Boot, especially when tweaking parameters like clocking.
For the remainder of this document we will use the U-Boot source code created by the Preloader Generator.
Preloader & U-Boot Source Code
The Preloader is based on the SPL (Secondary Program Loader), which is a component of U-Boot, the open source bootloader.
Common Source Code
The Preloader and U-Boot share most of the source code. This allows the Preloader access to the extensive set of available U-Boot drivers. U-Boot supports a lot of drivers mainly because it leverages the existing Linux kernel drivers.
While compiling the Preloader, the CONFIG_SPL_BUILD variable is automatically defined, both in the make environment and in the C compilation flags. Therefore the source code and the makefiles can discern whether they are compiled for U-Boot or the Preloader and perform the necessary customizations.
For example the file board/altera/socfpga/Makefilehas the following statement that adds the pinmuxing and iocsr configuration files to the Preloader build only:
COBJS-$(CONFIG_SPL_BUILD) += pinmux_config_cyclone5.o iocsr_config_cyclone5.o
Another example is the file arch/arm/cpu/armv7/socfpga/s_init.c:
#ifdef CONFIG_SPL_BUILD
   /* re-setup watchdog */
   DEBUG_MEMORY
   if (!(is_wdt_in_reset())) {
      /*
       * only disabled if wdt not in reset state
       * disable the watchdog prior PLL reconfiguration
       */
      DEBUG_MEMORY
      watchdog_disable();
   }
...
Top Level Files & Folders
The following table presents an overview of the U-Boot source code, at the top level.
File/Folder Description
api/ Architecture independent API for external applications
arch/ Architecture specific folder
board/ Board related files
common/ Different common files, such as SPL and U-Boot commands
disk/ Disk related files
doc/ Documentation folder, in text format
drivers/ Drivers folder
dts/ Device Tree related files
examples/ Example source code
fs/ Filesystem source code
include/ Include files
lib/ Various libraries, such as compression, random number generation etc.
nand_spl/ Files use when booting from NAND
net/ Network stack source code
post/ Power-on Self Test files
spl/ Preloader Files
test/ Test code
tools/ Host tools folder. The most important is mkimage
boards.cfg Describes all the supported platforms in a tabular text format
MAINTAINERS List of maintainers for all the supported platforms, including names and email addresses
MAKEALL Utility for building
Makefile Makefile
mkconfig Utility for configuring
README Readme file
rules.mk Makefile include file
Relevant Folders
The following table highlights a few of the most relevant folders, related to the Altera Cyclone V and Arria V SoCs.
Folder Description
arch/arm/cpu/armv7/socfpga/ Architecture specific files, like clock manager, interrupt controller etc
arch/arm/include/asm/arch-socfpga/ Include files for the architecture specific source code
board/altera/socfpga/ Board specific files - some generated by the Preloader Generator
board/altera/socfpga/sdram Board specific DDRAM files - some generated by the Preloader Generator
Board Files
The following table presents the Altera board specific files. The Generated column designates which files are generated by the Preloader Generator.
Folder File Generated Description
board/altera/socfpga/ build.h yes Preloader Build Parameters
 iocsr_config_arria5.c yes I/O Pin Configuration Blob (Arria V)
 iocsr_config_arria5.h yes 
 iocsr_config_cyclone5.c yes I/O Pin Configuration Blob (Cyclone V)
 iocsr_config_cyclone5.h yes 
 pinmux_config.h yes Pin Muxing Parameters Header
 pinmux_config_arria5.c yes Pin Muxing Parameters (Arria V)
 pinmux_config_cyclone5.c yes Pin Muxing Parameters (Cyclone V)
 pll_config.h yes Clocking Configuration
 reset_config.h yes Reset Configuration
 Makefile   Makefile
 socfpga_common.c   Common Functions
 socfpga_arria5.c   Displays Board Name (Arria V)
 socfpga_cyclone5.c   Displays Board Name (Cyclone V)
 timestamp_config.h   Timestamp File
board/altera/socfpga/sdram/ sdram_config.h yes SDRAM Configuration Parameters
 Makefile   SDRAM Configuration Makefile
 alt_types.h   SDRAM Configuration Source Code
 sdram.h   
 sdram_io.h   
 sequencer.c   
 sequencer.h   
 sequencer_auto.h   
 sequencer_auto_ac_init.c   
 sequencer_auto_inst_init.c   
 sequencer_defines.h   
 system.h   
 tclrpt.c   
 tclrpt.h   
Various Files
The following table presents a few more files that are relevant for the Altera SoCs:
File Description
doc/README.SOCFPGA SoC specific readme file
doc/README.SPL SPL specific readme file
include/configs/socfpga_arria5.h Arria V configuration file
include/configs/socfpga_cyclone5.h Cyclone V configuration file
include/configs/socfpga_common.h Common configuration file for Cyclone V and Arria V
boards.cfg File defining all the supported targets
Target Parameters
The parameters for each supported U-Boot board, the configuration parameters are stored in a C include file named include/configs/<board_name>.h. These parameters are shared between Preloader and U-Boot.
For the Cyclone V and Arria V SoCs, the following files are used:
  ● include/configs/socfpga_arria5.h - Arria V parameters
  ● include/configs/socfpga_cyclone5.h - Cyclone V parameters
  ● include/configs/socfpga_common.h - Shared parameters
The following table details some of the board parameters:
Parameter Description
CONFIG_SYS_PROMPT U-Boot command prompt string
CONFIG_EMAC_BASE Base address of EMAC peripheral control registers
CONFIG_EPHY_PHY_ADDR Address of EMAC PHY
CONFIG_PHY_INTERFACE_MODE EMAC mode of operation
CONFIG_BOOTDELAY U-Boot boot delay
CONFIG_BAUDRATE Baudrate to be used for serial commnication
CONFIG_EXTRA_ENV_SETTINGS Default environment variables for U-Boot
CONFIG_MMC SD Card related parameters
CONFIG_SDMMC_BASE 
CONFIG_SDMMC_HOST_HS 
CONFIG_GENERIC_MMC 
CONFIG_DWMMC 
CONFIG_ALTERA_DWMMC 
CONFIG_DWMMC_FIFO_DEPTH 
CONFIG_SYS_MMC_MAX_BLK_COUNT 
CONFIG_DWMMC_BUS_WIDTH 
CONFIG_DWMMC_BUS_HZ 
CONFIG_DWMMC_BUS_WIDTH 
CONFIG_DWMMC_BUS_HZ 
CONFIG_CADENCE_QSPI QSPI flash related parameters
CONFIG_CQSPI_BASE 
CONFIG_CQSPI_AHB_BASE 
CONFIG_SPI_FLASH 
CONFIG_SPI_FLASH_STMICRO 
CONFIG_SF_DEFAULT_SPEED 
CONFIG_SF_DEFAULT_MODE 
CONFIG_SPI_FLASH_QUAD 
CONFIG_CQSPI_REF_CLK 
CONFIG_CQSPI_PAGE_SIZE 
CONFIG_CQSPI_BLOCK_SIZE 
CONFIG_CQSPI_TSHSL_NS 
CONFIG_CQSPI_TSD2D_NS 
CONFIG_CQSPI_TCHSH_NS 
CONFIG_CQSPI_TSLCH_NS 
CONFIG_CQSPI_DECODER 
CONFIG_CQSPI_4BYTE_ADDR 
CONFIG_DESIGNWARE_ETH EMAC related parameters
CONFIG_EMAC0_BASE 
CONFIG_EMAC1_BASE 
CONFIG_NET_MULTI 
CONFIG_DW_ALTDESCRIPTOR 
CONFIG_DW_SEARCH_PHY 
CONFIG_MII 
CONFIG_PHY_GIGE 
CONFIG_DW_AUTONEG 
CONFIG_AUTONEG_TIMEOUT 
CONFIG_PHYLIB 
CONFIG_PHY_MICREL 
CONFIG_PHY_MICREL_KSZ9021 
CONFIG_EPHY0_PHY_ADDR 
CONFIG_EPHY1_PHY_ADDR 
CONFIG_KSZ9021_CLK_SKEW_ENV 
CONFIG_KSZ9021_CLK_SKEW_VAL 
CONFIG_KSZ9021_DATA_SKEW_ENV 
CONFIG_KSZ9021_DATA_SKEW_VAL 
CONFIG_SYS_SDRAM_BASE Physical SDRAM base address
PHYS_SDRAM_1_SIZE Physical SDRAM size
The U-Boot command line interface allows execution of different commands. These commands can also be executed from U-Boot scripts. The commands' source code is located in the folder common and are named cmd_<name>
The target configuration file can enable various commands by defining the macro CONFIG_CMD_<NAME>. Here are some of the commands enabled by the socfpga_common.h:
Macro Description
CONFIG_CMD_FAT Enable FAT filesystem support
CONFIG_CMD_EXT2 Enable EXT2 filesystem support
CONFIG_CMD_MMC Enable SD/MMC support
CONFIG_CMD_USB Enable USB support
CONFIG_CMD_DHCP Enable DHCP support
CONFIG_CMD_MII Enable MII commands
CONFIG_CMD_NET Enable networking commands
CONFIG_CMD_PING Enable ping command
CONFIG_CMD_MTDPARTS Enable MTD partition support
CONFIG_CMD_SF Enable serial flash support
CONFIG_CMD_FPGA Enable FPGA commands
Preloader Parameters
The following sections will present some of the settings that are included in the files generated by the Preloader Generator.
Preloader Build Parameters
The following Preloader parameters are passed in the generated file build.h. They are usually edited in the Preloader Generator GUI but can also be edited manually after they are generated.
Parameter Description
CONFIG_PRELOADER_BOOT_FROM_QSPI Preloader boot source, mutually exclusive.Also used by U-Boot to decide where to store the environment variables
CONFIG_PRELOADER_BOOT_FROM_SDMMC 
CONFIG_PRELOADER_BOOT_FROM_RAM 
CONFIG_PRELOADER_QSPI_NEXT_BOOT_IMAGE Location of boot image on QSPI Flash
CONFIG_PRELOADER_SDMMC_NEXT_BOOT_IMAGE Location of boot image on SD card
CONFIG_PRELOADER_WATCHDOG_ENABLE Enable watchdog operation
CONFIG_PRELOADER_DEBUG_MEMORY_WRITE Write debug info in memory
CONFIG_PRELOADER_SEMIHOSTING Use semihosting for printing messages - requies debugger
CONFIG_PRELOADER_CHECKSUM_NEXT_IMAGE Use checksum on the next image
CONFIG_PRELOADER_SERIAL_SUPPORT Enable serial port for debug messages
CONFIG_PRELOADER_HARDWARE_DIAGNOSTIC Enable hardware diagnostic support
CONFIG_PRELOADER_EXE_ON_FPGA Run Preloader from FPGA memory
CONFIG_FPGA_MAX_SIZE FPGA memory parameters, used when running Preloader from FPGA memory
CONFIG_FPGA_DATA_BASE 
CONFIG_FPGA_DATA_MAX_SIZE 
CONFIG_PRELOADER_STATE_REG_ENABLE Pass information to BootROM that Preloader executed OK
CONFIG_PRELOADER_BOOTROM_HANDSHAKE_CFGIO Pass information to BootROM that Preloader completed configuration of IOCSR and pin muxing
CONFIG_PRELOADER_WARMRST_SKIP_CFGIO Preloader to skip IOCSR configuration on warm resets
CONFIG_PRELOADER_SKIP_SDRAM Skip SDRAM initialization and calibration
Preloader Reset Parameters
The following parameters are passed in the file reset_config.h, which is generated by the Preloader Generator. The Editable column identifies the parameters that can be edited in the Preloader Generator GUI. If a parameter is not marked as editable, it means it is passed from the Qsys design and should not be manually edited. Each parameter instructs the Preloader whether to keep a module in reset or not.
Parameter Editable
CONFIG_HPS_RESET_ASSERT_EMAC0  
CONFIG_HPS_RESET_ASSERT_EMAC1  
CONFIG_HPS_RESET_ASSERT_USB0  
CONFIG_HPS_RESET_ASSERT_USB1  
CONFIG_HPS_RESET_ASSERT_NAND  
CONFIG_HPS_RESET_ASSERT_SDMMC  
CONFIG_HPS_RESET_ASSERT_QSPI  
CONFIG_HPS_RESET_ASSERT_UART0  
CONFIG_HPS_RESET_ASSERT_UART1  
CONFIG_HPS_RESET_ASSERT_I2C0  
CONFIG_HPS_RESET_ASSERT_I2C1  
CONFIG_HPS_RESET_ASSERT_I2C2  
CONFIG_HPS_RESET_ASSERT_I2C3  
CONFIG_HPS_RESET_ASSERT_SPIM0  
CONFIG_HPS_RESET_ASSERT_SPIM1  
CONFIG_HPS_RESET_ASSERT_SPIS0  
CONFIG_HPS_RESET_ASSERT_SPIS1  
CONFIG_HPS_RESET_ASSERT_CAN0  
CONFIG_HPS_RESET_ASSERT_CAN1  
CONFIG_HPS_RESET_ASSERT_L4WD1 yes
CONFIG_HPS_RESET_ASSERT_OSC1TIMER1 yes
CONFIG_HPS_RESET_ASSERT_SPTIMER0 yes
CONFIG_HPS_RESET_ASSERT_SPTIMER1 yes
CONFIG_HPS_RESET_ASSERT_GPIO0 yes
CONFIG_HPS_RESET_ASSERT_GPIO1 yes
CONFIG_HPS_RESET_ASSERT_GPIO2 yes
CONFIG_HPS_RESET_ASSERT_DMA yes
CONFIG_HPS_RESET_ASSERT_SDR yes
CONFIG_HPS_RESET_ASSERT_FPGA_DMA0 yes
CONFIG_HPS_RESET_ASSERT_FPGA_DMA1 yes
CONFIG_HPS_RESET_ASSERT_FPGA_DMA2 yes
CONFIG_HPS_RESET_ASSERT_FPGA_DMA3 yes
CONFIG_HPS_RESET_ASSERT_FPGA_DMA4 yes
CONFIG_HPS_RESET_ASSERT_FPGA_DMA5 yes
CONFIG_HPS_RESET_ASSERT_FPGA_DMA6 yes
CONFIG_HPS_RESET_ASSERT_FPGA_DMA7 yes
CONFIG_HPS_RESET_ASSERT_HPS2FPGA  
CONFIG_HPS_RESET_ASSERT_LWHPS2FPGA  
CONFIG_HPS_RESET_ASSERT_FPGA2HPS  
CONFIG_HPS_RESET_WARMRST_HANDSHAKE_FPGA yes
CONFIG_HPS_RESET_WARMRST_HANDSHAKE_ETR yes
CONFIG_HPS_RESET_WARMRST_HANDSHAKE_SDRAM yes
Preloader Clocking Parameters
The clocking parameters are created by the Preloader Generator and stored in the file pll_config.h. See Preloader Clocking Customizationfor more details about the file and a calculator to facilitate editing it.
Preloader IOCSR & Pinmuxing Parameters
The IOCSR parameters define the HPS pin behavior: input or output, drive strength, logic levels etc. The file is called iocsr_config_<cyclone/arria>5.h and .c and is generated automatically by the Preloader Generator based on the handoff information from Qsys. These files cannot be manually edited, since the IOCSR interface is not publicly documented.
The pin muxing parameters are stored in the file pinmux_config.h and are generated by the Preloader Generator based on Qsys settings. They should not be generally edited by hand.
Preloader SDRAM Parameters
The SDRAM parameters are stored in the file sdram_config.h that is generated by the Preloader Generator based on the handoff information from Qsys. Do not edit this file manually.
Compiling the Preloader & U-Boot
This section presents some details about compilation of Preloader and U-Boot.
Compiling the Preloader
The Preloader is compiled from an embedded command shell by using the following commands:
$ ~/altera/13.1/embedded/embedded_command_shell.sh
$ cd <hardware_folder>/software/spl_bsp
$ make
See Generating and Compiling the Preloader for more details about compiling the Preloader.
Compiling U-Boot
U-Boot can be compiled either standalone, or from the source code generated by the Preloader Generator. When compiled in standalone mode, the following commands can be used:
$ export CROSS_COMPILE=~<gnu_tools_path_and_prefix>
$ make mrproper
$ make socfpga_cyclone5_config or socfpga_arria5_config
$ make 
See Using Git Trees for more details about compiling U-Boot.
When using the source code generated by the SoC EDS Preloader Generator, the following commands can be used to compile U-Boot:
$ ~/altera/13.1/embedded/embedded_command_shell.sh
$ cd <hardware_folder>/software/spl_bsp
$ make uboot
Adding a New Board to Preloader & U-Boot
This section demonstrates how to add a new board to the Preloader and U-Boot source code, by cloning the socfpga_cyclone5 board. This is needed in case the user does not want to directly modify the Altera files, and it is mandatory if the user wants to eventually upmerge the U-Boot changes.
The following prerequisites are needed:
  ● Host PC running Windows or Linux (Linux is preferred)
  ● SoC EDS - can be downloaded from https://www.altera.com/download/software/soc-eds
  ● Hardware Design - can be based on the GHRD. This section assumes the hardware design is stored in a folder named ~/acme_hwdesign
For the purpose of this example, the new board will be called acme_dynamite, provided by the vendor acme and be based on the SoC socfpga.
1. Create the hardware design and compile it in Quartus, to obtain the handoff information folder. You can use the GHRD (Golden Hardware Reference Design) as a starting point. For more information on how to compile the hardware design see Compiling the GHRD.
2. Generate the Preloader based on the handoff information folder from Quartus. See Generating and Compiling the Preloader for more information on how to generate the Preloader.
3. Compile the Preloader once, to make sure all the source code is available. This is needed because the first time the Preloader is compiled, it will extract the Preloader and U-Boot source code from an archive that is part of the SoC EDS. Then clean the code, to remove intermediate files.
$ ~/altera/13.1/embedded/embedded_command_shell.sh
$ cd ~/acme_hwdesign/software/spl_bsp
$ make
$ make clean
4. Change the current folder to be the generated Preloader and U-boot source code:
$ cd ~/acme_hwdesign/software/spl_bsp/uboot-socfpga
5. Make a copy of the board folder board/altera/socfpgato the folder board/acme/dynamite
$ mkdir -p board/acme/dynamite
$ cp -r board/altera/socfpga/* board/acme/dynamite
6. Make a copy of the configuration files socfpga_cyclone5.h and socfpga_common.h to match the acme_dynamitename:
$ cp include/configs/socfpga_cyclone5.h include/configs/acme_dynamite.h
$ cp include/configs/socfpga_common.h include/configs/acme_dynamite_common.h
7. Edit the new configuration file acme_dynamite.h to:
  ● add the CONFIG_ACME_DYNAMITE in addition to the CONFIG_SOCFPGA_CYCLONE5:
  ● replace reference to socfpga_common.h to acme_dynamite_common.h
  ● replace path board/altera/socfpga with path board/acme/dynamite
  ● change the U-Boot prompt from SOCFPGA_CYCLONE5 to ACME_DYNAMITE
$ sed -i 's/#define CONFIG_SOCFPGA_CYCLONE5/&\n#define CONFIG_ACME_DYNAMITE/g' include/configs/acme_dynamite.h
$ sed -i 's/socfpga_common.h/acme_dynamite_common.h/g' include/configs/acme_dynamite.h
$ sed -i 's/board\/altera\/socfpga/board\/acme\/dynamite/g' include/configs/acme_dynamite.h
$ sed -i 's/SOCFPGA_CYCLONE5 #/ACME_DYNAMITE #/g' include/configs/acme_dynamite.h
8. Edit the file acme_dynamite_common.h to replace the path board/altera/socfpgawith path board/acme/dynamite
$ sed -i 's/board\/altera\/socfpga/board\/acme\/dynamite/g' include/configs/acme_dynamite_common.h
9. Edit the file that displays the board name to use the new name:
$ sed -i 's/Altera SOCFPGA Cyclone V Board/Acme Dynamite Board/g' board/acme/dynamite/socfpga_cyclone5.c
10. Edit the file boards.cfg to add the new acme_dynamite board, as shown in the table below:
Target ARCH CPU Board Name Vendor SoC options
acme_dynamite arm armv7 dynamite acme socfpga  
socfpga_cyclone5 arm armv7 socfpga altera socfpga  
socfpga_arria5 arm armv7 socfpga altera socfpga  
$ sed -i 's/socfpga_cyclone5/acme_dynamite                arm         armv7       dynamite            acme           socfpga\n&/' boards.cfg
11. Update the Makefilecreated by the Preloader Generator to use the new target board:
$ cd ~/acme_hwdesign/software/spl_bsp/
$ sed -i 's/board\/altera\/socfpga/board\/acme\/dynamite/g' Makefile
$ sed -i 's/socfpga_$(DEVICE_FAMILY)_config/acme_dynamite_config/g' Makefile 
12. Build Preloader and U-boot for the new acme_dynamiteboard
$ ~/altera/13.1/embedded/embedded_command_shell.sh
$ cd ~/acme_hwdesign/software/spl_bsp
$ make 
$ make uboot
13. Create a bootable SD card or use the one provided with the GSRD, and replace the Preloader and U-boot images with the new ones. Fore more details, please refer to:
  ● Booting Linux Using Prebuilt SD Card Image
  ● Creating and Updating SD Card
14. Boot the board, pressing any key to stop at U-Boot console. The messages displayed on the console will look similar to the following listing. Highlighted in red are the board name for Preloader and U-Boot and also the U-Boot console prompt.
U-Boot SPL 2013.01.01 (Oct 21 2013 - 13:44:30)
BOARD : Acme Dynamite Board
SDRAM: Initializing MMR registers
SDRAM: Calibrating PHY
SEQ.C: Preparing to start memory calibration
SEQ.C: CALIBRATION PASSED
SDRAM: ECC Enabled
ALTERA DWMMC: 0

U-Boot 2013.01.01 (Oct 21 2013 - 13:44:44)
CPU   : Altera SOCFPGA Platform
BOARD : Acme Dynamite Board
DRAM:  1 GiB
MMC:   ALTERA DWMMC: 0
*** Warning - bad CRC, using default environment

In:    serial
Out:   serial
Err:   serial
Net:   mii0
Warning: failed to set MAC address

Hit any key to stop autoboot:  0
ACME_DYNAMITE #

Common Customization Recipes
This section presents a list of useful customizations recipes for Preloader and/or U-Boot.
Loading U-Boot/Next Image From FAT Partition
When booting from SD/MMC the Preloader loads the next image from the offset CONFIG_PRELOADER_SDMMC_NEXT_BOOT_IMAGE inside the custom partition with id=0xA2.
The Preloader also offers the option of loading the next image from a FAT partition on the SD card instead. Here are the required steps in order to achieve this:
1. Enable the FAT support in Preloader by editing the include/configs/socfpga_common.h
#define CONFIG_SPL_FAT_SUPPORT
2. Tell Preloader the U-Boot's filename to be loaded and partition which FAT located:
#define CONFIG_SYS_MMC_SD_FAT_BOOT_PARTITION 1
#define CONFIG_SPL_FAT_LOAD_PAYLOAD_NAME "u-boot.img"
3. Build the Preloader
4. Copy the image file in the selected FAT partition.
Changing SDRAM Memory Size
The SDRAM memory is used by the Preloader to load U-Boot (or another image) and execute it.Changing the SDRAM memory size is achieved by editing the parameter PHYS_SDRAM_1_SIZE in the file include/configs/socfpga_common.h.
The base address of the SDRAM memory can also be edited in the same file by changing the parameter CONFIG_SYS_SDRAM_BASE.
Disabling SDRAM Initialization & Calibration
The SDRAM initialization can be disabled from the Preloader Generator GUI or by editing the file build.h and setting the parameter CONFIG_PRELOADER_SKIP_SDRAM to 1.
This can be useful for example if the user wants the Preloader to use the FPGA SDRAM memory instead of HPS SDRAM memory. In order to achieve that the user needs to disable SDRAM initalization, and define the=PHYS_SDRAM_1_SIZE= and CONFIG_SYS_SDRAM_BASE parameters to point to the FPGA SDRAM memory.
Changing HPS Clocking
The Preloader Generator sets up the HPS clock tree using default hardcoded values. See Customizing HPS Clocks in Preloader for details on how to modify the clock values.
Using a Different SDRAM Memory
Edit the HPS component in Qsys to enter the proper memory parameters, compile the hardware design, generate and compile the Preloader. All the parameters will be updated automatically.
Disabling SDRAM ECC
The SDRAM ECC can be enabled in Qsys, by editing the HPS component. If the ECC is enabled in Qsys, then the Preloader will also enable it.
For systems where the ECC was enabled, it can be disabled in the Preloader by editing the file board/altera/socfpga_cyclone5/sdram/sdram_config.h and defining the following parameters to 0:
#define CONFIG_HPS_SDR_CTRLCFG_CTRLCFG_ECCEN         (0)
#define CONFIG_HPS_SDR_CTRLCFG_CTRLCFG_ECCCORREN      (0)
Note that you cannot enable ECC using the above macros, for a design that does not have the ECC enabled in Qsys. You can only disable ECC for a system that was compiled with ECC enabled.
Using a Different EMAC instance
The GSRD uses EMAC1. In order to change that, you need to updated the board configuration file (include/condfigs/socfpga_cyclone5.h or similar) to change the following
#define CONFIG_EMAC_BASE      CONFIG_EMAC1_BASE
#define CONFIG_EPHY_PHY_ADDR      CONFIG_EPHY1_PHY_ADDR
to
#define CONFIG_EMAC_BASE      CONFIG_EMAC0_BASE
#define CONFIG_EPHY_PHY_ADDR      CONFIG_EPHY0_PHY_ADDR
Adding a New Driver in U-Boot
The U-Boot has a lot of drivers that are used on its various supported platforms. It is relatively easy to enable one of the existing drivers for the target board.
This section will show how to add the DesignWare I2C driver to the newly created acme_dynamite board.
1. Edit the file include/configs/acme_dynamite.h to add the following definitions:
#define CONFIG_HARD_I2C
#define CONFIG_DW_I2C   
#define CONFIG_SYS_I2C_BASE    0xffc04000
#define CONFIG_SYS_I2C_SPEED   100000
#define CONFIG_SYS_I2C_SLAVE   0x02
#define CONFIG_CMD_I2C 

The following table presents a description of the above macros:
Macro Description
CONFIG_HARD_I2C Enable I2C hardware module driver
CONFIG_DW_I2C Enable DesignWare I2C module driver
CONFIG_SYS_I2C_BASE Base address for the DesignWare module
CONFIG_SYS_I2C_SPEED I2C speed
CONFIG_SYS_I2C_SLAVE Address of device when used as slave
CONFIG_CMD_I2C Enable I2C commands - can be used from command line or scripts
2. Create empty file arch/arm/include/asm/arch-socfpga/hardware.h. The DesignWare I2C driver requires inclusion of this file, but the contents of the file is not actually used for our platform.
$ touch arch/arm/include/asm/arch-socfpga/hardware.h
3. Compile U-Boot and put it on the boot medium (SD card or QSPI).
4. Boot Board. The log will display the I2C initialization and the I2C commands will be available at the U-Boot prompt and in the U-Boot scripts.
U-Boot 2013.01.01 (Nov 01 2013 - 16:39:46)
CPU   : Altera SOCFPGA Platform
BOARD : Acme Dynamite Board
I2C:   ready
DRAM:  1 GiB
MMC:   ALTERA DWMMC: 0
*** Warning - bad CRC, using default environment

In:    serial
Out:   serial
Err:   serial
Net:   mii0
Warning: failed to set MAC address

Hit any key to stop autoboot:  0
ACME_DYNAMITE #
Adding a New Driver in Preloader
The U-Boot has a lot of drivers that are used on its various supported platforms. It is very easy to enable one of the existing drivers for the target board, to be used for the Preloader.
This section will show how to add the DesignWare I2C driver to the newly created acme_dynamite board, for the Preloader.
1. Edit the file include/configs/acme_dynamite.h to add the following definitions:
#define CONFIG_HARD_I2C
#define CONFIG_DW_I2C   
#define CONFIG_SYS_I2C_BASE    0xffc04000
#define CONFIG_SYS_I2C_SPEED   100000
#define CONFIG_SYS_I2C_SLAVE   0x02
#define CONFIG_SPL_I2C_SUPPORT

The following table presents a description of the above macros:
Macro Description
CONFIG_HARD_I2C Enable I2C hardware module driver
CONFIG_DW_I2C Enable DesignWare I2C module driver
CONFIG_SYS_I2C_BASE Base address for the DesignWare module
CONFIG_SYS_I2C_SPEED I2C speed
CONFIG_SYS_I2C_SLAVE Address of device when used as slave
CONFIG_SPL_I2C_SUPPORT Enable SPL/Preloader support for I2C
2. Create empty file arch/arm/include/asm/arch-socfpga/hardware.h. The DesignWare I2C driver requires inclusion of this file, but the contents of the file is not actually used for our platform.
$ touch arch/arm/include/asm/arch-socfpga/hardware.h
3. Call the I2C initialization function at the end of the spl_board_init() function in the file arch\arm\cpu\armv7\socfpga\spl.c:
...
#include <i2c.h>
…
void spl_board_init(void)
{
…
#ifdef CONFIG_SPL_I2C_SUPPORT
   i2c_init(CONFIG_SYS_I2C_SPEED, CONFIG_SYS_I2C_SLAVE);
   puts("I2C : Initialized\n");
#endif
}
4. Compile Preloader and put it on the boot medium (SD card or QSPI).
5. Boot Board. The log will display the I2C initialization message.
U-Boot SPL 2013.01.01 (Nov 01 2013 - 16:53:52)
BOARD : Acme Dynamite Board
SDRAM: Initializing MMR registers
SDRAM: Calibrating PHY
SEQ.C: Preparing to start memory calibration
SEQ.C: CALIBRATION PASSED
SDRAM: ECC Enabled
I2C : Initialized
ALTERA DWMMC: 0
Detailed Preloader Execution Flow
This section presents a detailed Preloader execution flow, to enable the user to better understand and debug the Preloader.

Changing Linux command line arguments to isolate an HPS core via U-Boot
U-Boot can pass boot arguments to the Linux kernel to achieve different goals.
It is sometimes necessary to keep Linux from scheduling processes in a given CPU so that that CPU could be dedicated to a given application.
This is achieved by first telling Linux to isolate the CPU core we wish to dedicate to our application, and then having our application indicate that it wishes to run on the CPU that has been isolated.
To isolate the CPU in a multi core system, we change the boot arguments U-Boot passes to Linux and recompile U-Boot.
In the Altera Cyclone V board this is accomplished by modifying the file: include/configs/socfpga_common.h by changing the line:
#define CONFIG_BOOTARGS "console=ttyS0," __stringify(CONFIG_BAUDRATE)

to
#define CONFIG_BOOTARGS "isolcpus=1 console=ttyS0," __stringify(CONFIG_BAUDRATE)

In this example the second CPU of the processor is being isolated. (CPU numbering is zero based)
Now, just compile and install U-Boot into your board. When Linux boots, you could verify the command line arguments passed to it by typing:
cat /proc/cmdline

You can also run htop to view the CPU assigned to each running process. They should all say 1. (htop uses one based CPU numbering).
Note: If the command line arguments are not what's expected, try rebooting and defaulting the board's U-Boot environment by doing the following:
Interrupt the boot sequence and at the U-Boot command prompt enter the following two commands and reboot:
env default -a
saveenv

The second part of the process involves changing your application to run in the CPU core that has been isolated.
Somewhere in your application initialization code do this:
unsigned int cpu = 1 // zero based index of the CPU being targeted
cpu_set_t mask;
CPU_ZERO(&mask);
CPU_SET(cpu, &mask);
assert(sched_setaffinity(0, sizeof(mask), &mask) == 0);

Now run your application and run htop again. You should see that only your application is running on the second CPU.
