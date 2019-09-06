#!/bin/bash

res_dir=./example
file=solver.in

segments="Group0_Seg0,Group1_Seg1"

data_names="flow,pressure"
data_loc="outlets"

out_dir=./output
out_file=1dsolver
out_format=csv

python_int=python3

${python_int} extract_results.py   \
    --results-directory ${res_dir} \
    --solver-file-name ${file}     \
    --segments ${segments}         \
    --data-names ${data_names}     \
    --data-location ${data_loc}    \
    --output-directory ${out_dir}  \
    --output-file-name ${out_file} \
    --output-format ${out_format}

