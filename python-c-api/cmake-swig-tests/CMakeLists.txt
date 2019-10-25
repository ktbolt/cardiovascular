cmake_minimum_required (VERSION 2.8)
project (Fibonacci)
set(CMAKE_VERBOSE_MAKEFILE 1)

#add_executable(Tutorial tutorial.cpp)
add_executable(Fibonacci fibonacci.cpp)

FIND_PACKAGE(SWIG REQUIRED)
INCLUDE(${SWIG_USE_FILE})

FIND_PACKAGE(PythonLibs)
INCLUDE_DIRECTORIES(${PYTHON_INCLUDE_PATH})
INCLUDE_DIRECTORIES(${CMAKE_CURRENT_SOURCE_DIR})

SET(CMAKE_SWIG_FLAGS "-Wall")

SET_SOURCE_FILES_PROPERTIES(fibonacci.i PROPERTIES CPLUSPLUS ON)
SET_PROPERTY(SOURCE fibonacci.i PROPERTY SWIG_FLAGS "-builtin")

SWIG_ADD_MODULE(fibonacci python fibonacci.i fibonacci.cpp)
SWIG_LINK_LIBRARIES(fibonacci ${PYTHON_LIBRARIES})
