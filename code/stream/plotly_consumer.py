#!/usr/bin/env python3
from kafka import KafkaConsumer
import json
import os
import yaml
from stream_charts import StreamCharts
import numpy as np
import time

WIN_SIZE = 5 # ticks
MIN_TICK = 3 # sec, less than this will not update plotly

class SingetonChart(StreamCharts):
    __instance = None
    def __new__(cls, chart_type, window_size=WIN_SIZE):
        if SingetonChart.__instance is None:
            SingetonChart.__instance = StreamCharts(chart_type, window_size)
        return SingetonChart.__instance

def main():

    # To consume latest messages and auto-commit offsets
    consumer = KafkaConsumer('plotly-topic',
                             group_id='plotly-consumer',
                             bootstrap_servers=['localhost:9092'],
                             value_deserializer=lambda m: json.loads(m.decode('utf-8')))

    chart = SingetonChart(chart_type='bar', window_size=WIN_SIZE)

    print("consumer started ...")

    x_to_plot = np.array([]) # x_labels
    y_to_plot = np.array([]) # y_values

    last_update = time.time()

    for message in consumer:
        # get new_x and new_y as 1D list
        record = message.value
        print("Received: ", record)
        if len(record) == 0:
            continue
#        continue

        # only update plotly at min interval of MIN_TICK
        if time.time() - last_update > MIN_TICK:
            print("x to plot: ", x_to_plot)
            print("y to plot: ", y_to_plot)
            chart.update(chart_type='bar',
                         x_labels=x_to_plot,
                         y_values=y_to_plot)
            # clear *_to_plot
            x_to_plot = np.array([])
            y_to_plot = np.array([])


        # init new arrival
        new_x = np.array(list(record.keys()))
        new_y = np.array(list(record.values()))

        # append new arrival
        x_to_plot = np.append(x_to_plot, new_x)
        y_to_plot = np.append(y_to_plot, new_y)

        # dedup
        unique_ind = np.unique(x_to_plot, return_index=True)[1]
        x_to_plot = x_to_plot[unique_ind]
        y_to_plot = y_to_plot[unique_ind]

        # sort & get first WIN_SIZE items, with ascending=False
        ind = np.argsort(y_to_plot)[::-1][:WIN_SIZE]
        x_to_plot = x_to_plot[ind]
        y_to_plot = y_to_plot[ind]

        last_update = time.time()


if __name__ == '__main__':
    main()
