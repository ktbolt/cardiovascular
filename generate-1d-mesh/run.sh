
test_name="wall_props"
test_name="read_centerlines"
test_name="compute_mesh"
test_name="compute_centerlines"
test_name="write_solver_file"

if [ $test_name  == "compute_centerlines" ]; then

    surfaces_dir=/home/davep/Simvascular/DemoProject/Simulations/demojob/mesh-complete/mesh-surfaces
    surface_model=/home/davep/Simvascular/DemoProject/Simulations/demojob/mesh-complete/mesh-complete.exterior.vtp
    inlet_file=cap_aorta.vtp

    surfaces_dir=example/mesh-surfaces
    surface_model=example/SU201_2005_RPA1_exterior.vtp
    inlet_file=inflow.vtp

    python generate_1d_mesh.py \
        --boundary-surfaces-directory ${surfaces_dir} \
        --inlet-face-input-file ${inlet_file} \
        --surface-model ${surface_model} \
        --output-directory $PWD/output \
        --compute-centerlines \
        --centerlines-output-file output/centerlines.vtp  \
        --write-solver-file   \
        --solver-output-file solver.in

elif [ $test_name  == "read_centerlines" ]; then

    cl_file=example/SU201_2005_RPA1_cl.vtp

    python generate_1d_mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --write-solver-file   \
        --solver-output-file solver.in

elif [ $test_name  == "wall_props" ]; then
    cl_file=example/SU201_2005_RPA1_cl.vtp
    python generate_1d_mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --wall-properties-input-file example/SU201_2005_RPA1_wallprop.vtp \
        --wall-properties-output-file output/wall_prop_grouped.vtp \
        --write-solver-file   \
        --solver-output-file solver.in

elif [ $test_name  == "write_solver_file" ]; then

    cl_file=example/SU201_2005_RPA1_cl.vtp
    inflow_file=$PWD/input/inflow.flow
    outlet_face_names_file=$PWD/input/outlet_face_names.dat
    outflow_bc_input_file=$PWD/input/rcrt.dat

    python generate_1d_mesh.py \
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

# Compute mesh only.
#
elif [ $test_name  == "compute_mesh" ]; then
    python generate_1d_mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --compute-mesh \
        --write-mesh-file \
        --mesh-output-file mesh1d.vtp

fi


