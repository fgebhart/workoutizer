# Workoutizer

The Workoutizer is a simple web application for organizing your workouts and sports activities. It is designed to work
locally on any system running Python. Track your activities to get an overview your overall training, similar to
platforms like [strava](https://www.strava.com/) or [garmin connect](https://connect.garmin.com/) - but without
uploading all your sensitive health data to the world-wide-web.

### Getting Started

**1. clone the repository**
```shell script
git clone git@gitlab.com:fgebhart/workoutizer.git
```
**2. create virtual environment and install pip requirements**
```shell script
virtualenv -p python3.7 wkz
source wkz/bin/activate
cd workoutizer
pip install -r requirements.txt
```

**3. prepare django application**
```shell script
cd workoutizer
python manage.py makemigrations
python manage.py migrate
python manage.py loaddata wizer.json
```

**4. run workoutizer application**
```shell script
python manage.py runserver
```

If you want to run workoutizer on a Raspberry Pi, see the [Setup section](https://gitlab.com/fgebhart/workoutizer/tree/master/setup).