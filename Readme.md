# Workoutizer
[![PyPI](https://badge.fury.io/py/workoutizer.svg)](https://badge.fury.io/py/workoutizer) [![Python](https://img.shields.io/pypi/pyversions/workoutizer.svg?style=plastic)](https://badge.fury.io/py/workoutizer) [![Build Status](https://github.com/fgebhart/workoutizer/workflows/Test/badge.svg)](https://github.com/fgebhart/workoutizer/actions?query=workflow%3ATest) [![Coverage Badge](https://raw.githubusercontent.com/fgebhart/workoutizer/master/.github/badges/coverage.svg)](https://raw.githubusercontent.com/fgebhart/workoutizer/master/.github/badges/coverage.svg)

The Workoutizer is a simple web application for organizing your workouts and sports activities. It is designed to work
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
* Find the fastest sections in your activities using [sportgems](https://github.com/fgebhart/sportgems) and highlight on map
* Keyboard navigation in browser
* Add untracked activities manually via the GUI
* Export activities as `.gpx` files
* Add as many different sports as you want
* Convenience CLI for installing, running, stopping, updating, ...


## Getting Started

Install workoutizer
```shell script
pip install workoutizer
```

Initialize workoutizer to provide some demo data and run it:
```shell script
wkz init --demo
wkz run
```

See the help description of the CLI with `wkz --help` and subcommands, e.g.: `wkz manage --help`. 

In case you want to run workoutizer on a Raspberry Pi in your local network, follow the 
[Raspberry Pi setup instructions](https://github.com/fgebhart/workoutizer/tree/master/setup).

## Gallery 

 Dashboard             |  Sport Page
:-------------------------:|:-------------------------:
![](https://i.imgur.com/FcB5JDl.png)  |  ![](https://i.imgur.com/6fwcEZX.png)

 Activity Page 1/2             |  Activity Page 2/2
:-------------------------:|:-------------------------:
![](https://i.imgur.com/tcS6L4Y.png)  |  ![](https://i.imgur.com/QSf3Dpo.png)

## Thanks

Thanks to the authors of projects I integrated into workoutizer:
* [leaflet-ui](https://github.com/Raruto/leaflet-ui) by [Raruto](https://github.com/Raruto)
* [django-colorfield](https://github.com/fabiocaccamo/django-colorfield) by [Fabio Caccamo](https://github.com/fabiocaccamo)
* [python-fitparse](https://github.com/dtcooper/python-fitparse) by [dtcooper](https://github.com/dtcooper)
* [leaflet-color-markers](https://github.com/pointhi/leaflet-color-markers) by [pointhi](https://github.com/pointhi)
* [Font Awesome Icons](https://fontawesome.com/)

## Changelog

See the [releases section](https://github.com/fgebhart/workoutizer/releases).

## Contributing

Contributions are welcome! Feel free to pick an [open issue](https://github.com/fgebhart/workoutizer/issues), open up 
a pull request or file a new issue.

For local development I recommend to run the development docker container. First clone the repo:
```
git clone git@github.com:fgebhart/workoutizer.git
cd workoutizer
```
and then start workoutizer in docker using the convenience script:
```
./run_docker.sh
```
This might take a while to build the image, run the container and initialize workoutizer. Once up and running, run the
tests with
```
pytest wizer/tests/ -n4
```
Once this was successful you are good to go.

In order to run workoutizer you could either run it using django's `manage.py` script
```
python manage.py runserver
```
or using the `wkz` cli
```
wkz run
```
In case you encounter any issues in the setup process, feel free to file an issue.

Note: If you are using VS-Code you might want to open the folder of this repo in a docker container directly using the
Remote - Containers extension.
