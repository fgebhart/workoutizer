
if ! docker image inspect wkz > /dev/null; then
  # to build the required image run:
  docker build . -t wkz
fi

docker run \
  --name workoutizer \
  --rm \
  -it \
  -e WKZ_LOG_LEVEL='DEBUG' \
  -p 8000:8000 \
  -v $(pwd):/wkz \
  -v ~/.wkz:/root/.wkz \
  wkz \
  /bin/bash -c "pip install -e . --no-deps --disable-pip-version-check && bash"
