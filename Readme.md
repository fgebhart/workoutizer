# Workoutizer

The Workoutizer is a simple web application for organizing your workouts and sports activities. It is designed to work
locally on any UNIX-like system running Python.

Track your activities to get an overview of your overall training, similar to platforms like
[strava](https://www.strava.com/) or [garmin connect](https://connect.garmin.com/) - but without
uploading all your sensitive health data to some 3rd party cloud.

#### Features
* Automatic import of Garmin `.fit` files and `.gpx` files
* Dashboard overview page of all activities
* Render your activity gps data on different OSM maps
* Show either all activities of one sport or only one activity on the map
* Plots of activity specific data like: heart rate, pace, temperature, cadence and altitude
* Integrate laps into both plots and maps
* Connect plots and map via mouse hovering
* Keyboard navigation in browser
* Add untracked activities manually via the GUI
* Create and download `.gpx` files to share your activities
* Add as many different sports as you want.
* Convenience CLI for installing, configuring, updating, ...


## Getting Started

Install workoutizer
```shell script
pip install workoutizer
```

Initialize and run workoutizer
```shell script
wkz init
wkz run
```

See the help description of the CLI with `wkz --help` and even subcommands, e.g.: `wkz manage --help`. 

Note: This should work for any Linux and Mac system. Please
[report any occurring issues](https://github.com/fgebhart/workoutizer/issues) when installing workoutizer.

Workoutizer comes bundled with some initial toy activity data, which can be deleted easily on the Settings page.

In case you want to run workoutizer on a Raspberry Pi in your local network, follow the 
[Raspberry Pi setup instructions](https://github.com/fgebhart/workoutizer/tree/master/setup).

## Gallery 

 Dashboard             |  Sport Page
:-------------------------:|:-------------------------:
![](https://i.imgur.com/FcB5JDl.png)  |  ![](https://i.imgur.com/6fwcEZX.png)

 Activity Page 1/2             |  Activity Page 2/2
:-------------------------:|:-------------------------:
![](https://i.imgur.com/iuXhiab.png)  |  ![](https://i.imgur.com/7nV4Ks2.png)

## Thanks

Thanks to the authors of projects I integrated into workoutizer:
* [leaflet-ui](https://github.com/Raruto/leaflet-ui) by [Raruto](https://github.com/Raruto)
* [django-colorfield](https://github.com/fabiocaccamo/django-colorfield) by [Fabio Caccamo](https://github.com/fabiocaccamo)
* [python-fitparse](https://github.com/dtcooper/python-fitparse) by [dtcooper](https://github.com/dtcooper)
* [leaflet-color-markers](https://github.com/pointhi/leaflet-color-markers) by [pointhi](https://github.com/pointhi)
* [Font Awesome Icons](https://fontawesome.com/)

Enjoy!

## Changelog

See the [releases section](https://github.com/fgebhart/workoutizer/releases).

For older releases have a look at the [archived project at gitlab](https://gitlab.com/fgebhart/workoutizer).

## Contributing

Contributions are welcome! Feel free to pick an [open issue](https://github.com/fgebhart/workoutizer/issues), open up 
a pull request or file a new issue.

For local development first clone the repo and install the `dev-requirements.txt` like
```shell script
pip install -r setup/requirements/dev-requirements.txt
``` 
Afterwards I recommend to run the development docker container:
```shell script
./run_docker.sh
```
This will build the image, run the container and initialize workoutizer. Once up and running, run the tests
```shell script
pytest wizer/tests/
```
Once this was successful you are good to go.

Note: The `browser_tests` cannot (yet) be ran from within the docker container, but it is possible to run them form your
host system. You might need to install [gecko driver](https://github.com/mozilla/geckodriver/releases) though.
