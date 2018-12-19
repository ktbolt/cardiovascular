set(lib ${SV_LIB_MODULE_TEST_NAME})
message(STATUS "SV_LIB_MODULE_TEST_NAME '${SV_LIB_MODULE_TEST_NAME}' ")

#set(export_directive parasolid)
#set(export_file_name svParasolidExports.h)

SET(CXXSRCS test.cxx )

SET(HDRS test .h ) 

add_library(${lib} SHARED ${CXXSRCS} test.cxx)

target_link_libraries(${lib})

