# This script is used to execute a Python script to convert solver 1d files to csv format. 

from sv_rom_extract_results import *

extract_results.run(
  centerlines_file="/Users/Shared/sim-1d-demo-rom/ROMSimulations/demo/centerlines.vtp",
  data_names="flow,pressure",
  model_order=1,
  outlet_segments=True,
  output_directory="/Users/Shared/sim-1d-demo-rom/ROMSimulations/demo/demo-converted-results_1d"
  output_file_name="demo",
  results_directory="/Users/Shared/sim-1d-demo-rom/ROMSimulations/demo",
  solver_file_name="solver_1d.in",
  time_range="0.0,2.001",
  volume_mesh_file="/Users/Shared/sim-1d-demo-rom/Simulations/sim-1/mesh-complete/mesh-complete.mesh.vtu",
  walls_mesh_file="/Users/Shared/sim-1d-demo-rom/Simulations/sim-1/mesh-complete/walls_combined.vtp",
)


