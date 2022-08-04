// Test LPNSolverInterface class for interfacing to a LPN solver. 
//
// Usage:
//
//   p SOLVER_JSON 

#include "LPNSolverInterface.h" 

#include <iostream>

//------
// main
//------
//
int main(int argc, char** argv)
{
  LPNSolverInterface interface;

  // Load shared library and get interface functions.
  auto interface_lib = std::string(std::getenv("LPN_SOLVER_LIBRARY"));
  std::cout << "[main] interface_lib: " << interface_lib << std::endl;
  interface.load_library(interface_lib);

  // Initialze the solver.
  const char* file_name = argv[1];
  double time_step = 0.01;
  interface.initialize(file_name, time_step);

  // Increment in time.
  int num_time_steps = 3001;
  double time = 0.0;
  std::vector<double> solution(interface.system_size_);

  for (int i = 0; i < num_time_steps; i++) {
    time += time_step;
    interface.increment_time(time, solution);
    std::cout << "[main] time: " << time << " solution: ";
    for (auto value : solution) {
      std::cout << value << " "; 
    }
    std::cout << std::endl;
  }

  return 0;
}
