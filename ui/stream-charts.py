#!/usr/bin/env python3
# plotting libraries
import matplotlib.pyplot as plt
import plotly
import plotly.plotly as py
from plotly.graph_objs import *

import plotly.tools as tls
import plotly.graph_objs as go
import yaml
from os.path import expanduser

class StreamCharts(object):
    def __init__(self):
        # 2 stream id
        # api_cred.yml looks like this:
        # plotly:
        #     username: xxxx
        #     api_key: xxxx
        #     stream_ids:
        #         - xxxx
        #         - xxxx
        #         - xxxxx
        credentials = yaml.load(open(expanduser('tmp_cred.yml')))
        plotly.tools.set_credentials_file(**credentials['plotly']) # plotly credentials

        stream_ids = tls.get_credentials_file()['stream_ids']

        self.ids = {
            'line': stream_ids[0],
            'pie': stream_ids[1],
            'bar': stream_ids[2]
        }
        self.traces = {
            'line': {
                'stream_id': self.ids['line'],
                'trace': go.Scatter(
                    x=[],
                    y=[],
                    mode='lines+markers',
                    stream=go.Stream(token=self.ids['line'], maxpoints=80)
                ),
                'title': 'Time Series',
                'filename': 'line-streaming'
            },
            'pie': {
                'stream_id': self.ids['pie'],
                'trace': go.Pie(
                    labels=['one','two','three'],
                    values=[20,50,100],
                    domain=dict(x=[0, 1]),
                    text=['one', 'two', 'three'],
                    stream=go.Stream(token=self.ids['pie'], maxpoints=80),
                    sort=False
                ),
                'title': 'Moving Pie',
                'filename': 'pie-streaming'
            },
            'bar': {
                'stream_id': self.ids['bar'],
                'trace': go.Bar(
                    x=['one', 'two', 'three'],
                    y=[4, 3, 2],
                    xaxis='x2',
                    yaxis='y2',
                    marker=dict(color="maroon"),
                    name='Random Numbers',
                    stream=go.Stream(token=self.ids['bar'], maxpoints=80),
                    showlegend=False
                ),
                'title': 'Moving Bar',
                'filename': 'bar-streaming'
            }
        }

    def init_stream(self, chart_type=None):

        stream_id=self.traces[chart_type]['stream_id']
        trace = self.traces[chart_type]['trace']
        title = self.traces[chart_type]['title']
        filename = self.traces[chart_type]['filename']

        data = go.Data([trace])

        # Add title to layout object
        layout = go.Layout(title=title)

        # Make a figure object
        fig = go.Figure(data=data, layout=layout)

        # Send fig to Plotly, initialize streaming plot, open new tab
        url = py.plot(fig, filename=filename, auto_open=False)

        s = py.Stream(stream_id)
        s.open()

        return s, url

def main():
    import datetime
    import time
    import numpy as np

    i = 0    # a counter
    k = 5    # some shape parameter

    # create stream
    s_line, url_line = StreamCharts().init_stream(chart_type='line')
    s_pie, url_pie = StreamCharts().init_stream(chart_type='pie')
    s_bar, url_bar = StreamCharts().init_stream(chart_type='bar')
    # Delay start of stream by 5 sec (time to switch tabs)
    time.sleep(5)

    print("line URL:", url_line)
    print("pie URL:", url_pie)
    print("bar URL:", url_bar)

    while True:
        ## write line
        x = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        y = (np.cos(k*i/50.)*np.cos(i/50.)+np.random.randn(1))[0]
        s_line.write(dict(x=x, y=y))

        nums = np.random.random_integers(0,10, size=(3))
        ## write pie
        s_pie.write(dict(labels=['one', 'two', 'three'], values=nums, type='pie'))

        ## write bar
        s_bar.write(dict(x=['one', 'two', 'three'], y=nums, marker=dict(color=["blue", "orange", "green"]), type='bar'))

        time.sleep(1)  # plot a point every second
    # Close the stream when done plotting
    s.close()


if __name__ == '__main__':
    main()
