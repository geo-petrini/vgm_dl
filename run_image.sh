#!/bin/bash
docker run \
    --volume=vgmdl_download:/app/downloads \
    --volume=vgmdl_db:/app/instance \
    --name=vgmdl \
    -p 5000:5000 \
    --env http_proxy=$http_proxy \
    --env https_proxy=$https_proxy \
    --restart=no \
    -d \
    vgmdl:latest