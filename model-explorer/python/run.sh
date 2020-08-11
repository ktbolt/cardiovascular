
test_name="merged-vertices.stl"
test_name="stl-model.vtp"

python=python
python=python3

if [ $test_name  == "stl-model.vtp" ]; then
    model_file=mv-4.vtp
    model_file=stl-model.vtp
    ${python} model_explorer.py     \
        --model-file ${model_file}  \
        --filter-faces 2            \
        --show-edges True  

elif [ $test_name  == "merged-vertices.stl" ]; then
    model_file=demo.stl
    model_file=merged-vertices.stl
    ${python} model_explorer.py     \
        --model-file ${model_file} \
        --use-feature-angle true \
        --angle 40.0              \
        --show-faces 2 

fi



