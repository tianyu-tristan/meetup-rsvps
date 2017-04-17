#!/bin/bash

source activate de
export PYSPARK_DRIVER_PYTHON=`which jupyter`
export PYSPARK_DRIVER_PYTHON_OPTS="notebook"
pyspark
