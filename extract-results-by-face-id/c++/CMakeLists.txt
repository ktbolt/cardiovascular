
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11) 
 
PROJECT(extract-faceid-results)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(extract-faceid-results
    main.cpp 
)
 
target_link_libraries(extract-faceid-results ${VTK_LIBRARIES})
