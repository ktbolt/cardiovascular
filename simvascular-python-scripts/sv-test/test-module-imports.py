"""
This script is used to test importing SV module names.
"""

import sv

from sv import contour

## This does not work.
# from contour import Contour

# import sv.contour.Contour as Contour


print(dir(sv))

## This works.
#print("Create Contour object")
c = sv.contour.Contour()

## This works.
c1 = contour.Contour()

#c2 = Contour()

