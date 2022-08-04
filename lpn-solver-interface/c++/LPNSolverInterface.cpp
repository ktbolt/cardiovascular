#include "LPNSolverInterface.h"
#include <dlfcn.h>
#include <iostream>
#include <string>

//--------------------
// LPNSolverInterface
//--------------------
//
LPNSolverInterface::LPNSolverInterface()
{
  // Set the default names of the LPN interface functions.
  lpn_initialize_name_ = "initialize";
  lpn_increment_time_name_ = "increment_time";
}

LPNSolverInterface::~LPNSolverInterface()
{
  dlclose(library_handle_);
}

//----------------
// increment_time
//----------------
// Increment the LPN solution in time.
//
// Parameters:
//
//   time: The solution time.
//
//   solution: The returned LPN solution.
//
void LPNSolverInterface::increment_time(const double time, std::vector<double>& solution)
{
  lpn_increment_time_(problem_id_, time, solution);
}

//------------
// initialize
//------------
// Initialze the LPN solver.
//
// Parameters:
//
//   file_name: The name of the LPN configuration file (JSON).
//
//   time_step: The time step to use in the LPN simulation. 
//
void LPNSolverInterface::initialize(const char* file_name, const double time_step)
{
  lpn_initialize_(file_name, time_step, problem_id_, system_size_);
  std::cout << "[LPNSolverInterface::initialize] Problem ID: " << problem_id_ << std::endl;
  std::cout << "[LPNSolverInterface::initialize] System size: " << system_size_ << std::endl;
  solution_.resize(system_size_);
}

//--------------
// load_library
//--------------
// Load the LPN shared library and get pointers to its interface functions.
//
void LPNSolverInterface::load_library(const std::string& interface_lib)
{
  library_handle_ = dlopen(interface_lib.c_str(), RTLD_LAZY);

  if (!library_handle_) {
    std::cerr << "Error loading shared library '" << interface_lib << "'  with error: " << dlerror() << std::endl;
    return;
  }

  // Get a pointer to the svzero 'initialize' function.
  //
  *(void**)(&lpn_initialize_) = dlsym(library_handle_, lpn_initialize_name_.c_str());
  if (!lpn_initialize_) {
    std::cerr << "Error loading function '" << lpn_initialize_name_ << "'  with error: " << dlerror() << std::endl;
    dlclose(library_handle_);
    return;
  }

  // Get a pointer to the svzero 'increment_time' function.
  //
  *(void**)(&lpn_increment_time_) = dlsym(library_handle_, lpn_increment_time_name_.c_str());
  if (!lpn_increment_time_) {
    std::cerr << "Error loading function '" << lpn_increment_time_name_ << "'  with error: " << dlerror() << std::endl;
    dlclose(library_handle_);
    return;
  }
}
