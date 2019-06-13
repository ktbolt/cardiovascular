
cmake_minimum_required(VERSION 2.8)
 
PROJECT(dicom-to-vti)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(dicom-to-vti main.cpp )
 
target_link_libraries(dicom-to-vti ${VTK_LIBRARIES})
