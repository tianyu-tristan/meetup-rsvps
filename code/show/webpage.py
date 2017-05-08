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

    return render_template('webpage.html',
                            bar_embed='https://plot.ly/~mosquitou/15.embed',
                            pie_embed='https://plot.ly/~mosquitou/11.embed',
                            line_embed='https://plot.ly/~mosquitou/9.embed',
                            timestamp=time.time())


if __name__ == '__main__':
    app.run("0.0.0.0",port=80)
