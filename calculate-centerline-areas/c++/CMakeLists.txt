
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11) 
 
PROJECT(centerline-areas)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(centerline-areas  
    main.cpp 
    Centerlines.h Centerlines.cpp 
    Graphics.h Graphics.cpp 
    Mesh.h Mesh.cpp
    Slice.h Slice.cpp 
    SurfaceMesh.h SurfaceMesh.cpp 
)
 
target_link_libraries(centerline-areas ${VTK_LIBRARIES})
