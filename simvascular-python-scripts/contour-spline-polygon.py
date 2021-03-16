
from sv import *
import sv_vis as vis

# Render this all to a viewer.
window_name = 'contour_spline_polygon'
ren, renwin = vis.initRen(window_name)

# Create a path.
control_points = []
control_points.append([2.0, 2.0, 0.0])
control_points.append([3.0, 3.0, 0.0])
control_points.append([4.0, 4.0, 0.0])
control_points.append([5.0, 5.0, 0.0])

print ("=============== create_contours ============")
p = Path.pyPath()
path_name = 'path'
p.NewObject(path_name)

## Set path points.
for i in range(0,len(control_points)):
    p.AddPoint(control_points[i])
p.CreatePath()
points = p.GetPathPosPts()
control_points = p.GetControlPts()
pos_pts = p.GetPathPosPts()

radius = 1.0

name = path_name + "_ct" + str(1)
print ("Create a circle Contour: " + name)
#Contour.SetContourKernel('Circle')
Contour.SetContourKernel('SplinePolygon')
c = Contour.pyContour()

## Find index of the point in pos_pts[] corresponding
#  to the ith control point.
#
min_d = 1e9
min_i = -1
i = 2
pt = control_points[i] 
for j in range(0,len(pos_pts)):
    pos = pos_pts[j]
    d = sum([(pt[k]-pos[k])*(pt[k]-pos[k]) for k in range(3)])
    if (d < min_d):
       min_d = d
       min_i = j
#__for j in range(0,len(pos_pts))
print(">>> min_d %g  min_id %d" % (min_d, min_i))

## Create a contour at the min_i th pos_pts[]. 
c.NewObject(name, path_name, min_i)

# Set control points.
center = control_points[i] 
cpts = [ 
[-1.42990141139223, -1.08194200123724, 11.880945203619143], 
[-1.11727986218069, -0.769320452025699, 12.114889163397541], 
[-2.34877475374378, -0.269265750073828, 11.766182836610824], 
[-1.06921808543848, -0.0952108211931773, 12.35797395335976], 
[-0.468609861272853, -1.90342502103886, 12.010503340279683], 
[-1.93096033879556, -1.97471795498859, 11.376394149498083], 
]

c.SetCtrlPts(cpts)
    
#c.SetCtrlPtsByRadius(center, radius)

# Creat contour.
c.Create()
print (">>> Contour center: " + str(c.Center()))

# Get countour PolyData
pname = name + 'p'
c.GetPolyData(pname)
#c.GetPolyData('ctp')
act = vis.pRepos(ren, pname)

#path_name_pd = path_name + 'pd'
#p.GetObject(path_name_pd)
#p.GetObject(path_name)

#act = vis.pRepos(ren, path_name_pd)

# Set the renderer to draw the solids as a wireframe.

vis.interact(ren, 15000)

