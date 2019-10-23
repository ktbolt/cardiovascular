
// Example of wrapping cos function from math.h with the Python-C-API. 
//
// Taken from: http://scipy-lectures.org/advanced/interfacing_with_c/interfacing_with_c.html

#include <Python.h>
#include <math.h>
#include <string>

//////////////////////////////////////////////////////
//          M o d u l e  F u n c t i o n s          //
//////////////////////////////////////////////////////
//
// Python API functions. 

//----------
// cos_func 
//----------
//
static PyObject * 
cos_func(PyObject* self, PyObject* args)
{
    double value;
    double answer;

    if (!PyArg_ParseTuple(args, "d", &value)) {
        return NULL;
    }

    answer = cos(value);

    return Py_BuildValue("f", answer);
}

////////////////////////////////////////////////////////
//          M o d u l e  D e f i n i t i o n          //
////////////////////////////////////////////////////////

static char* MODULE_NAME = "cos_module";

PyDoc_STRVAR(module_doc, "cos_module module functions.");

//----------------
// Module methods
//----------------
//
static PyMethodDef module_methods[] =
{
    {"cos_func", cos_func, METH_VARARGS, "evaluate the cosine"},

   {NULL, NULL, 0, NULL}

};

//---------------------------------------------------------------------------
//                           PYTHON_MAJOR_VERSION 3                         
//---------------------------------------------------------------------------

#if PY_MAJOR_VERSION >= 3

//---------------------
// Module definitation
//---------------------
//
static struct PyModuleDef module_definition =
{
    PyModuleDef_HEAD_INIT,
    MODULE_NAME, 
    module_doc,
    -1,
    module_methods
};

//-------------------
// PyInit_cos_module
//-------------------
// The initialization function called by the Python interpreter 
// when the module is loaded.
//
PyMODINIT_FUNC
PyInit_cos_module(void)
{
    return PyModule_Create(&module_definition);
}

//---------------------------------------------------------------------------
//                           PYTHON_MAJOR_VERSION 2                         
//---------------------------------------------------------------------------

#else

/* module initialization */
/* Python version 2 */
PyMODINIT_FUNC
initcos_module(void)
{
    (void) Py_InitModule(MODULE_NAME, module_methods);
}

#endif
