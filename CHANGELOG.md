# Workoutizer Changelog


## Workoutizer 0.14.0 (2021-03-15)

### Changes
* #94:  Decoupling fit file collecting (copying files from device) from mounting device. The mount endpoint now only
        mounts the device. An additional watchdog was added which monitors whether a device was mounted and triggers the
        fit collector in case a device shows up. This supports systems where devices are automatically mounted by the OS.
        Workoutizer now also automatically finds the `Activity` directory on your device irrespective on the path in
        which the activity files are stored.

### Bugfixes
* #95:  Compute average values in case they are not provided in the fit file. Also make application more robust against
        missing data by adding if cases to template.

### Other
* Upgrade to `sportgems v0.4.1`, which allows to reduce code in workoutizer.
* Add more logging when mounting device and importing files to support debugging.
* remove `django-leaflet` dependency and add respective css and js to html header in order to resolve deprecation
        warnings.


## Previous Releases
For earlier releases, have a look at [the release section at github](https://github.com/fgebhart/workoutizer/releases).