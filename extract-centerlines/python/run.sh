
export PATH="/Users/parkerda/vmtk/bin:$PATH"

test_name="demo"
#test_name="Kawasaki_Disease_Patient_2"

python=python
#python=python3

if [ $test_name  == "Kawasaki_Disease_Patient_2" ]; then

    surface_file=Kawasaki_Disease_Patient_2.vtp

    ${python} extract_centerlines.py \
        --surface-file ${surface_file} \
        --source-face-ids 16               \
        --target-face-ids "9, 10, 11, 12, 13, 14, 15, 17"

elif [ $test_name  == "Collateral" ]; then

    surface_file=Collateral.vtp

    ${python} extract_centerlines.py \
        --surface-file ${surface_file} \
        --source-face-ids "4, 5"      \
        --target-face-ids "9, 2, 12, 8, 10, 3"

elif [ $test_name  == "demo" ]; then

    surface_file=demo.vtp

    ${python} extract_centerlines.py \
        --surface-file ${surface_file} \
        --source-face-ids "3"      \
        --target-face-ids "4, 5"

fi

