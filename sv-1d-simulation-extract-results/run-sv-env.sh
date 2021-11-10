#!/bin/bash

# This shell script is used to execute a Python script to convert 
# solver 1d files to csv format. 

SV_HOME=/Users/parkerda/software/ktbolt/SimVascular/build/SimVascular-build/

# Set the Python interpreter if the default it not Python 3.
python=python
python=python3
python=/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/python-3.5.5/bin/python

export PATH=""

## Add env variables. 
#  
# Externals link directories
export DYLD_LIBRARY_PATH=/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/qt-5.11.3/5.11.3/clang_64/lib
export QT_QPA_FONTDIR=/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/qt-5.11.3/5.11.3/clang_64/plugins/../../Src/qtbase/lib/fonts
export QT_PLUGIN_PATH=/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/qt-5.11.3/5.11.3/clang_64/plugins
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/bin
export QT_PLUGIN_PATH=/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/qt-5.11.3/5.11.3/clang_64/plugins
# Plugins Path for Qt GUI
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:%SV_HOME%/bin/plugins
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/qt-5.11.3/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/qt-5.11.3/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/hdf5-1.10.1/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/hdf5-1.10.1/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/tinyxml2-6.2.0/lib/cmake/tinyxml2/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/tinyxml2-6.2.0/lib/cmake/tinyxml2/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/tcltk-8.6.4/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/tcltk-8.6.4/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/python-3.5.5/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/python-3.5.5/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/freetype-2.6.3/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/freetype-2.6.3/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/vtk-8.1.1/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/vtk-8.1.1/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/gdcm-2.6.3/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/gdcm-2.6.3/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/itk-4.13.2/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/itk-4.13.2/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/opencascade-7.3.0/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/opencascade-7.3.0/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/mitk-2018.04.2/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/mitk-2018.04.2/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/mitk-2018.04.2/lib/plugins

# Tcl environment variables
export TCL_LIBRARY=/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/tcltk-8.6.4/lib/tcl8.6
export TK_LIBRARY=/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/tcltk-8.6.4/lib/tk8.6
export TCLLIBPATH=/usr/local/Cellar/vtk/8.1.0/lib/tcltk/vtk-8.1/

# Python environment variables
export PYTHONHOME=/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/python-3.5.5
export HDF5_DISABLE_VERSION_CHECK=1
export PYTHONPATH=/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/python-3.5.5/lib/python3.5/site-packages
export PYTHONPATH=$PYTHONPATH:/Users/parkerda/software/ktbolt/SimVascular/build/Externals-build/svExternals/bin/vtk-8.1.1/lib/python3.5/site-packages
export PYTHONPATH=$PYTHONPATH:/Users/parkerda/software/ktbolt/SimVascular/Python/site-packages
export PYTHONPATH=$PYTHONPATH:$SV_PLUGIN_PATH

# SimVascular runtime locations
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/SimVascular-build/bin
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/SimVascular-build/lib/plugins
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/SimVascular-build/lib
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/SimVascular-build/bin/RelWithDebInfo
export DYLD_LIBRARY_PATH=$DYLD_LIBRARY_PATH:/Users/parkerda/software/ktbolt/SimVascular/build/SimVascular-build/bin/Release

## Set input parameters
#
res_dir=./example
res_dir=/Users/parkerda/SimVascular/sim-1d-SU201_2005-resistance/Simulations1d/su201/
res_dir=/Users/parkerda/SimVascular/sim-1d-demo-rom/ROMSimulations/demo/
solver_file=solver_1d.in
#
#res_dir=/home/davep/tmp/1d-solver
#file=12_AortoFem_Pulse_R.in
#
#res_dir=/Users/parkerda/tmp/1d-sim-results/
#file=12_AortoFem_Pulse_R.in
#
#res_dir=/Users/parkerda/tmp/1d-bif
#file=05_bifurcation_RCR.in
#
#res_dir=/Users/parkerda/SimVascular/sim-1d-SU201_2005-resistance/Simulations1d/su201/
#file=solver.in

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

    #${python} -m sv_rom_extract_results.extract_results  \

    ${python} -m sv_rom_extract_results.bob \
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


