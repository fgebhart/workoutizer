# to build the required image run:
docker build . -t wkz

docker run \
  --name workoutizer \
  --rm \
  -it \
  -e WKZ_LOG_LEVEL='DEBUG' \
  -p 8000:8000 \
  -v $(pwd):/wkz \
  -v ~/.wkz:/root/.wkz \
  wkz \
  /bin/bash -c "source /tmp/venv/bin/activate && pip install -e . --no-deps --disable-pip-version-check && bash"