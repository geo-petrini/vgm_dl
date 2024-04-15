#!/bin/bash
docker build \
--build-arg http_proxy=$HTTP_PROXY \
--build-arg HTTP_PROXY=$HTTP_PROXY \
--build-arg https_proxy=$HTTPS_PROXY \
--build-arg HTTPS_PROXY=$HTTPS_PROXY \
--build-arg ftp_proxy=$HTTP_PROXY \
--build-arg no_proxy=$NO_PROXY \
--build-arg NO_PROXY=$NO_PROXY \
--pull --rm -f "Dockerfile_noredis" -t vgmdl_noredis:latest "." 