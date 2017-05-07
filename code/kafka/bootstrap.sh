#!/bin/bash

# something i need to set first for everything else to run
export LC_ALL=C

# add java repo
sudo add-apt-repository -y ppa:webupd8team/java

# update & install stuff
sudo apt-get update -y
sudo apt install python3-pip -y
sudo python3 -m pip install pip websocket-client kafka boto3 yaml -U
# nohup sudo python3 /vagrant/stream_meetup.py &

# install java silently
echo "oracle-java8-installer shared/accepted-oracle-license-v1-1 select true" | sudo debconf-set-selections
sudo apt-get install oracle-java8-installer -y

# install zookeeper
sudo apt-get install zookeeperd -y

# install kafka
wget http://apache.claz.org/kafka/0.10.2.0/kafka_2.12-0.10.2.0.tgz
sudo mkdir /opt/Kafka
sudo tar -xvf kafka_2.12-0.10.2.0.tgz -C /opt/Kafka/
nohup sudo /opt/Kafka/kafka_2.12-0.10.2.0/bin/kafka-server-start.sh /opt/Kafka/kafka_2.12-0.10.2.0/config/server.properties &

# install spark
/vagrant/install_spark.sh

# start producer & consumer
nohup python3 /vagrant/meetup_producer.py &
nohup python3 /vagrant/meetup_consumer.py &
