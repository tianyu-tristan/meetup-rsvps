#!/bin/bash
for plotly in $(ls /vagrant/plotly_*)
do
    python3 $plotly &
done
