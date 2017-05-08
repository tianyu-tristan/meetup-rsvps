#!/usr/bin/env python3
from kafka import KafkaConsumer
import json
import os
import yaml
from stream_charts import StreamCharts
import numpy as np
import time

MIN_TICK = 3 # sec, less than this will not update plotly

class SingetonChart(StreamCharts):
    __instance = None
    def __new__(cls, chart_type, window_size=20):
        if SingetonChart.__instance is None:
            SingetonChart.__instance = StreamCharts(chart_type, window_size)
        return SingetonChart.__instance

def main():

    # To consume latest messages and auto-commit offsets
    consumer = KafkaConsumer('response-count-topic',
                             group_id='response-count-consumer',
                             bootstrap_servers=['localhost:9092'],
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    chart = SingetonChart(chart_type='pie')

    print("consumer started ...")

    for message in consumer:
        # get new_x and new_y as 1D list
        record = message.value
        print("Received: ", record)
        if len(record) == 0:
            continue
#        continue

        x_to_plot = record.keys()
        y_to_plot = record.values()

        # only update plotly at min interval of MIN_TICK
        if time.time() - last_update > MIN_TICK:
            print("x to plot: ", x_to_plot)
            print("y to plot: ", y_to_plot)
            chart.update(chart_type='pie',
                         x_labels=x_to_plot,
                         y_values=y_to_plot)
            last_update = time.time()


if __name__ == '__main__':
    main()
