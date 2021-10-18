# Setup Workoutizer on a Raspberry Pi

Follow these instructions to install Workoutizer on a Raspberry Pi in your local network.

I assume you have your Raspberry Pi already set up and running. If not I recommend to follow
the official [Raspberry Pi Setup Guide](https://projects.raspberrypi.org/en/projects/raspberry-pi-setting-up).
In order to follow the below instructions, you need a command line interface to your Pi.

Note: The below instructions have been tested on a Raspberry Pi 4 Model B running Raspbian 10 (Buster). I assume it will
also work on a variety of other Pis and OS combinations, but I recommend to use the latest versions of both.


## Install Apt Packages

The following packages are required and need to be installed:
```
sudo apt update && sudo apt install -y gvfs \
        gvfs-fuse \
        gvfs-bin \
        gvfs-backends \
        ifuse \
        libblas-dev \
        liblapack-dev \
        python-dev \
        libatlas-base-dev \
        libopenjp2-7 \
        virtualenv \
        pmount
```


## Preparation & Installation

Create virtual environment and activate it:
```
virtualenv -p python3 venv && source venv/bin/activate 
```
Install workoutizer
```
pip install workoutizer
```


## Setup Workoutizer

To configure your Raspberry Pi to automatically detect and mount your garmin watch you'll need to follow these steps:

### 1. Create a udev rule
Create a file at `/etc/udev/rules.d/99-mount_device.rules` with the following content:

```
ACTION=="add", ATTRS{idVendor}=="091e", TAG+="systemd", ENV{SYSTEMD_WANTS}="wkz_mount"
```

### 2. Create the wkz mount service
Create a file at `/etc/systemd/system/wkz_mount.service` with the following content and replace `{{ address }}`
with the address (and port) to your Raspberry Pi in you local network.
For example if your Raspberry Pi has the IP address `192.168.0.55`, you would need to replace `{{ address }}`
with `192.168.0.55:8000` and thus the url would read `http://192.168.0.55:8000/mount-device/`.

```
[Unit]
Description=Workoutizer Device Mounting Service

[Service]
User=pi
ExecStart=curl -X POST -H "Content-Type: application/json" http://{{ address }}/mount-device/
```

### 3. (Optional) Create the wkz service
In order to automatically start workoutizer on system boot, create a file at `/etc/systemd/system/wkz.service`
with the following content:

```
[Unit]
Description=Workoutizer
After=syslog.target network.target

[Service]
User=pi
WorkingDirectory=~
ExecStart=/home/pi/venv/bin/wkz run
Restart=on-abort

[Install]
WantedBy=multi-user.target
```

Execute the following command to enable the wkz service automatically after reboot.

```
systemctl enable wkz
```

### 4. Init and run Workoutizer
Afterwards initialize - if you haven't done so yet - workoutizer:
```
wkz init
```

and run it either with:
```
systemctl start wkz
```
in case you are using the systemd service or, if you don't use systemd:
```
wkz run
```

## Background

Whenever you connect your Garmin device to your Raspberry Pi, workoutizer will automatically mount the device.
Workoutizer currently supports devices with MTP (e.g. FR645) and Block (e.g. FR920XT) modes. Some devices support both
modes, some only one. 

All devices are mounted using `udev` which is used to define the type of device. MTP devices are mounted as a
[gvfs](https://en.wikipedia.org/wiki/GVfs) device, the file system of your device will be mounted at
`/run/user/1000/gvfs/...`. This is the default location for Raspbian and workoutizer will look for your device in this
location as default.

The Block devices are mounted using `pmount`, the file system is found at `/media/garmin`. You should configure this
location under `Fetch Files from Device` under the setting from workoutizer.