cmake_minimum_required(VERSION 3.8)

project(dummy)

find_package(PythonLibs 3 REQUIRED)
find_package(PythonInterp ${PYTHONLIBS_VERSION_STRING} REQUIRED)

find_package(SWIG REQUIRED)
include(${SWIG_USE_FILE})

if(PYTHONLIBS_VERSION_STRING MATCHES "^2.*$" )
    set(CMAKE_SWIG_FLAGS -classic)
else()
    set(CMAKE_SWIG_FLAGS -py3)
endif()

message("PYTHONLIBS_VERSION_STRING: ${PYTHONLIBS_VERSION_STRING}")
message("CMAKE_SWIG_FLAGS: ${CMAKE_SWIG_FLAGS}")

include_directories(example ${PYTHON_INCLUDE_PATH} ${CMAKE_CURRENT_SOURCE_DIR})

set_source_files_properties(example.i PROPERTIES CPLUSPLUS ON)

swig_add_library(example TYPE SHARED LANGUAGE python SOURCES example.i)
swig_link_libraries(example ${PYTHON_LIBRARIES})

enable_testing()
add_test(test1 ${PYTHON_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/test_example_wrapper.py)
