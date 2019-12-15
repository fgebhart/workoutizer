logfile="/home/pi/logfile"

lsusb="$(lsusb | grep 091e:4b48)"
set -- $lsusb
bus=$2
echo "Bus: $bus" >> $logfile
device=${4::-1}
echo "Device: $device" >> $logfile
device_mount_path="/dev/bus/usb/${bus}/${device}"
echo "mounting device: $device_mount_path" >> $logfile
sleep 3
gio mount -d $device_mount_path
