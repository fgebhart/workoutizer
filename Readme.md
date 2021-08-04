# Workoutizer

[![PyPI](https://badge.fury.io/py/workoutizer.svg)](https://badge.fury.io/py/workoutizer)
[![Python](https://img.shields.io/pypi/pyversions/workoutizer.svg?style=plastic)](https://badge.fury.io/py/workoutizer)
[![Build Status](https://github.com/fgebhart/workoutizer/actions/workflows/matrix_test.yml/badge.svg)](https://github.com/fgebhart/workoutizer/actions/workflows/matrix_test.yml)
[![Setup on Raspberry Pi](https://github.com/fgebhart/workoutizer/actions/workflows/raspberry_pi_test.yml/badge.svg)](https://github.com/fgebhart/workoutizer/actions/workflows/raspberry_pi_test.yml)
[![Coverage Badge](https://raw.githubusercontent.com/fgebhart/workoutizer/master/.github/badges/coverage.svg)](https://raw.githubusercontent.com/fgebhart/workoutizer/master/.github/badges/coverage.svg)
[![Downloads](https://img.shields.io/pypi/dm/workoutizer.svg?label=Pypi%20downloads)](https://pypi.org/project/workoutizer/)
[![workoutizer](https://snyk.io/advisor/python/workoutizer/badge.svg)](https://snyk.io/advisor/python/workoutizer)

Workoutizer is a simple web application for organizing your workouts and sports activities. It is designed to work
locally on any UNIX-like system running Python.

Track your activities to get an overview of your overall training, similar to platforms like
[strava](https://www.strava.com/) or [garmin connect](https://connect.garmin.com/) - but without
uploading all your sensitive health data to some 3rd party cloud.


## Features

* Automatic import of Garmin `.fit` files and `.gpx` files
* Automatic naming of activities based on daytime, sport and geo location
* Render your activity gps data on different OSM maps
* Plot your activity specific data e.g. heart rate, pace, temperature, cadence and altitude
* Integrate laps into both plots and maps
* Connected plots and map via mouse hovering
* Find sections with highest speed and max altitude gain using [sportgems](https://github.com/fgebhart/sportgems) and
  highlight on map
* Add untracked activities manually via the GUI
* Export activities as `.gpx` files
* Add as many different sports as you want


## Status

Workoutizer is still in a somewhat experimental phase. Things might change a lot from one version to another. However,
I'm happy to receive bug reports and feedback.


## Getting Started

Install workoutizer using pip
```
pip install workoutizer
```

Initialize workoutizer to provide some demo data and run it:
```
wkz init --demo
wkz run
```

See the help description of the CLI with `wkz --help` and subcommands, e.g.: `wkz manage --help`. 

In case you want to run workoutizer on a Raspberry Pi in your local network, follow the 
[Raspberry Pi setup instructions](https://github.com/fgebhart/workoutizer/tree/main/setup).


## Gallery 

 Dashboard             |  Sport Page
:-------------------------:|:-------------------------:
![](https://i.imgur.com/3CUCGC8.png)  |  ![](https://i.imgur.com/p5FcrHz.png)

 Activity Page 1/2             |  Activity Page 2/2
:-------------------------:|:-------------------------:
![](https://i.imgur.com/FnVFz9P.png)  |  ![](https://i.imgur.com/zp8iQcm.png)


## Changelog

See [Changelog](https://github.com/fgebhart/workoutizer/blob/main/CHANGELOG.md).


## Contributing

Contributions are welcome - check out the [Contribution Guidelines](https://github.com/fgebhart/workoutizer/blob/main/CONTRIBUTING.md).


## Thanks

Libraries and other tools used by Workoutizer:
* [leaflet-ui](https://github.com/Raruto/leaflet-ui) by [Raruto](https://github.com/Raruto)
* [django-colorfield](https://github.com/fabiocaccamo/django-colorfield) by [Fabio Caccamo](https://github.com/fabiocaccamo)
* [python-fitparse](https://github.com/dtcooper/python-fitparse) by [dtcooper](https://github.com/dtcooper)
* [leaflet-color-markers](https://github.com/pointhi/leaflet-color-markers) by [pointhi](https://github.com/pointhi)
* [Font Awesome Icons](https://fontawesome.com/)
* [Paper-Dashboard Pro](https://www.creative-tim.com/product/paper-dashboard-2-pro) by [Creative Tim](https://www.creative-tim.com/)
