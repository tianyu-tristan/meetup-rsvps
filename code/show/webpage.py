#!/usr/bin/env python3

import os
import yaml
from flask import render_template
from flask import Flask
import time

app = Flask(__name__)


@app.route('/')
def doit():
    '''
    '''

    return render_template('webpage.html', plotly_embed='https://plot.ly/~mosquitou2/0.embed', timestamp=time.time())


if __name__ == '__main__':
    app.run("0.0.0.0",port=80)
