
cmake_minimum_required(VERSION 2.8.12)

## Set the version of external packages used by the module.
#
set(SV_EXTERNALS_VERSION_NUMBER "2018.05" CACHE STRING "SimVascular Externals Release Version")

## Set the names of the Parasolid module shared libraries.
#
project(SV_PLUGIN)
set(PLUGIN_NAME TestPlugin)
set(SV_LIB_MODULE_TEST_NAME _simvascular_module_test)
message(STATUS "CMAKE_PREFIX_PATH '${CMAKE_PREFIX_PATH}' ")

## Get the SimVascular variables for libraries, includes, etc.
#
set(CMAKE_PREFIX_PATH /Applications/SimVascular.app/Contents/Resources/lib/cmake/simvascular-2018.11/)
find_package(SimVascular REQUIRED)
include_directories(${SimVascular_INCLUDE_DIRS})
message(STATUS "SimVascular_DIR '${SimVascular_DIR}' ")
message(STATUS "CMAKE_PREFIX_PATH '${CMAKE_PREFIX_PATH}' ")


## This enables downloading externals.
#
#include(${SimVascular_USE_EXTERNALS_FILE})

set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${SimVascular_C_FLAGS}")
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${SimVascular_CXX_FLAGS}")

include_directories(
  "${CMAKE_SOURCE_DIR}/Code"
  "${CMAKE_BINARY_DIR}/Code"
  )

add_subdirectory("${CMAKE_SOURCE_DIR}/Code/")

