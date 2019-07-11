
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11) 
 
PROJECT(slice-results)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(slice-results  
    main.cpp 
    Centerlines.h Centerlines.cpp 
    Graphics.h Graphics.cpp 
    Mesh.h Mesh.cpp
    SurfaceMesh.h SurfaceMesh.cpp 
)
 
target_link_libraries(slice-results ${VTK_LIBRARIES})
