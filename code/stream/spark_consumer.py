#!/usr/bin/env python3

from pyspark.streaming.kafka import KafkaUtils, Broker
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import json
import numpy as np
from kafka import KafkaProducer
from collections import Counter

TOP_N = 5
BATCH_DUR = 10 # sec
WIN_DUR = 300 # sec
SLIDE_DUR = 10 # sec


def rsvp_event(kvpair):
    try:
        rsvp = json.loads(kvpair[1])
        rsvp = json.loads(rsvp)
        event = rsvp.get('event', {})
        event_id = event.get('event_id', None)
        event_name = event.get('event_name', None)
        response = 1 if rsvp.get('response', None) == 'yes' else 0
        return ((event_id, event_name), response)
    except ValueError:
        return None


def do_partition(partition):
    """
        - create kafka producer per partition
        - "serialize" TOP_N ((event_id, event,name), count) as json dict
        - send to kafka topic
    """
    producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                             bootstrap_servers=['localhost:9092'])
    records = dict(list(partition))
    records = Counter(records)
    print("Records:", json.dumps(records))
    producer.send('plotly-topic', records)
    producer.flush()

    producer.close()

def send_rdd(rdd):
    """send rdd to kafka, where another plotly consumer is picking up on the other end
    """
    rdd.foreachPartition(do_partition)

def take_top_rdd(rdd):
    """ Per rdd:
        - sort rdd by count
        - taking TOP_N
        - discard the rest
    """

    top_n = rdd.sortBy(lambda pair: pair[1], ascending=False).take(TOP_N)
    print("top_n:",top_n)
    return rdd.filter(lambda record: record in top_n)


def main():

    zkQuorum = "localhost:2181"
    topic = "meetup-rsvps-topic"

    sc = SparkContext("local[*]")
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, BATCH_DUR) # 5 sec batch duration

    # utf-8 text stream from kafka
    kvs = KafkaUtils.createStream(ssc, zkQuorum, "spark_consumer", {topic: 1}).cache()

    event_count = kvs.map(rsvp_event).filter(lambda line: line is not None)
    event_count.reduceByKeyAndWindow(func=lambda x,y:x+y,
                                     invFunc=lambda x,y:x-y,
                                     windowDuration=WIN_DUR,
                                     slideDuration=SLIDE_DUR) \
                .filter(lambda pair: pair[1] > 0) \
                .transform(take_top_rdd) \
                .map(lambda pair: (pair[0][1], pair[1])) \
                .foreachRDD(send_rdd)

    # event_count.pprint()
    ssc.checkpoint("rsvps_checkpoint_dir")
    ssc.start()
    ssc.awaitTermination()

if __name__ == '__main__':
    main()
