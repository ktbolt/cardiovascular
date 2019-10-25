
from distutils.core import setup, Extension

setup(ext_modules=[Extension("_shape", 
                             sources=["shape.h", "shape.cpp" 
                                      "circle.h", "circle.cpp", 
                                      "square.h",  "square.cpp", 
                                       "shape.i", "shape_wrap.cxx"]
                            )])
