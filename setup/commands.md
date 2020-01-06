udev infos: https://wiki.archlinux.org/index.php/Udev

display usb devices `lsusb`  
get attributes of usb device `udevadm info --attribute-walk --name=/dev/bus/usb/001/010`  
monitor changes when plugging devices `udevadm monitor --environment --udev`  

 