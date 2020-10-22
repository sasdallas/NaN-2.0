FROM gitpod/workspace-full

RUN sudo apt-get update \
 && sudo apt-get install -y \
    python-dev libsdl-image1.2-dev libsdl-mixer1.2-dev libsdl-ttf2.0-dev libsdl1.2-dev libsmpeg-dev python-numpy subversion libportmidi-dev ffmpeg libswscale-dev libavformat-dev libavcodec-dev libfreetype6-dev \
 && sudo rm -rf /var/lib/apt/lists/*
