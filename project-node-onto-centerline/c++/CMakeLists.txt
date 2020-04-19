
cmake_minimum_required(VERSION 2.8)
 
PROJECT(project-nodes)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(project-nodes main.cxx )
 
target_link_libraries(project-nodes ${VTK_LIBRARIES})
