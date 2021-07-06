# Workoutizer Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]
Placeholder section for unreleased changes.

## [0.21.0](https://github.com/fgebhart/workoutizer/releases/tag/v0.21.0) - 2021-07-06
### Added
* Add support for mounting devices which identify as block device.
* Add `check-for-update` command to `wkz` CLI.
### Changed
* When looking for activities on device allow files next to device dir.
### Fixed
* Test for mounting devices fails sometimes, because it was not ready for block device mounting.
* Fix reading package version of already installed workoutizer package.

## [0.20.1](https://github.com/fgebhart/workoutizer/releases/tag/v0.20.1) - 2021-06-25
### Changed
* Updated the url to releases on help page to now point to the changelog on github.
### Fixed
* Remove temporary payload from parsing files during reimport from both the scheduler
  `as_completed` list and the worker. This avoids piling up memory when reimporting
  many files.

## [0.20.0](https://github.com/fgebhart/workoutizer/releases/tag/v0.20.0) - 2021-06-21
### Added
* Port-forwarding added when using the `run_docker.sh` script.
* Added support for Python3.7 and armv7 architecture to simplify the installation on
  Raspberry Pi - which is based on debian buster which itself comes with Python3.7,
  currently.
### Changed
* Made the extension of fit files to be imported case insensitive.
### Fixed
* Apply initial check to file importing process, which skips running a dask cluster
  in case all existing files are preset in the db already. This should fix a memory
  leak.
* Set `processes=False` for dask client and only use scheduler with one worker to fix
  worker timeout when running `wkz init --demo`
  ([#160](https://github.com/fgebhart/workoutizer/issues/160)).

## [0.19.0](https://github.com/fgebhart/workoutizer/releases/tag/v0.19.0) - 2021-06-13
Note, when upgrading to this version you need to run `wkz reimport` in order to parse
and display the additional data fields added in this release.
### Added
* Add `gpx` file to demo activities.
* Use [dask](https://docs.dask.org/en/) to parse activity files in parallel to speed
  up file import / reimport.
* Reduce number of data points of tracked activities by only selecting every 5th value
  (configurable) in order to speed up activity page load.
* Parse `total ascent` and `total descent` values from `fit` files and display them
  on the activity page.
* Integrate `total ascent` into awards page by listing the top three activities with
  highest `total ascent` value per sport.
### Changed
* Show "made with ❤️" in footer only on settings and help page.
* Moved `tests` folder from `workoutizer/wkz/tests/` to `workoutizer/tests` root folder.
* Run all tests together in github actions `Test` and `Release` pipeline.
* Ensure activity leaflet map has always height of > 400 pixels
### Removed
* Removed `reimport` button/functionality from settings page in order to avoid threads
  from interfering when accessing sqlite db.
* Removed retries around fit file reading and md5sum calculation, turned out that the
  io errors were caused by a too long usb cable...

## [0.18.0](https://github.com/fgebhart/workoutizer/releases/tag/v0.18.0) - 2021-05-16
### Added
* Added custom 500 error page to catch internal server errors.
* Re-trigger FileWatchdog whenever `Path to Trace Directory` gets updated on settings
  page in order to automatically import files from newly given path.
* Added description on `Path to Traces Directory` in settings page when hovering over
  question mark icon in order to easily distinguish it from `Path to Garmin Device`.
* Set default log level of django to `WARNING`. Django log level can also be changed
  by setting the value of the `DJANGO_LOG_LEVEL` environment variable.
* Avoid showing `None` in case of an activity having `None` calories. Show `-` instead.
* Enable `Server Sent Events (SSE)` to inform user on backend events. This allows for
  progress updates during importing/reimporting and validates paths for their
  existence on the machine workoutizer is running on.
* The settings icon located in the top right corner is colored red in case the
  connection to the server is broken and green in case it is established. Note that a
  established connection is required in order to receive `SSEs`.
* Wrap `retry` around checksum calculation to remedy io errors.
* Use `huey` for queueing reimport & import tasks from within the settings page. Now
  both file watchdog and device watchdog are triggered periodically every minute and
  will be queued on huey to run independent of the django process.
  It is also ensured that only one file importer is run at a time and thus fixes some
  concurrency issues.
### Changed
* Catch fit file parsing errors to ensure to continue parsing other files in case only
  one file is corrupted.
* Reduce number of retries from 5 to 3 to speed-up importing multiple files.
* Set `zsh` as default shell and remove `terminal.sh` docker entrypoint script.
### Fixed
* Prevent `unique constraint` sql error when importing activity files with same
  checksum but different name. Note, this happened only in rare situations, when
  initially importing multiple files, which are not known to workoutizer.
* Removed and reduced unneeded logging from `fit collector`.

## [0.17.1](https://github.com/fgebhart/workoutizer/releases/tag/v0.17.1) - 2021-04-20
### Changed
* Setting `Debug` mode to `False` to handle HTTP errors with redirecting to home
* always show number of selected days as either days or years on dashboard
* show only hours (and not minutes) in summary facts duration card
* provide shortcut cli options, e.g.:
  - `wkz --version` equals `wkz -v` and 
  - `wkz init --demo` equals `wkz init -d`
### Fixed
* fix incorrect displaying of colors in "Sport Distribution" pie chart

## [0.17.0](https://github.com/fgebhart/workoutizer/releases/tag/v0.17.0) - 2021-04-18
### Changed
* Migrate to new frontend: Paper Dashboard 🎉
* Introduce 7-days sport and activity trend given as hours per 7 days.
* restructure test directories
* rename django app `wizer` to `wkz` (follow 
[this guide](https://odwyer.software/blog/how-to-rename-an-existing-django-application) if you have trouble renaming your
 existing django app)

## [0.16.0](https://github.com/fgebhart/workoutizer/releases/tag/v0.16.0) - 2021-04-03
### Changed
* upgrade `sportgems` to avoid spikes in speed in situation with poor gps signal. Requires `reimport`.
* remove obsolete zooming feature of best sections activity html tables.
* Add box zoom tool to time series activity plots and link it for all plots.
* Ensure vertical lap line in time series activity speed plot is rendered over entire plot height.
* Increase max size for log files to 5MB.
* Set log level for logging to file to WARNING.

## [0.15.1](https://github.com/fgebhart/workoutizer/releases/tag/v0.15.1) - 2021-03-25
### Changed
* Also catch `InconsistentLengthException` when parsing best sections with `sportgems` since some `gpx` activities might
  come with different data array lengths.
* Always run initial activity import when triggering `wkz run` to ensure all activities get imported in case of any files
  have been added since the last run.

## [0.15.0](https://github.com/fgebhart/workoutizer/releases/tag/v0.15.0) - 2021-03-21
### Added
* Parse best climb sections from activity files using [sportgems](https://github.com/fgebhart/sportgems) and integrate it
  into awards and activity page (next to fastest sections).

## [0.14.0](https://github.com/fgebhart/workoutizer/releases/tag/v0.14.0) - 2021-03-15
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
