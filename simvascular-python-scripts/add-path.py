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



