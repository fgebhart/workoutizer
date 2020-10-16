# to build the required image run:
docker build . -t wkz

docker run \
  --name workoutizer \
  --rm \
  -it \
  -v $(pwd):/wkz \
  wkz \
  /bin/bash -c "source /tmp/venv/bin/activate && bash"