
test_name="aorta.vti"

python=python
python=python3

if [ $test_name  == "aorta.vti" ]; then
    image_file=aorta.vti 
    path_file=aorta.pth 
    ${python} slice-image.py \
        --image-file ${image_file}  \
        --path-file ${path_file} 

fi


