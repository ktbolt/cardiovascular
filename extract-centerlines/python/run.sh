
export PATH="/Users/parkerda/vmtk/bin:$PATH"

test_name="Kawasaki_Disease_Patient_2"

python=python
#python=python3

## Write a 1D solver input file.
#
# Centerlines are read from a file.
# 
if [ $test_name  == "Kawasaki_Disease_Patient_2" ]; then

    surface_file=Kawasaki_Disease_Patient_2.vtp

    ${python} extract_centerlines.py \
        --surface-file ${surface_file} \
        --source-face-ids 16               \
        --target-face-ids "9, 10, 11, 12, 13, 14, 15, 17"

fi



