#!/bin/bash

# https://github.com/pyusb/pyusb
# https://medium.com/@darshankt/setting-up-the-udev-rules-for-connecting-multiple-external-devices-through-usb-in-linux-28c110cf9251
# To check USB device IDs, type lusb into console. For example, This DDC device is 2fe3:0100
# type sudo gedit /etc/udev/rules.d/50-myusb.rules
# paste this shit: SUBSYSTEMS=="usb", ATTRS{idVendor}=="2fe3", ATTRS{idProduct}=="0100", GROUP="dialout", MODE="0666"
#
# Note, 50-myusb.rules was created by us. Follow the guide on line 5.
#

# Add line to .bashrc (No sudo)
RVER=$(lsb_release -r)
VER='22.04'
CONTENT="export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6"

if [[ "$RVER" == *"$VER"* ]]; then
	if ! grep -s $CONTENT ~/.bashrc; then
		sudo -u $USER echo "export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libstdc++.so.6" >> ~/.bashrc 
	fi
fi

# sudo is needed for anything beyond this line
USBRULES1=/etc/udev/rules.d/50-myusb.rules
USBRULES2=/etc/udev/rules.d/51-myusb.rules

ENTRY1='SUBSYSTEMS=="usb", ATTRS{idVendor}=="2fe3", ATTRS{idProduct}=="0100", GROUP="dialout", MODE="0666"'
ENTRY2='SUBSYSTEMS=="usb", ATTRS{idVendor}=="2fe3", ATTRS{idProduct}=="0102", GROUP="dialout", MODE="0666"'

if grep -sq $ENTRY1 "$USBRULES1"
	then
		echo "permissions for PID = 0100 already enabled. Not appending anything to permissions file."
	else
		echo "$ENTRY1" >> $USBRULES1
		echo "Permissions for PID = 0100 not yet enabled. Appending permissions to permissions file now."
fi

if grep -sq $ENTRY2 "$USBRULES2"
	then
		echo "permissions for PID = 0102 already enabled. Not appending anything to permissions file."
	else
		echo "$ENTRY2" >> $USBRULES2 
		echo "Permissions for PID = 0102 not yet enabled. Appending permissions to permissions file now."
fi
