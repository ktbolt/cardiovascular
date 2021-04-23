
cmake_minimum_required(VERSION 2.8)
 
PROJECT(set-origin)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(set-origin main.cpp )
 
target_link_libraries(set-origin ${VTK_LIBRARIES})
