FROM python:3.8

RUN mkdir /workoutizer
WORKDIR /workoutizer
COPY setup/requirements/* /workoutizer/
RUN ls
RUN pwd
RUN pip install -r requirements.txt
RUN pip install -r dev-requirements.txt
CMD ["/bin/bash"]
