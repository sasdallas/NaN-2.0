FROM gitpod/workspace-full

RUN sudo apt-get update \
 && sudo apt-get install -y \
    sdl \
 && sudo rm -rf /var/lib/apt/lists/*
