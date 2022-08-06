
#include "LPNSolverInterface.h"

#include <iostream>
#include <map>

static std::string lpn_library;
static std::map<int,LPNSolverInterface*> blocks;

//--------------------
// lpn_interface_init
//--------------------
//
extern "C" void lpn_interface_init_(const char* lpn_library_name)
{
  std::cout << "[lpn_interface_init] " << std::endl;
  std::cout << "[lpn_interface_init] lpn_library: '" << lpn_library_name << "'" << std::endl;
  lpn_library = std::string(lpn_library_name);

}

//-------------------------
// lpn_interface_add_block
//-------------------------
//
extern "C" void lpn_interface_add_block_(const char* lpn_json_file, const double* time_step, int* block_id)
{
  auto block = new LPNSolverInterface();
  block->load_library(lpn_library);
  block->initialize(lpn_json_file, *time_step);
  *block_id = block->problem_id_;
  blocks[*block_id] = block;
}

//----------------------------
// lpn_interface_get_solution
//----------------------------
//
extern "C" void lpn_interface_get_solution_(const int* block_id, const double* time, double* solution)
{
  auto block = blocks[*block_id];
  std::vector<double> lpn_solution(block->system_size_);
  block->increment_time(*time, lpn_solution);

  for (int i = 0; i < lpn_solution.size(); i++) {
    solution[i] = lpn_solution[i];
  }
}

