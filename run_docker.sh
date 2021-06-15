# to build the required image run:
docker build . -t wkz

docker run \
  --name workoutizer \
  --rm \
  -p 8000:8000 \
  -it \
  -v $(pwd):/wkz \
  wkz \
  /bin/bash -c "source /tmp/venv/bin/activate && bash"