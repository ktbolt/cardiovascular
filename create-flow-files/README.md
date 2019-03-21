# Create Average Flow Files

This program is used to create average flow files from converted simulation results fileis (.vtp or .vtu).

The program creates the following files:

    all_results-pressures.txt
    results-flows.txt
    all_results-averages.txt
    all_results-averages-from_cm-to-mmHg-L_per_min.txt


## Example ##

create-flow-files --mesh-directory $HOME/SimVascular/CylinderProject/Simulations/steady/mesh-complete/mesh-surfaces  --output-directory $HOME/software/ktbolt/cardiovascular/create-flow-files/test  --results-directory  $HOME/SimVascular/CylinderProject/Simulations/steady/4-procs_case/steady-converted-results  --single-file no --skip-walls yes  --units cm
