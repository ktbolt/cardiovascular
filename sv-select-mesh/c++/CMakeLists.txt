
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11) 
 
PROJECT(select-mesh)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(select-mesh  
    main.cpp 
    Graphics.h Graphics.cpp 
    Mesh.h Mesh.cpp
    SurfaceMesh.h SurfaceMesh.cpp 
    VolumeMesh.h VolumeMesh.cpp 
)
 
target_link_libraries(select-mesh ${VTK_LIBRARIES})
