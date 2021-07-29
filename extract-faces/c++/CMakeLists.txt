
cmake_minimum_required(VERSION 2.8)
 
PROJECT(extract-faces)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(extract-faces main.cpp )
 
target_link_libraries(extract-faces ${VTK_LIBRARIES})
