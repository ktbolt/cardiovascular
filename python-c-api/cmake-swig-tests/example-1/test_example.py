import example

# python callback
def py_callback(i, s):
    print('py_callback(%d, %s)'%(i, s))

example.use_callback(py_callback)
