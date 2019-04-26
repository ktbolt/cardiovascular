
#include <iostream>
#include <string>
#include <Python.h>

int main()
{
  PyObject *pName, *pModule;
  auto pythonModuleName = "generate_1d_mesh";

/*
  auto pythonHome = (wchar_t*)"/Users/parkerda/vmtk/bin/";
  Py_SetPythonHome(pythonHome);
  printf("python home: %s\n", Py_GetPythonHome());
  printf("get path: %s\n", Py_GetPath());
  printf("get prefix: %s\n", Py_GetPrefix());
  printf("get exec prefix: %s\n", Py_GetExecPrefix());
  printf("get prog full path: %s\n", Py_GetProgramFullPath());
*/

  Py_Initialize();

  PyRun_SimpleString("import sys");
  PyRun_SimpleString("print('sys path: ', sys.path)");

  PyRun_SimpleString("import generate_1d_mesh");

/*
  pName = PyUnicode_DecodeFSDefault(pythonModuleName);
  std::cout << "pName: " << pName << std::endl;

  pModule = PyImport_Import(pName);

  Py_DECREF(pName);

  if (pModule != NULL) {
      std::cout << "Module is not null" << std::endl;
  } else {
      std::cout << "**** Module is null" << std::endl;

  }
*/

    

}

