udev infos: https://wiki.archlinux.org/index.php/Udev

display usb devices `lsusb`
show attaching of new devices `dmesg`  
get attributes of usb device `udevadm info --attribute-walk --name=/dev/bus/usb/001/010`  
monitor changes when plugging devices `udevadm monitor --environment --udev`  

mount device via gio `gio mount -d /dev/bus/usb/001/004`  
unmount device `gio mount -u /run/user/1000/gvfs/mtp:host=091e_4b48_0000c4fa0516`

## my device
(various models)
idVendor=091e
idProduct=0003
bcdDevice= 0.01

OR: ?
idVendor=091e
idProduct=4b48
bcdDevice= 0.0

ATTRS{serial}=="0000c4fa0516"

get properties of udev device `udevadm info --name=/dev/bus/usb/$BUS_NUMBER/$DEV_NUMBER --query=property`
show info on partitions `cat /proc/partitions`
get info on mount process `cat /proc/11/mountinfo`


## Ubuntu OS
install 
```shell script
sudo apt install gvfs gvfs-fuse gvfs-bin gvfs-backends ifuse
```
check dev and bus
```shell script
lsusb
```
mount
```shell script
gio mount -d /dev/bus/usb/001/004
```
access
```shell script
ls /run/user/1000/gvfs/
```