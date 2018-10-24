#!/usr/bin/env bash

DOCKER_IMAGE_NAME="stefansavev/graphformation:0.0.1"

docker build -f Dockerfile.package -t $DOCKER_IMAGE_NAME .

mkdir -p `pwd`/dist

docker run -v `pwd`/dist:/host -it $DOCKER_IMAGE_NAME bash -c 'cp dist/* /host/'
