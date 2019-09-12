#!/bin/bash

## Set input parameters
#
res_dir=./example
file=solver.in
#
res_dir=$HOME/tmp/1d-solver
#res_dir=$HOME/tmp/1d-sim-results/
file=12_AortoFem_Pulse_R.in

## Set output parameters.
#
out_dir=./output
out_file=1dsolver
out_format=csv

radius="0.1"

time_range="0.0,0.8"

python_int=python
python_int=python3

test_name="named_segments"
test_name="outlet_segments"
test_name="all_segments"
test_name="selected_segments"

## Convert and plot results at named segment outlets.
#
if [ $test_name  == "named_segments" ]; then

    data_names="flow"
    data_names="flow,pressure"
    segments="Group0_Seg0,Group1_Seg1"
    segments="aorta_7,left_internal_iliac_13"
    disp_geom="off"
    plot="on"

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

## Convert only outlet segment data.
#
elif [ $test_name  == "outlet_segments" ]; then

    disp_geom="off"
    plot="on"
    data_names="flow,pressure"

    ${python_int} extract_results.py     \
        --results-directory ${res_dir}   \
        --solver-file-name ${file}       \
        --display-geometry ${disp_geom}  \
        --node-sphere-radius ${radius}   \
        --plot ${plot}                   \
        --outlet-segments                \
        --data-names ${data_names}       \
        --time-range ${time_range}       \
        --output-directory ${out_dir}    \
        --output-file-name ${out_file}   \
        --output-format ${out_format}

## Convert all segment data.
#
elif [ $test_name  == "all_segments" ]; then

    data_names="flow,pressure"
    plot="off"
    disp_geom="off"

    ${python_int} extract_results.py     \
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

## Interactively select segments to write.
#
# Need to set --all-segments to true to read in all segement data.
#
elif [ $test_name  == "selected_segments" ]; then

    echo "========== selected_segments =========="

    data_names="flow,pressure"
    disp_geom="on"

    ${python_int} extract_results.py     \
        --results-directory ${res_dir}   \
        --solver-file-name ${file}       \
        --display-geometry ${disp_geom}  \
        --node-sphere-radius ${radius}   \
        --all-segments                   \
        --select-segments                \
        --data-names ${data_names}       \
        --time-range ${time_range}       \
        --output-directory ${out_dir}    \
        --output-file-name ${out_file}   \
        --output-format ${out_format}

fi


