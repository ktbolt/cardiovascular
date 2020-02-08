#!/bin/bash

# This shell script is used to execute a Python script to convert 
# solver 1d files to csv format. 

# Set the Python interpreter if the default it not Python 3.
python=python
python=python3

## Set input parameters
#
res_dir=../example
file=solver.in
#

## Set output parameters.
#
out_dir=./output
out_file=1dsolver
out_format=csv

disp_geom="off"
radius="0.1"

plot="off"
time_range="0.01,0.8"

data_names="flow,pressure"
all_segs="true"

${python}  extract_results.py  \
        --results-directory ${res_dir}   \
        --solver-file-name ${file}       \
        --display-geometry ${disp_geom}  \
        --node-sphere-radius ${radius}   \
        --plot ${plot}                   \
        --all-segments                   \
        --data-names ${data_names}       \
        --time-range ${time_range}       \
        --output-directory ${out_dir}    \
        --output-file-name ${out_file}   \
        --output-format ${out_format}


