
test_name="pressure"
test_name="compare_pressure"

if [ $test_name == "pressure" ]; then

    file_name=$PWD/output/modelGroup0_Seg0_pressure.dat

    python3 vis_results.py --file-name output/modelGroup0_Seg0_pressure.dat \
                           --data-name pressure

elif [ $test_name == "compare_pressure" ]; then

    file_name=$PWD/output/modelGroup0_Seg0_pressure.dat
    compare_file_name=$PWD/example/SU201_2005Group0_Seg0_pressure.dat 

    python3 vis_results.py --file-name ${file_name} \
                           --compare-file-name ${compare_file_name}  \
                           --data-name pressure

fi


