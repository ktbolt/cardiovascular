
#include <dlfcn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string>
#include <vector>

#ifndef LPNSolverInterface_h
#define LPNSolverInterface_h

//--------------------
// LPNSolverInterface
//--------------------
//
class LPNSolverInterface
{
  public:
    LPNSolverInterface();
    ~LPNSolverInterface();

    void increment_time(const double time, std::vector<double>& solution);
    void initialize(const char* file_name, const double time_step);
    void load_library(const std::string& interface_lib);

    // Interface functions.
    //
    std::string lpn_initialize_name_;
    void (*lpn_initialize_)(const char*, const double, int&, int&);

    std::string lpn_increment_time_name_;
    void (*lpn_increment_time_)(const int, const double, std::vector<double>& solution);

    void* library_handle_ = nullptr;
    int problem_id_ = 0;
    int system_size_ = 0;
    std::vector<double> solution_;
};

#endif

