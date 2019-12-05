import sv
import sv_vis as vis

import os

#help(sv.solid)
print(dir(sv))
#help(sv.solid.SolidModel)
#help(sv.SolidParaSolid)

# Set mesh kernel
sv.solid.set_kernel('PolyData')
sv.solid.set_kernel('Parasolid')

solid = sv.solid.SolidModel()
solid.new_object('cyl')
solid.set_vtk_polydata('cap')




