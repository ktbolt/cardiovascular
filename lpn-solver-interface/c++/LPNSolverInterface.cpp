#include "LPNSolverInterface.h"
#include <string>
#include <dlfcn.h>

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
//
void LPNSolverInterface::increment_time(const double time)
{
  lpn_increment_time_(problem_id_, time);
}

//------------
// initialize
//------------
// Initialze the solver.
//
void LPNSolverInterface::initialize(const char* file_name, const double time_step)
{
  lpn_initialize_(file_name, time_step, problem_id_);
  printf("[LPNSolverInterface::initialize] Problem ID: %d\n", problem_id_); 
}

//--------------
// load_library
//--------------
//
void LPNSolverInterface::load_library(const std::string& interface_lib)
{
  library_handle_ = dlopen(interface_lib.c_str(), RTLD_LAZY);

  if (!library_handle_) {
    fprintf(stderr, "Error: %s\n", dlerror());
    return;
  }

  // Get a pointer to the svzero 'initialize' function.
  //
  *(void**)(&lpn_initialize_) = dlsym(library_handle_, lpn_initialize_name_.c_str());
  if (!lpn_initialize_) {
    fprintf(stderr, "Error: %s\n", dlerror());
    dlclose(library_handle_);
    return;
  }

  // Get a pointer to the svzero 'increment_time' function.
  //
  *(void**)(&lpn_increment_time_) = dlsym(library_handle_, lpn_increment_time_name_.c_str());
  if (!lpn_increment_time_) {
    fprintf(stderr, "Error: %s\n", dlerror());
    dlclose(library_handle_);
    return;
  }
}
