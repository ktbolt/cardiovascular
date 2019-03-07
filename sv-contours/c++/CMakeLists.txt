
cmake_minimum_required(VERSION 2.8)
 
PROJECT(sv-contours)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(sv-contours main.cpp )
 
target_link_libraries(sv-contours ${VTK_LIBRARIES})
