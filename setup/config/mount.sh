logfile="/home/pi/logfile"

date >> $logfile

sleep 3
lsusb="$(lsusb | grep 091e)"
set -- $lsusb
bus=$2
echo "Bus: $bus" >> $logfile
device=${4::-1}
echo "Device: $device" >> $logfile
device_mount_path="/dev/bus/usb/${bus}/${device}"
echo "mounting device: $device_mount_path" >> $logfile
gio mount -d $device_mount_path >> $logfile