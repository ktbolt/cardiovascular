
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11) 
 
PROJECT(compare-results)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(compare-results  
    main.cpp 
)
 
target_link_libraries(compare-results ${VTK_LIBRARIES})
