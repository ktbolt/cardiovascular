
group=$1
segment=$2
data_name=$3

model_name=SU201_2005
comp_model_name=SU201_2005

if [ "$#" -eq 4 ]; then
    test_name="compare"
else
    test_name="single"
fi

if [ $test_name == "single" ]; then

    python3 vis_results.py \
        --output-directory $PWD/output \
        --model-name $model_name \
        --group ${group} \
        --segment ${segment} \
        --data-name ${data_name}

elif [ $test_name == "compare" ]; then

    python3 vis_results.py \
        --output-directory $PWD/output \
        --model-name $model_name \
        --group ${group} \
        --segment ${segment} \
        --data-name ${data_name} \
        --compare-output-directory $PWD/example \
        --compare-model-name ${comp_model_name} 

fi


