from sv import *
import sv_vis as vis

## Create new path object
#
p = Path.pyPath()
p.NewObject('path1')
p.AddPoint([0.0,  0.0, 0.0])
p.AddPoint([1.0, 0.0, 0.0])
p.AddPoint([2.0, 0.0, 0.0])
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

ren, renwin = vis.initRen('demo')

## Create a circle contour.
#
for i in range(0,len(control_pts)):
    name = "ct" + str(i)
    print ("==================================")
    print ("Create a circle Contour: " + name)
    Contour.SetContourKernel('Circle')
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

    c.NewObject(name, 'path1', min_i)

    # Set control points.
    radius = 2.0
    center = control_pts[i] 
    #center = [0.0, 0.0, 0.0]
    c.SetCtrlPtsByRadius(center, radius)
    #print ("Radius: " + str(radius))
    #print ("Center: " + str(center))

    # Creat contour.
    c.Create()
    print ("Get contour properties ")
    print ("  Center: " + str(c.Center()))
    print ("  Area: " + str(c.Area()))

    # Get countour PolyData
    pname = name + 'p'
    c.GetPolyData(pname)
    #c.GetPolyData('ctp')
    act = vis.pRepos(ren, pname)
    #vis.polyDisplayWireframe(ren, name)

## Display the contour.
##
vis.interact(ren, 1500000000)


