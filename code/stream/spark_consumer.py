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


def extract_event_count(pair):
    """extract event_id, event_name and response from rsvp
    INPUT: (None, json_str)
    OUTPUT: ((event_id, event_name), yes_count)
    """
    try:
        rsvp = json.loads(pair[1])
        rsvp = json.loads(rsvp)
        event = rsvp.get('event', {})
        event_id = event.get('event_id', None)
        event_name = event.get('event_name', None)
        response = 1 if rsvp.get('response', None) == 'yes' else 0
        return ((event_id, event_name), response)
    except ValueError:
        return None

def extract_response(pair):
    """extract response from rsvp
    INPUT: (None, json_str)
    OUTPUT: (None, (yes_count, no_count, other_count))
    """
    try:
        rsvp = json.loads(pair[1])
        rsvp = json.loads(rsvp)
        response = rsvp.get('response', None)

        if response == 'yes':
            return (None, (1, 0, 0))
        elif response == 'no':
            return (None, (0, 1, 0))
        else:
            return (None, (0, 0, 1))
    except ValueError:
        return None

def send_recent_top(partition):
    """for each partition, send recent top event name and count
        - create kafka producer per partition
        - "serialize" TOP_N ((event_id, event,name), count) as json dict
        - send to kafka topic
    """
    producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                             bootstrap_servers=['localhost:9092'])
    records = dict(list(partition))
    records = Counter(records)
    print("Recent Top sending:", json.dumps(records))
    producer.send('recent-top-topic', records)
    producer.flush()

    producer.close()

def send_response_count(partition):
    """for each partition, send recent top event name and count
        - sum count of each partition
        - send to kafka topic
    """
    counts = dict(partition)
    if len(counts) == 0:
        return
    print("Counts: ", counts)

    producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                             bootstrap_servers=['localhost:9092'])

    sum_counts = counts.get(None, (0,0,0))
    to_send = {
        'yes': int(sum_counts[0]),
        'no': int(sum_counts[1]),
        'other': int(sum_counts[2])
    }
    print("Response Count sending: ", to_send)
    producer.send('response-count-topic', to_send)
    producer.flush()

    producer.close()


def send_rsvp_count(partition):
    """send rsvp count to kafka topic
    """
    # partition has only one count number
    count = list(partition)

    if len(count) == 0:
        return

    count = int(count[0])
    
    producer = KafkaProducer(value_serializer=lambda m: json.dumps(m).encode('utf-8'),
                             bootstrap_servers=['localhost:9092'])

    to_send = {'count': count}
    print("Recent Count sending: ", to_send)
    producer.send('recent-count-topic', to_send)
    producer.flush()
    producer.close()


def take_top_rdd(rdd):
    """ Per rdd:
        - sort rdd by count
        - taking TOP_N
        - discard the rest
    """

    top_n = rdd.sortBy(lambda pair: pair[1], ascending=False).take(TOP_N)
    return rdd.filter(lambda record: record in top_n)

def update_count(new_value, running_count):
    if running_count is None:
        running_count = np.array([0, 0, 0])
    if len(new_value) == 0:
        new_value = np.array([0, 0, 0])
    print("new_value: ", new_value)
    print("running_count: ", running_count)
    counts = np.vstack([new_value, running_count])
    sum_count = np.sum(counts, axis=0)
    return tuple(sum_count)


def main():

    zkQuorum = "localhost:2181"
    topic = "meetup-rsvps-topic"

    sc = SparkContext("local[*]")
    sc.setLogLevel("ERROR")
    ssc = StreamingContext(sc, BATCH_DUR) # 5 sec batch duration

    # utf-8 text stream from kafka
    kvs = KafkaUtils.createStream(ssc, zkQuorum, "spark_consumer", {topic: 1}).cache()

    # recent top N event stream
    event_count = kvs.map(extract_event_count).filter(lambda line: line is not None)
    event_count.reduceByKeyAndWindow(func=lambda x,y:x+y,
                                     invFunc=lambda x,y:x-y,
                                     windowDuration=WIN_DUR,
                                     slideDuration=SLIDE_DUR) \
                .filter(lambda pair: pair[1] > 0) \
                .transform(take_top_rdd) \
                .map(lambda pair: (pair[0][1], pair[1])) \
                .foreachRDD(lambda rdd: rdd.foreachPartition(send_recent_top))

    # running response count stream
    response_count = kvs.map(extract_response).filter(lambda line: line is not None)
    # TODO: may use countByValueAndWindow instead of updateStateByKey
    response_count.updateStateByKey(update_count) \
                  .foreachRDD(lambda rdd: rdd.foreachPartition(send_response_count))

    # count recent rsvps
    rsvp_count = kvs.countByWindow(windowDuration=WIN_DUR, slideDuration=SLIDE_DUR) \
                    .foreachRDD(lambda rdd: rdd.foreachPartition(send_rsvp_count))


    # event_count.pprint()
    ssc.checkpoint("rsvps_checkpoint_dir")
    ssc.start()
    ssc.awaitTermination()

if __name__ == '__main__':
    main()
