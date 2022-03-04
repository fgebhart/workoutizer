FROM ubuntu:latest

# set apt to noninteractive mode  (for installing firefox)
ENV DEBIAN_FRONTEND='noninteractive'
# install sqlite3 package for the use of djangos db shell
RUN apt-get update && \
    apt-get install -y  sqlite3 \
                        build-essential \
                        vim \
                        git \
                        zsh \
                        wget \
                        htop \
                        curl \
                        firefox \
                        unzip

RUN apt-get update && \
    apt-get install -y python3-dev \
                       python3-pip \
                       python3.8 \
                       python3.9 \
                       python3.10


# install oh-my-zsh
RUN wget https://github.com/robbyrussell/oh-my-zsh/raw/master/tools/install.sh -O - | zsh || true

RUN echo "Europe/Berlin" > /etc/timezone && \
    ln -fs /usr/share/zoneinfo/`cat /etc/timezone` /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

# install gecko driver 
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz --no-check-certificate
RUN sh -c 'tar -x geckodriver -zf geckodriver-v0.30.0-linux64.tar.gz -O > /usr/bin/geckodriver'
RUN chmod +x /usr/bin/geckodriver
RUN rm geckodriver-v0.30.0-linux64.tar.gz

# first copy only project toml and lock file to only invalidate the next setps in case of changed requirements
COPY pyproject.toml /workspaces/workoutizer/pyproject.toml
COPY poetry.lock /workspaces/workoutizer/poetry.lock
WORKDIR /workspaces/workoutizer

# install pip dependencies
RUN pip install --upgrade poetry
RUN poetry install --no-interaction --no-root

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

RUN poetry install --no-interaction
