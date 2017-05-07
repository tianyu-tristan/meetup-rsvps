#!/usr/bin/env python3
import os
import yaml
import boto3
import websocket
import _thread
import time


def on_message(ws, message):
    client.put_record(DeliveryStreamName='tristan-meetup-stream',
                      Record={'Data': message})
    # print(message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("### closed ###")


def on_open(ws):
    def run(*args):
        while True:
            time.sleep(1)
            # ws.send("Hello %d" % i)
        ws.close()
        print("thread terminating...")
    _thread.start_new_thread(run, ())


def connect_aws(config_filepath='/vagrant/aws/aws_api_cred.yml'):
    credentials = yaml.load(open(os.path.expanduser(config_filepath)))
    client = boto3.client('firehose',
                          region_name='us-east-1', **credentials['aws'])
    # conn = kinesis.connect_to_region(region_name='us-east-1')
    return client


client = connect_aws()
websocket.enableTrace(True)
ws = websocket.WebSocketApp("ws://stream.meetup.com/2/open_events",
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)
# ws.on_open = on_open

ws.run_forever()
