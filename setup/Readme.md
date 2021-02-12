# Setup Workoutizer on a Raspberry Pi

Follow these instructions to install Workoutizer on a Raspberry Pi in your local network.

I assume you have your Raspberry Pi already set up and running. If not I recommend to follow
the official [Raspberry Pi Setup Guide](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up).
In order to follow the below instructions, you need a command line interface to your Pi.

Note: The below instructions have been tested on a Raspberry Pi 4 Model B running Raspbian 10 (Buster). I assume it will
also work on a variety of other Pis and OS combinations, but I recommend to use the latest versions of both.


## Preparation & Installation

Create virtual environment and activate it:
```
virtualenv -p python3 venv && source venv/bin/activate 
```
Install workoutizer
```
pip install workoutizer
```

## Install Apt Packages

The following packages are required and need to be installed:
```
apt update && install -y gvfs \
        gvfs-fuse \
        gvfs-bin \
        gvfs-backends \
        ifuse
        libblas-dev \
        liblapack-dev \
        python-dev \
        libatlas-base-dev \
        libopenjp2-7
```

## Configuring your Device

Figure out the `product_id` and `vendor_id` of your device by connecting it to your Raspberry Pi via USB and run 
```
lsusb
```
Wait 1-2 minutes until the `(various models)` line next to your Garmin device disappears and trigger the `lsusb` command
again. You want to have a similar output like: 
```
pi@raspberrypi:~ $ lsusb
Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 008: ID 091e:4b48 Garmin International 
Bus 001 Device 002: ID 2109:3431 VIA Labs, Inc. Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```
In this example the vendor id is `091e` and the product id is `4b48`. Keep your values for the next step.


## Setup Workoutizer

To configure your Raspberry Pi to automatically detect and mount your garmin watch you'll need to follow these steps:

### 1. Create a udev rule
Create a file at `/etc/udev/rules.d/device_mount.rules` with the following content and replace `{{ vendor_id }}` with
your vendor id and `{{ product_id }}` with your product id:

```
ACTION=="add", SUBSYSTEM=="usb", ATTRS{idVendor}=="{{ vendor_id }}", ATTRS{idProduct}=="{{ product_id }}", TAG+="systemd", ENV{SYSTEMD_WANTS}="wkz_mount"
```

### 2. Create the wkz mount systemd service
Create a file at `/etc/systemd/system/wkz_mount.service` with the following content and replace `{{ address }}`
with the address (and port) to your Raspberry Pi in you local network.
For example if your Raspberry Pi has the IP address `192.168.0.55`, you would need to replace `{{ address }}`
with `192.168.0.55:8000` and thus the url would read `http://192.168.0.55:8000/mount-device/`.

```
[Unit]
Description=Workoutizer Device Mounting Service

[Service]
User=pi
ExecStart=curl -X POST "Content-Type: application/json" http://{{ address }}/mount-device/
```
### 3. Init and run Workoutizer
Afterwards initialize and run workoutizer:
```
wkz init
wkz run
```

## Background

Whenever you connect your Garmin device to your Raspberry Pi, workoutizer will automatically mount the device using
`udev`. Since it is mounted as a [gvfs](https://en.wikipedia.org/wiki/GVfs) device, the file system of your device will
be mounted at `/run/user/1000/gvfs/...`. This is the default location for Raspbian and workoutizer will look for your
device in this location as default.
