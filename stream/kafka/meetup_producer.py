#!/usr/bin/env python3
import os
import websocket
import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError


def on_message(ws, message):
     print(message)
     producer.send('meetup-rsvps-topic', message)
     producer.flush()


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                         bootstrap_servers=['localhost:9092'])
websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://stream.meetup.com/2/rsvps",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

ws.run_forever()
