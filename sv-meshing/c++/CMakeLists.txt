
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11) 
 
PROJECT(meshing)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(meshing  
    main.cpp 
)
 
target_link_libraries(meshing ${VTK_LIBRARIES})
