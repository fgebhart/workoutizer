FROM python:3.8

# install systemctl replacement script for testing ansible playbooks
COPY setup/other/systemctl.py /usr/bin/systemctl
RUN chmod +x /usr/bin/systemctl

# install requirements
COPY . /wkz
WORKDIR /wkz
RUN pip install -r /wkz/setup/requirements/requirements.txt
RUN pip install -r /wkz/setup/requirements/dev-requirements.txt
