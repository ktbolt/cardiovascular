
test_name="coronarytree.stl"
test_name="demo.vtp"
test_name="harfdmeshbetter_HDF5-sv-mesh.vtp"
test_name="Cylinder_HDF5-sv-mesh.vtp"

python=python
python=python3

if [ $test_name  == "coronarytree.stl" ]; then
    surface_file=coronarytree.stl
    ${python} extract_faces.py \
        --surface-file ${surface_file} \
        --use-feature-angle true \
        --angle 60.0               

elif [ $test_name  == "remove-faces.vtp" ]; then
    surface_file=remove-faces.vtp
    ${python} extract_faces.py \
        --surface-file ${surface_file} 

elif [ $test_name  == "Cylinder_HDF5-sv-mesh.vtp" ]; then
    surface_file=Cylinder_HDF5-sv-mesh.vtp
    ${python} extract_faces.py \
        --surface-file ${surface_file} \
        --use-feature-angle true \
        --angle 60.0               

elif [ $test_name  == "harfdmeshbetter_HDF5-sv-mesh.vtp" ]; then
    surface_file=harfdmeshbetter_HDF5-sv-mesh.vtp
    ${python} extract_faces.py \
        --surface-file ${surface_file} \
        --use-feature-angle true \
        --angle 60.0               

elif [ $test_name  == "demo.vtp" ]; then
    surface_file=demo.vtp
    ${python} extract_faces.py \
        --surface-file ${surface_file} \
        --use-feature-angle true \
        --angle 60.0               

fi


