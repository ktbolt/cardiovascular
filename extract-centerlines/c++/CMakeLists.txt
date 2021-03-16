
cmake_minimum_required(VERSION 2.8)
 
PROJECT(extract-centerlines)

set(VMTK_DIR $ENV{HOME}/software/vmtk/vmtk-build)
message(STATUS "VMTK_DIR ${VMTK_DIR}") 

find_package(VMTK HINTS ${VMTK_DIR}/VMTK-Build REQUIRED )
include_directories(${VMTK_INCLUDE_DIRS})

find_package(ITK HINTS ${VMTK_DIR}/ITK-Build REQUIRED )
include_directories(${ITK_INCLUDE_DIRS})
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
link_directories(${VMTK_LIBRARY_DIRS})
#link_libraries(vtkvmtkCommon vtkvmtkComputationalGeometry vtkvmtkDifferentialGeometry vtkvmtkIO vtkvmtkITK vtkvmtkMisc vtkvmtkSegmentation )
add_executable(extract-centerlines main.cpp )
 
target_link_libraries(extract-centerlines ${VTK_LIBRARIES} ${ITK_LIBRARIES} ${VTK_LIBRARIES} ${VMTK_LIBRARIES} vtkvmtkCommon vtkvmtkComputationalGeometry vtkvmtkContrib vtkvmtkDifferentialGeometry vtkvmtkIO vtkvmtkITK vtkvmtkMisc vtkvmtkSegmentation nl tet)

#target_link_libraries(extract-centerlines ${VTK_LIBRARIES} ${ITK_LIBRARIES} ${VTK_LIBRARIES} ${VMTK_LIBRARIES} ITKCommon vtkvmtkCommon vtkvmtkComputationalGeometry vtkvmtkContrib vtkvmtkDifferentialGeometry vtkvmtkIO vtkvmtkITK vtkvmtkMisc vtkvmtkSegmentation nl tet)
