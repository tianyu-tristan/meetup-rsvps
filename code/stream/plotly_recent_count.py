#!/usr/bin/env python3
from kafka import KafkaConsumer
import json
import os
import yaml
from stream_charts import StreamCharts
import numpy as np
import time

WIN_SIZE = 10
MIN_TICK = 3 # sec, less than this will not update plotly

class SingetonChart(StreamCharts):
    __instance = None
    def __new__(cls, chart_type, window_size=20):
        if SingetonChart.__instance is None:
            SingetonChart.__instance = StreamCharts(chart_type, window_size)
        return SingetonChart.__instance

def main():

    # To consume latest messages and auto-commit offsets
    consumer = KafkaConsumer('recent-count-topic',
                             group_id='recent-count-consumer',
                             bootstrap_servers=['localhost:9092'],
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    chart = SingetonChart(chart_type='line')

    print("Line Chart consumer started ...")
    print("chart url: ", chart.chart_url)

    x_to_plot = np.array([])
    y_to_plot = np.array([])

    last_update = time.time()

    for message in consumer:
        # get new_x and new_y as 1D list
        record = message.value
        print("Received: ", record)
        if len(record) == 0:
            continue
#        continue

        count = record['count']
        timestamp = time.strftime('%b-%d %H:%M:%S')

        x_to_plot = np.append(x_to_plot, timestamp)[-WIN_SIZE:]
        y_to_plot = np.append(y_to_plot, count)[-WIN_SIZE:]

        # only update plotly at min interval of MIN_TICK
        if time.time() - last_update > MIN_TICK:
            print("x to plot: ", x_to_plot)
            print("y to plot: ", y_to_plot)
            chart.update(chart_type='line',
                         x_labels=x_to_plot,
                         y_values=y_to_plot)
            last_update = time.time()


if __name__ == '__main__':
    main()
