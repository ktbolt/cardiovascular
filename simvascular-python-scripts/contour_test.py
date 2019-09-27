"""
This script is used to test the SimVascular Contour module.
"""

import sv

#---------------------
# set_contour_kernel 
#---------------------

try:
    sv.Contour.set_contour_kernel()
except Exception as error:
    print(error)

try:
    sv.Contour.set_contour_kernel(10)
except Exception as error:
    print(error)

try:
    sv.Contour.set_contour_kernel("circle")
except Exception as error:
    print(error)

try:
    sv.Contour.set_contour_kernel("Circle")
except Exception as error:
    print(error)
else:
    print("Set contour kernel passed")


