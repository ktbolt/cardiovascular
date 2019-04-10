
cl_file=example/SU201_2005_RPA1_cl.vtp

test_name="compute_centerlines"
test_name="wall_props"
test_name="read_centerlines"
test_name="compute_mesh"

if [ $test_name  == "compute_centerlines" ]; then

    python generate-1d-mesh.py \
        --output-directory $PWD/output \
        --boundary-surfaces-directory example/mesh-surfaces \
        --compute-centerlines \
        --surface-model example/SU201_2005_RPA1_exterior.vtp \
        --centerlines-output-file output/centerlines.vtp  \
        --write-solver-file   \
        --solver-output-file mesh.in

elif [ $test_name  == "read_centerlines" ]; then

    python generate-1d-mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --write-solver-file   \
        --solver-output-file mesh.in

elif [ $test_name  == "wall_props" ]; then
    python generate-1d-mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \ 
        --wall-properties-input-file example/SU201_2005_RPA1_wallprop.vtp \
        --wall-properties-output-file output/wall_prop_grouped.vtp \
        --write-solver-file   \
        --solver-output-file mesh.in

# Compute mesh only.
#
elif [ $test_name  == "compute_mesh" ]; then
    python generate-1d-mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --compute-mesh \
        --write-mesh-file \
        --mesh-output-file mesh1d.vtp

fi


