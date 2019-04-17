
cl_file=/home/davep/software/ktbolt/cardiovascular/generate-1d-mesh/output/centerlines.vtp
# Can't use Merged_Centerlines.vtp.
#cl_file=/home/davep/Simvascular/sim-1d-demo/Models/Merged_Centerlines.vtp
cl_file=/home/davep/Simvascular/sim-1d-demo/Models/Full_Centerlines.vtp
cl_file=example/SU201_2005_RPA1_cl.vtp

surfaces_dir=/home/davep/Simvascular/DemoProject/Simulations/demojob/mesh-complete/mesh-surfaces
surfaces_dir=example/mesh-surfaces

inlet_file=cap_aorta.vtp
inlet_file=inflow.vtp

inflow_file=inflow.flow

surface_model=/home/davep/Simvascular/DemoProject/Simulations/demojob/mesh-complete/mesh-complete.exterior.vtp
surface_model=example/SU201_2005_RPA1_exterior.vtp

test_name="wall_props"
test_name="read_centerlines"
test_name="compute_mesh"
test_name="compute_centerlines"
test_name="write_solver_file"

if [ $test_name  == "compute_centerlines" ]; then

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

    python generate_1d_mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --write-solver-file   \
        --solver-output-file solver.in

elif [ $test_name  == "wall_props" ]; then
    python generate_1d_mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --wall-properties-input-file example/SU201_2005_RPA1_wallprop.vtp \
        --wall-properties-output-file output/wall_prop_grouped.vtp \
        --write-solver-file   \
        --solver-output-file solver.in

elif [ $test_name  == "write_solver_file" ]; then
    python generate_1d_mesh.py \
        --output-directory $PWD/output \
        --units mm \
        --centerlines-input-file ${cl_file} \
        --user-outlet-face-names-file $PWD/example/outlets.dat \
        --uniform-bc false \
        --outflow-bc-type rcr \
        --inflow-input-file ${inflow_file} \
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


