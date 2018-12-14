
cmake_minimum_required(VERSION 2.8)
 
PROJECT(create-vti)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(create-vti main.cpp )
 
target_link_libraries(create-vti ${VTK_LIBRARIES})
