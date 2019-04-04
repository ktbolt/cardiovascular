
test_name="compute_centerlines"
test_name="wall_props"
test_name="read_centerlines"

if [ $test_name  == "compute_centerlines" ]; then

    python3 generate-1d-mesh.py \
        --output-directory $PWD/output \
        --boundary-surfaces-directory example/mesh-surfaces \
        --compute-centerlines \
        --surface-model example/SU201_2005_RPA1_exterior.vtp \
        --centerlines-output-file output/centerlines.vtp 

elif [ $test_name  == "read_centerlines" ]; then

    python3 generate-1d-mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file output/centerlines.vtp 

elif [ $test_name  == "wall_props" ]; then
    python3 generate-1d-mesh.py \
        --output-directory $PWD/output \
        --centerlines-input-file output/centerlines.vtp \
        --wall-properties-input-file example/SU201_2005_RPA1_wallprop.vtp \
        --wall-properties-output-file output/wall_prop_grouped.vtp

fi


