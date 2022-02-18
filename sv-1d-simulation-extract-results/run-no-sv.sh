#!/bin/bash

# This shell script is used to execute a Python script to convert 
# solver 1d files to csv format. 

# Set the Python interpreter if the default it not Python 3.
python=python
python=python3

export PYTHONPATH=$PYTHONPATH:/Applications/SimVascular.app/Contents/Resources/Python3.5/site-packages

## Set input parameters
#
res_dir=./example
res_dir=$HOME/SimVascular/sim-1d-SU201_2005-resistance/Simulations1d/su201/
res_dir=$HOME/SimVascular/sim-1d-demo-rom/ROMSimulations/demo/
solver_file=solver_1d.in
#
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
time_range="\"0.4,4.0\""

test_name="named_segments"
test_name="all_segments"
test_name="selected_segments"
test_name="outlet_segments"

## Plot and write results at named segment outlets.
#
if [ $test_name  == "named_segments" ]; then

    data_names="flow,pressure"
    data_names="flow"
    segments="Group0_Seg0,Group1_Seg1"
    segments="aorta_7,left_internal_iliac_13"

    ${python} -m sv_rom_extract_results.extract_results  \
        --results-directory ${res_dir}   \
        --solver-file-name ${solver_file}\
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

    ${python} -m sv_rom_extract_results.extract_results  \
        --model-order 1                  \
        --results-directory ${res_dir}   \
        --solver-file-name ${solver_file}\
        --display-geometry ${disp_geom}  \
        --node-sphere-radius ${radius}   \
        --plot ${plot}                   \
        --outlet-segments                \
        --data-names ${data_names}       \
        --time-range ${time_range}       \
        --output-directory ${out_dir}    \
        --output-file-name ${out_file}   \
        --output-format ${out_format}

elif [ $test_name  == "all_segments" ]; then

    data_names="flow,pressure"
    all_segs="true"

    ${python} -m sv_rom_extract_results.extract_results  \
        --results-directory ${res_dir}   \
        --solver-file-name ${solver_file}       \
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


