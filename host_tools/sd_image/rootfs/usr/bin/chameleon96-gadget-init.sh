#!/bin/sh

#find the GPIO mapping for GPIO9 at 0xff708000 (Module Instance gpio0 from Cyclone V HPS Memory Map)
LINE=`ls -l /sys/class/gpio | grep gpiochip | grep ff708000`
NUM=`sed -e 's#.*gpiochip\(\)#\1#' <<< $LINE`
GPIO9=$((NUM+9))

#set GPIO9 as input so we can read the FORCE_3V3_USB_HUB switch position
echo $GPIO9 > /sys/class/gpio/export
echo "in" > /sys/class/gpio/gpio$GPIO9/direction

#if switch is set to OTG then load gadget driver

if [ `cat /sys/class/gpio/gpio$GPIO9/value` = 0 ]; then
    modprobe g_multi file=/usr/share/chameleon96-usb-gadget/fat_image.img

    sleep 5

    /sbin/ifconfig usb0 hw ether 00:01:02:03:c5:96
    /sbin/ifconfig usb0 192.168.96.96 netmask 255.255.255.0
    /usr/sbin/udhcpd -fS -I 192.168.96.96 /etc/udhcpd.conf
fi
