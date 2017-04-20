#!/usr/bin/env python3
from kafka import KafkaConsumer
import json

# To consume latest messages and auto-commit offsets
consumer = KafkaConsumer('rsvps',
                         group_id='my-group',
                         bootstrap_servers=['localhost:9092'],
                         value_deserializer=lambda m: m.decode('ascii'))
for message in consumer:
    # message value and key are raw bytes -- decode if necessary!
    # e.g., for unicode: `message.value.decode('utf-8')`
    # print ("%s:%d:%d: key=%s value=%s" % (message.topic, message.partition,
    #                                      message.offset, message.key,
    #                                      message.value))
    print(json.loads(message.value))
