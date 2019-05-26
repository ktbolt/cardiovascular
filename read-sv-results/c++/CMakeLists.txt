
cmake_minimum_required(VERSION 2.8)

set(CMAKE_CXX_STANDARD 11) 
 
PROJECT(read-results)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(read-results  
    main.cpp 
)
 
target_link_libraries(read-results ${VTK_LIBRARIES})
