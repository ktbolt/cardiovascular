
#include <iostream>
#include <string>
#include <Python.h>

int main()
{
  // Set PYTHONPATH TO working directory
   setenv("PYTHONPATH",".",1);

   PyObject *pName, *pModule, *pDict, *pFunc, *pValue, *result;

   Py_Initialize();

   pName = PyUnicode_DecodeFSDefault((char*)"generate_1d_mesh");
   std::cout << "pName: " << pName << std::endl;

   // Load the module object
   pModule = PyImport_Import(pName);

   if (pModule != NULL) {
      std::cout << "Module is not null" << std::endl;
    } else {
      std::cout << "**** Module is null" << std::endl;
      return 1;
    }

   // pDict is a borrowed reference 
   pDict = PyModule_GetDict(pModule);

   // pFunc is also a borrowed reference 
   pFunc = PyDict_GetItemString(pDict, (char*)"crun");
   if (!PyCallable_Check(pFunc)) {
       printf("Can't find fpFunc\n");
   }

   // Set arguments.
   PyObject *args = PyTuple_New(1);
   pValue = PyUnicode_DecodeFSDefault("/Users/parkerda/software/ktbolt/cardiovascular/generate-1d-mesh/c-interface");
   PyTuple_SetItem(args, 0, pValue);

   PyObject *keywords = PyDict_New();

   std::string arg1("model_name"), val1("bob");
   PyDict_SetItemString(keywords, arg1.c_str(), PyUnicode_DecodeFSDefault(val1.c_str()));
   result = PyObject_Call(pFunc, args, keywords);

   PyErr_Print();

   Py_DECREF(args);
   Py_DECREF(keywords);
 
   if (result != nullptr) {
       auto uResult = PyUnicode_FromObject(result);
       auto sResult = std::string(PyUnicode_AsUTF8(uResult));
       printf("----- c++ result -----\n");
       printf("Result is '%s'\n", PyUnicode_AsUTF8(uResult));

      if ((sResult.find("error") != std::string::npos) || (sResult.find("ERROR") != std::string::npos)) {
          printf("**** ERROR: \n");
      }
   }

/*
   if (PyCallable_Check(pFunc)) {
       pArgs = PyTuple_New(2);

       pValue = PyUnicode_DecodeFSDefault("--model-name");
       PyTuple_SetItem(pArgs, 0, pValue);

       pValue = PyUnicode_DecodeFSDefault("bob");
       PyTuple_SetItem(pArgs, 1, pValue);

       //pValue = Py_BuildValue("(z)",(char*)"something");
       PyErr_Print();
       printf("Exectute function from c++ ...\n");
       presult = PyObject_CallObject(pFunc, pArgs);
       //presult = PyObject_CallObject(pFunc, pValue);
       PyErr_Print();
   } else {
       PyErr_Print();
   }

   printf("Result is %d\n", PyLong_AsLong(presult));
   Py_DECREF(pValue);
*/

   // Clean up
   Py_DECREF(pModule);
   Py_DECREF(pName);

   // Finish the Python Interpreter
   Py_Finalize();

    return 0;
}

