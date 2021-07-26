
test_name="aorta-dicom.vti"
test_name="aorta-vti-from-dicom.vti"
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

elif [ $test_name  == "aorta-dicom.vti" ]; then
    header_file=aorta-dicom.vti.hdr
    image_file=aorta-dicom.vti 
    path_file=aorta-dicom.pth 
    ${python} slice-image.py \
        --header-file ${header_file}  \
        --image-file ${image_file}  \
        --path-file ${path_file} 

elif [ $test_name  == "aorta-vti-from-dicom.vti" ]; then
    header_file=aorta-vti-from-dicom.vti.hdr
    image_file=aorta-vti-from-dicom.vti 
    path_file=aorta-vti-from-dicom.pth 
    ${python} slice-image.py \
        --header-file ${header_file}  \
        --image-file ${image_file}  \
        --path-file ${path_file} 

fi


