%module example

// a typemap for the callback, it expects the argument to be an integer
// whose value is the address of an appropriate callback function
%typemap(in) void (*f)(int, const char*) {
    $1 = (void (*)(int i, const char*))PyLong_AsVoidPtr($input);;
}

%{
    void use_callback(void (*f)(int i, const char* str));
%}

%inline
%{

// a C function that accepts a callback
void use_callback(void (*f)(int i, const char* str))
{
    f(100, "callback arg");
}

%}

%pythoncode
%{

import ctypes

# a ctypes callback prototype
py_callback_type = ctypes.CFUNCTYPE(None, ctypes.c_int, ctypes.c_char_p)

def use_callback(py_callback):

    # wrap the python callback with a ctypes function pointer
    f = py_callback_type(py_callback)

    # get the function pointer of the ctypes wrapper by casting it to void* and taking its value
    f_ptr = ctypes.cast(f, ctypes.c_void_p).value

    _example.use_callback(f_ptr)

%}
