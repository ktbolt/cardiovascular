
cmake_minimum_required(VERSION 2.8)
 
PROJECT(create-flow-files)
 
find_package(VTK REQUIRED)
include(${VTK_USE_FILE})
 
add_executable(create-flow-files main.cpp vtkSVIntegrateAttributes.cxx vtkSVIntegrateAttributes.h vtkSVIntegrateFlowThroughSurface.cxx vtkSVIntegrateFlowThroughSurface.h vtkSVMiscModule.h vtkSVGlobals.h vtkSVSurfaceVectors.cxx vtkSVSurfaceVectors.h)
 
target_link_libraries(create-flow-files ${VTK_LIBRARIES})
