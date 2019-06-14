
cmake_minimum_required(VERSION 2.8)
 
PROJECT(sphere-to-image)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(sphere-to-image main.cpp )
 
target_link_libraries(sphere-to-image ${VTK_LIBRARIES})
