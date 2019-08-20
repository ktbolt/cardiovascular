#!/bin/bash

# This shell script is used to execute a Python script to generate an 
# input file for the 1D solver.
#
# The example problem is a vessel network with five branches. Resistance 
# boundary conditions are used for the vessel outlets.

# Set the Python interpreter if the default it not Python 3.
python=python3

# Augment the default search path for module files. 
export PYTHONPATH=$PYTHONPATH:/Users/parkerda/software/ktbolt/cardiovascular/sv-1d-simulation/sv_1d_simulation

## Files containing data input to the Python script.
#
input_dir=$PWD/example/input
output_dir=$PWD/example/output

cl_file=$input_dir/centerlines.vtp
inflow_file=$input_dir/inflow.flow
outlet_face_names_file=$input_dir/outlet_face_names.dat
outflow_bc_input_file=$input_dir/resistance.dat

## Execute the Python script as a module.
#
${python} -m sv_1d_simulation.generate_1d_mesh \
    --model-name SU201_2005 \
    --output-directory $output_dir \
    --units cm \
    --centerlines-input-file ${cl_file} \
    --outlet-face-names-input-file ${outlet_face_names_file} \
    --uniform-bc false \
    --inflow-input-file ${inflow_file} \
    --material-model OLUFSEN \
    --olufsen-material-k1 0.0 \
    --olufsen-material-k2 -22.5267 \
    --olufsen-material-k3 10000000.0 \
    --olufsen-material-exp 1.0 \
    --olufsen-material-pressure 0.0 \
    --density 1.07 \
    --viscosity 0.041 \
    --outflow-bc-type resistance \
    --outflow-bc-input-file ${outflow_bc_input_file} \
    --num-time-steps '2000' \
    --write-solver-file   \
    --solver-output-file solver.in

