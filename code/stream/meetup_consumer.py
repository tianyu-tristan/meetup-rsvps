#!/usr/bin/env python3
from kafka import KafkaConsumer
import json
import os
import yaml
import boto3

def connect_aws(config_filepath='/vagrant/aws_api_cred.yml'):
    """return firehose boto3 client
    """
    credentials = yaml.load(open(os.path.expanduser(config_filepath)))
    client = boto3.client('firehose',
                          region_name='us-east-1', **credentials['aws'])
    return client

# assume aws configure has been done
client = connect_aws()

# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer('meetup-rsvps-topic',
                         group_id='my-group',
                         bootstrap_servers=['localhost:9092'],
                         value_deserializer=lambda m: json.loads(m.decode('utf-8')))
print("consumer started ...")

for message in consumer:
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
    # print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition, message.offset, message.key, message.value))
    data = str(message.value)
    # print("Sending: ", data)
    client.put_record(DeliveryStreamName='tristan-meetup-stream',
                      Record={'Data': data})
