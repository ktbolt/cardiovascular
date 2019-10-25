
from distutils.core import setup, Extension

shape_module = Extension("_shape", 
  sources = ["shape.cpp", "circle.cpp", "square.cpp", "shape.i" ],
  headers = ["shape.h", "circle.h", "square.h" ],
  swig_opts = ['-c++'],
)

setup (
  name = 'shape',
  version = '0.1',
  author = "My name",
  description = """Simple Test""",
  ext_modules = [shape_module],
  py_modules = ["shape"],
)


