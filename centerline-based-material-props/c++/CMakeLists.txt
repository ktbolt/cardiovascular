
cmake_minimum_required(VERSION 2.8)
 
PROJECT(cl-material-props)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(cl-material-props main.cxx )
 
target_link_libraries(cl-material-props ${VTK_LIBRARIES})
