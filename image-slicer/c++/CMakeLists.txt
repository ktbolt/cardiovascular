
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11) 
 
PROJECT(slice-image)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(slice-image
    main.cpp 
    Graphics.h Graphics.cpp 
    Image.h Image.cpp
)
 
target_link_libraries(slice-image ${VTK_LIBRARIES})
