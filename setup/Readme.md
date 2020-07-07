# Setup Workoutizer on a Raspberry Pi

Follow these instructions to install Workoutizer on a Raspberry Pi in your local network.

I assume you have your Raspberry Pi already set up and running. If not I recommend to follow
the official [Raspberry Pi Setup Guide](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up).
In order to follow the below instructions, you need a command line interface to your Pi.

Note: The below instructions have been tested on a Raspberry Pi 4 Model B running Raspbian 10 (Buster). I assume it will
also work on a variety of other Pis and OS combinations, but I recommend to use the latest versions of both.


### Preparation & Installation

Create virtual environment and activate it:
```shell script
virtualenv -p python3 venv && source venv/bin/activate 
```
Install workoutizer
```shell script
pip install workoutizer
```

### Configuring your Device

Figure out the `product_id` and `vendor_id` of your device by connecting it to your Raspberry Pi via USB and run 
```shell script
lsusb
```
Wait 1-2 minutes until the `(various models)` line next to your Garmin device disappears. You want to have a similar
output like: 
```shell script
pi@raspberrypi:~ $ lsusb
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 008: ID 091e:4b48 Garmin International 
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```
In this example the vendor id is `091e` and the product id is `4b48`. Keep your values for the next step.


### Setup Workoutizer

Now we'll run the `setup-rpi` workoutizer command. This will install and run [ansible](https://www.ansible.com/) to
configure your Raspberry Pi. It will install some required `apt` packages, insert your device ids to the
[udev](https://wiki.debian.org/udev) rule file and copy it together with the [systemd](https://wiki.debian.org/systemd)
(both are needed for the automated mounting of Garmin devices) file to your system. Note, that ansible will issue `sudo`
privileges to do so. See the `workoutizer/setup/ansible/setup_on_rpi.yml` ansible playbook for more details.
   
Pass your `vendor_id` and `product_id` as arguments to the command like:
```shell script
wkz setup-rpi --vendor_id 091e --product_id 4b48
``` 

Afterwards initialize workoutizer:
```shell script
wkz init
```
and run workoutizer as usual:
```shell script
wkz run
```

### Background

Whenever you connect your Garmin device to your Raspberry Pi, workoutizer will automatically mount the device using
`udev`. Since it is mounted as a [gvfs](https://en.wikipedia.org/wiki/GVfs) device, the file system of your device will
be mounted at `/run/user/1000/gvfs/...`. This is the default location for Raspbian and workoutizer will look for your
device in this location as default.   
