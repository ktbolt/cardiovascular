
from sv import *
import sv_vis as vis

#displat a box and a cylinder in a render window 
Solid.SetKernel('Parasolid')
#Solid.SetKernel('PolyData')
ctr = [0,0,0]
axis = [0,0,1]
a = Solid.pySolidModel()
a.Cylinder('cyl1', 1, 5, ctr, axis)
a.GetPolyData('cyl1_pd',0.5)

b = Solid.pySolidModel()
b.Cylinder('cyl2', 2, 2.0, ctr, axis)
b.GetPolyData('cyl2_pd',0.5)

ren, renwin = vis.initRen('demo')
act = vis.pRepos(ren,'cyl1_pd')
vis.polyDisplayWireframe(ren, 'cyl1_pd')
act2 = vis.pRepos(ren,'cyl2_pd')
vis.polyDisplayWireframe(ren, 'cyl2_pd')

wall = Solid.pySolidModel()
wall.Subtract('wall', 'cyl2', 'cyl1')
#wall.Subtract('wall', 'cyl1', 'cyl2')
#wall.Subtract('cyl1', 'cyl2', 'wall')
wall.GetPolyData('wall_pd', 0.5)
wall_act = vis.pRepos(ren,'wall_pd')

#wall.GetBoundaryFaces(90)
#wall.WriteNative("wall.vtp")
wall.WriteNative("wall")

vis.interact(ren, 1500000000)

