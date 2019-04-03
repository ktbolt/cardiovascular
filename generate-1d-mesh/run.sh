
test_name="compute_centerlines"
test_name="read_centerlines"

if [ $test_name  == "compute_centerlines" ]; then

    python3 generate-1d-mesh.py \
        --boundary-surfaces-directory example/mesh-surfaces \
        --compute-centerlines \
        --surface-model example/SU201_2005_RPA1_exterior.vtp \
        --centerlines-output-file output/centerlines.vtp 

elif [ $test_name  == "read_centerlines" ]; then

    python3 generate-1d-mesh.py \
        --centerlines-input-file output/centerlines.vtp 

fi


