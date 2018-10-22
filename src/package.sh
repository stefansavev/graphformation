#!/usr/bin/env bash

DOCKER_IMAGE_NAME="graphformation-img"

docker build -f Dockerfile.package -t $DOCKER_IMAGE_NAME .

mkdir -p `pwd`/dist

docker run -v `pwd`/dist:/host -it $DOCKER_IMAGE_NAME bash -c 'cp dist/* /host/'

