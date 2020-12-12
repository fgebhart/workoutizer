FROM ubuntu:latest

# set apt to noninteractive mode  (for installing firefox)
ENV DEBIAN_FRONTEND='noninteractive'
# install sqlite3 package for the use of djangos db shell
RUN apt-get update
RUN apt-get install -y sqlite3 virtualenv vim git zsh wget firefox

# install oh-my-zsh
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

# install gecko driver 
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.28.0/geckodriver-v0.28.0-linux64.tar.gz
RUN sh -c 'tar -x geckodriver -zf geckodriver-v0.28.0-linux64.tar.gz -O > /usr/bin/geckodriver'
RUN chmod +x /usr/bin/geckodriver
RUN rm geckodriver-v0.28.0-linux64.tar.gz

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
