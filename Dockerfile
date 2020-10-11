FROM python:3.8

# install systemctl replacement script for testing ansible playbooks
COPY setup/other/systemctl.py /usr/bin/systemctl
RUN chmod +x /usr/bin/systemctl

 # install sqlite3 package for the use of djangos db shell
RUN apt-get update
RUN apt-get install -y sqlite3 virtualenv vim

# first copy only requirements files to only invalidate the next setps in case of changed requirements
COPY ./setup/requirements/ /wkz/setup/requirements/

# install pip dependencies
RUN virtualenv -p python3.8 /tmp/venv
RUN /bin/bash -c 'source /tmp/venv/bin/activate && pip install -r /wkz/setup/requirements/requirements.txt'
RUN /bin/bash -c 'source /tmp/venv/bin/activate && pip install -r /wkz/setup/requirements/dev-requirements.txt'

# now copy also the remaining source files
COPY . /wkz
WORKDIR /wkz