
# Example of how to specify the arguments needed by create-flow-files program.

../build/create-flow-files \
  --mesh-directory $HOME/SimVascular/CylinderProject/Simulations/steady/mesh-complete/mesh-surfaces \
  --output-directory $HOME/software/ktbolt/cardiovascular/create-flow-files/test \
  --results-directory  $HOME/SimVascular/CylinderProject/Simulations/steady/4-procs_case/steady-converted-results \
  --single-file no \
  --skip-walls yes \
  --units cm

