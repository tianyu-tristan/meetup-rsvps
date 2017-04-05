# meetup-rsvps

Study meetup RSVP stream data

## Data Source

Meetup RSVP stream API:

`http://stream.meetup.com/2/rsvps`

[DocRef](https://secure.meetup.com/meetup_api/docs/stream/2/rsvps/#websockets)

## Sample Code

```python
#!/usr/bin/env python3
import websocket
import _thread
import time

def on_message(ws, message):
    print (message)

def on_error(ws, error):
    print (error)

def on_close(ws):
    print ("### closed ###")

def on_open(ws):
    def run(*args):
        while True:
            time.sleep(1)
            # ws.send("Hello %d" % i)
        ws.close()
        print ("thread terminating...")
    _thread.start_new_thread(run, ())


if __name__ == "__main__":
    websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://stream.meetup.com/2/rsvps",
                                on_message = on_message,
                                on_error = on_error,
                                on_close = on_close)
    ws.on_open = on_open

    ws.run_forever()
```

## Pipline

Meetup Stream API --> Websocket Client --> Message Broker (Kafka) --> Stream Processing (Spark) --> data lake (HBase/MongoDB) --> UI (Flask)

## Business Case

* Count RSVP per region
* Categorize RSVP
	* Study what category of meetup is popular
* Predict RSVP Yes/No based on other attributes
