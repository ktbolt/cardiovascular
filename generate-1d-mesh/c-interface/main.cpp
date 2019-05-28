
#include <iostream>
#include <string>
#include <Python.h>

int main(int argc, char *argv[])
{
   // Set PYTHONPATH TO working directory
   setenv("PYTHONPATH", ".", 1);
   //setenv("PYTHONPATH", "/Users/parkerda/software/ktbolt/cardiovascular/generate-1d-mesh", 1);
   std::cout << "arg[0]: " << argv[0] << std::endl;

   PyObject *pName, *pModule, *pDict, *pFunc, *pValue; 


   // wchar_t* progName = L"/Users/parkerda/vmtk/bin/python";
   //Py_SetProgramName(progName);

   Py_Initialize();

   auto version = Py_GetVersion();
   std::cout << "Python version: " << version << std::endl;

   auto wpath = Py_GetPath();
   std::wstring ws(wpath);
   std::string path( ws.begin(), ws.end() );
   std::cout << "Python path: " << path << std::endl;

   auto w_exec_prefix = Py_GetExecPrefix();
   std::wstring ws_exec_prefix(w_exec_prefix);
   std::string exec_prefix( ws_exec_prefix.begin(), ws_exec_prefix.end() );
   std::cout << "Python exec prefix: " << exec_prefix << std::endl;

   //auto w_home = Py_GetPythonHome();
   //std::wstring ws_home(w_home);
   //std::string home( ws_home.begin(), ws_home.end() );
   //std::cout << "Python home: " << home << std::endl;

   pName = PyUnicode_DecodeFSDefault((char*)"generate_1d_mesh");
   //pName = PyUnicode_FromString("generate_1d_mesh");
   std::cout << "pName: " << pName << std::endl;

   // Load the module object
   pModule = PyImport_Import(pName);

   if (pModule != NULL) {
      std::cout << "Module is not null" << std::endl;
    } else {
      std::cout << "**** Module is null" << std::endl;
      PyErr_Print();
      return 1;
    }

   // pDict is a borrowed reference 
   pDict = PyModule_GetDict(pModule);

   // pFunc is also a borrowed reference 
   pFunc = PyDict_GetItemString(pDict, (char*)"run_from_c");
   if (!PyCallable_Check(pFunc)) {
       printf("Can't find fpFunc\n");
   }

  // Create an argument containing the output directory.
  // This is used to write a script log file to the
  // solver job directory.
  //
  std::string outputDirectory = "/Users/parkerda/software/ktbolt/cardiovascular/generate-1d-mesh/c-interface";
  auto dummyArgs = PyTuple_New(1);
  auto dummyValue = PyUnicode_DecodeFSDefault(outputDirectory.c_str());
  PyTuple_SetItem(dummyArgs, 0, dummyValue);

  auto kwargs = PyDict_New();
  std::string first = "output_directory";
  std::string second = outputDirectory; 
  PyDict_SetItemString(kwargs, first.c_str(), PyUnicode_DecodeFSDefault(second.c_str()));

  first = "element_size";
  second = "0.5"; 
  PyDict_SetItemString(kwargs, first.c_str(), PyUnicode_DecodeFSDefault(second.c_str()));

  first = "num_time_steps";
  second = "20000"; 
  PyDict_SetItemString(kwargs, first.c_str(), PyUnicode_DecodeFSDefault(second.c_str()));

  first = "time_step";
  second = "0.00058"; 
  PyDict_SetItemString(kwargs, first.c_str(), PyUnicode_DecodeFSDefault(second.c_str()));

  auto result = PyObject_Call(pFunc, dummyArgs, kwargs);

  PyErr_Print();

  if (result) {
      auto uResult = PyUnicode_FromObject(result);
      auto sResult = std::string(PyUnicode_AsUTF8(uResult));
      if ((sResult.find("error") != std::string::npos) || (sResult.find("ERROR") != std::string::npos)) {
          std::cout << "ERROR: " << sResult << std::endl;
      }
  }

   // Finish the Python Interpreter
  Py_Finalize();

  return 0;
}

