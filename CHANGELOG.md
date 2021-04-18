# Workoutizer Changelog

## Workoutizer 0.17.0 (2021-04-18)
### Changes
* Migrate to new frontend: Paper Dashboard 🎉
* Introduce 7-days sport and activity trend given as hours per 7 days.
### Clean-ups
* restructure test directories
* rename django app `wizer` to `wkz`

## Workoutizer 0.16.0 (2021-04-03)
### Changes
* upgrade `sportgems` to avoid spikes in speed in situation with poor gps signal. Requires `reimport`.
* remove obsolete zooming feature of best sections activity html tables.
* Add box zoom tool to time series activity plots and link it for all plots.
* Ensure vertical lap line in time series activity speed plot is rendered over entire plot height.
* Increase max size for log files to 5MB.
* Set log level for logging to file to WARNING.

## Workoutizer 0.15.1 (2021-03-25)
### Changes
* Also catch `InconsistentLengthException` when parsing best sections with `sportgems` since some `gpx` activities might
  come with different data array lengths.
* Always run initial activity import when triggering `wkz run` to ensure all activities get imported in case of any files
  have been added since the last run.

## Workoutizer 0.15.0 (2021-03-21)
### Features
* Parse best climb sections from activity files using [sportgems](https://github.com/fgebhart/sportgems) and integrate it
  into awards and activity page (next to fastest sections).

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
