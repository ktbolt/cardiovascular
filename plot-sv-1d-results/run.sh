
output_directory=$PWD/example
model_name=demo
segments="Group0_Seg0,Group2_Seg1,Group2_Seg2"
data_name=flow

python3 plot_results.py \
    --output-directory ${output_directory} \
    --model-name ${model_name} \
    --segments ${segments} \
    --data-name ${data_name}

