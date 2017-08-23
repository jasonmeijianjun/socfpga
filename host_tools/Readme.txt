#using make_sdimage.py to generate the sd card images.
$ sudo ~/make_sdimage.py  \
  -f \
  -P preloader-mkpimage.bin,u-boot-socfpga_cyclone5.img,num=3,format=raw,size=10M,type=A2  \
  -P rootfs/*,num=2,format=ext3,size=1500M  \
  -P zImage,u-boot.scr,soc_system.rbf,socfpga.dtb,num=1,format=vfat,size=500M  \
  -s 2G  \
  -n sd_card_image_cyclone5.bin
