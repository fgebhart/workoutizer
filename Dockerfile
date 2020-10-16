FROM python:3.8

 # install sqlite3 package for the use of djangos db shell
RUN apt-get update
RUN apt-get install -y sqlite3 virtualenv vim

# first copy only requirements files to only invalidate the next setps in case of changed requirements
COPY ./setup/requirements/ /workoutizer/setup/requirements/

# install pip dependencies
RUN virtualenv -p python3.8 /tmp/venv
RUN /bin/bash -c 'source /tmp/venv/bin/activate && pip install -r /workoutizer/setup/requirements/requirements.txt'
RUN /bin/bash -c 'source /tmp/venv/bin/activate && pip install -r /workoutizer/setup/requirements/dev-requirements.txt'

ENV WKZ_ENV='devel'
ENV WKZ_LOG_LEVEL='DEBUG'

EXPOSE 8000

COPY . /workoutizer
WORKDIR /workoutizer

RUN /bin/bash -c 'source /tmp/venv/bin/activate && pip install -e . --no-deps --disable-pip-version-check'
