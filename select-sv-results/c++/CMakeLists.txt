
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11) 
 
PROJECT(select-results)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(select-results  
    main.cpp 
    Graphics.h Graphics.cpp 
    Mesh.h 
    SurfaceMesh.h SurfaceMesh.cpp 
)
 
target_link_libraries(select-results ${VTK_LIBRARIES})
