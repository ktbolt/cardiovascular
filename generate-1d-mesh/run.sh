
test_name="wall_props"
test_name="read_centerlines"
test_name="compute_mesh"
test_name="compute_centerlines"

test_name="write_solver_file"
test_name="resistance_bc"

python=python3
python=python

## Write a 1D solver input file.
#
# Centerlines are read from a file.
# 
if [ $test_name  == "write_solver_file" ]; then

    cl_file=~/centerlines.vtp
    inflow_file=$PWD/input/inflow.flow
    outlet_face_names_file=$PWD/input/outlet_face_names.dat
    outflow_bc_input_file=$PWD/input/rcrt.dat

    # This should match the example results.
    cl_file=example/SU201_2005_RPA1_cl.vtp
    inflow_file=$PWD/input/inflow.flow
    outlet_face_names_file=$PWD/input/outlet_face_names_ex.dat
    outflow_bc_input_file=$PWD/input/rcrt_ex.dat

    ${python} generate_1d_mesh.py \
        --model-name SU201_2005 \
        --output-directory $PWD/output \
        --units mm \
        --centerlines-input-file ${cl_file} \
        --outlet-face-names-input-file ${outlet_face_names_file} \
        --uniform-bc false \
        --inflow-input-file ${inflow_file} \
        --outflow-bc-type rcr \
        --outflow-bc-input-file ${outflow_bc_input_file} \
        --write-solver-file   \
        --solver-output-file solver.in

## Resistance bc. 
#
elif [ $test_name  == "resistance_bc" ]; then

    cl_file=example/SU201_2005_RPA1_cl.vtp
    inflow_file=$PWD/input/inflow.flow
    outlet_face_names_file=$PWD/input/outlet_face_names.dat
    outflow_bc_input_file=$PWD/input/resistance.dat

    cl_file=~/centerlines.vtp
    inflow_file=$PWD/input/inflow.flow
    outlet_face_names_file=$PWD/input/outlet_face_names.dat
    outflow_bc_input_file=$PWD/input/resistance.dat

    ${python} generate_1d_mesh.py \
        --model-name SU201_2005 \
        --output-directory $PWD/output \
        --units mm \
        --centerlines-input-file ${cl_file} \
        --outlet-face-names-input-file ${outlet_face_names_file} \
        --uniform-bc false \
        --inflow-input-file ${inflow_file} \
        --outflow-bc-type resistance \
        --outflow-bc-input-file ${outflow_bc_input_file} \
        --num-time-steps '2000' \
        --write-solver-file   \
        --solver-output-file solver.in

## Just compute centerlines.
#
elif [ $test_name  == "compute_centerlines" ]; then

    surfaces_dir=/home/davep/Simvascular/DemoProject/Simulations/demojob/mesh-complete/mesh-surfaces
    surface_model=/home/davep/Simvascular/DemoProject/Simulations/demojob/mesh-complete/mesh-complete.exterior.vtp
    inlet_file=cap_aorta.vtp

    surfaces_dir=example/mesh-surfaces
    surface_model=example/SU201_2005_RPA1_exterior.vtp
    inlet_file=inflow.vtp

    ${python} generate_1d_mesh.py \
        --model-name SU201_2005 \
        --boundary-surfaces-directory ${surfaces_dir} \
        --inlet-face-input-file ${inlet_file} \
        --surface-model ${surface_model} \
        --output-directory $PWD/output \
        --compute-centerlines \
        --centerlines-output-file output/centerlines.vtp  \
        --write-solver-file   \
        --solver-output-file solver.in

## Read centerlines.
#
elif [ $test_name  == "read_centerlines" ]; then

    cl_file=example/SU201_2005_RPA1_cl.vtp

    ${python} generate_1d_mesh.py \
        --model-name SU201_2005 \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --write-solver-file   \
        --solver-output-file solver.in

elif [ $test_name  == "wall_props" ]; then
    cl_file=example/SU201_2005_RPA1_cl.vtp
    ${python} generate_1d_mesh.py \
        --model-name SU201_2005 \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --wall-properties-input-file example/SU201_2005_RPA1_wallprop.vtp \
        --wall-properties-output-file output/wall_prop_grouped.vtp \
        --write-solver-file   \
        --solver-output-file solver.in

# Compute mesh only.
#
elif [ $test_name  == "compute_mesh" ]; then
    ${python} generate_1d_mesh.py \
        --model-name SU201_2005 \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --compute-mesh \
        --write-mesh-file \
        --mesh-output-file mesh1d.vtp

fi


