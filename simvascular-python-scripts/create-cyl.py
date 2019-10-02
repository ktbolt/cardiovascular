from sv import *
import sv_vis as vis
import vtk
import math

## Create new path object
#
pt1 = [0.0, 0.0, 0.0]
#pt1 = [0.0, 1.0, 1.0]

#pt2 = [0.0, 1.0, 0.0]
#pt2 = [1.0, 0.0, 0.0]
#pt2 = [-1.0, 0.0, 0.0]
#pt2 = [1.0, 1.0, 0.0]
pt2 = [1.0, 2.0, 2.0]

pt3 = [0.0, 2.0, 0.0]
pt4 = [1.0, 2.0, 0.0]
pt5 = [2.0, 2.0, 0.0]

#pt1 = [ -0.1385,   1.0171,   0.3352] 
#pt2 = [-0.2418,   1.7405,  -1.9305] 

p = Path.pyPath()
p.NewObject('path1')
p.AddPoint(pt1)
p.AddPoint(pt2)
#p.AddPoint(pt3)
#p.AddPoint(pt4)
#p.AddPoint(pt5)
p.PrintPoints()

# Generate path points.
p.CreatePath()
points = p.GetPathPosPts()
control_pts = p.GetControlPts()
print(">>> control points: " + str(control_pts))
pos_pts = p.GetPathPosPts()
print(">>> pos points: " + str(len(pos_pts)))
num_pos_pts = len(pos_pts)

p.GetObject('path1')

Solid.SetKernel('PolyData')
dist_squared = vtk.vtkMath.Distance2BetweenPoints(pt1,pt2)
dist = math.sqrt(dist_squared)

axis = [pt2[i] - pt1[i] for i in range(0,3)]
vtk.vtkMath.Normalize(axis)
center = [(pt2[i] + pt1[i])/2.0 for i in range(0,3)]
print('[PathFitCyl] Axis: [{0:f} {1:f} {2:f}]'.format(axis[0], axis[1], axis[2]))
print('[PathFitCyl] Center: [{0:f} {1:f} {2:f}]'.format(center[0], center[1], center[2]))

Solid.SetKernel('PolyData')
solid = Solid.pySolidModel()

radius = 1.0
length = dist
solid.Cylinder('cylinder', radius, length, center, axis)
solid.GetPolyData('cylPolydata', 0.5)

ren, renwin = vis.initRen('demo')

vis.pRepos(ren,'cylPolydata')

## Create a circle contour.
#
for i in range(0,len(control_pts)):
    name = "ct" + str(i)
    print ("==================================")
    print ("Create a circle Contour: " + name)
    Contour.set_contour_kernel('Circle')
    c = Contour.pyContour()
    pt = control_pts[i] 

    min_d = 1e9
    min_i = -1
    for j in range(0,len(pos_pts)):
      pos = pos_pts[j]
      d = sum([(pt[k]-pos[k])*(pt[k]-pos[k]) for k in range(3)])
      if (d < min_d):
        min_d = d
        min_i = j
    #__for j in range(0,len(pos_pts))
    print(">>> min_d %g  min_id %d" % (min_d, min_i))

    c.new_object(name, 'path1', min_i)

    # Set control points.
    radius = 1.0
    center = control_pts[i] 
    #center = [0.0, 0.0, 0.0]
    c.SetCtrlPtsByRadius(center, radius)
    #print ("Radius: " + str(radius))
    #print ("Center: " + str(center))

    # Creat contour.
    c.Create()
    print ("Get contour properties ")
    print ("  Center: " + str(c.Center()))

    # Get countour PolyData
    pname = name + 'p'
    c.GetPolyData(pname)
    #c.GetPolyData('ctp')
    act = vis.pRepos(ren, pname)
    #vis.polyDisplayWireframe(ren, name)

## Display the contour.
##
vis.interact(ren, 1500000000)


