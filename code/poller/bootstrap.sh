#!/bin/bash

# something i need to set first for everything else to run
export LC_ALL=C

# update & install stuff
sudo apt-get update -y
sudo apt install python3-pip -y
sudo python3 -m pip install pip boto3 websocket-client -U
for cmd in $(ls /vagrant/stream_meetup*)
do
    nohup sudo python3 $cmd &
done
