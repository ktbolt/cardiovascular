import sv 
import sv_vis as vis
import vtk

print(dir(sv))

sv.Solid.SetKernel('PolyData')
sv.Solid.SetKernel('Parasolid')

axis = [1.0, 0.0, 0.0] 
center = [0.0, 0.0, 0.0] 

solid = sv.Solid.pySolidModel()

radius = 1.0
length = 10.0
solid.Cylinder('cylinder', radius, length, center, axis)
solid.GetPolyData('cylPolydata', 0.5)

ren, renwin = vis.initRen('demo')

vis.pRepos(ren,'cylPolydata')

## Display the contour.
##
vis.interact(ren, 1500000000)


