#!/bin/bash
wget http://d3kbcqa49mib13.cloudfront.net/spark-2.1.0-bin-hadoop2.7.tgz
tar xvf spark-2.1.0-bin-hadoop2.7.tgz
sudo mv spark-2.1.0-bin-hadoop2.7 /usr/local/spark
echo 'export SPARK_HOME=/usr/local/spark' >> /home/ubuntu/.bashrc
echo 'export PYSPARK_PYTHON=/usr/bin/python3' >> /home/ubuntu/.bashrc
echo 'export PATH=$SPARK_HOME/bin:$PATH' >> /home/ubuntu/.bashrc
source /home/ubuntu/.bashrc
