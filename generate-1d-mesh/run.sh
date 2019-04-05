
test_name="compute_centerlines"
test_name="wall_props"
test_name="read_centerlines"

cl_file=example/SU201_2005_RPA1_cl.vtp

if [ $test_name  == "compute_centerlines" ]; then

    python generate-1d-mesh.py \
        --output-directory $PWD/output \
        --boundary-surfaces-directory example/mesh-surfaces \
        --compute-centerlines \
        --surface-model example/SU201_2005_RPA1_exterior.vtp \
        --centerlines-output-file output/centerlines.vtp  \
        --solver-output-file mesh.in

elif [ $test_name  == "read_centerlines" ]; then

    python generate-1d-mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \
        --solver-output-file mesh.in

elif [ $test_name  == "wall_props" ]; then
    python generate-1d-mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file ${cl_file} \ 
        --wall-properties-input-file example/SU201_2005_RPA1_wallprop.vtp \
        --wall-properties-output-file output/wall_prop_grouped.vtp \
        --solver-output-file mesh.in

fi


