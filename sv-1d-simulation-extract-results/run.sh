#!/bin/bash

## Set input parameters
#
res_dir=./example
file=solver.in
#
res_dir=/home/davep/tmp/1d-solver
file=12_AortoFem_Pulse_R.in
#
res_dir=/Users/parkerda/tmp/1d-sim-results/
file=12_AortoFem_Pulse_R.in

## Set output parameters.
#
out_dir=./output
out_file=1dsolver
out_format=csv

disp_geom="off"
disp_geom="on"
radius="0.1"

plot="on"
plot="off"
time_range="0.0,0.8"

python_int=python
python_int=python3

test_name="outlet_segments"
test_name="named_segments"
test_name="all_segments"

## Plot and write results at named segment outlets.
#
if [ $test_name  == "named_segments" ]; then

    data_names="flow"
    data_names="flow,pressure"
    segments="Group0_Seg0,Group1_Seg1"
    segments="aorta_7,left_internal_iliac_13"

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

elif [ $test_name  == "outlet_segments" ]; then

    data_names="flow,pressure"
    outlet_segs="true"

    ${python_int} extract_results.py     \
        --results-directory ${res_dir}   \
        --solver-file-name ${file}       \
        --display-geometry ${disp_geom}  \
        --node-sphere-radius ${radius}   \
        --plot ${plot}                   \
        --outlet-segments ${outlet_segs} \
        --data-names ${data_names}       \
        --time-range ${time_range}       \
        --output-directory ${out_dir}    \
        --output-file-name ${out_file}   \
        --output-format ${out_format}

elif [ $test_name  == "all_segments" ]; then

    data_names="flow,pressure"
    all_segs="true"

    ${python_int} extract_results.py     \
        --results-directory ${res_dir}   \
        --solver-file-name ${file}       \
        --display-geometry ${disp_geom}  \
        --node-sphere-radius ${radius}   \
        --plot ${plot}                   \
        --all-segments ${all_segs}       \
        --data-names ${data_names}       \
        --time-range ${time_range}       \
        --output-directory ${out_dir}    \
        --output-file-name ${out_file}   \
        --output-format ${out_format}
fi


