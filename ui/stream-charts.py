#!/usr/bin/env python3
# plotting libraries
import matplotlib.pyplot as plt
import plotly
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
import numpy as np
import yaml
from os.path import expanduser

class StreamCharts(object):
    def __init__(self, window_size=20):
        """
        INPUT:
            - window_size: how many data points to keep track of
        """
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
                    marker=dict(color="black"),
                    stream=go.Stream(token=self.ids['line'], maxpoints=80),
                    name='Average Score',
                    showlegend=False
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
                    x=[],
                    y=[],
                    # xaxis='x2',
                    # yaxis='y2',
                    marker=dict(color="green"),
                    name='Sentiment Score',
                    stream=go.Stream(token=self.ids['bar'], maxpoints=80),
                    showlegend=False
                ),
                'title': 'Moving Bar',
                'filename': 'bar-streaming'
            }
        }
        self.x = np.array([]) # list of x labels
        self.y = np.array([]) # list of y values
        self.y_mean = np.array([]) # list of y.mean()
        self.WIN_SIZE = window_size
        self.stream_line = None
        self.stream_bar = None
        self.chart_url = None

        self.init_interview_stream()

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

    def init_interview_stream(self):
        """initialize stream object of interview sentiment
        INPUT: None
        OUTPUT:
            - s_line: line stream object
            - s_bar: bar stream object
            - url: url to the plotly graph
        """

        s_line_id=self.traces['line']['stream_id']
        s_bar_id=self.traces['bar']['stream_id']

        trace_line = self.traces['line']['trace']
        trace_bar = self.traces['bar']['trace']

        title = 'Performance Metrics'
        filename = 'perf-metric'

        data = go.Data([trace_line, trace_bar])

        # Send fig to Plotly, initialize streaming plot, open new tab
        url = py.plot(data, filename=filename, auto_open=False)

        self.stream_line = py.Stream(s_line_id)
        self.stream_bar = py.Stream(s_bar_id)
        self.stream_line.open()
        self.stream_bar.open()
        self.chart_url = url

    def update(self, x_label, y_value):
        """Update streaming chart
        INPUT:
            - x_label: the x axis label (e.g. "Question1")
            - y_value: the y axis value (e.g. between -10, 10)
        """
        self.x = np.append(self.x, x_label)[-self.WIN_SIZE:]
        self.y = np.append(self.y, y_value)[-self.WIN_SIZE:]
        self.y_mean = np.append(self.y_mean, self.y.mean())[-self.WIN_SIZE:]

        color = ["green" if positive else "red" for positive in self.y > 0]

        self.stream_bar.write(dict(x=self.x, y=self.y, marker=dict(color=color), type='bar'))
        self.stream_line.write(dict(x=self.x, y=self.y_mean))

    def close():
        """Close when done
        """
        self.stream_bar.close()
        self.stream_line.close()

def main():
    import datetime
    import time

    # Delay start of stream by 5 sec (time to switch tabs)
    time.sleep(5)

    chart = StreamCharts(window_size=20)
    print("URL: ",chart.chart_url)
    while True:
        ###### replace x_label by question name #######
        x_label = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        ###### replace y_value by score between [-10, 10] #######
        y_value = np.random.random_integers(-10,10, size=1)

        chart.update(x_label=x_label, y_value=y_value)
        time.sleep(1)  # plot a point every second

    # Close the stream when done plotting
    chart.close()


if __name__ == '__main__':
    main()
