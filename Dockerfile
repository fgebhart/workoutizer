FROM ubuntu:latest

# set apt to noninteractive mode  (for installing firefox)
ENV DEBIAN_FRONTEND='noninteractive'
# install sqlite3 package for the use of djangos db shell
RUN apt-get update && \
    apt-get install -y sqlite3 virtualenv vim git zsh wget htop curl firefox unzip

# install oh-my-zsh
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

RUN echo "Europe/Berlin" > /etc/timezone && \
    ln -fs /usr/share/zoneinfo/`cat /etc/timezone` /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# install gecko driver 
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.28.0/geckodriver-v0.28.0-linux64.tar.gz --no-check-certificate
RUN sh -c 'tar -x geckodriver -zf geckodriver-v0.28.0-linux64.tar.gz -O > /usr/bin/geckodriver'
RUN chmod +x /usr/bin/geckodriver
RUN rm geckodriver-v0.28.0-linux64.tar.gz

# Install chrome driver, use link for static version of chrome version
# You can also use: https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
# But this can result in a new version breaking the setup
RUN wget https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_91.0.4472.114-1_amd64.deb
RUN dpkg -i google-chrome-stable_91.0.4472.114-1_amd64.deb; apt-get install -fy
RUN wget https://chromedriver.storage.googleapis.com/91.0.4472.101/chromedriver_linux64.zip
RUN unzip -p chromedriver_linux64.zip > /usr/bin/chromedriver
RUN chmod +x /usr/bin/chromedriver
RUN rm google-chrome-stable_91.0.4472.114-1_amd64.deb chromedriver_linux64.zip

# first copy only requirements files to only invalidate the next setps in case of changed requirements
COPY ./setup/requirements/ /workspaces/workoutizer/setup/requirements/

# install pip dependencies
RUN virtualenv -p python3.8 /tmp/venv
RUN /bin/bash -c 'source /tmp/venv/bin/activate && pip install -r /workspaces/workoutizer/setup/requirements/dev-requirements.txt'
RUN /bin/bash -c 'source /tmp/venv/bin/activate && pip install -r /workspaces/workoutizer/setup/requirements/requirements.txt'

ENV SHELL /bin/zsh
ENV WKZ_ENV='devel'
ENV WKZ_LOG_LEVEL='DEBUG'
ENV DJANGO_DEBUG=True
ENV PYTHONBREAKPOINT=ipdb.set_trace

EXPOSE 8000

COPY . /workspaces/workoutizer
WORKDIR /workspaces/workoutizer

# set convenience alias
RUN echo 'alias run_all_tests="pytest tests -v -n auto --html=pytest-report.html"' >> ~/.zshrc

RUN /bin/bash -c 'source /tmp/venv/bin/activate && pip install -e . --no-deps --disable-pip-version-check'
