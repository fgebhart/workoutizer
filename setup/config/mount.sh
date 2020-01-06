logfile="/home/pi/logfile"

echo "------- new run ---------" >> $logfile
date >> $logfile
FILE=/home/pi/mounted

sleep 3

if ! [ -f "$FILE" ]; then
    echo "$FILE does not exist - mounting..." >> $logfile
    lsusb="$(lsusb | grep 091e)"
    set -- $lsusb
    bus=$2
    #echo "Bus: $bus" >> $logfile
    device=${4::-1}
    #echo "Device: $device" >> $logfile
    device_mount_path="/dev/bus/usb/${bus}/${device}"
    echo "mounting device: $device_mount_path" >> $logfile
    gio mount -d $device_mount_path >> $logfile
    touch $FILE
else
    echo "$FILE exists - skipping mount" >> $logfile
fi

echo " --- END --- " >> $logfile
