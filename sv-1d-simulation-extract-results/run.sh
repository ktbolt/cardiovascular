#!/bin/bash

out_dir=./example
file=solver.in

segments="Group0_Seg0"
data_name="flow"

python extract_results.py \
    --output-directory ${out_dir} \
    --solver-file-name ${file}    \
    --segments ${segments}        \
    --data-name ${data_name} 

