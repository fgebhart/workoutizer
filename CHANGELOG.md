# Workoutizer Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
* Added custom 500 error page to catch internal server errors.
* Re-trigger FileWatchdog whenever `Path to Trace Directory` gets updated on settings
  page in order to automatically import files from newly given path.
* Added description on `Path to Traces Directory` in settings page when hovering over
  question mark icon in order to easily distinguish it from `Path to Garmin Device`.
### Fixed
* Prevent `unique constraint` sql error when importing activity files with same
  checksum but different name. Note, this happened only in rare situations, when
  initially importing multiple files, which are not known to workoutizer.

## [0.17.1](https://github.com/fgebhart/workoutizer/releases/tag/0.17.1) - 2021-04-20
### Changed
* Setting `Debug` mode to `False` to handle HTTP errors with redirecting to home
* always show number of selected days as either days or years on dashboard
* show only hours (and not minutes) in summary facts duration card
* provide shortcut cli options, e.g.:
  - `wkz --version` equals `wkz -v` and 
  - `wkz init --demo` equals `wkz init -d`
### Fixed
* fix incorrect displaying of colors in "Sport Distribution" pie chart

## [0.17.0](https://github.com/fgebhart/workoutizer/releases/tag/0.17.0) - 2021-04-18
### Changed
* Migrate to new frontend: Paper Dashboard 🎉
* Introduce 7-days sport and activity trend given as hours per 7 days.
* restructure test directories
* rename django app `wizer` to `wkz` (follow 
[this guide](https://odwyer.software/blog/how-to-rename-an-existing-django-application) if you have trouble renaming your
 existing django app)

## [0.16.0](https://github.com/fgebhart/workoutizer/releases/tag/0.16.0) - 2021-04-03
### Changed
* upgrade `sportgems` to avoid spikes in speed in situation with poor gps signal. Requires `reimport`.
* remove obsolete zooming feature of best sections activity html tables.
* Add box zoom tool to time series activity plots and link it for all plots.
* Ensure vertical lap line in time series activity speed plot is rendered over entire plot height.
* Increase max size for log files to 5MB.
* Set log level for logging to file to WARNING.

## [0.15.1](https://github.com/fgebhart/workoutizer/releases/tag/0.15.1) - 2021-03-25
### Changed
* Also catch `InconsistentLengthException` when parsing best sections with `sportgems` since some `gpx` activities might
  come with different data array lengths.
* Always run initial activity import when triggering `wkz run` to ensure all activities get imported in case of any files
  have been added since the last run.

## [0.15.0](https://github.com/fgebhart/workoutizer/releases/tag/0.15.0) - 2021-03-21
### Added
* Parse best climb sections from activity files using [sportgems](https://github.com/fgebhart/sportgems) and integrate it
  into awards and activity page (next to fastest sections).

## [0.14.0](https://github.com/fgebhart/workoutizer/releases/tag/0.14.0) - 2021-03-15
### Changed
* #94:  Decoupling fit file collecting (copying files from device) from mounting device. The mount endpoint now only
        mounts the device. An additional watchdog was added which monitors whether a device was mounted and triggers the
        fit collector in case a device shows up. This supports systems where devices are automatically mounted by the OS.
        Workoutizer now also automatically finds the `Activity` directory on your device irrespective on the path in
        which the activity files are stored.
### Fixed
* #95:  Compute average values in case they are not provided in the fit file. Also make application more robust against
        missing data by adding if cases to template.
### Other
* Upgrade to `sportgems v0.4.1`, which allows to reduce code in workoutizer.
* Add more logging when mounting device and importing files to support debugging.
* remove `django-leaflet` dependency and add respective css and js to html header in order to resolve deprecation
        warnings.

## Previous Releases
For earlier releases, have a look at [the release section at github](https://github.com/fgebhart/workoutizer/releases).
