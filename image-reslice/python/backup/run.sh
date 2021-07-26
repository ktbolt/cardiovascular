
test_name="aorta.vti"

python=python
python=python3

if [ $test_name  == "aorta.vti" ]; then
    header_file=aorta.vti.hdr
    image_file=aorta.vti 
    path_file=aorta.pth 
    ${python} slice-image.py \
        --header-file ${header_file}  \
        --image-file ${image_file}  \
        --path-file ${path_file} 

fi


