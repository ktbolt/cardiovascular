#!/bin/bash

## Set input parameters
#
res_dir=./example
file=solver.in
res_dir=/home/davep/tmp/1d-solver
file=12_AortoFem_Pulse_R.in

## Set output parameters.
#
out_dir=./output
out_file=1dsolver
out_format=csv

#disp_geom="on"
disp_geom="off"
radius="0.1"

plot="on"
time_range="0.0,0.8"

python_int=python
python_int=python3

test_name="all_outlets"
test_name="named_segment_outlets"

## Plot and write results at named segment outlets.
#
if [ $test_name  == "named_segment_outlets" ]; then

    data_names="flow,pressure"
    data_names="flow"
    segments="Group0_Seg0,Group1_Seg1"
    segments="aorta_7"
    data_loc="outlet"

    ${python_int} extract_results.py     \
        --results-directory ${res_dir}   \
        --solver-file-name ${file}       \
        --display-geometry ${disp_geom}  \
        --node-sphere-radius ${radius}   \
        --plot ${plot}                   \
        --segments ${segments}           \
        --data-names ${data_names}       \
        --time-range ${time_range}       \
        --output-directory ${out_dir}    \
        --output-file-name ${out_file}   \
        --output-format ${out_format}

elif [ $test_name  == "all_outlets" ]; then

    data_names="flow,pressure"

    ${python_int} extract_results.py     \
        --results-directory ${res_dir}   \
        --solver-file-name ${file}       \
        --display-geometry ${disp_geom}  \
        --node-sphere-radius ${radius}   \
        --plot ${plot}                   \
        --data-names ${data_names}       \
        --time-range ${time_range}       \
        --output-directory ${out_dir}    \
        --output-file-name ${out_file}   \
        --output-format ${out_format}

fi



