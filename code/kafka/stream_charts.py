#!/usr/bin/env python3
# plotting libraries
import plotly
import plotly.plotly as py
import plotly.tools as tls
import plotly.graph_objs as go
import numpy as np
import yaml
from os.path import expanduser

class StreamCharts(object):
    def __init__(self, chart_type, window_size=20):
        """
        INPUT:
            - chart_type: 'line', 'pie', 'bar'
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
        credentials = yaml.load(open(expanduser('tristan_cred.yml')))
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
                    name='Dynamic Bar',
                    stream=go.Stream(token=self.ids['bar'], maxpoints=80),
                    showlegend=False
                ),
                'title': 'Moving Bar',
                'filename': 'bar-streaming'
            }
        }
        self.WIN_SIZE = window_size
        self.streams = {}
        self.chart_url = None

        # self.init_interview_stream()
        self.init_stream(chart_type=chart_type)

    def init_stream(self, chart_type=None):
        # Read params
        stream_id=self.traces[chart_type]['stream_id']
        trace = self.traces[chart_type]['trace']
        title = self.traces[chart_type]['title']
        filename = self.traces[chart_type]['filename']

        # prepare data
        data = go.Data([trace])

        # Add title to layout object
        layout = go.Layout(title=title)

        # Make a figure object
        fig = go.Figure(data=data, layout=layout)

        # Send fig to Plotly, initialize streaming plot, open new tab
        url = py.plot(fig, filename=filename, auto_open=False)

        s = py.Stream(stream_id)
        s.open()

        # TODO: now support only one chart per type
        self.streams[chart_type] = s

        self.chart_url = url


    def update(self, chart_type, x_labels, y_values):
        x = np.array(x_labels)[-self.WIN_SIZE:]
        y = np.array(y_values)[-self.WIN_SIZE:]
        self.streams[chart_type].write(dict(x=x, y=y, marker=dict(color="blue"), type='bar'))


    def close():
        """Close when done
        """
        for stream in self.streams.values():
            stream.close()
        # self.stream_bar.close()
        # self.stream_line.close()


def main():
    import datetime
    import time

    # Delay start of stream by 5 sec (time to switch tabs)
    time.sleep(5)

    chart = StreamCharts(chart_type='bar', window_size=20)
    print("URL: ",chart.chart_url)
    print("Streams:", chart.streams)
    while True:
        ###### replace x_label by question name #######
        # x_label = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        x_label = 'tristan'
        ###### replace y_value by score between [-10, 10] #######
        y_value = np.random.random_integers(-10,10, size=1)[0]
        print("x_label: ",x_label)
        print("y_value: ",y_value)
        chart.update('bar', x_labels=[x_label], y_values=[y_value])
        time.sleep(1)  # plot a point every second

    # Close the stream when done plotting
    chart.close()


if __name__ == '__main__':
    main()
